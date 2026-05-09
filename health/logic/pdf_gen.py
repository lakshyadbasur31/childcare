import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Flowable
from django.conf import settings

class MilestonePath(Flowable):
    """
    Custom Vector Flowable for ReportLab to draw the vertical dashed quest line.
    """
    def __init__(self, width, height, is_completed=False, title=""):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.is_completed = is_completed
        self.title = title

    def draw(self):
        c = self.canv
        # Draw dashed line
        c.setDash(4, 4)
        c.setStrokeColor(colors.HexColor("#e2e8f0"))
        c.setLineWidth(2)
        c.line(20, 0, 20, self.height)
        
        c.setDash() # reset dash
        
        # Draw Node
        if self.is_completed:
            c.setFillColor(colors.HexColor("#10b981"))
            c.setStrokeColor(colors.HexColor("#047857"))
        else:
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.HexColor("#f59e0b"))
            
        c.circle(20, self.height/2, 10, fill=1, stroke=1)
        
        # Draw Text
        c.setFillColor(colors.darkslategray)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, self.height/2 - 3, self.title)

def generate_storybook_page(elements, child, recommendation, styles):
    """
    Guardian Angel Feature: Generates a superhero-themed storybook page for the child.
    """
    # Dynamic Title based on stats
    title_prefix = "The Mighty Giant" if child.current_weight > 10 else "The Wise Explorer"
    elements.append(Paragraph(f"THE ADVENTURES OF {title_prefix.upper()}: {child.name.upper()}", styles['Title']))
    elements.append(Spacer(1, 24))
    
    superfood = recommendation.recommended_foods.first()
    superfood_name = superfood.name if superfood else "Magic Potion"
    
    story_text = f"""
    Once upon a time in the beautiful village of {child.locality.name}, a young hero named <b>{child.name}</b> set out 
    to become the strongest in the land. <br/><br/>
    
    To gain the 'Iron Will', Hero {child.name} must consume the sacred <b>{superfood_name}</b> found in the local market. 
    Completing this quest will unlock the next level of strength and agility!
    """
    
    story_style = ParagraphStyle('StoryStyle', parent=styles['Normal'], fontSize=12, leading=18, alignment=1, textColor=colors.HexColor("#4f46e5"))
    elements.append(Paragraph(story_text, story_style))
    elements.append(Spacer(1, 36))
    
    # RPG Stats
    elements.append(Paragraph("HERO STATS", styles['Heading2']))
    progress_data = [["Strength (Weight)", "Agility (Height)", "Wisdom", "Overall Rank"]]
    progress_data.append([f"{child.current_weight}kg", f"{child.current_height}cm", "Level 2", "Hero in Training"])
    
    progress_table = Table(progress_data, colWidths=[120, 120, 100, 120])
    progress_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e0e7ff")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(progress_table)

def generate_health_passport(child, vaccination_schedule, nutrition_recommendation):
    file_path = os.path.join(settings.BASE_DIR, f"health_passport_{child.id}.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    # PAGE 1: STORYBOOK
    generate_storybook_page(elements, child, nutrition_recommendation, styles)
    elements.append(PageBreak())

    # PAGE 2: VACCINATION ROADMAP (Vector Flowables)
    elements.append(Paragraph("IMMUNIZATION ROADMAP", styles['Title']))
    elements.append(Spacer(1, 24))
    
    for vax in vaccination_schedule:
        is_completed = vax.status == 'completed'
        status_text = "Shield Unlocked!" if is_completed else "Mystery Chest (Pending)"
        elements.append(MilestonePath(400, 40, is_completed, f"{vax.vaccine.name} - {status_text}"))
        elements.append(Spacer(1, 10))

    elements.append(PageBreak())

    # PAGE 3: SHOPPING LIST (Grid Layout with Checkboxes)
    elements.append(Paragraph("SMART MARKET CHECKLIST", styles['Title']))
    elements.append(Spacer(1, 24))
    
    food_data = [["[ ] / [x]", "Ingredient", "Local Source", "Power Gained"]]
    for food in nutrition_recommendation.recommended_foods.all():
        food_data.append(["[  ]", food.name, child.locality.name, food.nutritional_description])
    
    food_table = Table(food_data, colWidths=[60, 150, 120, 180])
    food_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f59e0b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(food_table)

    doc.build(elements)
    return file_path
