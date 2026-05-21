from datetime import date
from health.models import OfflineActivity

def get_child_age_months(child):
    today = date.today()
    return (today - child.date_of_birth).days // 30

def is_infant_priority_mode(child):
    """
    Infant Priority Mode is active for babies under 6 months.
    During this period, primary medical items (vaccines, feeding, sleep, hydration) are prioritized in the UI.
    """
    return get_child_age_months(child) < 6

def get_medically_safe_activities(child):
    """
    Restricts activities for infants under 6 months to sensory, eye tracking, and bonding.
    Prevents physical/motor fallback activities that could be unsafe.
    """
    age_months = get_child_age_months(child)
    
    if age_months < 6:
        # Strictly query only 'sensory' tier activities
        qs = OfflineActivity.objects.filter(age_tier='sensory')
        if qs.exists():
            return qs
        
        # If database is completely unseeded, filter general 'infant' activities for sensory/bonding keywords only
        fallback_qs = OfflineActivity.objects.filter(age_tier='infant')
        safe_ids = []
        keywords = ['sensory', 'eye', 'track', 'bond', 'sing', 'cuddle', 'touch', 'sound', 'look', 'hear', 'voice', 'smile', 'gaze']
        for act in fallback_qs:
            desc_lower = act.description.lower() + act.title.lower()
            if any(kw in desc_lower for kw in keywords):
                safe_ids.append(act.id)
        return OfflineActivity.objects.filter(id__in=safe_ids)
    
    elif age_months <= 12:
        return OfflineActivity.objects.filter(age_tier='grasping')
    elif age_months <= 36:
        return OfflineActivity.objects.filter(age_tier='toddler')
    elif age_months <= 72:
        return OfflineActivity.objects.filter(age_tier='preschool')
    else:
        return OfflineActivity.objects.filter(age_tier='school')
