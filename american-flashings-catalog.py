from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import urllib.request
import io

# Colors
AF_BLUE = colors.HexColor('#1a4a7a')
AF_ORANGE = colors.HexColor('#e85c2a')
AF_LIGHT = colors.HexColor('#f4f7fa')
AF_GRAY = colors.HexColor('#5a6a7a')
AF_DARK = colors.HexColor('#1a2a3a')

def download_image(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except:
        return None

def build_pdf():
    doc = SimpleDocTemplate(
        "/Users/tradbot/.openclaw/workspace/American_Flashings_Catalog.pdf",
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Normal'],
        fontSize=28, textColor=AF_BLUE, alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
        fontSize=14, textColor=AF_GRAY, alignment=TA_CENTER, spaceAfter=2, fontName='Helvetica')
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'],
        fontSize=10, textColor=AF_GRAY, alignment=TA_CENTER, spaceAfter=16)
    section_style = ParagraphStyle('Section', parent=styles['Normal'],
        fontSize=16, textColor=colors.white, alignment=TA_LEFT, fontName='Helvetica-Bold', spaceAfter=8)
    product_title = ParagraphStyle('ProductTitle', parent=styles['Normal'],
        fontSize=14, textColor=AF_BLUE, fontName='Helvetica-Bold', spaceAfter=4)
    product_desc = ParagraphStyle('ProductDesc', parent=styles['Normal'],
        fontSize=9, textColor=AF_GRAY, spaceAfter=6, leading=13)
    price_style = ParagraphStyle('Price', parent=styles['Normal'],
        fontSize=12, textColor=AF_ORANGE, fontName='Helvetica-Bold')
    spec_label = ParagraphStyle('SpecLabel', parent=styles['Normal'],
        fontSize=9, textColor=AF_DARK, fontName='Helvetica-Bold')
    spec_value = ParagraphStyle('SpecValue', parent=styles['Normal'],
        fontSize=9, textColor=AF_GRAY)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=10, textColor=AF_DARK, spaceAfter=8, leading=14)
    bold_italic_style = ParagraphStyle('BoldItalic', parent=styles['Normal'],
        fontSize=11, textColor=AF_BLUE, fontName='Helvetica-BoldOblique', spaceAfter=6)

    # ==================== PAGE 1: COVER ====================
    # Header bar
    header_data = [[Paragraph('<b>AMERICAN FLASHINGS</b>', ParagraphStyle('H', fontSize=22, textColor=colors.white, fontName='Helvetica-Bold')),
                    Paragraph('Building Products You Can Trust', ParagraphStyle('H2', fontSize=11, textColor=colors.white, alignment=TA_RIGHT))]]
    header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AF_BLUE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (0,0), 20),
        ('RIGHTPADDING', (-1,0), (-1,0), 20),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 30))

    # Tagline
    story.append(Paragraph("Premium Building Products for Professionals", ParagraphStyle('Tag', fontSize=16, textColor=AF_GRAY, alignment=TA_CENTER, fontName='Helvetica-Oblique')))
    story.append(Spacer(1, 20))

    # Subtitle block
    sub_data = [[Paragraph('Quality Products.<br/>Family Values.<br/>Proven Results.', ParagraphStyle('Sub', fontSize=22, textColor=AF_BLUE, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=30))]]
    sub_table = Table(sub_data, colWidths=[7*inch])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AF_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 24),
        ('BOTTOMPADDING', (0,0), (-1,-1), 24),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 30))

    # About section
    story.append(Paragraph('About American Flashings', ParagraphStyle('AboutTitle', fontSize=14, textColor=AF_BLUE, fontName='Helvetica-Bold', spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=2, color=AF_ORANGE, spaceAfter=10))
    story.append(Paragraph(
        "Based in Michigan, American Flashings is a <b>family-owned company</b> with <b>20 years of experience</b> in construction and roofing. "
        "We engineer building products that contractors and builders rely on to protect homes from water intrusion — one of the most common and costly problems in residential construction.",
        body_style))
    story.append(Paragraph(
        "Our flashings, ridge vents, and underlayment products are designed for <b>easy installation</b>, <b>durability</b>, and <b>superior performance</b> in all weather conditions.",
        body_style))
    story.append(Spacer(1, 20))

    # Products grid
    story.append(Paragraph('Featured Products', ParagraphStyle('FP', fontSize=14, textColor=AF_BLUE, fontName='Helvetica-Bold', spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=2, color=AF_ORANGE, spaceAfter=16))

    # Products table
    prod_header = [
        Paragraph('<b>Product</b>', ParagraphStyle('PH', fontSize=10, textColor=colors.white, fontName='Helvetica-Bold')),
        Paragraph('<b>Description</b>', ParagraphStyle('PH', fontSize=10, textColor=colors.white, fontName='Helvetica-Bold')),
        Paragraph('<b>Price</b>', ParagraphStyle('PH', fontSize=10, textColor=colors.white, fontName='Helvetica-Bold', alignment=TA_RIGHT)),
    ]

    products = [
        [
            Paragraph('<b>EZ Gunner Ridge Vent</b><br/><font color="#e85c2a">Standard Profile NFA 18</font>', product_title),
            Paragraph('Industry-exclusive design with reinforced pockets to fit your nail gun. Extra-wide water-shedding filter keeps wind-driven water and snow out. UL Approved.', product_desc),
            Paragraph('$5.96/ea', price_style),
        ],
        [
            Paragraph('<b>EZ Gunner Ridge Vent</b><br/><font color="#e85c2a">Low Profile NFA 12</font>', product_title),
            Paragraph('Same proven design as the Standard Profile in a lower profile. Built with reinforced pockets and extra-wide water shedding filter.', product_desc),
            Paragraph('$5.61/ea', price_style),
        ],
        [
            Paragraph('<b>Building Armor House Wrap</b><br/><font color="#e85c2a">9\' x 150\' Roll</font>', product_title),
            Paragraph('Premium weather barrier protecting homes against air and moisture infiltration. Allows walls to breathe while blocking drafts.', product_desc),
            Paragraph('$56.16/roll', price_style),
        ],
        [
            Paragraph('<b>Roof Armor 15</b><br/><font color="#e85c2a">Synthetic Felt Underlayment</font>', product_title),
            Paragraph('Durable synthetic underlayment providing superior water resistance and slip resistance. 15-year warranty available.', product_desc),
            Paragraph('$29.55/roll', price_style),
        ],
    ]

    prod_table = Table([prod_header] + products, colWidths=[1.8*inch, 4.2*inch, 1*inch])
    prod_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AF_BLUE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, AF_LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dde3ea')),
    ]))
    story.append(prod_table)
    story.append(Spacer(1, 30))

    # Why choose
    story.append(Paragraph('Why Choose American Flashings?', ParagraphStyle('WC', fontSize=14, textColor=AF_BLUE, fontName='Helvetica-Bold', spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=2, color=AF_ORANGE, spaceAfter=12))

    reasons = [
        ['Family Owned & Operated', '20 Years in Construction', 'Professional Grade Products'],
        ['Easy Installation', 'UL Approved', 'Weather-Resistant Design'],
        ['Contractor Recommended', 'Consistent Quality', 'Built for Performance'],
    ]
    reason_style = ParagraphStyle('RS', fontSize=10, textColor=AF_DARK, fontName='Helvetica-Bold', alignment=TA_CENTER)
    reason_table = Table([[Paragraph('<br/>'.join(row), reason_style) for row in reasons]], colWidths=[2.33*inch, 2.33*inch, 2.34*inch])
    reason_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), AF_LIGHT),
        ('BACKGROUND', (1,0), (1,-1), colors.white),
        ('BACKGROUND', (2,0), (2,-1), AF_LIGHT),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 1, AF_BLUE),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dde3ea')),
    ]))
    story.append(reason_table)
    story.append(Spacer(1, 20))

    # ==================== PAGE 2: PRODUCT DETAILS ====================
    story.append(Spacer(1, 20))
    header2_data = [[Paragraph('<b>PRODUCT DETAILS</b>', ParagraphStyle('H2', fontSize=16, textColor=colors.white, fontName='Helvetica-Bold')),
                     Paragraph('americanflashings.com', ParagraphStyle('H2b', fontSize=10, textColor=colors.white, alignment=TA_RIGHT))]]
    header2_table = Table(header2_data, colWidths=[3.5*inch, 3.5*inch])
    header2_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AF_ORANGE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (0,0), 20),
        ('RIGHTPADDING', (-1,0), (-1,0), 20),
    ]))
    story.append(header2_table)
    story.append(Spacer(1, 20))

    # EZ Gunner Detail
    story.append(Paragraph('EZ Gunner Ridge Vent', ParagraphStyle('P2', fontSize=16, textColor=AF_BLUE, fontName='Helvetica-Bold', spaceAfter=4)))
    story.append(Paragraph('<i>Industry-Exclusive Design for Professional Contractors</i>', bold_italic_style))
    story.append(HRFlowable(width="100%", thickness=1, color=AF_ORANGE, spaceAfter=12))

    story.append(Paragraph(
        "The EZ Gunner Ridge Vent is an industry-exclusive ridge vent featuring <b>reinforced pockets</b> designed to fit your nail gun — with no structural give. "
        "Equipped with an <b>extra-wide water-shedding filter</b>, this vent keeps wind-driven water and snow out of your attic while allowing proper ventilation. "
        "<b>UL Approved</b> for peace of mind.",
        body_style))
    story.append(Spacer(1, 12))

    # Two sizes side by side
    ez_specs = [
        [Paragraph('<b>Standard Profile NFA 18</b>', ParagraphStyle('ES', fontSize=12, textColor=AF_BLUE, fontName='Helvetica-Bold')),
         Paragraph('<b>Low Profile NFA 12</b>', ParagraphStyle('ES', fontSize=12, textColor=AF_BLUE, fontName='Helvetica-Bold'))],
        [Paragraph('$5.96 / each', ParagraphStyle('EP', fontSize=14, textColor=AF_ORANGE, fontName='Helvetica-Bold')),
         Paragraph('$5.61 / each', ParagraphStyle('EP', fontSize=14, textColor=AF_ORANGE, fontName='Helvetica-Bold'))],
        [Paragraph('Standard profile height', spec_value),
         Paragraph('Lower profile for tight spaces', spec_value)],
        [Paragraph('Reinforced nail pockets', spec_value),
         Paragraph('Same reinforced design', spec_value)],
        [Paragraph('Extra-wide water-shedding filter', spec_value),
         Paragraph('Extra-wide water-shedding filter', spec_value)],
        [Paragraph('UL Approved', spec_value),
         Paragraph('UL Approved', spec_value)],
    ]
    ez_table = Table(ez_specs, colWidths=[3.4*inch, 3.6*inch])
    ez_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AF_LIGHT),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (0,-1), 1, AF_BLUE),
        ('BOX', (1,0), (1,-1), 1, AF_ORANGE),
        ('LINEBEFORE', (1,0), (1,-1), 1, colors.HexColor('#dde3ea')),
    ]))
    story.append(ez_table)
    story.append(Spacer(1, 25))

    # Building Armor House Wrap
    story.append(Paragraph('Building Armor House Wrap', ParagraphStyle('P2', fontSize=16, textColor=AF_BLUE, fontName='Helvetica-Bold', spaceAfter=4)))
    story.append(Paragraph('<i>Premium Weather Barrier for Complete Wall Protection</i>', bold_italic_style))
    story.append(HRFlowable(width="100%", thickness=1, color=AF_ORANGE, spaceAfter=12))

    story.append(Paragraph(
        "Building Armor House Wrap is a premium weather barrier designed to protect homes against <b>air and moisture infiltration</b> while allowing walls to breathe. "
        "This breathable barrier helps reduce energy costs, prevents mold and rot, and provides a consistent protective layer that works with all types of siding — vinyl, fiber cement, cedar, and more.",
        body_style))
    story.append(Spacer(1, 10))

    wrap_specs = [
        [Paragraph('<b>Building Armor House Wrap</b>', spec_label), Paragraph('<b>Specifications</b>', spec_label)],
        [Paragraph('Roll Size:', spec_label), Paragraph('9 feet x 150 feet (1,350 sq ft)', spec_value)],
        [Paragraph('Material:', spec_label), Paragraph('Synthetic microfiber construction', spec_value)],
        [Paragraph('Perm Rating:', spec_label), Paragraph('Allows moisture vapor to escape', spec_value)],
        [Paragraph('UV Resistance:', spec_label), Paragraph('90 days exposure rating', spec_value)],
        [Paragraph('Price:', spec_label), Paragraph('$56.16 per roll', ParagraphStyle('PV', fontSize=12, textColor=AF_ORANGE, fontName='Helvetica-Bold'))],
    ]
    wrap_table = Table(wrap_specs, colWidths=[2*inch, 5*inch])
    wrap_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AF_LIGHT),
        ('BACKGROUND', (0,2), (0,2), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1, AF_BLUE),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dde3ea')),
    ]))
    story.append(wrap_table)
    story.append(Spacer(1, 25))

    # Roof Armor
    story.append(Paragraph('Roof Armor 15 Synthetic Felt Underlayment', ParagraphStyle('P2', fontSize=16, textColor=AF_BLUE, fontName='Helvetica-Bold', spaceAfter=4)))
    story.append(Paragraph('<i>Superior Water Resistance for Steep Slope Roofs</i>', bold_italic_style))
    story.append(HRFlowable(width="100%", thickness=1, color=AF_ORANGE, spaceAfter=12))

    story.append(Paragraph(
        "Roof Armor 15 is a <b>premium synthetic felt underlayment</b> engineered for steep slope roofing applications. "
        "It provides <b>superior water resistance</b>, excellent slip resistance during installation, and exceptional durability. "
        "Compatible with all roof coverings including asphalt shingles, metal, and tile.",
        body_style))
    story.append(Spacer(1, 10))

    roof_specs = [
        [Paragraph('<b>Roof Armor 15</b>', spec_label), Paragraph('<b>Specifications</b>', spec_label)],
        [Paragraph('Roll Coverage:', spec_label), Paragraph('10 squares (1,000 sq ft) coverage', spec_value)],
        [Paragraph('Weight:', spec_label), Paragraph('Lightweight — easier to handle than traditional felt', spec_value)],
        [Paragraph('Water Resistance:', spec_label), Paragraph('Superior water barrier performance', spec_value)],
        [Paragraph('Slip Resistance:', spec_label), Paragraph('Textured surface for secure footing', spec_value)],
        [Paragraph('Warranty:', spec_label), Paragraph('15-year limited warranty available', spec_value)],
        [Paragraph('Price:', spec_label), Paragraph('$29.55 per roll', ParagraphStyle('PV', fontSize=12, textColor=AF_ORANGE, fontName='Helvetica-Bold'))],
    ]
    roof_table = Table(roof_specs, colWidths=[2*inch, 5*inch])
    roof_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AF_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1, AF_ORANGE),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dde3ea')),
    ]))
    story.append(roof_table)
    story.append(Spacer(1, 20))

    # ==================== PAGE 3: CONTACT & ORDERING ====================
    story.append(Spacer(1, 20))
    header3_data = [[Paragraph('<b>CONTACT & ORDERING</b>', ParagraphStyle('H3', fontSize=16, textColor=colors.white, fontName='Helvetica-Bold')),
                     Paragraph('americanflashings.com', ParagraphStyle('H3b', fontSize=10, textColor=colors.white, alignment=TA_RIGHT))]]
    header3_table = Table(header3_data, colWidths=[3.5*inch, 3.5*inch])
    header3_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AF_BLUE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (0,0), 20),
        ('RIGHTPADDING', (-1,0), (-1,0), 20),
    ]))
    story.append(header3_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph('Your Sales Representatives', ParagraphStyle('CR', fontSize=14, textColor=AF_BLUE, fontName='Helvetica-Bold', spaceAfter=12)))
    story.append(HRFlowable(width="100%", thickness=2, color=AF_ORANGE, spaceAfter=16))

    # Contact cards
    contacts = [
        ['Pat Mead', '616.304.3743', 'pmead@accinc.us'],
        ['Leo Vallone', '616.262.7977', 'lvallone@accinc.us'],
        ['Kenny Bull', '231.767.5083', 'kbull@accinc.us'],
    ]
    contact_style2 = ParagraphStyle('CS2', fontSize=11, textColor=AF_DARK, fontName='Helvetica-Bold', alignment=TA_CENTER)
    contact_phone = ParagraphStyle('CP', fontSize=10, textColor=AF_BLUE, alignment=TA_CENTER)
    contact_email = ParagraphStyle('CE', fontSize=9, textColor=AF_GRAY, alignment=TA_CENTER)

    contact_data = []
    for c in contacts:
        contact_data.append([
            Paragraph(c[0], contact_style2),
            Paragraph(c[1], contact_phone),
            Paragraph(c[2], contact_email),
        ])

    contact_table = Table(contact_data, colWidths=[2.33*inch, 2.33*inch, 2.34*inch])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AF_LIGHT),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('BOX', (0,0), (0,-1), 1, AF_BLUE),
        ('BOX', (1,0), (1,-1), 1, colors.HexColor('#dde3ea')),
        ('BOX', (2,0), (2,-1), 1, AF_ORANGE),
        ('LINEBEFORE', (1,0), (1,-1), 1, colors.white),
        ('LINEBEFORE', (2,0), (2,-1), 1, colors.white),
    ]))
    story.append(contact_table)
    story.append(Spacer(1, 25))

    # Order info
    story.append(Paragraph('How to Order', ParagraphStyle('HO', fontSize=14, textColor=AF_BLUE, fontName='Helvetica-Bold', spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=2, color=AF_ORANGE, spaceAfter=12))

    order_steps = [
        ['1', 'Contact your sales representative by phone or email'],
        ['2', 'Discuss your project requirements and quantities'],
        ['3', 'Receive a custom quote based on your needs'],
        ['4', 'Place your order — most orders ship within 5-7 business days'],
        ['5', 'Track delivery or arrange pickup at our Michigan facility'],
    ]
    step_num = ParagraphStyle('SN', fontSize=14, textColor=colors.white, fontName='Helvetica-Bold', alignment=TA_CENTER)
    step_text = ParagraphStyle('ST', fontSize=10, textColor=AF_DARK, leading=14)

    order_data = []
    for step in order_steps:
        order_data.append([
            Paragraph(step[0], step_num),
            Paragraph(step[1], step_text),
        ])

    order_table = Table(order_data, colWidths=[0.5*inch, 6.5*inch])
    order_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), AF_BLUE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (0,-1), 12),
        ('LEFTPADDING', (1,0), (1,-1), 16),
        ('ROWBACKGROUNDS', (1,0), (1,-1), [colors.white, AF_LIGHT]),
        ('BOX', (0,0), (-1,-1), 1, AF_BLUE),
    ]))
    story.append(order_table)
    story.append(Spacer(1, 25))

    # Shipping info
    story.append(Paragraph('Shipping & Availability', ParagraphStyle('SS', fontSize=14, textColor=AF_BLUE, fontName='Helvetica-Bold', spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=2, color=AF_ORANGE, spaceAfter=12))

    ship_data = [
        ['Location:', 'Michigan-based facility — shipping throughout the Midwest and beyond'],
        ['Lead Time:', '5-7 business days for most orders'],
        ['Bulk Orders:', 'Volume discounts available — contact your sales rep'],
        ['Pickup:', 'Available at our Michigan location'],
    ]
    ship_style = ParagraphStyle('Ship', fontSize=10, textColor=AF_DARK, leading=14)
    ship_label = ParagraphStyle('ShipL', fontSize=10, textColor=AF_BLUE, fontName='Helvetica-Bold')

    ship_table_data = [[Paragraph(s[0], ship_label), Paragraph(s[1], ship_style)] for s in ship_data]
    ship_table = Table(ship_table_data, colWidths=[1.5*inch, 5.5*inch])
    ship_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, AF_LIGHT]),
        ('BOX', (0,0), (-1,-1), 1, AF_BLUE),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dde3ea')),
    ]))
    story.append(ship_table)
    story.append(Spacer(1, 30))

    # Footer quote
    footer_data = [[Paragraph(
        '"80% of damaging water intrusions to side walls are due to missing or improperly installed kickouts."<br/>'
        '<font size="9">— American Flashings / Fine Home Building</font>',
        ParagraphStyle('FQ', fontSize=11, textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica-Oblique', leading=16)
    )]]
    footer_table = Table(footer_data, colWidths=[7*inch])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AF_DARK),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 24),
        ('RIGHTPADDING', (0,0), (-1,-1), 24),
    ]))
    story.append(footer_table)
    story.append(Spacer(1, 10))

    # Website footer
    story.append(Paragraph(
        'americanflashings.com  |  Questions? Contact your sales representative listed above',
        ParagraphStyle('Footer', fontSize=9, textColor=AF_GRAY, alignment=TA_CENTER)
    ))

    doc.build(story)
    print("PDF created successfully!")

build_pdf()
