"""Reconstruct finished copper from the manufacturing archive, preserving artwork polarity."""
from itertools import groupby
from zipfile import ZipFile

from gerbonara import GerberFile
from gerbonara.graphic_primitives import Circle, Line
from gerbonara.utils import MM
from shapely.geometry import GeometryCollection, LineString, Point, Polygon
from shapely.ops import unary_union


def artwork(archive, member):
    with ZipFile(archive) as files:
        gerber = GerberFile.from_string(files.read(member).decode())
    image = GeometryCollection()
    primitives = (primitive for obj in gerber.objects for primitive in obj.to_primitives(unit=MM))
    for dark, group in groupby(primitives, lambda primitive: primitive.polarity_dark):
        shapes = []
        for primitive in group:
            if isinstance(primitive, Circle):
                shape = Point(primitive.x, primitive.y).buffer(primitive.r, quad_segs=96)
            elif isinstance(primitive, Line):
                shape = LineString([(primitive.x1, primitive.y1), (primitive.x2, primitive.y2)]).buffer(
                    primitive.width / 2, quad_segs=96)
            else:
                polygon = primitive.to_arc_poly()
                outline = polygon.approximate_arcs(max_error=0.000005).outline if any(polygon.arc_centers) else polygon.outline
                shape = Polygon(outline)
            if not shape.is_valid:
                raise ValueError(f"Invalid aperture or region in {member}")
            shapes.append(shape)
        mask = unary_union(shapes)
        image = image.union(mask) if dark else image.difference(mask)
    return image


def reference(archive, member, seed):
    image = artwork(archive, member)
    pieces = image.geoms if image.geom_type == "MultiPolygon" else [image]
    matches = [piece for piece in pieces if piece.covers(seed)]
    if len(matches) != 1:
        raise ValueError(f"{member} lacks a unique connected reference at ({seed.x:.5f}, {seed.y:.5f}) mm")
    return matches[0]
