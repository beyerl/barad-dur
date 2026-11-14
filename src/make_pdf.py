"""Build the building-instructions PDF from the step renders, thumbnails and the LDR file."""
import collections, os, sys
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from inventory import PART_NAMES, COLOR_NAMES, INV

LDR = sys.argv[1] if len(sys.argv) > 1 else 'barad_dur.ldr'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'barad_dur_instructions.pdf'
W, H = A4
M = 15 * mm

# ------------------------------------------------------------------ parse steps
steps, titles = [[]], []
for line in open(LDR, encoding='utf-8'):
    t = line.split()
    if not t:
        continue
    if t[0] == '0' and len(t) > 3 and t[1] == '//' and t[2].startswith('Step'):
        titles.append(line.split(':', 1)[1].strip())
    elif t[0] == '0' and len(t) > 1 and t[1] == 'STEP':
        steps.append([])
    elif t[0] == '1':
        steps[-1].append((t[-1][:-4], int(t[1])))
steps = [s for s in steps if s]
step_boms = [collections.Counter(s) for s in steps]
total_bom = sum(step_boms, collections.Counter())
n_parts = sum(total_bom.values())

HINTS = {
    1: "Start with the two light gray 6x8 plates and the 2x2 plate; they are the only ground the model touches. "
       "Each rock panel (3x8x7) sits on a 6x8 plate with its jagged face pointing outwards and its flat back "
       "towards the tower. The two black 1x2 plates tie the other two corners together.",
    2: "The four 1x12x3 arches form a pinwheel: front, right and left are black, the back one is light gray. "
       "Each arch overlaps the next one's foot by one stud, so the ring closes without gaps. The 2x2 pillar of "
       "light gray 1x2 bricks stands in the centre on its 2x2 plate and later supports the deck.",
    3: "Plates on top of the arches turn the ring into one rigid unit. Only the middle eight studs of each arch "
       "are at full height (the ends step down), so the plates rest on those and bridge the corners.",
    4: "A black ring of long bricks on the deck edge: 1x12 at the front, the two Technic 1x12 bricks on the "
       "right and back (their holes read as arrow slits), 1x8 + 1x4 on the left. Same pinwheel as the arches.",
    5: "Fill the ring inside the parapet with light gray bricks so the top becomes a flat 13x13 platform. "
       "Leave the central 7x7 area (three studs in from every edge) empty for the wall panels.",
    6: "The tower body: four 2x5x6 wall panels in a pinwheel around a 3x3 hollow. The one-stud-thick wall "
       "of each panel faces outwards, the two-stud-deep block faces inwards. Put the printed panel at the back.",
    7: "Buttresses lean against the panel walls: the three 3x1x3.3 slopes (studs on the slope face out), the "
       "2x3 and 1x3 slopes on the sides and the 2x4 slope at the back. A 3x3 facet brick sits on each corner.",
    8: "The panel tops are jagged. Put a black 1x1 brick on each low panel end and a black 1x2 plate on each "
       "inner block so everything reaches the same height, then close the 7x7 top with black plates. "
       "Add the four corner pinnacles on top of the cap.",
    9: "Four 1x1x5 bricks and one black 1x2x5 brick form a 3x3 shaft on the centre of the cap. Two openings "
       "(front and right) are left open as dark slits.",
    10: "Two layers of 1x2 bricks, each layer a pinwheel of four bricks, close the shaft. Cap the 3x3 top with the "
        "2x2 corner plate and three 1x2 plates.",
    11: "The crown: a 1x1 brick in the centre, the two 2x2 and four 1x2 inverted slopes around it, each with its "
        "single-stud underside on the shaft cap and the sloped part overhanging outwards. Cover with black plates.",
    12: "The two 75-degree slopes are the horns: vertical faces towards the centre, slopes facing outwards. "
        "Stack a 1x1 brick and a headlight brick (opening to the front) between them; press two trans-red round "
        "plates onto the headlight's stud - this is the Eye. The two 1x1 round bricks behind it hold flames.",
    13: "Push the bar end of each flame into an open stud: two into the horns' hollow tops, two into the round "
        "bricks behind the Eye. Lean them slightly outwards.",
}

CONCEPT = [
    "<b>Concept.</b> Barad-dûr, the Dark Tower of Sauron, re-imagined at a small scale using nothing but the parts "
    "of LEGO set 6082-1 <i>Fire Breathing Fortress</i> (1993). No part is used that is not in the set, and no "
    "part is used more often than the set contains it. The dark, iron-like character of the tower comes from the "
    "set's black castle parts; its light gray stones become the ancient masonry of the foundations and the platform.",
    "<b>Silhouette.</b> The model follows the classic reading of the tower: a wide, hollow arched foundation "
    "growing out of rock, a massive walled body with buttresses, a slender shaft, and a flaring crown whose two "
    "horns frame the Eye. Everything is arranged as pinwheels (arches, parapet, panels, shaft rings): the "
    "rotational twist gives the tower the restless, asymmetric look of the film design.",
    "<b>Foundations.</b> Four 1x12x3 arches (three black, one light gray at the back) form a 13x13 ring with "
    "open arches on every side. The dark void underneath and the single central pillar hint at the vast "
    "foundations of the tower. Two dark gray rock panels flank the base as the crag of Mordor.",
    "<b>Body.</b> Four 2x5x6 wall panels with their windows form a 7x7 keep six bricks high. Their broken, "
    "stepped tops are levelled with fillers and capped in black. Three 3x1x3.3 slopes with studs on the slope "
    "lean against the walls like iron buttresses; smaller slopes and four facet bricks complete the platform.",
    "<b>Shaft and crown.</b> Four 1x1x5 bricks and a 1x2x5 brick form a hollow 3x3 shaft with open slits. Two "
    "rings of 1x2 bricks and a plate cap close it, then inverted slopes flare the crown outwards. Two 75-degree "
    "slopes are the horns, a headlight brick between them carries two trans-red round plates as the Eye, and the "
    "set's four trans-neon-orange flames burn around it.",
    "<b>Not used.</b> The dragon, horse, minifigures, weapons, plants, red roof, brown doors, the treasure chest "
    "and the raised baseplate stay in the box. Every part of the model is black, light gray, dark gray, "
    "trans-red or trans-neon-orange; 135 of the set's parts are used.",
]

styles = {
    'h1': ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=34, leading=40, textColor=colors.HexColor('#111111')),
    'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#111111')),
    'sub': ParagraphStyle('sub', fontName='Helvetica', fontSize=12, leading=16, textColor=colors.HexColor('#555555')),
    'body': ParagraphStyle('body', fontName='Helvetica', fontSize=10, leading=14, alignment=TA_LEFT),
    'small': ParagraphStyle('small', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#444444')),
    'cell': ParagraphStyle('cell', fontName='Helvetica', fontSize=8, leading=9.5),
    'step': ParagraphStyle('step', fontName='Helvetica-Bold', fontSize=40, leading=44, textColor=colors.HexColor('#111111')),
}


def draw_image_fit(c, path, x, y, w, h, crop=None):
    im = Image.open(path)
    if crop:
        im = im.crop(crop)
    iw, ih = im.size
    s = min(w / iw, h / ih)
    dw, dh = iw * s, ih * s
    tmp = path + '.crop.png'
    im.save(tmp)
    c.drawImage(tmp, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, mask=None)
    os.remove(tmp)


def footer(c, page):
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#777777'))
    c.drawString(M, 8 * mm, 'Barad-dûr - concept MOC from the parts of LEGO set 6082-1 Fire Breathing Fortress')
    c.drawRightString(W - M, 8 * mm, str(page))
    c.setFillColor(colors.black)


def autocrop_box(path, pad=20):
    im = Image.open(path).convert('L')
    bbox = Image.eval(im, lambda v: 255 - v).getbbox()
    if not bbox:
        return None
    return (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad))


def part_label(part, color):
    name = PART_NAMES.get(part, part)
    return f"{name}<br/><font color='#666666'>{part} · {COLOR_NAMES.get(color, color)}</font>"


c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle('Barad-dûr - building instructions (concept MOC from set 6082-1)')
c.setAuthor('Claude')
page = 1

# ------------------------------------------------------------------ cover
c.setFillColor(colors.HexColor('#0d0f14'))
c.rect(0, 0, W, H, fill=1, stroke=0)
draw_image_fit(c, 'hero_front_dark.png', M, 52 * mm, W - 2 * M, H - 52 * mm - 52 * mm)
c.setFillColor(colors.white)
c.setFont('Helvetica-Bold', 40)
c.drawString(M, H - 32 * mm, 'BARAD-DÛR')
c.setFont('Helvetica', 13)
c.setFillColor(colors.HexColor('#c9c9c9'))
c.drawString(M, H - 41 * mm, 'The Dark Tower of Mordor, built only from the parts of')
c.drawString(M, H - 47 * mm, 'LEGO® set 6082-1 Fire Breathing Fortress (1993)')
c.setFont('Helvetica', 10)
c.drawString(M, 40 * mm, f'{n_parts} parts  ·  {len(steps)} building steps  ·  approx. 23 cm tall, 19 x 13 studs footprint')
c.drawString(M, 34 * mm, 'Concept model, building instructions and LDraw file generated with LDView renders.')
c.setFont('Helvetica', 8)
c.drawString(M, 22 * mm, 'LEGO® is a trademark of the LEGO Group, which does not sponsor, authorise or endorse this fan concept.')
c.showPage(); page += 1

# ------------------------------------------------------------------ concept page
c.setFillColor(colors.black)
Paragraph('The concept', styles['h2']).wrapOn(c, W - 2 * M, 30);
f = Frame(M, M, W - 2 * M, H - 2 * M, showBoundary=0, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
story = [Paragraph('The concept', styles['h2']), Paragraph('', styles['body'])]
for p in CONCEPT:
    story.append(Paragraph(p, styles['body']))
    story.append(Paragraph('', styles['body']))
f.addFromList(story, c)
# three views at the bottom
yb = M
hb = 95 * mm
for i, (img, cap) in enumerate((('hero_front.png', 'front-right'), ('hero_side.png', 'left side'), ('hero_back.png', 'back'))):
    xw = (W - 2 * M) / 3
    draw_image_fit(c, img, M + i * xw, yb + 6 * mm, xw - 4 * mm, hb, crop=autocrop_box(img))
    c.setFont('Helvetica', 8); c.setFillColor(colors.HexColor('#555555'))
    c.drawCentredString(M + i * xw + xw / 2, yb, cap)
footer(c, page); c.showPage(); page += 1

# ------------------------------------------------------------------ bill of materials
items = sorted(total_bom.items(), key=lambda kv: (kv[0][1], PART_NAMES.get(kv[0][0], kv[0][0])))
cols, rows_per_page = 4, 7
cell_w = (W - 2 * M) / cols
cell_h = (H - 2 * M - 22 * mm) / rows_per_page
idx = 0
while idx < len(items):
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 18)
    c.drawString(M, H - M - 6 * mm, 'Parts list' if idx == 0 else 'Parts list (continued)')
    c.setFont('Helvetica', 9); c.setFillColor(colors.HexColor('#555555'))
    c.drawString(M, H - M - 12 * mm, f'{n_parts} parts, {len(items)} different part/colour combinations. '
                 'One of the four black wall panels is the set\'s dragon-printed panel; it goes at the back.')
    top = H - M - 22 * mm
    for r in range(rows_per_page):
        for k in range(cols):
            if idx >= len(items):
                break
            (part, color), qty = items[idx]
            x = M + k * cell_w
            y = top - (r + 1) * cell_h
            th = f'thumbs/{part}_{color}.png'
            if os.path.exists(th):
                draw_image_fit(c, th, x + 2 * mm, y + 12 * mm, cell_w - 4 * mm, cell_h - 14 * mm, crop=autocrop_box(th, 10))
            c.setFillColor(colors.black); c.setFont('Helvetica-Bold', 12)
            c.drawString(x + 2 * mm, y + 7 * mm, f'{qty}x')
            p = Paragraph(part_label(part, color), styles['cell'])
            pw, ph = p.wrap(cell_w - 14 * mm, 20 * mm)
            p.drawOn(c, x + 12 * mm, y + 9 * mm - ph + 4)
            idx += 1
    footer(c, page); c.showPage(); page += 1

# ------------------------------------------------------------------ steps
FIXED_CROP = autocrop_box(f'steps/step-Step{len(steps):02d}.png', 40)
for i, (bom, title) in enumerate(zip(step_boms, titles), 1):
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 40)
    c.drawString(M, H - M - 12 * mm, f'{i}')
    c.setFont('Helvetica-Bold', 15)
    c.drawString(M + 18 * mm, H - M - 7 * mm, title)
    hint = Paragraph(HINTS.get(i, ''), styles['body'])
    hw, hh = hint.wrap(W - 2 * M - 18 * mm, 40 * mm)
    hint.drawOn(c, M + 18 * mm, H - M - 12 * mm - hh)
    # parts strip below the hint
    items_s = sorted(bom.items(), key=lambda kv: (kv[0][1], PART_NAMES.get(kv[0][0], kv[0][0])))
    per_row = 4
    n_rows = (len(items_s) + per_row - 1) // per_row
    cell_w = (W - 2 * M) / per_row
    row_h = 18 * mm
    strip_top = H - M - 16 * mm - hh
    strip_h = 6 * mm + n_rows * row_h
    c.setStrokeColor(colors.HexColor('#999999')); c.setLineWidth(0.6)
    c.roundRect(M, strip_top - strip_h, W - 2 * M, strip_h, 3 * mm, stroke=1, fill=0)
    c.setFont('Helvetica-Bold', 9); c.setFillColor(colors.HexColor('#333333'))
    c.drawString(M + 3 * mm, strip_top - 4.5 * mm, f'Parts in this step ({sum(bom.values())})')
    for k, ((part, color), qty) in enumerate(items_s):
        r, col = divmod(k, per_row)
        x = M + col * cell_w
        y = strip_top - 6 * mm - (r + 1) * row_h
        th = f'thumbs/{part}_{color}.png'
        if os.path.exists(th):
            draw_image_fit(c, th, x + 2 * mm, y + 2 * mm, 13 * mm, 13 * mm, crop=autocrop_box(th, 10))
        c.setFillColor(colors.black); c.setFont('Helvetica-Bold', 10)
        c.drawString(x + 16 * mm, y + 9 * mm, f'{qty}x')
        p = Paragraph(part_label(part, color), styles['cell'])
        pw, ph = p.wrap(cell_w - 25 * mm, row_h)
        p.drawOn(c, x + 24 * mm, y + row_h - 2 * mm - ph)
    # main image, same scale for every step
    img_top = strip_top - strip_h - 4 * mm
    img_bottom = M + 8 * mm
    step_img = f'steps/step-Step{i:02d}.png'
    area_w, area_h = W - 2 * M, img_top - img_bottom
    fw, fh = FIXED_CROP[2] - FIXED_CROP[0], FIXED_CROP[3] - FIXED_CROP[1]
    s_final = min(area_w / fw, area_h / fh)
    own = autocrop_box(step_img, 40)
    ow, oh = own[2] - own[0], own[3] - own[1]
    s_own = min(min(area_w / ow, area_h / oh), 1.6 * s_final)
    dw, dh = ow * s_own, oh * s_own
    draw_image_fit(c, step_img, M + (area_w - dw) / 2, img_bottom + (area_h - dh) / 2, dw, dh, crop=own)
    # inset: the new parts only
    new_img = f'steps_new/new{i:02d}.png'
    if os.path.exists(new_img):
        iw, ih = 58 * mm, 46 * mm
        ix, iy = W - M - iw, img_bottom
        c.setFillColor(colors.white); c.setStrokeColor(colors.HexColor('#bbbbbb'))
        c.roundRect(ix, iy, iw, ih, 2 * mm, stroke=1, fill=1)
        draw_image_fit(c, new_img, ix + 1 * mm, iy + 6 * mm, iw - 2 * mm, ih - 7 * mm, crop=autocrop_box(new_img, 15))
        c.setFont('Helvetica', 7); c.setFillColor(colors.HexColor('#555555'))
        c.drawCentredString(ix + iw / 2, iy + 2 * mm, 'new parts of this step, same viewing angle')
    footer(c, page); c.showPage(); page += 1

# ------------------------------------------------------------------ final page
c.setFillColor(colors.black); c.setFont('Helvetica-Bold', 18)
c.drawString(M, H - M - 6 * mm, 'Finished model')
draw_image_fit(c, 'hero_front.png', M, M + 10 * mm, W - 2 * M, H - 2 * M - 20 * mm, crop=autocrop_box('hero_front.png'))
footer(c, page)
c.save()
print('wrote', OUT, 'pages:', page)
