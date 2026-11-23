"""Publish the exact previously qualified populated circuit as the build output."""
import gzip
import hashlib
import os
import tempfile
from pathlib import Path

here = Path(__file__).resolve().parent
expected = "74e8c2705896d813a8e4332f04456c8494cc3675aed1e890d1f79576b020ed61"
board = gzip.decompress((here / "populated-handheld.circuit.json.gz").read_bytes())
if hashlib.sha256(board).hexdigest() != expected:
    raise ValueError("Populated board differs from the qualified dual-byte checkpoint")
dist = here.parents[1] / "dist"
dist.mkdir(exist_ok=True)
with tempfile.NamedTemporaryFile(dir=dist, delete=False) as temporary:
    temporary.write(board)
os.replace(temporary.name, dist / "index.circuit.json")
