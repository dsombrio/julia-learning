"""
American Flashings — One-Page Product Sell Sheet
Full-width layout, equal-height 2×2 grid, company info footer.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus.flowables import HRFlowable
from PIL import Image as PILImage
import os

NAVY   = colors.HexColor('#1a365d')
ORANGE = colors.HexColor('#c05621')
WHITE  = colors.white
OFFWHT = colors.HexColor('#f7fafc')
GRAY   = colors.HexColor('#4a5568')
LGRAY  = colors.HexColor('#e2e8f0')
IMG_DIR = "/Users/tradbot/.openclaw/workspace/flashings_images"
OUT_PDF = "/Users/tradbot/.openclaw/workspace/American_Flashings_OnePage.pdf"

def fit(src, max_w, max_h):
    try:
        img = PILImage.open(src)
        r = min(max_w / img.width, max_h / img.height)
        nw, nh = int(img.width * r), int(img.height * r)
        out = f"/tmp/fit_{os.path.basename(src)}"
        img.resize((nw, nh), PILImage.LANCZOS).save(
            out, format='PNG' if src.endswith('.png') else 'JPEG', quality=90)
        return out
    except:
        return None

def P(txt, sty=None, **kw):
    d = dict(fontName='Helvetica', textColor=GRAY, leading=11,
             spaceAfter=0, spaceBefore=0, alignment=TA_LEFT)
    if sty is not None:
        for a in ('fontName','textColor','leading','spaceAfter','spaceBefore','alignment','fontSize'):
            v = getattr(sty, a, None)
            if v is not None and a not in kw:
                d[a] = v
    d.update(kw)
    return Paragraph(txt, ParagraphStyle('_', **d))

def build():
    doc = SimpleDocTemplate(OUT_PDF, pagesize=letter,
        rightMargin=0.35*inch, leftMargin=0.35*inch,
        topMargin=0.25*inch, bottomMargin=0.22*inch)
    story = []

    PW  = letter[0] - 0.70*inch
    COL = (PW - 5) / 2

    def sty(**kw):
        d = dict(fontName='Helvetica', textColor=GRAY, leading=11,
                 spaceAfter=0, spaceBefore=0, alignment=TA_LEFT)
        d.update(kw); return ParagraphStyle('_', **d)

    S_HDRB = sty(fontName='Helvetica-Bold', fontSize=16, textColor=WHITE, leading=20)
    S_HDRS = sty(fontSize=8, textColor=colors.HexColor('#c8d0db'))
    S_PN   = sty(fontName='Helvetica-Bold', fontSize=11, textColor=NAVY, leading=14)
    S_TAG  = sty(fontName='Helvetica-Oblique', fontSize=6.5, textColor=ORANGE)
    S_DESC = sty(fontSize=7, leading=9.5)
    S_SPEC = sty(fontSize=6.3, textColor=GRAY, leading=9)
    S_PRICE= sty(fontName='Helvetica-Bold', fontSize=13, textColor=ORANGE)
    S_SZH  = sty(fontName='Helvetica-Bold', fontSize=7.5, textColor=WHITE, alignment=TA_CENTER)
    S_SZD  = sty(fontSize=6.3, textColor=GRAY, alignment=TA_CENTER, leading=9)
    S_SZP  = sty(fontName='Helvetica-Bold', fontSize=13, textColor=ORANGE, alignment=TA_CENTER)
    S_SHR  = sty(fontSize=6, textColor=GRAY, alignment=TA_CENTER, leading=8, fontName='Helvetica-Oblique')
    S_FOOT = sty(fontSize=6.5, textColor=GRAY, alignment=TA_CENTER)
    S_FOOTB= sty(fontName='Helvetica-Bold', fontSize=7.5, textColor=NAVY, alignment=TA_CENTER)

    def img_el(src, w, h):
        p = fit(src, w, h)
        return RLImage(p, width=w, height=h) if p else Spacer(1, 2)

    CW    = COL - 0.18*inch
    IMG_H = 0.88*inch
    # Fixed card height: top section (image+title+tag) + description + specs + price = ~3.5in
    CARD_INNER_H = 3.45*inch

    def vfill(inner, w=CW, h=CARD_INNER_H):
        """Pad inner content to fill fixed height card."""
        rows = [[inner], [Spacer(1, h)]]
        t = Table(rows, colWidths=[w])
        t.setStyle(TableStyle([
            ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
            ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),0),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
        ]))
        return t

    def card(inner, w=COL):
        t = Table([[ inner ]], colWidths=[w])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0),(-1,-1), WHITE),
            ('BOX', (0,0),(-1,-1), 1, LGRAY),
            ('TOPPADDING',(0,0),(-1,-1),9), ('BOTTOMPADDING',(0,0),(-1,-1),9),
            ('LEFTPADDING',(0,0),(-1,-1),9), ('RIGHTPADDING',(0,0),(-1,-1),9),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
        ]))
        return t

    # ── HEADER ──────────────────────────────────────────────────────────────
    hdr_r1 = Table([[
        RLImage(f"{IMG_DIR}/af_logo.jpg", width=1.70*inch, height=0.68*inch),
        Table([[
            P('AMERICAN FLASHINGS', S_HDRB),
            P('Flashing. Ridge Vents. And More.', S_HDRS),
        ]], colWidths=[PW - 3.55*inch]),
        Table([[ P('Based in Michigan', S_HDRS), P('Family Owned', S_HDRS) ]],
              colWidths=[1.75*inch]),
    ]], colWidths=[1.80*inch, PW - 3.55*inch, 1.75*inch])
    hdr_r1.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), NAVY),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),10), ('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('LEFTPADDING',(0,0),(0,0),10),
        ('RIGHTPADDING',(-1,0),(-1,0),10),
        ('LEFTPADDING',(1,0),(1,0),6),
        ('RIGHTPADDING',(1,0),(1,0),6),
    ]))

    hdr_r2 = Table([[P(
        '20 Years in Construction  ·  Premium Building Products for Professionals',
        sty(fontSize=7.5, textColor=WHITE, alignment=TA_CENTER)
    )]], colWidths=[PW])
    hdr_r2.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), ORANGE),
        ('TOPPADDING',(0,0),(-1,-1),4), ('BOTTOMPADDING',(0,0),(-1,-1),4),
    ]))

    hdr = Table([[hdr_r1],[hdr_r2]], colWidths=[PW])
    hdr.setStyle(TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),0),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 6))

    # ── TOP-LEFT: KICKOUT ─────────────────────────────────────────────────
    half = CW / 2 - 2
    kickout_inner = Table([
        [img_el(f"{IMG_DIR}/kickout.jpg", CW, IMG_H)],
        [P("J'd Out Kickout Flashing", S_PN)],
        [P('J-Channel Built In  ·  Consistent Protection', S_TAG)],
        [Spacer(1, 2)],
        [P('Revolutionary kickout flashing with J-Channel pre-built in — no more installing a kickout only to have it removed or damaged by the siding crew. Seamlessly directs water away from the house, preventing rot and mold.', S_DESC)],
        [Spacer(1, 3)],
        [P('10 1/4" Long  ·  5 1/2" at Widest  ·  1" J-Channel Pocket  ·  6 Colors', S_SPEC)],
        [Spacer(1, 6)],
        [P('Call for pricing', S_PRICE)],
    ], colWidths=[CW])
    kickout_inner.setStyle(TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),2),
    ]))

    # ── TOP-RIGHT: EZ GUNNER ───────────────────────────────────────────────
    sz_tbl = Table([
        [P('EZ GUNNER — NFA 12  ·  LOW PROFILE', S_SZH),
         P('EZ GUNNER — NFA 18  ·  STANDARD', S_SZH)],
        [P('$5.61 / ea', S_SZP), P('$5.96 / ea', S_SZP)],
        [P('Lower height for tight spaces', S_SZD), P('Standard profile height', S_SZD)],
        [P('', S_SZD), P('', S_SZD)],
        [P('Reinforced nail gun pockets', S_SHR), P('Reinforced nail gun pockets', S_SHR)],
        [P('Extra-wide water-shedding filter', S_SHR), P('Extra-wide water-shedding filter', S_SHR)],
        [P('Includes 1¾" nails', S_SHR), P('Includes 1¾" nails', S_SHR)],
        [P('UL Approved', S_SHR), P('UL Approved', S_SHR)],
    ], colWidths=[half, half])
    sz_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), NAVY),
        ('BACKGROUND',(0,1),(-1,1), OFFWHT),
        ('BACKGROUND',(0,2),(-1,2), WHITE),
        ('BACKGROUND',(0,3),(-1,3), LGRAY),
        ('BACKGROUND',(0,4),(-1,4), WHITE),
        ('BACKGROUND',(0,5),(-1,5), OFFWHT),
        ('BACKGROUND',(0,6),(-1,6), WHITE),
        ('BACKGROUND',(0,7),(-1,7), OFFWHT),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),4), ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('BOX',(0,0),(-1,-1),0.5, LGRAY),
        ('INNERGRID',(0,0),(-1,-1),0.5, LGRAY),
        ('LINEBEFORE',(1,0),(1,-1),1, LGRAY),
    ]))

    ez_inner = Table([
        [img_el(f"{IMG_DIR}/ez_gunner.jpg", CW, IMG_H)],
        [P('EZ Gunner Ridge Vent', S_PN)],
        [P('Industry-Exclusive Design  ·  Nail Gun Compatible  ·  UL Approved', S_TAG)],
        [Spacer(1, 2)],
        [P('Built with reinforced pockets designed to fit your nail gun and extra wide water shedding filter to protect your attic.', S_DESC)],
        [Spacer(1, 4)],
        [sz_tbl],
    ], colWidths=[CW])
    ez_inner.setStyle(TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),2),
    ]))

    # ── BOTTOM-LEFT: HOUSE WRAP ────────────────────────────────────────────
    wrap_inner = Table([
        [img_el(f"{IMG_DIR}/house_wrap.jpg", CW, IMG_H)],
        [P('Building Armor House Wrap', S_PN)],
        [P("9' x 150' Roll  ·  Weather Barrier", S_TAG)],
        [Spacer(1, 2)],
        [P('Premium weather barrier protecting homes against air and moisture infiltration. Allows walls to breathe while blocking drafts. UV resistant for up to 90 days of exposure.', S_DESC)],
        [Spacer(1, 3)],
        [P("9' x 150' — 1,350 sq ft per roll  ·  Synthetic microfiber construction", S_SPEC)],
        [Spacer(1, 6)],
        [P('$56.16 / roll', S_PRICE)],
    ], colWidths=[CW])
    wrap_inner.setStyle(TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),2),
    ]))

    # ── BOTTOM-RIGHT: ROOF ARMOR ───────────────────────────────────────────
    roof_inner = Table([
        [img_el(f"{IMG_DIR}/roof_armor.jpg", CW, IMG_H)],
        [P('Roof Armor 15 Synthetic Felt Underlayment', S_PN)],
        [P('Steep Slope Roofing  ·  15-Year Warranty Available', S_TAG)],
        [Spacer(1, 2)],
        [P('Premium synthetic felt underlayment providing superior water resistance and slip resistance during installation. Compatible with all roof coverings.', S_DESC)],
        [Spacer(1, 3)],
        [P('Coverage: 10 squares (1,000 sq ft) per roll  ·  Textured surface for secure footing', S_SPEC)],
        [Spacer(1, 6)],
        [P('$29.55 / roll', S_PRICE)],
    ], colWidths=[CW])
    roof_inner.setStyle(TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),2),
    ]))

    # ── ASSEMBLE EQUAL-HEIGHT 2×2 ──────────────────────────────────────────
    grid = Table([
        [card(vfill(kickout_inner)), card(vfill(ez_inner))],
        [card(vfill(wrap_inner)),   card(vfill(roof_inner))],
    ], colWidths=[COL, COL])
    grid.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPSPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),0),
    ]))
    story.append(grid)
    story.append(Spacer(1, 5))

    # ── FOOTER ──────────────────────────────────────────────────────────────
    ft_line = Table([[
        P('American Flashings', S_FOOTB),
        P('Michigan, USA', S_FOOT),
        P('Pat Mead: 616.304.3743  ·  Leo Vallone: 616.262.7977  ·  Kenny Bull: 231.767.5083', S_FOOT),
    ]], colWidths=[1.8*inch, 1.4*inch, PW - 3.2*inch])
    ft_line.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),0),
    ]))
    ft_sub = Table([[P(
        'Order today — ships within 5–7 business days  ·  americanflashings.com',
        sty(fontSize=6.5, textColor=GRAY, alignment=TA_CENTER)
    )]], colWidths=[PW])
    ft_sub.setStyle(TableStyle([
        ('TOPPADDING',(0,0),(-1,-1),4), ('BOTTOMPADDING',(0,0),(-1,-1),2),
    ]))
    ft = Table([[ft_line],[ft_sub]], colWidths=[PW])
    ft.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), OFFWHT),
        ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),10), ('RIGHTPADDING',(0,0),(-1,-1),10),
        ('LINEABOVE',(0,0),(-1,0),1.5, ORANGE),
    ]))
    story.append(ft)

    doc.build(story)
    print(f"Done — {os.path.getsize(OUT_PDF)/1024:.0f} KB")

build()
