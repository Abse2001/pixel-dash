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


def delay(wave, ps):
    return np.interp(time - ps, time, wave, left=0.)


def load_voltage(incident, cap, impedance):
    tau = impedance * cap
    a = np.exp(-dt / tau)
    beta = 1 - tau / dt * (1 - a)
    return lfilter(2 * np.array([beta, 1-a-beta]), [1., -a], incident)


def at_receiver(edge, cap, flight, impedance=50.):
    drive, _, gamma = edge
    if impedance != model["Z"]:
        # Renormalize the affine source scattering law b = drive + gamma*a
        # from the 50-ohm IBIS fixtures to the trial line impedance.
        source_ohms = model["Z"] * (1 + gamma) / (1 - gamma)
        drive = drive * (impedance / model["Z"]) * (source_ohms + model["Z"]) / (source_ohms + impedance)
        gamma = (source_ohms - impedance) / (source_ohms + impedance)
    # At a capacitive load the returning wave is terminal voltage minus
    # incident voltage. Propagate it back to the source and reflect it there.
    if not np.isfinite(flight) or flight <= dt:
        raise ValueError("Flight must exceed one positive time step")
    incident = delay(drive, flight)
    first = load_voltage(incident, cap, impedance)
    terminal = first.copy()
    reflected = first - incident
    round_trips = int(np.ceil((time[-1] - time[0]) / (2 * flight)))
    for _ in range(round_trips):
        incident = delay(gamma * delay(reflected, flight), flight)
        if np.max(np.abs(incident)) < 1e-12:
            break
        voltage = load_voltage(incident, cap, impedance)
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


def screen(board, timing, archive, out, ioctrl, dwell=False, launch_window=False, slew_screen=False, receiver_window=False, corner="typ", jlc_channel=False, receiver_vref=None):
    _, vdd = model["FIXTURE_CORNERS"][corner]
    edges = model["fixture"](archive, board, with_reflection=True, corner=corner, ioctrl=ioctrl)
    clock_edges = edges if ioctrl & 31 == (ioctrl >> 5) & 31 else model["fixture"](
        archive, board, with_reflection=True, corner=corner, ioctrl=ioctrl, clock=True)
    rows = {row["net"]: row for row in csv.DictReader(timing)}
    @lru_cache(None)
    def pin(name, up, cap):
        driver = clock_edges if name in ("DDR_CK", "DDR_CKn") else edges
        impedance = model["Z"]
        if jlc_channel:
            impedance = 99.26 / 2 if name in ("DDR_CK", "DDR_CKn") else 54.16
        return at_receiver(driver[up], cap, float(rows[name]["estimated_flight_ps"]), impedance)

    writer = csv.writer(out, lineterminator="\n")
    if receiver_window:
        writer.writerow(("net", "load_CK_CKn_CA_pF", "edge", "clock_V_ns", "effective_setup_V_ns",
                         "effective_hold_V_ns", "ac_dwell_ps", "earliest_capture_ps",
                         "latest_capture_ps", "scope", *(("clock_crossing_V", "VIX_margin_mV")
                         if receiver_vref is not None else ())))
    elif slew_screen:
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
    if launch_window or slew_screen or receiver_window:
        names = sorted(name for name, row in rows.items() if row["current_mm"] != "open"
                       and name not in ("DDR_CK", "DDR_CKn", "DDR_RESETn"))
    for name in names:
        setup_bounds, hold_bounds = [], []
        for ck, ckn, cap in model["capacitances"]():
            clock = [cross(time, p+n, vdd) for p,n in zip(pin("DDR_CK",True,ck), pin("DDR_CKn",False,ckn))]
            for up in (True,False):
                dc_ref = vdd/2 if receiver_vref is None else (receiver_vref if up else vdd - receiver_vref)
                ac, dc = zip(*[(cross(time,w,dc_ref+.135),cross(time,w,dc_ref-.090)) for w in pin(name,up,cap)])
                if slew_screen or receiver_window:
                    # Falling pin() gives the positive voltage change from the high state.
                    wave = pin(name, up, cap)[1]
                    mid = cross(time, wave, dc_ref)
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
                    lag = max(0., np.max((dc_ref - wave[setup_samples])*1000 +
                                         (time[setup_samples]-mid)*setup_rate, initial=0.))
                    lead = max(0., np.max((wave[hold_samples]-dc_ref)*1000 -
                                          (time[hold_samples]-mid)*hold_rate, initial=0.))
                    if receiver_window:
                        # Figures 36/37 anchor the enclosing tangent at AC (setup)
                        # or DC (hold). Each secant extremum of piecewise-linear
                        # samples is attained at a vertex or at the other endpoint.
                        setup_eff = max(setup_rate, np.max(
                            1000 * (dc_ref + .135 - wave[setup_samples]) /
                            (t_ac - time[setup_samples]), initial=setup_rate))
                        hold_eff = max(hold_rate, np.max(
                            1000 * (wave[hold_samples] - (dc_ref - .090)) /
                            (time[hold_samples] - t_dc), initial=hold_rate))
                        duration, _ = dwell_after_crossing(wave, dc_ref+.135, t_ac)
                        crossing_v = np.interp(clock[1], time, pin("DDR_CK", True, ck)[1])
                        crossing_margin = .150 - abs(crossing_v - (receiver_vref if receiver_vref is not None else vdd/2))
                        valid = (1 <= ck_rate <= 4 and .4 <= setup_eff <= 2
                                 and .4 <= hold_eff <= 2 and duration >= 213)
                        if receiver_vref is not None:
                            valid = valid and crossing_margin >= 0
                        # Conservative upper envelopes of Tables 62 and 64.
                        earliest = 365 + 108 + t_ac - clock[1]
                        latest = 2500 - (285 + 95 + clock[1] - t_dc)
                        writer.writerow((name, f"{ck:g}/{ckn:g}/{cap:g}", "rise" if up else "fall",
                                         *(round(x, 6) for x in (ck_rate, setup_eff, hold_eff, duration)),
                                         round(earliest, 3) if valid else "",
                                         round(latest, 3) if valid else "",
                                         "conditional source window" if valid else (
                                             "outside receiver limits" if receiver_vref is not None
                                             else "outside slew/dwell screen"),
                                         *((round(crossing_v, 6), round(crossing_margin*1000, 4))
                                           if receiver_vref is not None else ())))
                        continue
                    writer.writerow((name, hex(ioctrl), f"{ck:g}/{ckn:g}/{cap:g}",
                                     "rise" if up else "fall", *(round(x, 6) for x in
                                     (ck_rate, setup_rate, hold_rate, lag, lead)),
                                     lag > 1e-8, lead > 1e-8,
                                     1 <= ck_rate <= 4 and .4 <= setup_rate <= 2,
                                     1 <= ck_rate <= 4 and .4 <= hold_rate <= 2))
                    continue
                if dwell:
                    # Table 64 lists 213 ps as the largest AC135 tVAC requirement at DDR3L-800.
                    duration, reason = dwell_after_crossing(pin(name, up, cap)[1], dc_ref+.135, ac[1])
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
                earliest = min((clock_edges if n in ("DDR_CK", "DDR_CKn") else edges)[e][1]+3*float(rows[n]["estimated_flight_ps"])-arrival
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
    parser.add_argument("--ioctrl", type=lambda s: int(s, 0), choices=(0, 0x108, 0x18b, 0x273, 0x308, 0x30b, 0x318), default=0x273,
                        help="Low ten bits of all three command IOCTRL registers")
    parser.add_argument("--fixture-corner", choices=model["FIXTURE_CORNERS"], default="typ")
    parser.add_argument("--jlc1080-channel", action="store_true",
                        help="Screen uniform 54.16-ohm CA and 49.63-ohm odd-mode clock lines")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--launch-window", action="store_true", help="Screen capture phase for all routed synchronous commands at DDR3L-800")
    modes.add_argument("--slew-screen", action="store_true", help="Check nominal receiver slopes and the Micron tangent-line conditions")
    modes.add_argument("--receiver-window", action="store_true", help="Bound source phase only inside the slew and dwell screens")
    modes.add_argument("--dwell", action="store_true", help="Report receiver AC135 threshold dwell for isolated edges")
    args = parser.parse_args()
    with args.timing.open() as timing:
        screen(json.loads(args.board.read_bytes()),timing,args.ti_ibis,sys.stdout,args.ioctrl,args.dwell,args.launch_window,args.slew_screen,args.receiver_window,args.fixture_corner,args.jlc1080_channel)
