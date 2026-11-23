import pcbnew as k,json,sys
b=k.LoadBoard(sys.argv[1]);pat=[]
def mmxy(p):return [p.x/1e6,p.y/1e6]
for fp in b.GetFootprints():
 for p in fp.Pads():
  pat.append(dict(kind='pad',shape=p.GetShape(),layer=('B.Cu' if p.IsOnLayer(k.B_Cu) else 'F.Cu'),size=mmxy(p.GetSize()),pos=mmxy(p.GetPosition()),rot=p.GetOrientationDegrees(),net=p.GetNetname(),ref=fp.GetReference(),pin=p.GetNumber()))
for p in b.GetTracks():
 if isinstance(p,k.PCB_VIA):
  pat.append(dict(kind='via',pos=mmxy(p.GetPosition()),net=p.GetNetname(),diam=p.GetWidth(k.F_Cu)/1e6,drill=p.GetDrillValue()/1e6))
 else:pat.append(dict(kind='track',layer=p.GetLayerName(),start=mmxy(p.GetStart()),end=mmxy(p.GetEnd()),net=p.GetNetname(),width=p.GetWidth()/1e6))
print(json.dumps(pat,separators=(',',':')))
