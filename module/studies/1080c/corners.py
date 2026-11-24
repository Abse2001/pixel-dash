"""Electrostatic half-section of one isolated DDR trace on JLC06161H-1080C."""
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
def section(layer, width, gap_scale, foil_scale, dk_scale, mesh):
    inner = layer == "inner"
    h = (.075 if inner else .0764) * gap_scale
    t = (.0152 if inner else .035) * foil_scale
    top = h+t
    half = width/2
    x = axis([0,half,half+.12,half+.40,2.0], [mesh,mesh,.012,.032])
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
        mask = (yy<h+.03048) | ((xx<half)&(yy<top+.01524))
        er = np.where(yy<h,3.91*dk_scale,np.where(mask,3.8*dk_scale,1.))
    nx = len(x)
    ids = np.arange(nx*len(y)).reshape(len(y),nx)
    conductor = (x[None,:]<=half)&(y[:,None]>=h)&(y[:,None]<=top)
    fixed = conductor.copy()
    fixed[[0,-1],:] = True
    fixed[:,-1] = True
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
        caps.append(2*8.8541878128e-12*np.dot(weights,(voltage[a]-voltage[b])**2))
    return 1/(299792458*math.sqrt(math.prod(caps)))


if __name__ == "__main__":
    writer = csv.writer(sys.stdout,lineterminator="\n")
    writer.writerow(["section","artwork_mm","corner","width_mm","height_scale","foil_scale","Dk_scale","mesh_mm","ohm"])
    for layer,widths in (("outer",(.102,.115,.125,.135)),("inner",(.102,))):
        for width in widths:
            for name,dw,dh,dt,dk in (("nominal",0,1,1,1),("low_Z",.008,.95,1.1,1.04),
                                        ("high_Z",-.008,1.05,.9,.96)):
                for mesh in (.004,.0025):
                    z = section(layer,width+dw,dh,dt,dk,mesh)
                    writer.writerow([layer,width,name,round(width+dw,4),dh,dt,dk,mesh,round(z,4)])
