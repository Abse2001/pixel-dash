"""Publish the exact previously qualified populated circuit as the build output."""
import gzip
import hashlib
import os
import tempfile
from pathlib import Path

here = Path(__file__).resolve().parent
expected = "1b440cdc64f5bafaa535a22b637bca952f57ae7ee465a15897c62c038e7cbb91"
board = gzip.decompress((here / "populated-handheld.circuit.json.gz").read_bytes())
if hashlib.sha256(board).hexdigest() != expected:
    raise ValueError("Populated board differs from the qualified dual-byte checkpoint")
dist = here.parents[1] / "dist"
dist.mkdir(exist_ok=True)
with tempfile.NamedTemporaryFile(dir=dist, delete=False) as temporary:
    temporary.write(board)
os.replace(temporary.name, dist / "index.circuit.json")
