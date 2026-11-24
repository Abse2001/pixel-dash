"""Electrostatic half-section of one isolated DDR trace on JLC06161H-1080B."""
import csv
import math
import sys
from functools import lru_cache

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve


def axis(breaks, steps):
    parts = [np.linspace(a, b, math.ceil((b-a)/step), endpoint=False)
             for a, b, step in zip(breaks, breaks[1:], steps)]
    return np.concatenate([*parts, breaks[-1:]])


@lru_cache(maxsize=256)
def cross_section(layer, width, gap_scale, foil_scale, dk_scale, mesh, edge_gap=None):
    inner = layer == "inner"
    h = (.100 if inner else .0764) * gap_scale
    t = (.0152 if inner else .035) * foil_scale
    top = h+t
    half = width/2
    if edge_gap is None:
        left, right = 0., half
        x = axis([0, right, right+.12, right+.40, 2.0], [mesh, mesh, .012, .032])
    else:
        if inner:
            raise ValueError("Clock pair is on outer copper")
        left, right = edge_gap/2, edge_gap/2 + width
        x = axis([0, left, right, right+.12, right+.40, 2.0],
                 [mesh, mesh, mesh, .012, .032])
    if inner:
        pp = .2104 * gap_scale
        core = .700 * gap_scale
        y = axis([0,h,top,top+pp,top+pp+core,top+2*pp+core],
                 [mesh,mesh,mesh*2,.016,.01])
    else:
        y = axis([0,h,h+.03048,top,top+.01524,.32,1.5]
                 if t > .03048 else [0,h,top,h+.03048,top+.01524,.32,1.5],
                 [mesh,mesh,mesh,mesh,.008,.025])
    dx, dy = np.diff(x), np.diff(y)
    xx, yy = np.meshgrid((x[:-1]+x[1:])/2, (y[:-1]+y[1:])/2)
    if inner:
        er = np.where((yy<h) | ((yy>top+pp)&(yy<top+pp+core)), 4.6, 4.4)*dk_scale
    else:
        mask = (yy<h+.03048) | ((xx>=left)&(xx<right)&(yy<top+.01524))
        er = np.where(yy<h,3.91*dk_scale,np.where(mask,3.8*dk_scale,1.))
    nx = len(x)
    ids = np.arange(nx*len(y)).reshape(len(y),nx)
    conductor = (x[None,:]>=left)&(x[None,:]<=right)&(y[:,None]>=h)&(y[:,None]<=top)
    fixed = conductor.copy()
    fixed[[0,-1],:] = True
    fixed[:,-1] = True
    if edge_gap is not None:
        fixed[:,0] = True  # Odd symmetry between opposite-polarity conductors.
    free = ~fixed.ravel()
    caps = []
    for material in (er,np.ones_like(er)):
        gx = material * dy[:,None]/dx[None,:]/2
        gy = material * dx[None,:]/dy[:,None]/2
        horizontal = np.zeros((len(y),len(x)-1))
        vertical = np.zeros((len(y)-1,len(x)))
        horizontal[:-1]+=gx
        horizontal[1:]+=gx
        vertical[:,:-1]+=gy
        vertical[:,1:]+=gy
        a = np.r_[ids[:,:-1].ravel(),ids[:-1].ravel()]
        b = np.r_[ids[:,1:].ravel(),ids[1:].ravel()]
        weights = np.r_[horizontal.ravel(),vertical.ravel()]
        matrix = coo_matrix((np.tile(weights,4)*np.repeat([1,1,-1,-1],len(a)),
                             (np.r_[a,b,a,b],np.r_[a,b,b,a])),shape=(ids.size,ids.size)).tocsr()
        voltage = conductor.ravel().astype(float)
        voltage[free] = spsolve(matrix[free][:,free],-(matrix@voltage)[free])
        caps.append((2 if edge_gap is None else 1)*8.8541878128e-12*np.dot(weights,(voltage[a]-voltage[b])**2))
    return (1/(299792458*math.sqrt(math.prod(caps))), 1e9*math.sqrt(caps[0]/caps[1])/299792458)



if __name__ == "__main__":
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(["layer", "corner", "mesh_mm", "finished_width_mm",
                     "height_scale", "foil_scale", "Dk_scale", "Z_ohm", "delay_ps_per_mm"])
    for name, dw, height, foil, dk in [
        ("nominal", 0, 1, 1, 1),
        ("tight_low_Z", .008, .95, 1.10, 1.04),
        ("tight_high_Z", -.008, 1.05, .90, .96),
        ("wide_low_Z", .0204, .95, 1.10, 1.04),
        ("wide_high_Z", -.0204, 1.05, .90, .96),
    ]:
        width = .102 + dw
        for layer, gap in (("outer", None), ("inner", None), ("clock_odd", .1505 - dw)):
            for mesh in (.004, .0025):
                z, delay = cross_section(layer, width, height, foil, dk, mesh, gap)
                writer.writerow([layer, name, mesh, round(width, 4), height,
                                 foil, dk, round(z, 4), round(delay, 5)])
