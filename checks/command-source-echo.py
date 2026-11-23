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


def dwell_after_crossing(wave, level, start):
    """Time continuously beyond an AC threshold on a single normalized edge."""
    below = np.flatnonzero((time > start) & (wave < level))
    if not len(below):
        return time[-1] - start, "simulation end"
    i = below[0]
    end = time[i-1] + dt * (wave[i-1] - level) / (wave[i-1] - wave[i])
    return end - start, "recrossing"


def screen(board, timing, archive, out, ioctrl, dwell=False, launch_window=False, slew_screen=False):
    edges = model["fixture"](archive, board, with_reflection=True, ioctrl=ioctrl)
    rows = {row["net"]: row for row in csv.DictReader(timing)}
    @lru_cache(None)
    def pin(name, up, cap):
        return at_receiver(edges[up], cap, float(rows[name]["estimated_flight_ps"]))

    writer = csv.writer(out, lineterminator="\n")
    if slew_screen:
        writer.writerow(("net", "ioctrl", "load_CK_CKn_CA_pF", "edge", "clock_slew_V_ns",
                         "nominal_CA_setup_V_ns", "nominal_CA_hold_V_ns", "setup_lag_mV",
                         "hold_lead_mV", "setup_needs_tangent", "hold_needs_tangent",
                         "nominal_setup_in_table62", "nominal_hold_in_table62"))
    elif launch_window:
        writer.writerow(("net", "ioctrl", "load_polarity_cases", "max_source_setup_ps",
                         "max_source_hold_ps", "earliest_capture_ps", "latest_capture_ps",
                         "setup_limiting_load_edge", "hold_limiting_load_edge"))
    elif dwell:
        writer.writerow(("net", "load_CK_CKn_CA_pF", "edge", "modeled_tVAC_ps", "interval_end",
                         "table64_largest_tVAC_ps", "modeled_excess_over_213_ps"))
    else:
        writer.writerow(("net","load_CK_CKn_CA_pF","edge","first_echo_headroom_ps","first_setup_ps",
                     "echo_setup_ps","setup_delta_ps","first_hold_ps","echo_hold_ps","hold_delta_ps"))
    cross = model["crossing"]
    names = ("DDR_BA0", "DDR_CKE", "DDR_WEn")
    if launch_window or slew_screen:
        names = sorted(name for name, row in rows.items() if row["current_mm"] != "open"
                       and name not in ("DDR_CK", "DDR_CKn", "DDR_RESETn"))
    for name in names:
        setup_bounds, hold_bounds = [], []
        for ck, ckn, cap in model["capacitances"]():
            clock = [cross(time, p+n, vdd) for p,n in zip(pin("DDR_CK",True,ck), pin("DDR_CKn",False,ckn))]
            for up in (True,False):
                ac, dc = zip(*[(cross(time,w,vdd/2+.135),cross(time,w,vdd/2-.090)) for w in pin(name,up,cap)])
                if slew_screen:
                    # Falling pin() gives the positive voltage change from the high state.
                    wave = pin(name, up, cap)[1]
                    mid = cross(time, wave, vdd / 2)
                    t_ac, t_dc = ac[1], dc[1]
                    clock_wave = pin("DDR_CK", True, ck)[1] + pin("DDR_CKn", False, ckn)[1] - vdd
                    t_lo = cross(time, clock_wave, -.180)
                    t_hi = cross(time, clock_wave, .180)
                    ck_rate = 360 / (t_hi - t_lo)
                    setup_rate, hold_rate = 135 / (t_ac - mid), 90 / (mid - t_dc)
                    # The model linearly interpolates waveform samples. Interior extrema
                    # of the difference from the secant occur at sample times.
                    setup_samples = (time > mid) & (time < t_ac)
                    hold_samples = (time > t_dc) & (time < mid)
                    lag = max(0., np.max((vdd/2 - wave[setup_samples])*1000 +
                                         (time[setup_samples]-mid)*setup_rate, initial=0.))
                    lead = max(0., np.max((wave[hold_samples]-vdd/2)*1000 -
                                          (time[hold_samples]-mid)*hold_rate, initial=0.))
                    writer.writerow((name, hex(ioctrl), f"{ck:g}/{ckn:g}/{cap:g}",
                                     "rise" if up else "fall", *(round(x, 6) for x in
                                     (ck_rate, setup_rate, hold_rate, lag, lead)),
                                     lag > 1e-8, lead > 1e-8,
                                     1 <= ck_rate <= 4 and .4 <= setup_rate <= 2,
                                     1 <= ck_rate <= 4 and .4 <= hold_rate <= 2))
                    continue
                if dwell:
                    # Table 64 lists 213 ps as the largest AC135 tVAC requirement at DDR3L-800.
                    duration, reason = dwell_after_crossing(pin(name, up, cap)[1], vdd/2+.135, ac[1])
                    writer.writerow((name, f"{ck:g}/{ckn:g}/{cap:g}", "rise" if up else "fall",
                                     round(duration, 4), reason, 213, round(duration - 213, 4)))
                    continue
                setup = [365+a-c for a,c in zip(ac,clock)]
                hold = [285+c-d for c,d in zip(clock,dc)]
                if launch_window:
                    case = f"{ck:g}/{ckn:g}/{cap:g} " + ("rise" if up else "fall")
                    # Upper envelope of the tabulated DDR3L-800 slew deratings.
                    setup_bounds.append((setup[1] + 108, case))
                    hold_bounds.append((hold[1] + 95, case))
                    continue
                earliest = min(edges[e][1]+3*float(rows[n]["estimated_flight_ps"])-arrival
                               for e,n,arrival in [(True,"DDR_CK",clock[0]),(False,"DDR_CKn",clock[0]),(up,name,ac[0])])
                writer.writerow((name,f"{ck:g}/{ckn:g}/{cap:g}","rise" if up else "fall",
                                 *(round(x,4) for x in (earliest,*setup,setup[1]-setup[0],*hold,hold[1]-hold[0]))))

        if launch_window:
            setup, setup_case = max(setup_bounds)
            hold, hold_case = max(hold_bounds)
            writer.writerow((name, hex(ioctrl), len(setup_bounds), round(setup, 3), round(hold, 3),
                             round(setup, 3), round(2500 - hold, 3), setup_case, hold_case))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board",type=Path)
    parser.add_argument("timing",type=Path)
    parser.add_argument("ti_ibis",type=Path)
    parser.add_argument("--ioctrl", type=lambda s: int(s, 0), choices=(0, 0x273), default=0x273,
                        help="Low ten bits of all three command IOCTRL registers")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--launch-window", action="store_true", help="Screen capture phase for all routed synchronous commands at DDR3L-800")
    modes.add_argument("--slew-screen", action="store_true", help="Check nominal receiver slopes and the Micron tangent-line conditions")
    modes.add_argument("--dwell", action="store_true", help="Report receiver AC135 threshold dwell for isolated edges")
    args = parser.parse_args()
    with args.timing.open() as timing:
        screen(json.loads(args.board.read_bytes()),timing,args.ti_ibis,sys.stdout,args.ioctrl,args.dwell,args.launch_window,args.slew_screen)
