"""Compare the full mask and paste command streams after resolving aperture IDs."""
import re
import sys
from zipfile import ZipFile


def operations(archive, member):
    apertures = {}
    result = []
    for line in archive.read(member).decode("ascii").splitlines():
        if line.startswith(("%TF.CreationDate,", "G04 Created by tscircuit (builder) date ")):
            continue
        definition = re.fullmatch(r"%ADD(\d+)(.+)\*%", line)
        if definition:
            apertures[int(definition[1])] = definition[2]
            continue
        selection = re.fullmatch(r"D(\d+)\*", line)
        if selection and int(selection[1]) >= 10:
            line = "SELECT " + apertures[int(selection[1])]
        result.append(line)
    return result


with ZipFile(sys.argv[1]) as baseline, ZipFile(sys.argv[2]) as trial:
    for name in ("F_Mask.gbr", "F_Paste.gbr", "B_Mask.gbr", "B_Paste.gbr"):
        before, after = operations(baseline, name), operations(trial, name)
        if before != after:
            raise SystemExit(f"{name} mask or paste operations changed")
        print(f"{name} PASS, {len(before)} operations including aperture transformations")
