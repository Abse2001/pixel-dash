"""Compare all 50 rendered DDR connections to the AM3354 and Micron ball maps."""
import json
import re
import sys
from pathlib import Path


def check(board, cpu, ram):
    parts = {e["source_component_id"]: e.get("name") for e in board if e["type"] == "source_component"}
    ports = {e["source_port_id"]: (parts.get(e["source_component_id"]), e["name"])
             for e in board if e["type"] == "source_port"}
    fixed = {"CK": "CK", "CK#": "CKn", "RESET#": "RESETn", "CKE": "CKE", "ODT": "ODT",
             "CS#": "CSn0", "WE#": "WEn", "RAS#": "RASn", "CAS#": "CASn", "LDM": "DQM0",
             "UDM": "DQM1", "LDQS": "DQS0", "LDQS#": "DQSn0", "UDQS": "DQS1", "UDQS#": "DQSn1"}
    fixed.update({pin: pin for pin in [*(f"A{i}" for i in range(16)), *(f"BA{i}" for i in range(3))]})
    expected = {"DDR_" + label for label in fixed.values()} | {f"DDR_D{i}" for i in range(16)}
    seen, ram_balls, changes = set(), set(), []
    for trace in board:
        signal = trace.get("name") or ""
        if trace["type"] != "source_trace" or not signal.startswith("DDR_"):
            continue
        ends = [ports[port] for port in trace["connected_source_port_ids"]]
        if len(ends) != 2 or {ref for ref, _ in ends} != {"U1", "U_DDR"}:
            raise ValueError(f"{signal} has unexpected terminals {ends}")
        by_ref = dict(ends)
        proc_ball, mem_ball = by_ref["U1"], by_ref["U_DDR"]
        if signal in seen or mem_ball in ram_balls or cpu.get(proc_ball) != signal:
            raise ValueError(f"{signal} has duplicate or incorrect ball assignment {ends}")
        memory_pin = ram[mem_ball].split("/")[0]
        bit = re.fullmatch(r"DDR_D(\d+)", signal)
        if bit:
            data = re.fullmatch(r"DQ(\d+)", memory_pin)
            cpu_bit = int(bit[1])
            if not data or int(data[1]) >= 16 or int(data[1]) // 8 != cpu_bit // 8:
                raise ValueError(f"{signal} connects to {memory_pin} on the wrong RAM byte or function")
            if cpu_bit != int(data[1]):
                changes.append((cpu_bit, f"U1.{proc_ball} {signal} -> U_DDR.{mem_ball} {memory_pin}"))
        elif fixed.get(memory_pin) != signal.removeprefix("DDR_"):
            raise ValueError(f"{signal} connects to the wrong RAM pin {memory_pin} at {mem_ball}")
        seen.add(signal)
        ram_balls.add(mem_ball)
    if seen != expected or len(ram_balls) != 50:
        raise ValueError(f"DDR interface differs from the ball maps: {seen ^ expected}")
    return [line for _, line in sorted(changes)]


if __name__ == "__main__":
    directory = Path(__file__).resolve().parents[1] / "am3354"
    changes = check(json.loads(Path(sys.argv[1]).read_text()),
                    json.loads((directory / "processor-balls.json").read_text()),
                    json.loads((directory / "memory-balls.json").read_text()))
    print(f"50 unique connections match the package functions. {len(changes)} within-byte DQ remaps.")
    for row in changes:
        print(row)
