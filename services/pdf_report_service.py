"""PDF Report Generation Service for Legacy Dataforce.

Provides publication-grade PDF generation using ReportLab for:
1. Complete Individual Student Profile PDF
2. Individual Mandatory Internship Compliance PDF
3. Student Internship History PDF
4. Missing Mandatory Internship Audit PDF
"""

import io
from typing import Optional
from datetime import datetime

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from services.student_service import get_student
from services.internship_service import (
    check_internship_eligibility,
    get_students_missing_mandatory_internships,
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for Page X of Y numbering."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_footer(self, page_count):
        self.saveState()
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 30, 576, 30)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(36, 20, "Legacy Dataforce Portal  •  Official Institutional Academic Record")
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0f172a"))
        self.drawRightString(576, 20, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def _get_styles():
    base = getSampleStyleSheet()
    styles = {
        'DocTitle': ParagraphStyle('DocTitle', parent=base['Heading1'], fontName='Helvetica-Bold', fontSize=16, leading=19, textColor=colors.HexColor('#1e3a8a'), spaceAfter=4),
        'DocSub': ParagraphStyle('DocSub', parent=base['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#64748b'), spaceAfter=10),
        'SecHead': ParagraphStyle('SecHead', parent=base['Heading2'], fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=colors.HexColor('#0f172a'), spaceBefore=8, spaceAfter=4, keepWithNext=True),
        'TableHead': ParagraphStyle('TableHead', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#ffffff')),
        'TableCell': ParagraphStyle('TableCell', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#1e293b')),
        'TableCellBold': ParagraphStyle('TableCellBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#0f172a')),
        'TagSuccess': ParagraphStyle('TagSuccess', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor('#065f46')),
        'TagDanger': ParagraphStyle('TagDanger', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor('#991b1b')),
    }
    return styles


# -----------------------------------------------------------------------------
# 1. Complete Individual Student Profile PDF
# -----------------------------------------------------------------------------
def generate_student_profile_pdf(student_id: int) -> bytes:
    """Generates a comprehensive 360-degree Student Profile PDF."""
    student = get_student(student_id)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=40)
    styles = _get_styles()
    story = []

    # Document Header
    story.append(Paragraph("LEGACY DATAFORCE &bull; STUDENT DOSSIER", styles['DocSub']))
    story.append(Paragraph(f"Complete Student Profile: {student['Full_Name']} ({student['Roll_No']})", styles['DocTitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1e3a8a"), spaceBefore=0, spaceAfter=8))

    # Personal & Academic Summary Table
    personal_data = [
        [Paragraph("<b>Roll Number:</b>", styles['TableCellBold']), Paragraph(student['Roll_No'], styles['TableCell']),
         Paragraph("<b>Branch:</b>", styles['TableCellBold']), Paragraph(f"{student['Branch']} (Batch {student['Batch_Year']})", styles['TableCell'])],
        [Paragraph("<b>Student Name:</b>", styles['TableCellBold']), Paragraph(student['Full_Name'], styles['TableCell']),
         Paragraph("<b>Cumulative GPA:</b>", styles['TableCellBold']), Paragraph(f"{student['CGPA']:.2f} / 10.00", styles['TableCell'])],
        [Paragraph("<b>Institutional Email:</b>", styles['TableCellBold']), Paragraph(student['Email'], styles['TableCell']),
         Paragraph("<b>Active Backlogs:</b>", styles['TableCellBold']), Paragraph(str(student['Backlogs']), styles['TableCell'])],
        [Paragraph("<b>Contact Phones:</b>", styles['TableCellBold']), Paragraph(", ".join(student.get('Phones', [])) or "None registered", styles['TableCell']),
         Paragraph("<b>Technical Skills:</b>", styles['TableCellBold']), Paragraph(", ".join(student.get('Skills', [])) or "None recorded", styles['TableCell'])],
    ]
    t_personal = Table(personal_data, colWidths=[100, 170, 100, 170])
    t_personal.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_personal)
    story.append(Spacer(1, 6))

    # Academic Semester Results Ledger
    story.append(Paragraph("Chronological Semester Performance Ledger", styles['SecHead']))
    sem_rows = [[Paragraph("Semester", styles['TableHead']), Paragraph("Academic Year", styles['TableHead']),
                 Paragraph("SGPA", styles['TableHead']), Paragraph("Credits Earned", styles['TableHead']), Paragraph("Standing", styles['TableHead'])]]
    for s in student.get('Semester_Results', []):
        standing = "Excellent" if s['SGPA'] >= 9.0 else "Good" if s['SGPA'] >= 7.5 else "Passing"
        sem_rows.append([
            Paragraph(f"Semester {s['Semester']}", styles['TableCell']),
            Paragraph(str(s.get('Year', 'N/A')), styles['TableCell']),
            Paragraph(f"<b>{s['SGPA']:.2f}</b>", styles['TableCell']),
            Paragraph(str(s.get('Total_Credits', 24)), styles['TableCell']),
            Paragraph(standing, styles['TagSuccess'] if s['SGPA'] >= 7.5 else styles['TableCell'])
        ])
    t_sem = Table(sem_rows, colWidths=[100, 100, 100, 120, 120])
    t_sem.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_sem)
    story.append(Spacer(1, 6))

    # Enrolled Course Work
    if student.get('Registered_Courses'):
        story.append(Paragraph("Registered Course Work & Academic Curricula", styles['SecHead']))
        course_rows = [[Paragraph("Semester", styles['TableHead']), Paragraph("Course Name", styles['TableHead']),
                        Paragraph("Type", styles['TableHead']), Paragraph("Credits", styles['TableHead']), Paragraph("Final Grade", styles['TableHead'])]]
        for c in student['Registered_Courses']:
            course_rows.append([
                Paragraph(f"Sem {c['Semester']}", styles['TableCell']),
                Paragraph(c['Course_Name'], styles['TableCell']),
                Paragraph(c.get('Course_Type', 'Core'), styles['TableCell']),
                Paragraph(str(c.get('Credits', 4)), styles['TableCell']),
                Paragraph(f"<b>{c.get('Grade', 'N/A')}</b>", styles['TableCell']),
            ])
        t_course = Table(course_rows, colWidths=[65, 235, 80, 70, 90])
        t_course.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f766e')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ]))
        story.append(t_course)
        story.append(Spacer(1, 6))

    # Placement Offers
    story.append(Paragraph("Placement Offers & Compensation Records", styles['SecHead']))
    if student.get('Placements'):
        p_rows = [[Paragraph("Recruiting Organization", styles['TableHead']), Paragraph("Designated Role", styles['TableHead']),
                   Paragraph("Package (CTC)", styles['TableHead']), Paragraph("Offer Status", styles['TableHead']), Paragraph("PPO", styles['TableHead'])]]
        for p in student['Placements']:
            status_style = styles['TagSuccess'] if p.get('Joined') == 'Yes' or p.get('Offer_Status') in ('Accepted', 'Joined') else styles['TableCell']
            p_rows.append([
                Paragraph(p['Company_Name'], styles['TableCellBold']),
                Paragraph(p['Role'], styles['TableCell']),
                Paragraph(f"<b>{p['Package']:.2f} LPA</b>", styles['TableCell']),
                Paragraph(p.get('Offer_Status', 'Offered'), status_style),
                Paragraph(p.get('Is_PPO', 'No'), styles['TableCell'])
            ])
        t_p = Table(p_rows, colWidths=[150, 160, 80, 90, 60])
        t_p.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1d4ed8')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ]))
        story.append(t_p)
    else:
        story.append(Paragraph("<i>No placement offers recorded to date. Candidate currently in active placement pipeline.</i>", styles['TableCell']))
    story.append(Spacer(1, 6))

    # Internships Dossier
    story.append(Paragraph("Internship Experience & Degree Compliance", styles['SecHead']))
    if student.get('Internships'):
        i_rows = [[Paragraph("Category", styles['TableHead']), Paragraph("Company Name", styles['TableHead']),
                   Paragraph("Designated Role", styles['TableHead']), Paragraph("Duration", styles['TableHead']), Paragraph("Monthly Stipend", styles['TableHead']), Paragraph("Status", styles['TableHead'])]]
        for i_item in student['Internships']:
            cat_str = f"Mandatory #{i_item['Internship_No']}" if i_item['Internship_Type'] == 'Mandatory' else "Additional"
            i_rows.append([
                Paragraph(cat_str, styles['TableCellBold']),
                Paragraph(i_item['Company_Name'], styles['TableCell']),
                Paragraph(i_item['Role'], styles['TableCell']),
                Paragraph(i_item.get('Duration_Str', '8 weeks'), styles['TableCell']),
                Paragraph(f"Rs. {i_item.get('Stipend', 0):,.0f}", styles['TableCell']),
                Paragraph(i_item.get('Status', 'Completed'), styles['TagSuccess'] if i_item.get('Status') == 'Completed' else styles['TableCell'])
            ])
        t_i = Table(i_rows, colWidths=[85, 145, 120, 75, 65, 50])
        t_i.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#047857')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ]))
        story.append(t_i)
    else:
        story.append(Paragraph("<i>No internships recorded.</i>", styles['TableCell']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()


# -----------------------------------------------------------------------------
# 2. Individual Mandatory Internship Compliance PDF
# -----------------------------------------------------------------------------
def generate_individual_compliance_pdf(student_id: int) -> bytes:
    """Generates an official Individual Mandatory Internship Compliance Verification PDF."""
    student = get_student(student_id)
    elig_1 = check_internship_eligibility(student_id, 1)
    elig_2 = check_internship_eligibility(student_id, 2)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=40)
    styles = _get_styles()
    story = []

    story.append(Paragraph("INSTITUTIONAL ACCREDITATION & ACADEMIC AUDIT", styles['DocSub']))
    story.append(Paragraph("Mandatory Degree Internship Compliance Report", styles['DocTitle']))
    story.append(Paragraph(f"Candidate: <b>{student['Full_Name']}</b> &nbsp;|&nbsp; Roll No: <b>{student['Roll_No']}</b> &nbsp;|&nbsp; Branch: <b>{student['Branch']}</b> (Batch {student['Batch_Year']})", styles['DocSub']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#065f46"), spaceBefore=0, spaceAfter=10))

    # Academic Prerequisite Thresholds
    sem_rows = [
        [Paragraph("<b>Academic Requirement</b>", styles['TableCellBold']), Paragraph("<b>Prescribed Period</b>", styles['TableCellBold']),
         Paragraph("<b>Governing Semester</b>", styles['TableCellBold']), Paragraph("<b>Prerequisite SGPA</b>", styles['TableCellBold']), Paragraph("<b>Eligibility Status</b>", styles['TableCellBold'])],
        [Paragraph("Mandatory Internship #1", styles['TableCellBold']), Paragraph("Summer Break after Sem 4 (2nd Year)", styles['TableCell']),
         Paragraph("Semester 3", styles['TableCell']), Paragraph(f"{elig_1.get('prerequisite_sgpa', 'N/A')} (Req: >= 6.00)", styles['TableCell']),
         Paragraph("ELIGIBLE" if elig_1.get('is_eligible') else "INELIGIBLE", styles['TagSuccess'] if elig_1.get('is_eligible') else styles['TagDanger'])],
        [Paragraph("Mandatory Internship #2", styles['TableCellBold']), Paragraph("During 8th Semester", styles['TableCell']),
         Paragraph("Semester 7", styles['TableCell']), Paragraph(f"{elig_2.get('prerequisite_sgpa', 'N/A')} (Req: >= 6.00)", styles['TableCell']),
         Paragraph("ELIGIBLE" if elig_2.get('is_eligible') else "INELIGIBLE", styles['TagSuccess'] if elig_2.get('is_eligible') else styles['TagDanger'])],
    ]
    t_sem = Table(sem_rows, colWidths=[120, 160, 85, 105, 70])
    t_sem.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sem)
    story.append(Spacer(1, 10))

    # Actual Internship Engagement Records
    story.append(Paragraph("Detailed Internship Engagement Records", styles['SecHead']))
    internships = student.get('Internships', [])
    m1 = next((i for i in internships if i.get('Internship_Type') == 'Mandatory' and i.get('Internship_No') == 1), None)
    m2 = next((i for i in internships if i.get('Internship_Type') == 'Mandatory' and i.get('Internship_No') == 2), None)
    additionals = [i for i in internships if i.get('Internship_Type') == 'Additional' or i.get('Internship_No', 0) >= 3]

    detail_rows = [
        [Paragraph("Milestone", styles['TableHead']), Paragraph("Organization & Role", styles['TableHead']),
         Paragraph("Dates & Duration", styles['TableHead']), Paragraph("Stipend", styles['TableHead']), Paragraph("Credits", styles['TableHead']), Paragraph("Grade", styles['TableHead']), Paragraph("Completion", styles['TableHead'])]
    ]

    def _fmt_row(label, item):
        if not item:
            return [Paragraph(label, styles['TableCellBold']), Paragraph("<i>No record found (Missing)</i>", styles['TagDanger']),
                    Paragraph("&mdash;", styles['TableCell']), Paragraph("&mdash;", styles['TableCell']), Paragraph("&mdash;", styles['TableCell']), Paragraph("&mdash;", styles['TableCell']),
                    Paragraph("MISSING", styles['TagDanger'])]
        return [
            Paragraph(label, styles['TableCellBold']),
            Paragraph(f"<b>{item['Company_Name']}</b><br/>{item['Role']}", styles['TableCell']),
            Paragraph(f"{item.get('Start_Date', '')} to {item.get('End_Date', '')}<br/>({item.get('Duration_Str', '8 weeks')})", styles['TableCell']),
            Paragraph(f"Rs. {item.get('Stipend', 0):,.0f}", styles['TableCell']),
            Paragraph(str(item.get('Credits', 4)), styles['TableCell']),
            Paragraph(item.get('Report_Grade') or 'N/A', styles['TableCellBold']),
            Paragraph(item.get('Status', 'Completed').upper(), styles['TagSuccess'] if item.get('Status') == 'Completed' else styles['TableCell'])
        ]

    detail_rows.append(_fmt_row("Mandatory #1 (Sem 3 Req)", m1))
    detail_rows.append(_fmt_row("Mandatory #2 (Sem 7 Req)", m2))
    for idx, add in enumerate(additionals, 1):
        detail_rows.append(_fmt_row(f"Additional #{idx}", add))

    t_detail = Table(detail_rows, colWidths=[95, 140, 115, 65, 40, 35, 50])
    t_detail.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#065f46')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_detail)
    story.append(Spacer(1, 12))

    # Overall Audit Decision
    both_completed = bool(m1 and m1.get('Status') == 'Completed' and m2 and m2.get('Status') == 'Completed')
    decision_text = "<b>COMPLIANT & APPROVED:</b> Candidate has successfully satisfied all mandatory degree internship requirements." if both_completed else "<b>NON-COMPLIANT / DEFICIENCY RECORDED:</b> Candidate has not completed all prescribed mandatory degree internships."
    decision_bg = colors.HexColor('#dcfce7') if both_completed else colors.HexColor('#fee2e2')
    decision_border = colors.HexColor('#16a34a') if both_completed else colors.HexColor('#dc2626')

    decision_p = Paragraph(decision_text, styles['TagSuccess'] if both_completed else styles['TagDanger'])
    t_decision = Table([[decision_p]], colWidths=[540])
    t_decision.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), decision_bg),
        ('BOX', (0,0), (-1,-1), 1, decision_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_decision)

    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()


# -----------------------------------------------------------------------------
# 3. Student Internship History PDF
# -----------------------------------------------------------------------------
def generate_student_internship_history_pdf(student_id: int) -> bytes:
    """Generates a complete chronological internship history transcript."""
    return generate_individual_compliance_pdf(student_id)


# -----------------------------------------------------------------------------
# 4. Missing Mandatory Audit PDF
# -----------------------------------------------------------------------------
def generate_missing_mandatory_audit_pdf(branch: Optional[str] = None, batch_year: Optional[int] = None) -> bytes:
    """Generates an institutional audit report of all students with unfulfilled mandatory internships."""
    defaulters = get_students_missing_mandatory_internships(branch=branch, batch_year=batch_year)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(letter), leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = _get_styles()
    story = []

    story.append(Paragraph("INSTITUTIONAL ACCREDITATION & DEGREE GOVERNANCE", styles['DocSub']))
    story.append(Paragraph("Missing Mandatory Internship Audit Report & Defaulter Roster", styles['DocTitle']))
    filter_str = f"Branch Filter: {branch or 'All Branches'} &bull; Graduation Batch: {batch_year or 'All Batches'}"
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')} &nbsp;|&nbsp; {filter_str} &nbsp;|&nbsp; Total Defaulters Detected: <b>{len(defaulters)}</b>", styles['DocSub']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#dc2626"), spaceBefore=0, spaceAfter=8))

    rows = [[
        Paragraph("Roll No", styles['TableHead']), Paragraph("Student Name", styles['TableHead']),
        Paragraph("Branch", styles['TableHead']), Paragraph("Batch", styles['TableHead']),
        Paragraph("CGPA", styles['TableHead']), Paragraph("Institutional Email", styles['TableHead']),
        Paragraph("Mandatory #1 (Sem 3)", styles['TableHead']), Paragraph("Mandatory #2 (8th Sem)", styles['TableHead']),
        Paragraph("Outreach Action", styles['TableHead'])
    ]]

    if defaulters:
        for d in defaulters:
            rows.append([
                Paragraph(f"<b>{d['Roll_No']}</b>", styles['TableCell']),
                Paragraph(d['Full_Name'], styles['TableCellBold']),
                Paragraph(d['Branch'], styles['TableCell']),
                Paragraph(str(d['Batch_Year']), styles['TableCell']),
                Paragraph(f"{d['CGPA']:.2f}", styles['TableCell']),
                Paragraph(d['Email'], styles['TableCell']),
                Paragraph(d['Mandatory_I1_Status'], styles['TagDanger'] if d['Mandatory_I1_Status'] == 'MISSING' else styles['TagSuccess']),
                Paragraph(d['Mandatory_I2_Status'], styles['TagDanger'] if d['Mandatory_I2_Status'] == 'MISSING' else styles['TagSuccess']),
                Paragraph("Immediate Notice", styles['TagDanger'])
            ])
    else:
        rows.append([Paragraph("<i>Zero non-compliant students found. All candidates have satisfied mandatory degree internships.</i>", styles['TagSuccess'])] + [Paragraph("", styles['TableCell'])]*8)

    t_audit = Table(rows, colWidths=[65, 115, 45, 45, 40, 150, 95, 95, 90])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#991b1b")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_audit)

    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()
