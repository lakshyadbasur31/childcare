from datetime import date
from ..models import OfflineActivity, BedtimeStory

def get_story_background(tier, story_title):
    t = story_title.lower()
    if 'mongoose' in t:
        story_theme = 'forest'
    elif 'crow' in t:
        story_theme = 'water'
    elif 'lion' in t or 'rabbit' in t:
        story_theme = 'jungle'
    else:
        story_theme = 'cosmic'

    if tier == 'infant':
        if story_theme == 'forest':
            return 'bg-gradient-to-br from-slate-900 via-emerald-950/40 to-teal-900/40'
        elif story_theme == 'water':
            return 'bg-gradient-to-br from-slate-900 via-sky-950/40 to-indigo-900/40'
        elif story_theme == 'jungle':
            return 'bg-gradient-to-br from-slate-900 via-amber-950/40 to-orange-900/40'
        else:
            return 'bg-gradient-to-br from-slate-900 via-purple-950/40 to-pink-900/40'
    elif tier == 'early':
        if story_theme == 'forest':
            return 'bg-gradient-to-br from-[#032f30] via-[#064e3b] to-[#022c22]'
        elif story_theme == 'water':
            return 'bg-gradient-to-br from-[#0f172a] via-[#1e3a8a] to-[#1e1b4b]'
        elif story_theme == 'jungle':
            return 'bg-gradient-to-br from-[#1c1917] via-[#78350f] to-[#451a03]'
        else:
            return 'bg-gradient-to-br from-[#1e1b4b] via-[#311042] to-[#111827]'
    else:
        if story_theme == 'forest':
            return 'bg-gradient-to-br from-[#042f1a] via-[#115e59] to-[#022c22]'
        elif story_theme == 'water':
            return 'bg-gradient-to-br from-[#0c4a6e] via-[#1e1b4b] to-[#0f172a]'
        elif story_theme == 'jungle':
            return 'bg-gradient-to-br from-[#78350f] via-[#1e1b4b] to-[#451a03]'
        else:
            return 'bg-gradient-to-br from-[#0b0f19] via-[#1e1b4b] to-[#311042]'

def get_brain_development_context(child, story_id=None):
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
        if story_id:
            try:
                story_template = BedtimeStory.objects.get(id=story_id)
            except BedtimeStory.DoesNotExist:
                story_template = rng.choice(stories)
        else:
            story_template = rng.choice(stories)
            
        story = {
            'id': story_template.id,
            'title': story_template.title,
            'text': story_template.template_text,
            'lesson': story_template.moral_lesson,
            'bg_class': get_story_background(tier, story_template.title)
        }
        
    return {
        'activity': activity,
        'story': story,
        'age_years': age_years,
        'tier': tier
    }
