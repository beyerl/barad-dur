"""Barad-dur concept MOC built exclusively from the parts of LEGO 6082-1 Fire Breathing Fortress.

Coordinate conventions: x to the right, z toward the viewer (front = +z), levels in plates (1 brick = 3).
The footprint ring is 13 x 13 studs (x 0..12, z 0..12).
"""
import numpy as np, sys
from builder import Model, Ry, Rx, Rz, S, P

BK, LG, DG, BR, RD, TRO, TRR = 0, 7, 8, 6, 4, 38, 36

m = Model('Barad-dur - concept MOC from set 6082-1 parts')
m.global_R = Ry(180)  # LDraw viewers look from -z; our 'front' is +z

# ---------------------------------------------------------------- 1. ground
m.step('Ground plates and the two rock crags')
m.place('3036', LG, -3, 5, 0, rot=90, desc='ground plate left')
m.place('3036', LG, 10, 0, 0, rot=90, desc='ground plate right')
m.place('3023', BK, 0, 0, 0, desc='corner tie back-left')
m.place('3023', BK, 11, 12, 0, desc='corner tie front-right')
m.place('3022', LG, 5, 5, 0, desc='plate under central pillar')
m.place('6083', DG, -3, 5, 1, rot=90, desc='rock crag left')
m.place('6083', DG, 13, 0, 1, rot=270, desc='rock crag right')

# ---------------------------------------------------------------- 2. arch ring (pinwheel of 1x12x3 arches)
m.step('Arch ring: the hollow foundations')
m.place('6108', BK, 0, 12, 1, desc='front arch')
m.place('6108', BK, 12, 1, 1, rot=90, desc='right arch')
m.place('6108', LG, 1, 0, 1, desc='back arch')
m.place('6108', BK, 0, 0, 1, rot=90, desc='left arch')
for lvl, rot in ((1, 0), (4, 90), (7, 0)):
    if rot == 0:
        m.place('3004', LG, 5, 5, lvl, desc='central pillar 1x2'); m.place('3004', LG, 5, 6, lvl, desc='central pillar 1x2')
    else:
        m.place('3004', LG, 5, 5, lvl, rot=90, desc='central pillar 1x2'); m.place('3004', LG, 6, 5, lvl, rot=90, desc='central pillar 1x2')

# ---------------------------------------------------------------- 3. deck plates at level 10
m.step('Deck plates tying the arches together')
m.place('3029', LG, 0, 1, 10, rot=90, desc='deck 4x12 left')
m.place('3710', LG, 0, 0, 10, desc='deck 1x4 back-left')
m.place('3032', LG, 4, 9, 10, desc='deck 4x6 front')
m.place('3031', LG, 4, 0, 10, desc='deck 4x4 back')
m.place('3031', LG, 8, 0, 10, desc='deck 4x4 back-right')
m.place('3031', LG, 4, 4, 10, desc='deck 4x4 centre')
m.place('3020', LG, 8, 4, 10, rot=90, desc='deck 2x4 centre-right')
m.place('3666', LG, 4, 8, 10, desc='deck 1x6 centre')
m.place('3666', LG, 10, 4, 10, rot=90, desc='deck 1x6 right inner')
m.place('3623', LG, 10, 10, 10, rot=90, desc='deck 1x3 front-right inner')
m.place('3795', LG, 11, 4, 10, rot=90, desc='deck 2x6 right')
m.place('3021', LG, 11, 10, 10, rot=90, desc='deck 2x3 front-right')

# ---------------------------------------------------------------- 4. parapet ring (black, level 11-14)
m.step('Black parapet ring on top of the arches')
m.place('6112', BK, 0, 12, 11, desc='parapet front 1x12')
m.place('3895', BK, 12, 1, 11, rot=90, desc='parapet right 1x12 technic')
m.place('3895', BK, 1, 0, 11, desc='parapet back 1x12 technic')
m.place('3008', BK, 0, 0, 11, rot=90, desc='parapet left 1x8')
m.place('3010', BK, 0, 8, 11, rot=90, desc='parapet left 1x4')

# ---------------------------------------------------------------- 5. platform fill (light gray, level 11-14)
m.step('Stone platform fill inside the parapet')
m.place('3001', LG, 1, 1, 11, desc='fill 2x4')
m.place('3002', LG, 5, 1, 11, desc='fill 2x3')
m.place('3003', LG, 8, 1, 11, desc='fill 2x2')
m.place('3003', LG, 10, 1, 11, desc='fill 2x2')
m.place('3002', LG, 1, 10, 11, desc='fill 2x3 front-left')
m.place('3003', LG, 4, 10, 11, desc='fill 2x2 front')
m.place('3010', LG, 6, 10, 11, desc='fill 1x4 front')
m.place('3004', LG, 10, 10, 11, desc='fill 1x2 front')
m.place('3010', LG, 6, 11, 11, desc='fill 1x4 front edge')
m.place('3004', LG, 10, 11, 11, desc='fill 1x2 front edge')
for x in (1, 2, 10, 11):
    m.place('3010', LG, x, 3, 11, rot=90, desc=f'fill 1x4 col {x}')
    m.place('3622', LG, x, 7, 11, rot=90, desc=f'fill 1x3 col {x}')

# ---------------------------------------------------------------- 6. wall panels (pinwheel, level 11-29)
m.step('The tower body: four wall panels in a pinwheel')
U0, V0 = 3, 3
panels = [  # (part, x0, z0, rot, desc)
    ('4444', U0 + 0, V0 + 5, 180, 'front panel'),
    ('4444', U0 + 5, V0 + 2, 270, 'right panel'),
    ('4444p01', U0 + 2, V0 + 0, 0, 'back panel (printed)'),
    ('4444', U0 + 0, V0 + 0, 90, 'left panel'),
]
panel_info = []
for part, x0, z0, rot, desc in panels:
    info = m.place(part, BK, x0, z0, 11, rot=rot, desc=desc)
    # compute world positions of the local top cells for later filling
    R = Ry(rot)
    pos = m.cur[-1][2]
    def cell(cx, cz):
        loc = np.array([-50 + 20 * cx + 10, 0, -10 + 20 * cz + 10])
        w = pos + R @ loc
        return int(round((w[0] - 10) / 20)), int(round((w[2] - 10) / 20))
    panel_info.append({'ends': [cell(0, 0), cell(4, 0)], 'block': [cell(2, 1), cell(3, 1)], 'rot': rot})

# ---------------------------------------------------------------- 7. buttresses on the platform
m.step('Buttresses and corner bastions on the platform')
m.place('6044', BK, 3, 10, 14, rot=180, desc='front buttress fin left')
m.place('6044', BK, 7, 10, 14, rot=180, desc='front buttress fin right')
m.place('6044', BK, 10, 8, 14, rot=270, desc='right buttress fin')
m.place('3298', BK, 10, 5, 14, rot=270, desc='right slope 2x3')
m.place('4286', LG if False else BK, 0, 4, 14, rot=90, desc='left slope 1x3 a')
m.place('4286', BK, 0, 6, 14, rot=90, desc='left slope 1x3 b')
m.place('3037', BK, 5, 1, 14, desc='back slope 2x4')
m.place('3040b', BK, 1, 8, 14, rot=90, desc='left small slope')
m.place('3040b', BK, 1, 3, 14, rot=90, desc='left small slope b')
for (cx, cz) in ((0, 0), (10, 0), (0, 10), (10, 10)):
    m.place('2462', LG, cx, cz, 14, desc='corner facet bastion')

# ---------------------------------------------------------------- 8. level the panel tops and cap them
m.step('Level the jagged panel tops and cap the tower body')
for pi in panel_info:
    for (cx, cz) in pi['ends']:
        m.place('3005', BK, cx, cz, 26, desc='panel end filler brick', check=False)
    (bx0, bz0), (bx1, bz1) = pi['block']
    x0, z0 = min(bx0, bx1), min(bz0, bz1)
    rot = 0 if bz0 == bz1 else 90
    m.place('3023', BK, x0, z0, 28, rot=rot, desc='panel block filler plate', check=False)
# cap 7x7 (x3-9, z3-9) at level 29, all black
m.place('3031', BK, 3, 3, 29, desc='cap 4x4')
m.place('3020', BK, 7, 3, 29, rot=90, desc='cap 2x4')
m.place('3710', BK, 9, 3, 29, rot=90, desc='cap 1x4')
m.place('3020', BK, 3, 7, 29, desc='cap 2x4 front')
m.place('3022', BK, 7, 7, 29, desc='cap 2x2')
m.place('3023', BK, 9, 7, 29, rot=90, desc='cap 1x2')
m.place('3710', BK, 3, 9, 29, desc='cap 1x4 front')
m.place('3023', BK, 7, 9, 29, desc='cap 1x2 front')
m.place('3024', BK, 9, 9, 29, desc='cap 1x1 front')

# pinnacles on the four corners of the tower body
m.place('3048b', BK, 3, 3, 30, desc='corner pinnacle back-left')
m.place('3048b', BK, 8, 9, 30, desc='corner pinnacle front-right')
m.place('3581', BK, 9, 3, 30, rot=270, desc='corner pinnacle back-right')
m.place('3581', BK, 3, 9, 30, rot=90, desc='corner pinnacle front-left')

# ---------------------------------------------------------------- 9. shaft (3x3, x5-7 z5-7), level 30-51
m.step('The shaft: four 1x1x5 columns and a 1x2x5 wall, two open slits')
for (cx, cz) in ((5, 5), (5, 6), (5, 7), (7, 7)):
    m.place('2453a', BK, cx, cz, 30, desc='shaft column 1x1x5')
m.place('2454', BK, 6, 5, 30, desc='shaft back wall 1x2x5')
# slits at (6,7) front and (7,6) right stay open
m.step('Shaft top: two pinwheel rings of 1x2 bricks, then the cap')
for lvl in (45, 48):
    m.place('3004', BK, 5, 7, lvl, desc='ring front')          # x5-6, z7
    m.place('3004', BK, 7, 6, lvl, rot=90, desc='ring right')  # x7, z6-7
    m.place('3004', BK, 6, 5, lvl, desc='ring back')           # x6-7, z5
    m.place('3004', BK, 5, 5, lvl, rot=90, desc='ring left')   # x5, z5-6
m.place('2420', BK, 6, 5, 51, desc='shaft cap corner plate')       # covers (6,5),(7,5),(6,6)
m.place('3023', BK, 5, 5, 51, rot=90, desc='shaft cap 1x2 left')  # (5,5),(5,6)
m.place('3023', BK, 5, 7, 51, desc='shaft cap 1x2 front')         # (5,7),(6,7)
m.place('3023', BK, 7, 6, 51, rot=90, desc='shaft cap 1x2 right') # (7,6),(7,7)

# ---------------------------------------------------------------- 10. crown, level 52-55
m.step('The crown: inverted slopes flare the top outwards')
m.place('3005', BK, 6, 6, 52, desc='crown centre')
m.place('3660a', BK, 5, 7, 52, rot=180, desc='crown front 2x2 inv')   # bottom on z7, overhang z8
m.place('3665a', BK, 7, 7, 52, rot=180, desc='crown front 1x2 inv')
m.place('3660a', BK, 6, 4, 52, rot=0, desc='crown back 2x2 inv')      # bottom on z5, overhang z4
m.place('3665a', BK, 5, 4, 52, rot=0, desc='crown back 1x2 inv')
m.place('3665a', BK, 4, 6, 52, rot=90, desc='crown left 1x2 inv')     # overhang toward -x
m.place('3665a', BK, 7, 6, 52, rot=270, desc='crown right 1x2 inv')   # overhang toward +x
for cx in (5, 6, 7):
    m.place('3023', BK, cx, 4, 55, rot=90, desc='crown cap back 1x2')
m.place('3022', BK, 5, 7, 55, desc='crown cap front 2x2')
m.place('3023', BK, 7, 7, 55, rot=90, desc='crown cap front 1x2')

# ---------------------------------------------------------------- 11. horns and the Eye
m.step('The two horns and the Eye of Sauron')
m.place('4460a', BK, 4, 6, 55, rot=90, desc='left horn')
m.place('4460a', BK, 7, 6, 55, rot=270, desc='right horn')
m.place('3005', BK, 6, 6, 55, desc='eye pedestal')
m.place('4070', BK, 6, 6, 58, rot=180, desc='eye headlight brick')
eye_x, eye_z = 6.5 * S, 6.5 * S
m.raw('6141', TRR, (eye_x, -(61 * P) + 12, eye_z + 14), Rx(-90), 'the Eye (trans-red round plate)')
m.raw('6141', TRR, (eye_x, -(61 * P) + 12, eye_z + 22), Rx(-90), 'the Eye, second layer')
m.place('3062b', BK, 5, 4, 56, desc='flame holder left')
m.place('3062b', BK, 7, 4, 56, desc='flame holder right')

# ---------------------------------------------------------------- 12. flames
m.step('Fire around the Eye')
def flame(cx, cz, top_level, lean_deg, twist=0):
    y_top = -top_level * P
    R = Ry(twist) @ Rz(lean_deg) @ Rx(90)
    m.raw('6126a', TRO, ((cx + 0.5) * S, y_top - 4, (cz + 0.5) * S), R, 'flame')
flame(5, 6, 64, -12)   # left horn top (open stud)
flame(7, 6, 64, 12)    # right horn top
flame(5, 4, 59, -20, 10)
flame(7, 4, 59, 20, -10)

out = sys.argv[1] if len(sys.argv) > 1 else 'barad_dur.ldr'
m.write(out)
left = m.report()
used_total = sum(m.used.values())
print('unused parts (part,color):', {k: v for k, v in left.items() if v > 0})
