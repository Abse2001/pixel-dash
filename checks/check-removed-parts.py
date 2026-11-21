"""Prove the retired component designators and the old silicon are absent from export."""
import csv
import io
import json
import sys
from pathlib import Path
from zipfile import ZipFile

circuit=json.loads(Path(sys.argv[1]).read_text())
retired=set(r["Former designator"] for r in csv.DictReader((Path(__file__).resolve().parents[1]/"production/removed-parts.csv").open()))
# U1 is intentionally reused by the AM3354. Validate both the MPN and supplier ID.
parts={e["name"]:e for e in circuit if e["type"]=="source_component"}
for name,mpn,lcsc in [("U1","AM3354BZCZD80","C128768"),("U_DDR","MT41K512M16VRP-107 IT:P","C2831669")]:
    e=parts[name]
    assert e["supplier_part_numbers"]["jlcpcb"]==[lcsc] and e.get("manufacturer_part_number")==mpn,(name,e)
    for kind in ["pcb_component","schematic_component"]:
        assert sum(t.get("source_component_id")==e["source_component_id"] for t in circuit if t["type"]==kind)==1,(name,kind)
assert not ((retired-{"U1"}) & parts.keys())
assert "RP2350" not in json.dumps(circuit).upper()
by_id={e["source_component_id"]:e["name"] for e in parts.values()}
for kind in ["pcb_component","schematic_component"]:
    for e in circuit:
        if e["type"]!=kind:continue
        owner=e.get("source_component_id","")
        assert owner in by_id or "source_manually_placed_via_" in owner,(kind,owner)
with ZipFile(sys.argv[2]) as archive:
    for fn in ["bom.csv","pick_and_place.csv"]:
        rows=list(csv.DictReader(io.StringIO(archive.read(fn).decode())))
        refs=[r["Designator"] for r in rows]
        assert len(refs)==len(set(refs))
        assert not ((retired-{"U1"}) & set(refs))
        for n,code in [("U1","C128768"),("U_DDR","C2831669")]:
            assert refs.count(n)==1
            if fn=="bom.csv":
                assert next(r for r in rows if r["Designator"]==n)["JLCPCB Part #"]==code
        print(f"{fn}: {len(rows)} designators, old processors and support parts absent")
print(f"Verified {len(retired)} removed designators including U1 reassigned to AM3354.")
