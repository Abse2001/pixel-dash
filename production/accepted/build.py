"""Publish the exact previously qualified populated circuit as the build output."""
import gzip
import hashlib
import os
import tempfile
from pathlib import Path

here = Path(__file__).resolve().parent
expected = "261f3c6f25307e7699ba8586ce034772d14e62ca6e2ab123298815d54d8bcff6"
board = gzip.decompress((here / "populated-handheld.circuit.json.gz").read_bytes())
if hashlib.sha256(board).hexdigest() != expected:
    raise ValueError("Populated board differs from the qualified dual-byte checkpoint")
dist = here.parents[1] / "dist"
dist.mkdir(exist_ok=True)
with tempfile.NamedTemporaryFile(dir=dist, delete=False) as temporary:
    temporary.write(board)
os.replace(temporary.name, dist / "index.circuit.json")
