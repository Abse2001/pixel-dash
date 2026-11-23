"""First incident wave at a capacitive DDR3L receiver, using TI's nominal 50-ohm V/T fixtures."""
import argparse
import csv
import itertools
import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from scipy.signal import lfilter

VDD = 1.35
Z = 50.0
DT_PS = 1.0
TIME = np.arange(-1000., 2001., DT_PS)


def number(text):
    scale = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3}
    return float(text[:-1]) * scale[text[-1]] if text[-1] in scale else float(text)


def fixture(archive, board, *, with_reflection=False, ioctrl=0x273, clock=False):
    """Get precharged-line edges. Rising uses a grounded fixture, falling a VDD fixture."""
    with ZipFile(archive) as files:
        source = files.read("sprm552c.ibs").decode("latin1")
    parts = {e["name"]: e for e in board if e["type"] == "source_component" and e.get("name")}
    if (parts["U1"].get("manufacturer_part_number") != "AM3354BZCZD80"
            or parts["U_DDR"].get("manufacturer_part_number") != "MT41K512M16VRP-107 IT:P"
            or parts["R_VTP"].get("resistance") != 49.9):
        raise ValueError("Fitted processor, TwinDie memory or VTP resistor differs from the screen")
    cpu = parts["U1"]["source_component_id"]
    pins = {p["source_port_id"]: p["name"] for p in board if p["type"] == "source_port"
            and p["source_component_id"] == cpu}
    pin_table = re.search(r"(?ims)^\[Pin\][^\n]*\n(.*?)^\[", source)[1]
    mapping = {v[0]: (v[1], v[2]) for line in pin_table.splitlines()
               if len(v := line.split()) >= 3}
    checked = set()
    for e in board:
        name = e.get("name") or ""
        if e["type"] != "source_trace" or not name.startswith("DDR_") or name.startswith("DDR_D"):
            continue
        ball, = [pins[p] for p in e["connected_source_port_ids"] if p in pins]
        if mapping.get(ball) != (name.upper(), "Selector_4"):
            raise ValueError(f"Wrong IBIS selector on {name} at {ball}")
        checked.add(name)
    if len(checked) != 28:
        raise ValueError(f"Expected 28 clock, address and control nets, found {len(checked)}")
    selector = re.search(r"(?ims)^\[Model Selector\]\s+Selector_4\s*$(.*?)^\[", source)[1]
    # TRM Table 9-97 assigns independent five-bit drive fields to CA and CK.
    field = ((ioctrl >> 5) if clock else ioctrl) & 0x1f
    driver, description = {
        0x13: ("Model_364", "fast, 1.00*RExt,IND,10%,SR10"),
        0x00: ("Model_370", "fastest, 1.60*RExt,IND,10%,SR00"),
        0x0b: ("Model_366", "slow, 1.00*RExt,IND,10%,SR01"),
        0x0c: ("Model_359", "slow, 0.88*RExt,IND,10%,SR01"),
    }[field]
    label = f"{driver} 3-STATE,1.35V,ODT off,{description}"
    if not re.search(r"(?im)^" + re.escape(label), selector):
        raise ValueError(f"Unexpected 1.35 V command driver selector for {ioctrl:#x}")
    model = re.search(r"(?ims)^\[model\]\s+" + driver + r"\s*$(.*?)^\[model\]", source)[1]
    fixtures = {}
    for name, table in re.findall(r"(?ims)^\[(Rising Waveform|Falling Waveform)\](.*?)(?=^\[|\Z)", model):
        bias = float(re.search(r"(?im)^V_fixture\s*=\s*([.\d]+)", table)[1])
        up = name.lower().startswith("rising")
        if float(re.search(r"(?im)^R_fixture\s*=\s*([.\d]+)", table)[1]) != Z:
            raise ValueError("Unexpected IBIS fixture impedance")
        data = [line.split() for line in table.splitlines() if re.match(r"^\s*\d", line)]
        t = np.array([number(row[0]) * 1e12 for row in data])
        volts = np.array([number(row[1]) for row in data])
        if (up, bias) in fixtures:
            raise ValueError("Duplicate fixture bias for this driver edge")
        fixtures[up, bias] = t, volts
    if set(fixtures) != {(up, bias) for up in (False, True) for bias in (0., VDD)}:
        raise ValueError("Missing complementary 50-ohm fixture")
    result = {}
    for up in (False, True):
        t, volts = fixtures[up, 0. if up else VDD]
        change = (volts - volts[0]) * (1 if up else -1)
        mid = crossing(t, change, change[-1]/2)
        # Refer both edge times to their own incident 50% swing. The IBIS
        # time axes do not specify the controller's relative launch time.
        t = t - mid
        first = np.flatnonzero(change != 0)[0]
        incident = np.interp(TIME, t, change)
        if with_reflection:
            # The reflection of an incident perturbation at the source is the
            # secant between the two V/T fixtures on their supplied time axes.
            low, high = (np.interp(TIME + mid, *fixtures[up, rail]) for rail in (0., VDD))
            reflection = 2 * (high - low) / VDD - 1
            if np.max(np.abs(reflection)) >= 1:
                raise ValueError("Fixture secant implies an active or singular source")
            result[up] = incident, t[first-1], reflection
        else:
            result[up] = incident, t[first-1]
    if set(result) != {False, True}:
        raise ValueError("Missing precharged rising/falling 50-ohm fixtures")
    return result


def crossing(t, values, level):
    hits = np.flatnonzero((values[:-1] < level) & (values[1:] >= level))
    if len(hits) != 1:
        raise ValueError(f"Expected one rising crossing of {level:g}, got {len(hits)}")
    i = hits[0]
    return t[i] + (t[i+1]-t[i]) * (level-values[i]) / (values[i+1]-values[i])


def capacitances():
    # Vertices of the TwinDie Table 7 load region. The last coordinate is
    # command C, the first two are CK and CKn. All capacitances are in pF.
    normals = np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1],
                        [1,-1,0],[-1,1,0],[-.5,-.5,1],[.5,.5,-1]])
    limits = np.array([4.,-2.4,4.,-2.4,4.6,-2.4,.3,.3,.8,.8])
    vertices = set()
    for triple in itertools.combinations(range(len(limits)), 3):
        matrix = normals[list(triple)]
        if abs(np.linalg.det(matrix)) < 1e-8:
            continue
        point = np.linalg.solve(matrix, limits[list(triple)])
        if (normals @ point <= limits + 1e-9).all():
            vertices.add(tuple(np.round(point, 6)))
    return sorted(vertices)


def screen(csv_path, edges, out):
    with csv_path.open() as source:
        rows = {r["net"]: r for r in csv.DictReader(source)}
    clock_flights = [float(rows[n]["estimated_flight_ps"]) for n in ("DDR_CK", "DDR_CKn")]

    @lru_cache(None)
    def wave(up, cap, flight):
        change, start = edges[up]
        incident = np.interp(TIME - flight, TIME, change)
        # First-incident response H(s)=2/(1+s Z C). Discretize the linear ramp
        # between consecutive input samples exactly over the time step.
        tau = Z*cap
        a = np.exp(-DT_PS/tau)
        beta = 1 - (tau/DT_PS)*(1-a)
        wave = lfilter(2*np.array([beta, 1-a-beta]), [1., -a], incident)
        return wave, start + 3*flight

    cases = capacitances()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(("signal", "corner_edges", "max_setup_at_reference_slew_ps", "setup_CA_edge",
                     "setup_loads_CK_CKn_CA_pF", "min_pre_echo_headroom_for_setup_case_ps",
                     "max_hold_at_reference_slew_ps", "hold_CA_edge", "hold_loads_CK_CKn_CA_pF",
                     "min_pre_echo_headroom_for_hold_case_ps", "setup_cases_after_echo", "hold_cases_after_echo", "scope"))
    for name, row in sorted(rows.items()):
        if name in ("DDR_CK", "DDR_CKn", "DDR_RESETn") or row["current_mm"] == "open":
            continue
        flight = float(row["estimated_flight_ps"])
        setup, hold = [], []
        for ck, ckn, cap in cases:
            p, pe = wave(True, ck, clock_flights[0])
            n, ne = wave(False, ckn, clock_flights[1])
            # CK rising, CKn falling from VDD: differential zero at p+n=VDD.
            tck = crossing(TIME, p+n, VDD)
            for up in (True, False):
                ca, echo = wave(up, cap, flight)
                tac = crossing(TIME, ca, VDD/2 + .135)
                tdc = crossing(TIME, ca, VDD/2 - .090)
                label = ("rise" if up else "fall", f"{ck:g}/{ckn:g}/{cap:g}")
                setup.append((365+tac-tck, *label, min(pe-tck, ne-tck, echo-tac)))
                hold.append((285+tck-tdc, *label, min(pe-tck, ne-tck, echo-tdc)))
        a, b = max(setup), max(hold)
        writer.writerow((name, len(setup), round(a[0],3), *a[1:3], round(a[3],3),
                         round(b[0],3), *b[1:3], round(b[3],3), sum(v[3] <= 0 for v in setup), sum(v[3] <= 0 for v in hold),
                         "first incident; launch/receiver margin open"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path)
    parser.add_argument("command_timing", type=Path)
    parser.add_argument("ti_zcz_ibis_zip", type=Path)
    args = parser.parse_args()
    screen(args.command_timing, fixture(args.ti_zcz_ibis_zip, json.loads(args.board.read_bytes())), sys.stdout)
