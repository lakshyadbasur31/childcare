from health.models import PostpartumDiet, PostpartumCareGuide, Notification
from django.utils import timezone

def get_postpartum_context(mother):
    """
    Calculates the current phase and day of recovery for a mother.
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
        
    # Get recipe for the current day and region
    day_mod = ((days_since_delivery - 1) % 40) + 1
    region = mother.user.locality.region_tag if mother.user.locality else 'SOUTH_INDIA'
    recipe = PostpartumDiet.objects.filter(
        day_number__lte=day_mod, 
        region_tag=region
    ).order_by('-day_number').first()
    
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

    return {
        'day_number': days_since_delivery,
        'phase': phase,
        'recipe': recipe,
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
