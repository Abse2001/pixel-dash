"""Guard already-connected local power and return lands during a partial-board routing study."""
import argparse
import re
from pathlib import Path


def read_report(path):
    lines = path.read_text().splitlines()
    split = {}
    passes = set()
    for line in lines:
        match = re.fullmatch(r"OPEN (\S+) has (\d+) separate CAM networks: (.*)", line)
        if match:
            split[match[1]] = int(match[2])
        if line.startswith(("Startup copper PASS ", "RTC isolation PASS ")):
            passes.add(line)
        if line.startswith("SYSBOOT") and "CPU_to_resistor=True sense_isolated=True" in line:
            passes.add(line)
        if line.startswith(("U1 DDR bypass to ", "U_DDR DDR bypass to ", "DDR reference bypasses ",
                            "Processor supply/return to ", "DDR memory supply to ")):
            ratio = re.search(r"(\d+)/(\d+)", line)
            if ratio and ratio[1] == ratio[2]:
                passes.add(line)
        if re.match(r"U1\.\w+ \d+ uF \w+: CONNECTED;", line):
            passes.add(line.split(";", 1)[0])
    summary = [line for line in lines if line.endswith(" mapped land nets have multiple physical networks.")]
    if len(summary) != 1 or int(summary[0].split()[0]) != len(split):
        raise ValueError(f"Incomplete whole-board net report in {path}")
    if not any("No shorts between mapped land nets." in line for line in lines):
        raise ValueError(f"Missing mapped-short result in {path}")
    if not any(line.startswith("U1 DDR bypass to ") for line in lines):
        raise ValueError(f"Missing CPU power audit in {path}")
    return split, passes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    old, previous = read_report(args.before)
    new, current = read_report(args.after)
    failures = []
    for name, count in sorted(new.items()):
        prior = old.get(name, 1)
        if count > prior:
            failures.append(f"{name} gained physical islands ({prior} to {count})")
    for result in sorted(previous - current):
        failures.append(f"Recheck prior power or strap result: {result}")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Previous local power and strap results retained. Split nets {len(old)} to {len(new)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
