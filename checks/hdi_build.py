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
