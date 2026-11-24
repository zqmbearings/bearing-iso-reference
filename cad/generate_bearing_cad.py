"""
ZQM Bearings — Parametric 2D DXF (AutoCAD R12) + 3D Binary STL + OpenSCAD (.scad) Generator
Generates nominal ISO boundary-envelope CAD models for 5 flagship heavy-duty industrial bearings
for GrabCAD, TraceParts, and engineering layout verification.

Engineering Disclaimer:
Models represent ISO nominal boundary envelopes (d x D x B/H, W33 outer groove, -0.5 mm special OD)
for CAD space-claim and mounting layout verification only. Confirm internal geometry, chamfers,
clearances, and tolerances against ZQM factory drawings before manufacturing or procurement.
Official Website: https://www.zqmbearings.com/ | Inquiries: info@zqmbearings.com
"""
import math, struct
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'generated_envelopes'
OUT.mkdir(parents=True, exist_ok=True)

MODELS = [
    {
        'slug': 'ZQM-29488-EM-440x780x206',
        'designation': '29488 EM',
        'family': 'Spherical Roller Thrust Bearing (ISO 104)',
        'd': 440.0, 'D': 780.0, 'W': 206.0, 'wsym': 'H',
        'chamfer': 9.5, 'w33': False, 'rows': 1, 'special_od': False,
        'url': 'https://www.zqmbearings.com/products/29488-em/',
        'note': 'Flagship underground raise boring & mining thrust bearing (Ca 7,550 kN, C0a 32,000 kN, 410 kg, oil bath).'
    },
    {
        'slug': 'ZQM-23064-CA-W33-320x480x121',
        'designation': '23064 CA/W33',
        'family': 'Spherical Roller Bearing (ISO 15)',
        'd': 320.0, 'D': 480.0, 'W': 121.0, 'wsym': 'B',
        'chamfer': 4.0, 'w33': True, 'rows': 2, 'special_od': False,
        'url': 'https://www.zqmbearings.com/products/23064-ca-w33/',
        'note': 'Large-bore spherical roller bearing with W33 center groove & 3 oil holes (Cr 1,960 kN, C0r 3,850 kN, 75.6 kg).'
    },
    {
        'slug': 'ZQM-24164-CA-W33-320x540x218',
        'designation': '24164 CA/W33',
        'family': 'Wide Spherical Roller Bearing (ISO 15, opt. 1:30 K30)',
        'd': 320.0, 'D': 540.0, 'W': 218.0, 'wsym': 'B',
        'chamfer': 5.0, 'w33': True, 'rows': 2, 'special_od': False,
        'url': 'https://www.zqmbearings.com/products/24164-ca-w33/',
        'note': 'Heavy wide-section spherical roller bearing (Cr 3,550 kN, C0r 6,650 kN, 196 kg; tapered bore uses 1:30 K30).'
    },
    {
        'slug': 'ZQM-FCDP5678275-YA3-280x390x275',
        'designation': 'FCDP5678275/YA3',
        'family': 'Four-Row Rolling Mill Cylindrical Roller Bearing',
        'd': 280.0, 'D': 390.0, 'W': 275.0, 'wsym': 'B',
        'chamfer': 3.0, 'w33': True, 'rows': 4, 'special_od': False,
        'url': 'https://www.zqmbearings.com/products/fcdp-5678275-ya3/',
        'note': 'Four-row pin-type steel rolling mill roll-neck bearing (Cr 2,720 kN, C0r 6,130 kN).'
    },
    {
        'slug': 'ZQM-QJF1058MB-116756-280x419.5x65',
        'designation': 'QJF1058MB / 116756',
        'family': 'Four-Point Contact Ball Bearing (-0.5 mm Special OD)',
        'd': 280.0, 'D': 419.5, 'W': 65.0, 'wsym': 'B',
        'chamfer': 4.0, 'w33': False, 'rows': 1, 'special_od': True,
        'url': 'https://www.zqmbearings.com/products/116756/',
        'note': 'Special -0.5 mm reduced OD (419.5 mm, NOT 420 mm) dedicated axial locator for 4-row rolling mill chocks.'
    },
]

def write_dxf_2d(m, path: Path):
    """Write a clean AutoCAD R12 2D engineering cross-section + front-view DXF (millimeters)."""
    r_in = m['d'] / 2.0
    r_out = m['D'] / 2.0
    w = m['W']
    hw = w / 2.0
    ch = min(m['chamfer'], (r_out - r_in) * 0.15, w * 0.15)
    # Cross-section placed centered at X=0, Y=0; Front-view placed to the right at X = w + D*0.7
    cx = w + r_out * 1.4

    ents = []
    def line(x1, y1, x2, y2, layer='OUTLINE'):
        ents.append(f"0\nLINE\n8\n{layer}\n10\n{x1:.4f}\n20\n{y1:.4f}\n30\n0.0\n11\n{x2:.4f}\n21\n{y2:.4f}\n31\n0.0")
    def circle(x, y, r, layer='OUTLINE'):
        ents.append(f"0\nCIRCLE\n8\n{layer}\n10\n{x:.4f}\n20\n{y:.4f}\n30\n0.0\n40\n{r:.4f}")
    def text(x, y, h, s, layer='ANNOT'):
        ents.append(f"0\nTEXT\n8\n{layer}\n10\n{x:.4f}\n20\n{y:.4f}\n30\n0.0\n40\n{h:.2f}\n1\n{s}")

    # Upper & lower chamfered cross-section rectangles
    for sgn in (1.0, -1.0):
        y_in = sgn * r_in
        y_out = sgn * r_out
        pts = [
            (-hw + ch, y_in), (hw - ch, y_in),
            (hw, y_in + sgn * ch), (hw, y_out - sgn * ch),
            (hw - ch, y_out), (-hw + ch, y_out),
            (-hw, y_out - sgn * ch), (-hw, y_in + sgn * ch),
        ]
        for i in range(len(pts)):
            p1, p2 = pts[i], pts[(i + 1) % len(pts)]
            line(p1[0], p1[1], p2[0], p2[1], 'OUTLINE')
        # Inner / outer ring split visual line (schematic envelope)
        rm = sgn * (r_in + (r_out - r_in) * 0.35)
        rm2 = sgn * (r_in + (r_out - r_in) * 0.65)
        line(-hw, rm, hw, rm, 'DETAIL')
        line(-hw, rm2, hw, rm2, 'DETAIL')
        if m['w33']:
            gw = max(6.0, w * 0.08)
            gd = min(4.0, (r_out - r_in) * 0.06)
            line(-gw/2, y_out, -gw/2, y_out - sgn*gd, 'DETAIL')
            line(-gw/2, y_out - sgn*gd, gw/2, y_out - sgn*gd, 'DETAIL')
            line(gw/2, y_out - sgn*gd, gw/2, y_out, 'DETAIL')

    # Centerline
    line(-hw - 25, 0, hw + 25, 0, 'CENTERLINE')
    # Front view circles
    circle(cx, 0, r_in, 'OUTLINE')
    circle(cx, 0, r_out, 'OUTLINE')
    circle(cx, 0, (r_in + r_out) / 2.0, 'CENTERLINE')
    line(cx - r_out - 20, 0, cx + r_out + 20, 0, 'CENTERLINE')
    line(cx, -r_out - 20, cx, r_out + 20, 'CENTERLINE')

    # Clean engineering title annotation
    th = max(12.0, r_out * 0.045)
    text(-hw, -r_out - th * 2.2, th, f"ZQM BEARINGS - {m['designation']} ({m['d']:g} x {m['D']:g} x {m['W']:g} mm {m['wsym']})")
    text(-hw, -r_out - th * 3.8, th * 0.72, f"NOMINAL ISO ENVELOPE ONLY | {m['url']} | info@zqmbearings.com")

    dxf = "0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n"
    path.write_text(dxf, encoding='ascii', errors='ignore')

def write_stl_3d(m, path: Path, segs=96):
    """Write a watertight 3D binary STL revolved solid of the nominal chamfered bearing ring envelope (mm)."""
    r_in = m['d'] / 2.0
    r_out = m['D'] / 2.0
    hw = m['W'] / 2.0
    ch = min(m['chamfer'], (r_out - r_in) * 0.14, m['W'] * 0.14)

    # 2D profile (r, z) CCW around cross-section
    prof = [
        (r_in + ch, -hw),
        (r_out - ch, -hw),
        (r_out, -hw + ch),
    ]
    if m['w33']:
        gw = max(6.0, m['W'] * 0.08) / 2.0
        gd = min(4.0, (r_out - r_in) * 0.05)
        prof += [
            (r_out, -gw),
            (r_out - gd, -gw),
            (r_out - gd, gw),
            (r_out, gw),
        ]
    prof += [
        (r_out, hw - ch),
        (r_out - ch, hw),
        (r_in + ch, hw),
        (r_in, hw - ch),
        (r_in, -hw + ch),
    ]

    tris = []
    n_p = len(prof)
    for s in range(segs):
        a0 = 2.0 * math.pi * s / segs
        a1 = 2.0 * math.pi * ((s + 1) % segs) / segs
        c0, s0 = math.cos(a0), math.sin(a0)
        c1, s1 = math.cos(a1), math.sin(a1)
        for i in range(n_p):
            r0, z0 = prof[i]
            r1, z1 = prof[(i + 1) % n_p]
            p00 = (r0 * c0, r0 * s0, z0)
            p01 = (r0 * c1, r0 * s1, z0)
            p10 = (r1 * c0, r1 * s0, z1)
            p11 = (r1 * c1, r1 * s1, z1)
            tris.append((p00, p10, p11))
            tris.append((p00, p11, p01))

    def normal(a, b, c):
        ux, uy, uz = b[0]-a[0], b[1]-a[1], b[2]-a[2]
        vx, vy, vz = c[0]-a[0], c[1]-a[1], c[2]-a[2]
        nx, ny, nz = uy*vz - uz*vy, uz*vx - ux*vz, ux*vy - uy*vx
        l = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
        return (nx/l, ny/l, nz/l)

    header = f"ZQM Bearings {m['designation']} {m['d']:g}x{m['D']:g}x{m['W']:g}mm ISO Envelope".encode('ascii', 'ignore')[:80].ljust(80, b' ')
    with path.open('wb') as fh:
        fh.write(header)
        fh.write(struct.pack('<I', len(tris)))
        for a, b, c in tris:
            n = normal(a, b, c)
            fh.write(struct.pack('<12fH', n[0], n[1], n[2], a[0], a[1], a[2], b[0], b[1], b[2], c[0], c[1], c[2], 0))
    return len(tris)

def write_scad(m, path: Path):
    """Write a clean parametric OpenSCAD script so engineers can export STEP/STL/DXF directly."""
    gw = round(max(6.0, m['W'] * 0.08), 2)
    gd = round(min(4.0, (m['D'] - m['d']) * 0.025), 2)
    scad = f"""// ZQM Bearings Parametric ISO Boundary Envelope Model — {m['designation']}
// Dimensions: d = {m['d']:g} mm, D = {m['D']:g} mm, {m['wsym']} = {m['W']:g} mm
// Specs: {m['url']} | Inquiries: info@zqmbearings.com
// License: CC BY 4.0 (Nominal ISO space-claim envelope only — verify against factory drawing)

$fn = 128;
d_bore  = {m['d']:g};
D_od    = {m['D']:g};
W_width = {m['W']:g};
chamfer = {m['chamfer']:g};
has_w33 = {'true' if m['w33'] else 'false'};

r_in  = d_bore / 2;
r_out = D_od / 2;
hw    = W_width / 2;
ch    = min(chamfer, (r_out - r_in) * 0.14, W_width * 0.14);

rotate_extrude(angle = 360) {{
  difference() {{
    polygon(points = [
      [r_in + ch, -hw],
      [r_out - ch, -hw],
      [r_out, -hw + ch],
      [r_out, hw - ch],
      [r_out - ch, hw],
      [r_in + ch, hw],
      [r_in, hw - ch],
      [r_in, -hw + ch]
    ]);
    if (has_w33) {{
      translate([r_out - {gd}, -{gw/2:.2f}]) square([{gd + 1}, {gw}]);
    }}
  }}
}}
"""
    path.write_text(scad, encoding='utf-8')

for m in MODELS:
    sub = OUT / m['slug']
    sub.mkdir(exist_ok=True)
    write_dxf_2d(m, sub / f"{m['slug']}-2D.dxf")
    tris = write_stl_3d(m, sub / f"{m['slug']}-3D.stl")
    write_scad(m, sub / f"{m['slug']}.scad")
    print(f"CAD_OK {m['slug']} | 2D.dxf + 3D.stl ({tris} tris) + .scad")

print('ALL_5_CAD_MODELS_GENERATED')
