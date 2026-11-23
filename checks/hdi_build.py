"""Engineering stack references. Distances in mm at the finished copper centerlines."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Stack:
    name: str
    foil: float
    prepreg: float
    outer_to_inner: float
    outer_to_outer: float
    wall: float
    mask: float


# The supplier's ENIG and mask thickness are not part of a barrel traversal.
# Wall plating is a screening assumption, independent of finished foil thickness.
WURTH = Stack("HDI4_1-2b-1_149_35_2V13", .030, .065, .095, 1.420, .020, .015)
LEGACY = Stack("JLC04161H-1080 provisional", .035, .0764, .0764, 1.530, .020, .03048)

# JLC04161H-1080 public foil/dielectric thickness table. Use the published
# layer sum, without adding solder mask or nominal finished-board tolerance.
JLC1080_OUTER_FOIL = .035
JLC1080_INNER_FOIL = .0152
JLC1080_PREPREG = .0764
JLC1080_CORE = 1.265
JLC1080_OUTER_TO_INNER = JLC1080_OUTER_FOIL/2 + JLC1080_PREPREG + JLC1080_INNER_FOIL/2
JLC1080_INNER_TO_INNER = JLC1080_CORE + JLC1080_INNER_FOIL
JLC1080_DEPTH = {
    "top": 0.,
    "inner1": JLC1080_OUTER_TO_INNER,
    "inner2": JLC1080_OUTER_TO_INNER + JLC1080_INNER_TO_INNER,
    "bottom": 2*JLC1080_OUTER_TO_INNER + JLC1080_INNER_TO_INNER,
}
