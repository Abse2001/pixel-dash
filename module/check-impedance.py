"""Estimate uniform outer and inner DDR line impedances on JLC06161H-1080."""
import csv
import json
import math
import runpy
import sys
from pathlib import Path

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

def inner_capacitance(width, pitch, vacuum):
    # Both reference planes are ideal AC grounds. The second plane at L4
    # (at L3 for L4 traces) is an optimistic case, conditional on solid copper.
    bottom, foil, top = .55, .0152, .2104
    height = bottom + foil + top
    x = np.arange(-round(1.5 / pitch), round(1.5 / pitch)+1) * pitch
    y = np.linspace(0., height, round(height / pitch)+1)
    dx, dy = pitch, y[1]
    xx, yy = np.meshgrid(x, y)
    metal = (abs(xx) <= width/2) & (yy >= bottom) & (yy <= bottom+foil)
    fixed = metal.copy()
    fixed[[0,-1],:] = True
    fixed[:,[0,-1]] = True
    potential = metal.astype(float)
    er = np.where(yy <= bottom, 4.6, 4.4)
    if vacuum:
        er.fill(1.)
    ex = 2 * er[:,1:] * er[:,:-1] / (er[:,1:] + er[:,:-1]) * dy/dx
    ey = 2 * er[1:,:] * er[:-1,:] / (er[1:,:] + er[:-1,:]) * dx/dy
    sx, sy = np.zeros_like(xx), np.zeros_like(xx)
    sx[:,:-1], sy[:-1,:] = ex, ey
    diag = sx + sy + np.roll(sx,1,axis=1) + np.roll(sy,1,axis=0)
    nx = len(x)
    mat = diags([diag.ravel(), -sx.ravel()[:-1], -sx.ravel()[:-1],
                 -sy.ravel()[:-nx], -sy.ravel()[:-nx]], [0,1,-1,nx,-nx],format='csr')
    free = ~fixed.ravel()
    potential.ravel()[free] = spsolve(mat[free][:,free], -(mat@potential.ravel())[free])
    charge = sum(np.sum(f * np.diff(potential,axis=a) * np.diff(metal.astype(int),axis=a))
                 for a,f in [(1,ex),(0,ey)])
    return charge * 8.8541878128e-12

def main():
    checks = Path(__file__).resolve().parents[1] / "checks"
    sys.path.insert(0,str(checks))
    outer = runpy.run_path(str(checks/"estimate-ddr-impedance.py"))["capacitance"]
    geom = json.loads(Path(sys.argv[1]).read_text())
    with Path(__file__).with_name("timing.csv").open() as stream:
        names = {r["net"] for r in csv.DictReader(stream)}
    rows = [o for o in geom if o["kind"]=="track" and o["net"] in names]
    out = csv.writer(sys.stdout,lineterminator="\n")
    out.writerow(("section","width_mm","mesh_mm","line_Z_ohm","flight_ps_per_mm","screen_50_ohm_plus_minus_5"))
    for pitch in [.005,.003]:
        for label, layers in [('outer',('F.Cu','B.Cu')), ('inner_ideal_two_planes',('In2.Cu','In3.Cu'))]:
            for w in sorted({o["width"] for o in rows if o['layer'] in layers}):
                filled,air = [outer(w,None,pitch,.0764,3.91,vac) if label=='outer' else inner_capacitance(w,pitch,vac)
                              for vac in (False,True)]
                z = 1/(299792458*math.sqrt(filled*air))
                delay = math.sqrt(filled/air)/299792458*1e9
                out.writerow((label,w,pitch,round(z,3),round(delay,4),"PASS" if 45<=z<=55 else "FAIL"))

if __name__=="__main__":
    main()
