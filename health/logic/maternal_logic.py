from health.models import PostpartumDiet, PostpartumCareGuide, Notification
from django.utils import timezone

class DummyRecipe:
    def __init__(self, data):
        self.breakfast_name = data.get('breakfast_name', '')
        self.breakfast_details = data.get('breakfast_details', '')
        self.lunch_name = data.get('lunch_name', '')
        self.lunch_details = data.get('lunch_details', '')
        self.snack_name = data.get('snack_name', '')
        self.snack_details = data.get('snack_details', '')
        self.dinner_name = data.get('dinner_name', '')
        self.dinner_details = data.get('dinner_details', '')
        self.ingredients = data.get('ingredients', '')
        self.benefits = data.get('benefits', '')

def get_postpartum_context(mother):
    """
    Calculates the current phase and day of recovery for a mother.
    Integrated with a 7-day rotating regional matrix.
    """
    days_since_delivery = (timezone.now().date() - mother.delivery_date).days + 1
    
    # Phase logic: 1-10 (Healing), 11-30 (Lactation), 31-40 (Strength)
    if days_since_delivery <= 10:
        phase = 1
    elif days_since_delivery <= 30:
        phase = 2
    elif days_since_delivery <= 40:
        phase = 3
    else:
        phase = 3 # Maintenance
        
    # Generate the dynamic 7-day rotating regional menu
    from .recommender import generate_maternal_7_day_plan
    plan = generate_maternal_7_day_plan(mother, phase)
    
    # Get today's and tomorrow's day names
    today_name = timezone.now().strftime('%A')
    import datetime
    tomorrow_name = (timezone.now() + datetime.timedelta(days=1)).strftime('%A')
    
    today_data = plan.get(today_name)
    tomorrow_data = plan.get(tomorrow_name)
    
    recipe = DummyRecipe(today_data)
    alternate_recipe = DummyRecipe(tomorrow_data)
        
    # Get current week for the roadmap
    current_week = (days_since_delivery // 7) + 1
    guide = PostpartumCareGuide.objects.filter(
        week_number__lte=current_week
    ).order_by('-week_number').first()

    # Daily Mental Health rotation (40-day cycle)
    AFFIRMATIONS = [
        "I am exactly what my baby needs. Just being here is enough.",
        "My body is a miracle; it created life and is now healing beautifully.",
        "It's okay to feel overwhelmed. I am learning a new language: my baby's.",
        "I deserve rest. Taking a break makes me a better parent.",
        "My worth is not measured by my productivity today.",
        "I am resilient. Each day I grow more confident in my role.",
        "I am surrounded by love and support. I will reach out when needed.",
        "Small steps are still progress. Today I succeeded in caring for us.",
        "My bond with my baby is unique and grows stronger with every touch.",
        "I am healing at my own pace, and that is perfectly okay."
    ]
    TIPS = [
        "The 5-5-5 Rule: Name 5 things you see, 5 you hear, and 5 you feel.",
        "Hydration check: Drink a glass of water every time you breastfeed.",
        "Step outside for 2 minutes. Fresh air helps reset your nervous system.",
        "Practice deep belly breathing for 60 seconds while holding your baby.",
        "Dim the lights 30 minutes before your planned 'rest window'.",
        "Gentle neck rolls can release tension from holding the baby all day.",
        "Listen to one song that makes you feel like 'yourself' today.",
        "Lower your expectations for the house. Focus only on healing.",
        "Ask a partner or friend to hold the baby while you take a warm shower.",
        "Journal one positive thing that happened today, no matter how small."
    ]

    def apply_allergy_warning(diet):
        if not diet or not hasattr(mother, 'allergies') or not mother.allergies:
            return diet
        allergies = [a.strip().lower() for a in mother.allergies.split(',') if a.strip()]
        if not allergies: return diet
        
        substitutes = {
            'dairy': 'Almond Milk',
            'milk': 'Almond Milk',
            'peanut': 'Almonds',
            'peanuts': 'Almonds',
            'gluten': 'Quinoa',
            'wheat': 'Millet',
            'egg': 'Tofu',
            'eggs': 'Tofu',
            'nut': 'Roasted Seeds',
            'nuts': 'Roasted Seeds',
            'soy': 'Lentils',
            'seafood': 'Beans',
            'fish': 'Beans'
        }
        
        subs_messages = []
        import re
        for a in allergies:
            if a in substitutes:
                sub_text = substitutes[a]
                subs_messages.append(f"{a.title()} with {sub_text}")
                
                # Dynamically replace occurrences in the text
                pattern = re.compile(re.escape(a), re.IGNORECASE)
                diet.breakfast_details = pattern.sub(sub_text, diet.breakfast_details)
                diet.lunch_details = pattern.sub(sub_text, diet.lunch_details)
                diet.snack_details = pattern.sub(sub_text, diet.snack_details)
                diet.dinner_details = pattern.sub(sub_text, diet.dinner_details)
                
                diet.breakfast_name = pattern.sub(sub_text, diet.breakfast_name)
                diet.lunch_name = pattern.sub(sub_text, diet.lunch_name)
                diet.snack_name = pattern.sub(sub_text, diet.snack_name)
                diet.dinner_name = pattern.sub(sub_text, diet.dinner_name)
            else:
                subs_messages.append(f"{a.title()} with a safe alternative")
                
        warning = f" ⚠️ [Allergy Alert: Substituted {'; '.join(subs_messages)}]"
        
        # Attach warning to text fields in-memory if allergens might be present
        diet.breakfast_details += warning
        diet.lunch_details += warning
        diet.snack_details += warning
        diet.dinner_details += warning
        return diet

    return {
        'day_number': days_since_delivery,
        'phase': phase,
        'recipe': apply_allergy_warning(recipe),
        'alternate_recipe': apply_allergy_warning(alternate_recipe),
        'guide': guide,
        'week_number': current_week,
        'daily_affirmation': AFFIRMATIONS[(days_since_delivery - 1) % len(AFFIRMATIONS)],
        'daily_tip': TIPS[(days_since_delivery - 1) % len(TIPS)]
    }

def check_maternal_red_flags(metric):
    """
    Urgent Alert System: Checks for dangerous postpartum symptoms.
    """
    mother = metric.mother
    urgent_symptoms = ['fever', 'heavy_bleeding', 'severe_headache', 'vision_blurring']
    
    triggered = []
    for s in metric.symptoms:
        if s in urgent_symptoms:
            triggered.append(s.replace('_', ' ').title())
            
    # Check BP (Preeclampsia risk)
    if metric.systolic_bp and metric.systolic_bp >= 140:
        triggered.append("High Blood Pressure")
        
    if triggered:
        Notification.objects.create(
            user=mother.user,
            title="URGENT: Postpartum Red Flag Detected",
            message=f"Alert: {', '.join(triggered)} detected. Please visit the nearest District Hospital immediately. Links: [Hospital Guide]",
            is_urgent=True
        )
        return True
    return False

def get_chronological_phase(postpartum_day):
    """
    Blueprint: Chronologically segment logged vitals into programmatic phases.
    """
    if postpartum_day is None:
        return "Unknown Phase"
    if postpartum_day <= 3:
        return "Critical Recovery"
    elif postpartum_day <= 10:
        return "Early Healing"
    elif postpartum_day <= 21:
        return "Active Recovery"
    elif postpartum_day <= 40:
        return "Full Restoration"
    else:
        return "Maintenance"

def evaluate_maternal_triage(metric):
    """
    Blueprint Required: Rule-based triage flags without overwriting old logic.
    """
    flags = []
    symptoms = [s.lower() for s in metric.symptoms] if metric.symptoms else []
    
    systolic_high = metric.systolic_bp and metric.systolic_bp > 140
    severe_headache = any('headache' in s or 'severe_headache' in s for s in symptoms)
    visual_changes = any('vision' in s or 'vision_blurring' in s for s in symptoms)
    bleeding = any('bleeding' in s or 'heavy_bleeding' in s for s in symptoms)
    fever = any('fever' in s for s in symptoms) 
    
    epds = metric.mother.epds_score if hasattr(metric.mother, 'epds_score') else 0
    epds_high = epds and epds >= 13
    
    if systolic_high and severe_headache and visual_changes:
        flags.append("CRITICAL: Preeclampsia symptom cluster detected")
    elif systolic_high or bleeding:
        flags.append("HIGH: High Blood Pressure or Excessive Bleeding")
        
    if fever or epds_high:
        flags.append("MEDIUM: Persistent fever or High EPDS score")
        
    return flags
