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
    Now supports 5 explicit age brackets and real-time storytelling personalization.
    """
    # Calculate age in months
    today = date.today()
    age_months = (today - child.date_of_birth).days // 30
    
    # Determine the explicit age-bracket tier
    if age_months < 6:
        tier = 'sensory'
    elif age_months <= 12:
        tier = 'grasping'
    elif age_months <= 36:
        tier = 'toddler'
    elif age_months <= 72:
        tier = 'preschool'
    else:
        tier = 'school'
        
    # Map tier to backward-compatible mapped_tier for legacy UI / background styles
    mapped_tier = 'infant'
    if tier in ['toddler', 'preschool']:
        mapped_tier = 'early'
    elif tier == 'school':
        mapped_tier = 'preteen'
        
    # Daily rotation: deterministic seeded random
    import random
    seed = int(today.strftime('%Y%m%d')) + child.id
    rng = random.Random(seed)
    
    # Retrieve medically-safe activities using the rules engine
    from health.logic.age_rules import get_medically_safe_activities
    activities = list(get_medically_safe_activities(child).order_by('id'))
    activity = None
    if activities:
        activity = rng.choice(activities)
        
    # Choose from all available bedtime stories to ensure daily variety
    stories = list(BedtimeStory.objects.all().order_by('id'))
    story = None
    if stories:
        if story_id:
            try:
                story_template = BedtimeStory.objects.get(id=story_id)
            except BedtimeStory.DoesNotExist:
                story_template = rng.choice(stories)
        else:
            story_template = rng.choice(stories)
            
        story_text = story_template.template_text
        story_lesson = story_template.moral_lesson
        locality_name = child.locality.name if child.locality else "our peaceful village"
        
        # Inject child's name and locality
        story_text = story_text.replace("[Name]", child.name).replace("[name]", child.name)
        story_text = story_text.replace("[Locality]", locality_name).replace("[locality]", locality_name)
        story_lesson = story_lesson.replace("[Name]", child.name).replace("[name]", child.name)
        story_lesson = story_lesson.replace("[Locality]", locality_name).replace("[locality]", locality_name)
        
        story = {
            'id': story_template.id,
            'title': story_template.title,
            'text': story_text,
            'lesson': story_lesson,
            'bg_class': get_story_background(mapped_tier, story_template.title)
        }
        
    return {
        'activity': activity,
        'story': story,
        'age_months': age_months,
        'tier': mapped_tier
    }
