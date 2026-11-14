"""Minimal LDraw parser: resolves a model into world-space triangles and lines."""
import os, re, numpy as np
LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ldraw')
SEARCH = [os.path.join(LIB,'parts'), os.path.join(LIB,'p'), os.path.join(LIB,'parts','s'), os.path.join(LIB,'p','48'), os.path.join(LIB,'p','8')]
_cache = {}
COLORS = {}
EDGE = {}
def load_colors():
    with open(os.path.join(LIB,'LDConfig.ldr'), encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.startswith('0 !COLOUR'):
                m = re.search(r'CODE\s+(\d+)\s+VALUE\s+#([0-9A-Fa-f]{6})\s+EDGE\s+#?([0-9A-Fa-f]{6}|\d+)', line)
                if m:
                    code=int(m.group(1)); rgb=tuple(int(m.group(2)[i:i+2],16)/255 for i in (0,2,4))
                    e=m.group(3)
                    alpha = 1.0
                    ma = re.search(r'ALPHA\s+(\d+)', line)
                    if ma: alpha=int(ma.group(1))/255
                    COLORS[code]=(rgb,alpha)
                    EDGE[code]= tuple(int(e[i:i+2],16)/255 for i in (0,2,4)) if len(e)==6 and not e.isdigit() else e
load_colors()
def find(name):
    name=name.replace(chr(92),'/').lower()
    for d in SEARCH:
        p=os.path.join(d,name)
        if os.path.exists(p): return p
        # case-insensitive fallback
    for d in SEARCH:
        dd=os.path.join(d, os.path.dirname(name))
        if os.path.isdir(dd):
            for f in os.listdir(dd):
                if f.lower()==os.path.basename(name): return os.path.join(dd,f)
    return None
def parse_file(path):
    """Returns list of (type, color, data, subname) in local coords."""
    if path in _cache: return _cache[path]
    items=[]
    invert=False
    with open(path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            t=line.split()
            if not t: continue
            if t[0]=='0':
                if len(t)>=3 and t[1]=='BFC' and 'INVERTNEXT' in t: invert=True
                continue
            try:
                if t[0]=='1':
                    c=int(t[1]); v=list(map(float,t[2:14])); sub=' '.join(t[14:])
                    M=np.array([[v[3],v[4],v[5],v[0]],[v[6],v[7],v[8],v[1]],[v[9],v[10],v[11],v[2]],[0,0,0,1]])
                    items.append(('1',c,M,sub)); invert=False
                elif t[0]=='3':
                    c=int(t[1]); v=np.array(list(map(float,t[2:11]))).reshape(3,3); items.append(('3',c,v,None))
                elif t[0]=='4':
                    c=int(t[1]); v=np.array(list(map(float,t[2:14]))).reshape(4,3); items.append(('4',c,v,None))
                elif t[0]=='2':
                    c=int(t[1]); v=np.array(list(map(float,t[2:8]))).reshape(2,3); items.append(('2',c,v,None))
            except Exception as e:
                pass
    _cache[path]=items
    return items
def resolve(path, M=np.eye(4), color=16, depth=0, tris=None, lines=None):
    """Accumulate triangles (N,3,3) with colors, and lines (N,2,3) with colors."""
    if tris is None: tris=[]; lines=[]
    for typ,c,data,sub in parse_file(path):
        cc = color if c==16 else (('edge',color) if c==24 else c)
        if typ=='1':
            sp=find(sub)
            if sp is None: continue
            resolve(sp, M@data, cc, depth+1, tris, lines)
        elif typ in ('3','4'):
            pts=(M[:3,:3]@data.T).T+M[:3,3]
            if typ=='3': tris.append((pts,cc))
            else:
                tris.append((pts[[0,1,2]],cc)); tris.append((pts[[0,2,3]],cc))
        elif typ=='2':
            pts=(M[:3,:3]@data.T).T+M[:3,3]
            lines.append((pts,cc))
    return tris,lines
def load_model(path):
    """Parse a model .ldr with STEP markers. Returns list of steps, each a list of (color, part, M, line)."""
    steps=[[]]
    with open(path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            t=line.split()
            if not t: continue
            if t[0]=='0' and len(t)>1 and t[1]=='STEP': steps.append([]); continue
            if t[0]=='1':
                c=int(t[1]); v=list(map(float,t[2:14])); sub=' '.join(t[14:])
                M=np.array([[v[3],v[4],v[5],v[0]],[v[6],v[7],v[8],v[1]],[v[9],v[10],v[11],v[2]],[0,0,0,1]])
                steps[-1].append((c,sub,M,line.strip()))
    if not steps[-1]: steps.pop()
    return steps
def part_bbox(name):
    p=find(name)
    tris,_=resolve(p)
    pts=np.concatenate([t[0] for t in tris])
    return pts.min(0), pts.max(0)
if __name__=='__main__':
    import sys
    for n in sys.argv[1:]:
        mn,mx=part_bbox(n)
        print(n, 'min',np.round(mn,1),'max',np.round(mx,1), 'size', np.round(mx-mn,1))
