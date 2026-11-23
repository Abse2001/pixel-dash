"""Apply Micron DDR3L-800 AC135/DC90 reference and slow-clock slew screens to routed CA signals."""
import csv
import sys
from pathlib import Path

# Tables 60, 62 and 64 of Micron's 4 Gb x8 DDR3L specification, Rev Q.
# Each row gives CMD slew, differential CK slew (V/ns), setup/hold deltas and tVAC (ps).
# The last published point is the simultaneous maximum of both Table 62 deltas.
SCREENS = (
    (1.0, 2.0, 0, 0, 145),
    (1.0, 1.0, 40, 50, 145),
    (2.0, 1.0, 108, 95, 213),
)


def report(command_rows, output):
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("signal", "command_slew_V_per_ns", "differential_clock_slew_V_per_ns",
                     "estimated_CA_minus_CK_ps", "receiver_setup_min_ps", "receiver_hold_min_ps",
                     "source_setup_required_ps", "source_hold_required_ps", "receiver_tVAC_min_ps", "margin_status"))
    for row in command_rows:
        net = row["net"]
        if net in ("DDR_CK", "DDR_CKn", "DDR_RESETn"):
            continue
        if row["current_mm"] == "open":
            writer.writerow((net, "", "", "", "", "", "", "", "", "open connection"))
            continue
        delta = float(row["signed_ps_to_mate_or_CK_mean"])
        for ca, ck, setup_delta, hold_delta, dwell in SCREENS:
            setup, hold = 365 + setup_delta, 285 + hold_delta
            writer.writerow((net, ca, ck, delta, setup, hold, round(setup + delta, 3),
                             round(hold - delta, 3), dwell, "source and waveform unverified"))


if __name__ == "__main__":
    with Path(sys.argv[1]).open(newline="") as source:
        report(csv.DictReader(source), sys.stdout)
