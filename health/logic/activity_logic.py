from datetime import date
from ..models import OfflineActivity, BedtimeStory

def get_brain_development_context(child):
    """
    Service layer for fetching age-appropriate offline activities and personalized stories.
    """
    # Calculate age
    today = date.today()
    age_years = today.year - child.date_of_birth.year - ((today.month, today.day) < (child.date_of_birth.month, child.date_of_birth.day))
    
    # Determine tier
    if age_years < 2:
        tier = 'infant'
    elif age_years < 7:
        tier = 'early'
    elif age_years <= 11:
        tier = 'preteen'
    else:
        tier = 'preteen' # Cap at preteen
        
    # Daily rotation: deterministic seeded random
    import random
    seed = int(today.strftime('%Y%m%d')) + child.id
    rng = random.Random(seed)
    
    activities = list(OfflineActivity.objects.filter(age_tier=tier).order_by('id'))
    activity = None
    if activities:
        activity = rng.choice(activities)
        
    # Get locality-based story
    region = child.locality.region_tag if child.locality else 'NORTH_INDIA'
    stories = list(BedtimeStory.objects.filter(region_tag=region).order_by('id'))
    story = None
    if stories:
        story_template = rng.choice(stories)
        story = {
            'title': story_template.title,
            'text': story_template.template_text,
            'lesson': story_template.moral_lesson
        }
        
    return {
        'activity': activity,
        'story': story,
        'age_years': age_years,
        'tier': tier
    }
