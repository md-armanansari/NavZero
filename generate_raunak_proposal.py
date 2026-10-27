"""
Generates the customized official CU-TBI Incubation Proposal PDF
for Raunak Kumar, Student Innovator & Founder at Chandigarh University.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

pdf_path = Path(__file__).resolve().parent / "CU_TBI_INCUBATION_PROPOSAL_RAUNAK_KUMAR.pdf"
doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=letter,
    rightMargin=40,
    leftMargin=40,
    topMargin=40,
    bottomMargin=40
)

styles = getSampleStyleSheet()

# Custom typography
doc_title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=colors.HexColor('#0F2A4A'),
    alignment=1, # Center
    spaceAfter=6
)

doc_sub_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=15,
    textColor=colors.HexColor('#C0392B'),
    alignment=1,
    spaceAfter=12
)

meta_style = ParagraphStyle(
    'MetaText',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=13,
    textColor=colors.HexColor('#444444'),
    alignment=1,
    spaceAfter=10
)

h1_style = ParagraphStyle(
    'Heading1_Custom',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=12.5,
    leading=16.5,
    textColor=colors.HexColor('#0F2A4A'),
    spaceBefore=12,
    spaceAfter=6
)

h2_style = ParagraphStyle(
    'Heading2_Custom',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#1B5E20'),
    spaceBefore=8,
    spaceAfter=4
)

body_style = ParagraphStyle(
    'Body_Custom',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=13,
    textColor=colors.HexColor('#222222'),
    spaceAfter=6
)

bullet_style = ParagraphStyle(
    'Bullet_Custom',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=12.5,
    textColor=colors.HexColor('#333333'),
    leftIndent=12,
    spaceAfter=3
)

callout_style = ParagraphStyle(
    'Callout_Custom',
    parent=styles['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=8.5,
    leading=12.5,
    textColor=colors.HexColor('#0D47A1'),
    spaceAfter=5
)

elements = []

# Header
elements.append(Paragraph("CU-TBI FORMAL INCUBATION & PRE-SEED GRANT PROPOSAL", doc_title_style))
elements.append(Paragraph("Project: Autonomous GPS-Denied Vision-Based UAV Localization System (NavZero / Project Trishul)", doc_sub_style))
elements.append(Paragraph("<b>Applicant & Lead Innovator:</b> <b>Raunak Kumar</b> | Chandigarh University, Punjab<br/>"
                          "<b>Target Scheme:</b> CU-TBI Pre-Incubation / DST NIDHI-PRAYAS (₹10 Lakhs) / DST NIDHI-EIR Fellowship<br/>"
                          "<b>Domain:</b> Aerospace & Defense / Autonomous Robotics | <b>Readiness:</b> TRL 3/4 (Analytical Laboratory Prototype Complete)", meta_style))
elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F2A4A'), spaceAfter=10))

# 1. Executive Summary
elements.append(Paragraph("1. EXECUTIVE SUMMARY", h1_style))
elements.append(Paragraph(
    "Electronic Warfare (EW) and localized Global Navigation Satellite System (GNSS) jamming have emerged as the primary failure point "
    "for tactical Unmanned Aerial Vehicles (UAVs) in modern contested border sectors (e.g., Eastern Ladakh). Commercial-off-the-shelf and standard "
    "military UAVs relying on satellite positioning experience catastrophic navigational loss, drifting, or mission abortion when GPS signals are suppressed.",
    body_style
))
elements.append(Paragraph(
    "<b>Project Trishul / NavZero</b>, developed by <b>Raunak Kumar</b>, is an indigenous, edge-compute visual localization software engine that enables tactical UAVs to autonomously determine "
    "their global geodetic coordinates (X, Y) and execute autonomous Return-to-Home (V-RTH) maneuvers with <b>zero dependence on GPS, magnetometer compasses, "
    "or external radio-frequency emissions</b>.",
    body_style
))
elements.append(Paragraph("<b>Current Technical Accomplishments (Validated on Consumer Quad-Core CPU):</b>", body_style))
elements.append(Paragraph("• <b>Real-time execution:</b> 26–45 frames per second on low-power quad-core CPU architecture without requiring bulky dedicated GPUs.<br/>"
                          "• <b>Algorithmic architecture:</b> Multi-scale ORB binary descriptors, bitwise Hamming matching, Lowe's distance ratio filtering (d1 < 0.75 * d2), and projective RANSAC geometric outlier rejection.<br/>"
                          "• <b>Geospatial integration:</b> Standard 6-parameter GDAL/USGS affine coordinate transformations mapping camera frame pixels to metric map coordinates.<br/>"
                          "• <b>Software rigor:</b> 34 passing automated unit tests (100% pass rate) with a sub-250MB memory footprint.", bullet_style))
elements.append(Paragraph(
    "We are seeking <b>formal pre-incubation, laboratory workspace access, and prototype grant endorsement (NIDHI-PRAYAS / NIDHI-EIR)</b> through "
    "CU-TBI to transition this proven software engine onto an embedded physical airframe (Raspberry Pi 5 + Pixhawk 6C) for outdoor flight validation.",
    callout_style
))

elements.append(Spacer(1, 8))

# 2. Problem Statement
elements.append(Paragraph("2. PROBLEM STATEMENT & NATIONAL DEFENSE RELEVANCE", h1_style))
elements.append(Paragraph(
    "In contested environments, adversary ground vehicles deploy high-power Electronic Warfare (EW) jammers broadcasting broadband noise across L1/L2 satellite bands. "
    "Because satellite signals originate 20,000 km in space, their ground received power is exceptionally weak (~ -160 dBW). A low-cost 50-watt ground jammer effectively denies GPS across a 20–30 km radius.",
    body_style
))
elements.append(Paragraph(
    "When GPS fails, conventional drones enter fail-safe descent inside hostile territory or drift uncontrolled into mountain cliffs. "
    "Inertial Measurement Units (IMUs) accumulate quadratic drift over time (~ 1/2 * a * t^2), deviating by hundreds of meters in minutes. "
    "The Indian Ministry of Defence (MoD) and Innovations for Defence Excellence (iDEX) have identified <b>GPS-Denied UAV Navigation</b> as a high-priority "
    "challenge under recent Defence India Startup Challenges (DISC). Our project directly addresses this critical capability gap under <i>Aatmanirbhar Bharat</i>.",
    body_style
))

elements.append(Spacer(1, 8))

# 3. Technical Solution
elements.append(Paragraph("3. THE PROPOSED SOLUTION: NAVZERO OPTICAL ARCHITECTURE", h1_style))
elements.append(Paragraph(
    "Our system provides a passive, non-emissive optical autopilot that navigates by matching physical terrain passing beneath the drone's belly camera "
    "against pre-loaded reconnaissance orthophoto tiles stored in onboard memory, operating in two distinct operational modes:",
    body_style
))
elements.append(Paragraph("• <b>Mode A (Absolute Map Matching):</b> When satellite/aerial imagery is pre-loaded before takeoff, the drone computes exact geodetic coordinates (Lat, Lon) by locking onto permanent geological landmarks at 30 Hz update rates.<br/>"
                          "• <b>Mode B (Zero-Map Visual Breadcrumb Return):</b> When flying into uncharted territory with zero maps, the engine tracks inter-frame visual breadcrumbs along its outbound flight path. When GPS is jammed or radio contact severed, the autopilot engages Autonomous Visual Return-to-Home (V-RTH), reversing heading and retracing its visual footprints all the way back to the exact takeoff point.", bullet_style))

elements.append(PageBreak())

# Page 2: Budget and Roadmap
elements.append(Paragraph("4. BUDGET & BILL OF MATERIALS (BOM) FOR CU-TBI / NIDHI-PRAYAS", h1_style))
elements.append(Paragraph(
    "To transition this technology from <b>TRL 4 (Laboratory Validation)</b> to <b>TRL 6 (Physical Airframe Demonstration)</b>, we request temporary issue of "
    "existing college lab components or prototype grant funding under NIDHI-PRAYAS according to the following itemized Bill of Materials:",
    body_style
))

bom_data = [
    [Paragraph("<b>Item Description</b>", body_style), Paragraph("<b>Qty</b>", body_style), Paragraph("<b>Technical Purpose</b>", body_style), Paragraph("<b>Est. Cost (₹)</b>", body_style)],
    [
        Paragraph("<b>Raspberry Pi 5 (8GB) + Active Cooler</b>", bullet_style),
        Paragraph("2", body_style),
        Paragraph("Onboard companion computer running Python/OpenCV vision pipeline", body_style),
        Paragraph("₹18,000", body_style)
    ],
    [
        Paragraph("<b>Pixhawk 6C / 4 Flight Controller Kit</b>", bullet_style),
        Paragraph("1", body_style),
        Paragraph("Open-source autopilot running ArduPilot for MAVLink telemetry fusion", body_style),
        Paragraph("₹16,000", body_style)
    ],
    [
        Paragraph("<b>Global Shutter Downward Camera Module</b>", bullet_style),
        Paragraph("2", body_style),
        Paragraph("High-speed, distortion-free optical ground tracking sensor", body_style),
        Paragraph("₹8,000", body_style)
    ],
    [
        Paragraph("<b>F450 Quadcopter Airframe + Motors/ESCs</b>", bullet_style),
        Paragraph("1", body_style),
        Paragraph("Basic quadcopter test bench for outdoor flight integration", body_style),
        Paragraph("₹14,000", body_style)
    ],
    [
        Paragraph("<b>LiPo Batteries (4S 5000mAh) + Smart Charger</b>", bullet_style),
        Paragraph("2", body_style),
        Paragraph("Propulsion and avionics power supply", body_style),
        Paragraph("₹12,000", body_style)
    ],
    [
        Paragraph("<b>Benchtop Rig Hardware & Connectors</b>", bullet_style),
        Paragraph("-", body_style),
        Paragraph("Acrylic mounting plates, FTDI cables, telemetry radios", body_style),
        Paragraph("₹7,000", body_style)
    ],
    [
        Paragraph("<b>Field Testing & Safety Compliance</b>", bullet_style),
        Paragraph("-", body_style),
        Paragraph("Safety nets, ground calibration markers, field logistics", body_style),
        Paragraph("₹10,000", body_style)
    ],
    [
        Paragraph("<b>TOTAL ESTIMATED PROTOTYPE BUDGET:</b>", h2_style),
        Paragraph("", body_style),
        Paragraph("<b>Complete 6-Month Physical Airframe Integration</b>", h2_style),
        Paragraph("<b>₹85,000</b>", h2_style)
    ]
]

bom_table = Table(bom_data, colWidths=[2.2 * inch, 0.4 * inch, 3.4 * inch, 1.0 * inch])
bom_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#B0BEC5')),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ECEFF1')),
]))
elements.append(bom_table)
elements.append(Paragraph("<i>Note: If CU robotics/aerospace laboratories already possess Pixhawk controllers and Raspberry Pis, the required cash grant can be reduced to under ₹25,000 for consumables.</i>", callout_style))

elements.append(Spacer(1, 10))

# 5. Roadmap
elements.append(Paragraph("5. 6-MONTH MILESTONE EXECUTION ROADMAP", h1_style))

roadmap_data = [
    [Paragraph("<b>Phase</b>", body_style), Paragraph("<b>Timeline</b>", body_style), Paragraph("<b>Key Technical Deliverables & Milestones</b>", body_style)],
    [
        Paragraph("<b>Phase 1: Embedded Porting</b>", bullet_style),
        Paragraph("Month 1–2", body_style),
        Paragraph("Port existing Python/OpenCV vision codebase to Raspberry Pi OS (Linux ARM64). Benchmark C++ bindings to achieve stable 30+ FPS at under 7 watts power consumption.", body_style)
    ],
    [
        Paragraph("<b>Phase 2: Hardware-in-Loop</b>", bullet_style),
        Paragraph("Month 3–4", body_style),
        Paragraph("Establish two-way UART serial communication between Raspberry Pi and Pixhawk flight controller using pymavlink. Verify simulated GPS failsafe handoff on benchtop rig without propellers.", body_style)
    ],
    [
        Paragraph("<b>Phase 3: Tethered Flight</b>", bullet_style),
        Paragraph("Month 5", body_style),
        Paragraph("Integrate hardware onto F450 quadcopter airframe. Conduct low-altitude tethered hover tests over college ground markers. Demonstrate GPS jamming injection and automatic optical position holding.", body_style)
    ],
    [
        Paragraph("<b>Phase 4: Full Outdoor RTH & iDEX Filing</b>", bullet_style),
        Paragraph("Month 6", body_style),
        Paragraph("Execute full outdoor autonomous mission: manual takeoff -> GPS cut -> autonomous optical return-to-home and landing. Film high-resolution video proof and submit formal application for iDEX DISC (₹1.5 Cr) and Smart India Hackathon under Chandigarh University's banner.", body_style)
    ]
]

rm_table = Table(roadmap_data, colWidths=[1.8 * inch, 1.0 * inch, 4.2 * inch])
rm_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8F5E9')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1B5E20')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#B0BEC5')),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(rm_table)

elements.append(Spacer(1, 12))

# 6. Commercialization & Sign-Off
elements.append(Paragraph("6. COMMERCIAL OPPORTUNITY & PRESTIGE FOR CHANDIGARH UNIVERSITY", h1_style))
elements.append(Paragraph(
    "1. <b>Defense Procurement:</b> The primary customer is the Indian defense ecosystem (Indian Army artillery units, Northern Command surveillance, BSF border patrol). "
    "By developing an export-free, indigenous software kit, we can retrofit existing military drone fleets with GPS-denied survivability.<br/>"
    "2. <b>Institutional Prestige for CU:</b> Submitting a validated TRL-6 defense project to national platforms (iDEX, DefTech, SIH) significantly enhances "
    "Chandigarh University's NIRF research ranking, NAAC accreditation, and national media recognition.<br/>"
    "3. <b>Immediate Live Demo:</b> An interactive physical demonstration of the computer vision engine, flight simulator, and 34-test suite can be delivered to the CU-TBI screening committee on 10 minutes notice.",
    body_style
))

elements.append(Spacer(1, 15))

# Signature Block with Raunak Kumar's name
sig_data = [
    [
        Paragraph("<b>Submitted By:</b><br/><br/><br/>___________________________<br/><b>Raunak Kumar</b><br/>Lead Innovator & Founder<br/>Chandigarh University, Punjab", body_style),
        Paragraph("<b>Endorsed & Forwarded By:</b><br/><br/><br/>___________________________<br/><b>Head of Department / Mentor</b><br/>Faculty of Engineering & Technology<br/>Chandigarh University", body_style),
        Paragraph("<b>Received By CU-TBI:</b><br/><br/><br/>___________________________<br/><b>Incubation Manager / In-Charge</b><br/>Technology Business Incubator<br/>Chandigarh University", body_style)
    ]
]
sig_table = Table(sig_data, colWidths=[2.3 * inch, 2.4 * inch, 2.3 * inch])
sig_table.setStyle(TableStyle([
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#90A4AE')),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA')),
]))
elements.append(sig_table)

doc.build(elements)
print(f"SUCCESS: Generated proposal PDF for Raunak Kumar at {pdf_path}")
