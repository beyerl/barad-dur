import numpy as np, ldparse, math, collections
from inventory import INV
# parts whose exact print is not in the LDraw library are written as the plain part
LDR_ALIAS = {'4444p01': '4444'}
S = 20.0  # LDU per stud
P = 8.0   # LDU per plate


def Ry(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rx(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Rz(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


_bb = {}


def body_bbox(part):
    """(min, max, body_min, body_max) where body excludes the studs (y<0 region)."""
    if part in _bb:
        return _bb[part]
    tris, _ = ldparse.resolve(ldparse.find(part + '.dat'))
    pts = np.concatenate([t[0] for t in tris])
    sel = pts[:, 1] >= -0.01
    body = pts[sel] if sel.sum() > 10 else pts
    _bb[part] = (pts.min(0), pts.max(0), body.min(0), body.max(0))
    return _bb[part]


class Model:
    def __init__(self, name):
        self.name = name
        self.steps = []
        self.stepnames = []
        self.used = collections.Counter()
        self.cur = []
        self._title = ''
        self.occ = {}     # (x, z, level) -> description
        self.global_R = np.eye(3)  # applied on write (e.g. Ry(180) so that +z is the model's back, as LDraw expects)
        self.warn = []

    def step(self, title=''):
        if self.cur:
            self.steps.append(self.cur)
            self.stepnames.append(self._title)
        self.cur = []
        self._title = title

    def raw(self, part, color, pos, R, desc=''):
        self.used[(part, color)] += 1
        if self.used[(part, color)] > INV.get((part, color), 0):
            raise ValueError(f"inventory exceeded: {part} color {color} "
                             f"({self.used[(part, color)]} > {INV.get((part, color), 0)}) at {desc}")
        self.cur.append((color, part, np.array(pos, float), np.array(R, float), desc))

    def place(self, part, color, x0, z0, level, rot=0, desc='', R=None, check=True, dy=0.0, dx=0.0, dz=0.0):
        """Align the rotated part so its body footprint min corner is at stud (x0, z0)
        and its bottom sits at plate level `level` (level 0 = table)."""
        if R is None:
            R = Ry(rot)
        mn, mx, bmn, bmx = body_bbox(part)
        corners = np.array([[x, y, z] for x in (bmn[0], bmx[0]) for y in (bmn[1], bmx[1]) for z in (bmn[2], bmx[2])])
        rc = (R @ corners.T).T
        rmn, rmx = rc.min(0), rc.max(0)
        pos = np.array([x0 * S - rmn[0] + dx, -level * P - rmx[1] + dy, z0 * S - rmn[2] + dz])
        w = int(round((rmx[0] - rmn[0]) / S)); d = int(round((rmx[2] - rmn[2]) / S)); h = int(round((rmx[1] - rmn[1]) / P))
        if check:
            for xx in range(x0, x0 + w):
                for zz in range(z0, z0 + d):
                    for ll in range(level, level + h):
                        k = (xx, zz, ll)
                        if k in self.occ:
                            self.warn.append(f"overlap {part}@({x0},{z0},{level}) [{desc}] with {self.occ[k]} at {k}")
                        else:
                            self.occ[k] = f"{part}[{desc}]"
        self.raw(part, color, pos, R, desc)
        return (x0, z0, level, w, d, h)

    def finish(self):
        if self.cur:
            self.steps.append(self.cur)
            self.stepnames.append(self._title)
            self.cur = []

    def write(self, path):
        self.finish()
        L = [f"0 {self.name}", f"0 Name: {path.replace(chr(92), '/').split('/')[-1]}",
             "0 Author: Claude (concept MOC, parts of set 6082-1 only)",
             "0 !LDRAW_ORG Unofficial_Model", "0 BFC CERTIFY CCW", ""]
        for i, (st, title) in enumerate(zip(self.steps, self.stepnames)):
            L.append(f"0 // Step {i + 1}: {title}")
            for color, part, pos, R, desc in st:
                pos = self.global_R @ pos; R = self.global_R @ R
                v = [pos[0], pos[1], pos[2], *R.flatten()]
                L.append("1 %d %s %s.dat" % (color, ' '.join(('%g' % round(x, 4)) for x in v), LDR_ALIAS.get(part, part)))
            L.append("0 STEP")
        open(path, 'w').write('\n'.join(L) + '\n')

    def report(self):
        self.finish()
        print(f"parts placed: {sum(self.used.values())} in {len(self.steps)} steps")
        for w in self.warn[:40]:
            print("WARN", w)
        if len(self.warn) > 40:
            print(f"... {len(self.warn) - 40} more warnings")
        return {k: INV[k] - self.used.get(k, 0) for k in INV}
