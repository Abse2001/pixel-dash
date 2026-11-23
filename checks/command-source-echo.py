"""Single-edge command reflection screen from complementary TI 50-ohm fixtures."""
import argparse
import csv
import json
import runpy
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

model = runpy.run_path(str(Path(__file__).with_name("command-first-arrival.py")))
time = model["TIME"]
dt = model["DT_PS"]
vdd = model["VDD"]


def delay(wave, ps):
    return np.interp(time - ps, time, wave, left=0.)


def load_voltage(incident, cap):
    tau = model["Z"] * cap
    a = np.exp(-dt / tau)
    beta = 1 - tau / dt * (1 - a)
    return lfilter(2 * np.array([beta, 1-a-beta]), [1., -a], incident)


def at_receiver(edge, cap, flight):
    drive, _, gamma = edge
    # At a capacitive load the returning wave is terminal voltage minus
    # incident voltage. Propagate it back to the source and reflect it there.
    if not np.isfinite(flight) or flight <= dt:
        raise ValueError("Flight must exceed one positive time step")
    incident = delay(drive, flight)
    first = load_voltage(incident, cap)
    terminal = first.copy()
    reflected = first - incident
    round_trips = int(np.ceil((time[-1] - time[0]) / (2 * flight)))
    for _ in range(round_trips):
        incident = delay(gamma * delay(reflected, flight), flight)
        if np.max(np.abs(incident)) < 1e-12:
            break
        voltage = load_voltage(incident, cap)
        terminal += voltage
        reflected = voltage - incident
    return first, terminal


def screen(board, timing, archive, out, ioctrl):
    edges = model["fixture"](archive, board, with_reflection=True, ioctrl=ioctrl)
    rows = {row["net"]: row for row in csv.DictReader(timing)}
    @lru_cache(None)
    def pin(name, up, cap):
        return at_receiver(edges[up], cap, float(rows[name]["estimated_flight_ps"]))

    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(("net","load_CK_CKn_CA_pF","edge","first_echo_headroom_ps","first_setup_ps",
                     "echo_setup_ps","setup_delta_ps","first_hold_ps","echo_hold_ps","hold_delta_ps"))
    cross = model["crossing"]
    for name in ("DDR_BA0", "DDR_CKE", "DDR_WEn"):
        for ck, ckn, cap in model["capacitances"]():
            clock = [cross(time, p+n, vdd) for p,n in zip(pin("DDR_CK",True,ck), pin("DDR_CKn",False,ckn))]
            for up in (True,False):
                ac, dc = zip(*[(cross(time,w,vdd/2+.135),cross(time,w,vdd/2-.090)) for w in pin(name,up,cap)])
                setup = [365+a-c for a,c in zip(ac,clock)]
                hold = [285+c-d for c,d in zip(clock,dc)]
                earliest = min(edges[e][1]+3*float(rows[n]["estimated_flight_ps"])-arrival
                               for e,n,arrival in [(True,"DDR_CK",clock[0]),(False,"DDR_CKn",clock[0]),(up,name,ac[0])])
                writer.writerow((name,f"{ck:g}/{ckn:g}/{cap:g}","rise" if up else "fall",
                                 *(round(x,4) for x in (earliest,*setup,setup[1]-setup[0],*hold,hold[1]-hold[0]))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board",type=Path)
    parser.add_argument("timing",type=Path)
    parser.add_argument("ti_ibis",type=Path)
    parser.add_argument("--ioctrl", type=lambda s: int(s, 0), choices=(0, 0x273), default=0x273,
                        help="Low ten bits of all three command IOCTRL registers")
    args = parser.parse_args()
    with args.timing.open() as timing:
        screen(json.loads(args.board.read_bytes()),timing,args.ti_ibis,sys.stdout,args.ioctrl)
