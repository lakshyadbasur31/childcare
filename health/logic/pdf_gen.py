import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Flowable
from django.conf import settings

class MilestonePath(Flowable):
    """
    Enhanced Vector Flowable for Bharat-Health Guardian Roadmap.
    """
    def __init__(self, width, height, status='pending', title="", consequence=""):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.status = status
        self.title = title
        self.consequence = consequence

    def draw(self):
        c = self.canv
        # Draw dashed line
        c.setDash(2, 2)
        c.setStrokeColor(colors.HexColor("#cbd5e1"))
        c.setLineWidth(1)
        c.line(20, 0, 20, self.height)
        
        c.setDash() 
        
        # Color Logic
        if self.status == 'completed':
            fill_color = colors.HexColor("#10b981")
            stroke_color = colors.HexColor("#047857")
        elif self.status == 'overdue':
            fill_color = colors.HexColor("#ef4444")
            stroke_color = colors.HexColor("#991b1b")
        else:
            fill_color = colors.white
            stroke_color = colors.HexColor("#f59e0b")
            
        c.setFillColor(fill_color)
        c.setStrokeColor(stroke_color)
        c.circle(20, self.height - 15, 8, fill=1, stroke=1)
        
        # Title
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, self.height - 18, self.title)
        
        # Consequence (if not completed)
        if self.status != 'completed':
            c.setFillColor(colors.HexColor("#991b1b"))
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(40, self.height - 30, f"Risk if missed: {self.consequence[:80]}...")

def generate_health_passport(child, vaccination_schedule, nutrition_recommendation, maternal_context=None):
    file_path = os.path.join(settings.BASE_DIR, f"health_passport_{child.id}.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    # Custom Styles
    title_style = ParagraphStyle('MainTitle', parent=styles['Title'], fontSize=22, textColor=colors.HexColor("#1e293b"), spaceAfter=20)
    subtitle_style = ParagraphStyle('SubTitle', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor("#4f46e5"), spaceAfter=12)
    body_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontSize=11, leading=16)

    # PAGE 1: HERO STORYBOOK
    elements.append(Paragraph(f"BHARAT-HEALTH GUARDIAN: {child.name.upper()}", title_style))
    elements.append(Spacer(1, 12))
    
    district = child.locality.district if child.locality else "Your Region"
    state = child.locality.state if child.locality else "India"
    
    story_text = f"""
    Greetings to the family of <b>{child.name}</b> in {district}, {state}. <br/><br/>
    Your child is on a journey to become a 'Bharat Guardian'. This passport tracks their growth, 
    immunity, and nutritional milestones tailored specifically for the <b>{child.locality.get_region_tag_display() if child.locality else 'North India'}</b> region.
    """
    elements.append(Paragraph(story_text, body_style))
    elements.append(Spacer(1, 24))
    
    # Normalized Stats Table
    display_weight = child.current_weight * 1000 if child.weight_unit == 'g' else child.current_weight
    display_height = child.current_height / 100 if child.height_unit == 'm' else child.current_height
    
    stats_data = [
        ["Stat Category", "Value", "Unit", "Mentor Status"],
        ["Weight", f"{display_weight:.1f}", child.weight_unit, "Strong"],
        ["Height", f"{display_height:.1f}", child.height_unit, "Growing Fast"],
        ["Region", district, "Locality", child.locality.get_region_tag_display() if child.locality else "North"]
    ]
    
    stats_table = Table(stats_data, colWidths=[120, 100, 80, 150])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(stats_table)

    # MATERNAL HEALTH SECTION (If provided)
    if maternal_context:
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("MOTHER'S RECOVERY SUMMARY", subtitle_style))
        m_rec = maternal_context
        m_text = f"""
        <b>Recovery Day:</b> {m_rec['day_number']}/40 &bull; <b>Phase:</b> {m_rec['phase']} <br/>
        <b>Today's Healing Recipe:</b> {m_rec['recipe'].breakfast_name if m_rec['recipe'] else 'Standard Recovery Meal'} <br/>
        <b>Ingredients:</b> {m_rec['recipe'].ingredients if m_rec['recipe'] else 'Regional Staples'} <br/>
        <b>Benefits:</b> {m_rec['recipe'].benefits if m_rec['recipe'] else 'Tissue repair and lactation support'}
        """
        elements.append(Paragraph(m_text, body_style))

    elements.append(PageBreak())

    # PAGE 2: HIGH-STAKES IMMUNIZATION
    elements.append(Paragraph("HIGH-STAKES IMMUNIZATION ROADMAP", title_style))
    elements.append(Spacer(1, 24))
    for vax in vaccination_schedule:
        title = f"{vax.vaccine.name} ({vax.status.upper()})"
        consequence = vax.vaccine.consequence_text if vax.vaccine.consequence_text else "Risk of preventable illness."
        elements.append(MilestonePath(450, 45, vax.status, title, consequence))
        elements.append(Spacer(1, 5))

    elements.append(PageBreak())

    # PAGE 3: REGIONAL MARKET GUIDE
    elements.append(Paragraph(f"LOCAL MARKET GUIDE: {district.upper()}", title_style))
    elements.append(Spacer(1, 24))
    food_data = [["Check", "Ingredient", "Why It Matters", "Nutrition Power"]]
    for food in nutrition_recommendation.recommended_foods.all():
        food_data.append(["[  ]", food.name, food.nutritional_description[:60], f"{food.protein_content}g Prot"])
    
    food_table = Table(food_data, colWidths=[50, 120, 240, 100])
    food_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#059669")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(food_table)

    # PAGE 4: THE HERO'S MEMORY PAGE
    elements.append(PageBreak())
    elements.append(Paragraph("THE HERO'S MEMORY PAGE", title_style))
    elements.append(Paragraph("A record of real-world play and brain development milestones.", body_style))
    elements.append(Spacer(1, 24))
    
    memory_data = [["Activity", "Date Completed", "Parent's Note / Memory"]]
    completions = child.completions.all().order_by('-completed_at')[:10]
    for comp in completions:
        memory_data.append([comp.activity.title, comp.completed_at.strftime('%d %b %Y'), comp.parent_note or "Completed together!"])
    
    # Add empty rows for future activities
    for _ in range(max(0, 5 - completions.count())):
        memory_data.append(["[  ]", "", ""])

    memory_table = Table(memory_data, colWidths=[150, 100, 260])
    memory_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(memory_table)

    doc.build(elements)
    return file_path
