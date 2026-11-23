"""Compare nominal DDR_A8 receiver threshold crossings for stepped transmission lines."""
import argparse
import csv
import gzip
import json
import math
import runpy
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
ECHO = runpy.run_path(str(ROOT / "checks" / "command-source-echo.py"))
FIXTURE = ECHO["model"]
TIME = FIXTURE["TIME"]
DT = FIXTURE["DT_PS"]
DEPTH = dict(zip(("F.Cu", "In2.Cu", "In3.Cu", "B.Cu"), (0., .6667, .8923, 1.559)))

def conductor_sections(geometry):
    parts = [item for item in geometry if item["net"] == "DDR_A8"]
    nodes = defaultdict(list)
    neighbors = defaultdict(list)

    def node(layer, xy):
        for key in nodes[layer]:
            if math.dist(key[1:], xy) <= .000005:
                return key
        key = (layer, *xy)
        nodes[layer].append(key)
        return key

    def connect(a, b, length, kind, width):
        neighbors[a].append((b, length, kind, width))
        neighbors[b].append((a, length, kind, width))

    for track in (item for item in parts if item["kind"] == "track"):
        layer = track["layer"]
        a, b = track["start"], track["end"]
        kind = "outer" if layer in ("F.Cu", "B.Cu") else "inner"
        connect(node(layer,a), node(layer,b), math.dist(a,b), kind, track["width"])
    for via in (item for item in parts if item["kind"] == "via"):
        contacts = [key for group in nodes.values() for key in group
                    if math.dist(key[1:], via["pos"]) <= .000005]
        a, b = contacts
        connect(a, b, abs(DEPTH[a[0]] - DEPTH[b[0]]), "via", 0.)
    cpu = next(item for item in parts if item.get("ref") == "U1")
    location, = [key for key in neighbors if len(neighbors[key]) == 1
                 and math.dist(key[1:], cpu["pos"]) < min(cpu["size"])/2]
    sections = []
    seen = set()
    while location not in seen:
        seen.add(location)
        following = [edge for edge in neighbors[location] if edge[0] not in seen]
        if not following:
            break
        (location, length, kind, width), = following
        if sections and sections[-1][1:] == [kind, width]:
            sections[-1][0] += length
        else:
            sections.append([length, kind, width])
    assert len(seen) == len(neighbors)
    return sections

def receiver(edge, sections, capacitance):
    """Lossless line junctions, affine source reflection and lumped receiver capacitance."""
    drive, _, gamma = edge
    ohms = np.array([z for flight,z in sections])
    samples = np.array([flight / DT for flight,z in sections])
    delay = np.floor(samples).astype(int)
    fraction = samples - delay
    assert min(delay) >= 1, "Each electrical section needs at least one time step."
    source_ohms = 50 * (1 + gamma) / (1 - gamma)
    drive = drive * (ohms[0]/50) * (source_ohms+50) / (source_ohms+ohms[0])
    gamma = (source_ohms-ohms[0]) / (source_ohms+ohms[0])
    padding = max(delay)+2
    right = np.zeros((len(TIME)+padding, len(ohms)))
    left = np.zeros_like(right)
    indices = np.arange(len(ohms))
    voltage = np.zeros(len(TIME))
    last_voltage = last_incident = 0.
    tau = ohms[-1]*capacitance
    alpha = np.exp(-DT/tau)
    beta = 1 - tau/DT*(1-alpha)
    for t in range(len(TIME)):
        position = t + padding
        at = position - delay
        incoming_right = (1-fraction)*right[at,indices] + fraction*right[at-1,indices]
        incoming_left = (1-fraction)*left[at,indices] + fraction*left[at-1,indices]
        right[position,0] = drive[t] + gamma[t]*incoming_left[0]
        junction = 2*(incoming_right[:-1]*ohms[1:] + incoming_left[1:]*ohms[:-1])/(ohms[:-1]+ohms[1:])
        left[position,:-1] = junction - incoming_right[:-1]
        right[position,1:] = junction - incoming_left[1:]
        last_voltage = alpha*last_voltage + 2*(beta*incoming_right[-1] + (1-alpha-beta)*last_incident)
        last_incident = incoming_right[-1]
        left[position,-1] = last_voltage - last_incident
        voltage[t] = last_voltage
    return voltage

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("geometry", type=Path)
    parser.add_argument("ti_zcz_ibis_zip", type=Path)
    args = parser.parse_args()
    with gzip.open(ROOT / "studies/four-layer-through/board.circuit.json.gz", "rt") as stream:
        components = json.load(stream)
    edges = FIXTURE["fixture"](args.ti_zcz_ibis_zip, components, with_reflection=True, ioctrl=0x318)
    for edge in edges.values():
        reference = ECHO["at_receiver"](edge, 3., 200., 50.)[1]
        np.testing.assert_allclose(receiver(edge, [(200.,50.)], 3.), reference, atol=1.e-6, rtol=0)
    geometry = conductor_sections(json.loads(args.geometry.read_text()))
    out = csv.writer(sys.stdout, lineterminator="\n")
    out.writerow(("profile","edge","cap_pF","ac_last_crossing_ps","dc_last_crossing_ps","vref_last_crossing_ps"))
    for profile in ("isolated", "coplanar"):
        sections = []
        for length,kind,width in geometry:
            if kind == "via":
                speed, impedance = 6.6, 50.
            elif kind == "outer":
                speed, impedance = 5.8669, 54.987
            elif width == .102:
                speed, impedance = 7.0571, (72.564 if profile=="isolated" else 62.336)
            else:
                assert abs(width-.220) < 1.e-6
                speed, impedance = 7.06, (53.186 if profile=="isolated" else 46.501)
            sections.append((length*speed, impedance))
        for rising in (True,False):
            for cap in sorted({case[2] for case in FIXTURE["capacitances"]()}):
                wave = receiver(edges[rising], sections, cap)
                result = []
                for level in (.675+.135, .675-.09, .675):
                    index = np.flatnonzero((wave[1:] >= level) & (wave[:-1] < level))[-1]
                    crossing = TIME[index] + (level-wave[index])/(wave[index+1]-wave[index])*DT
                    result.append(round(crossing,4))
                out.writerow((profile, "rise" if rising else "fall", cap, *result))
if __name__ == "__main__":
    main()
