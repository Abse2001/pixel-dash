"""Compare the documented 1080 stack at manufacturable inner trace widths."""
import csv
import sys
from corners import cross_section

def sweep():
    out = csv.writer(sys.stdout, lineterminator="\n")
    out.writerow(["layer","width_mm","corner","mesh_mm","ohm","ps_per_mm"])
    for layer,widths in (("inner",(.230,.250,.270,.290,.310,.330)),("outer",(.102,.110,.115))):
        for width in widths:
            for name,dw,height,foil,dk in (("nominal",0,1,1,1),("low_Z",.008,.95,1.10,1.04),("high_Z",-.008,1.05,.90,.96)):
                for mesh in (.004,.0025):
                    z,flight = cross_section(layer,width+dw,height,foil,dk,mesh,"1080")
                    out.writerow([layer,width,name,mesh,round(z,4),round(flight,5)])
if __name__=="__main__":
    sweep()
