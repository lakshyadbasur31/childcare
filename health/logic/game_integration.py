import requests
from django.conf import settings

def validate_game_link(url):
    """
    Check if the URL is reachable. 
    If this fails, we'll still provide the link but with a warning.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # Use a longer timeout and verify=False to be more permissive
        response = requests.get(url, timeout=5, headers=headers, stream=True, verify=False)
        return response.status_code == 200
    except:
        return False

def get_pbs_kids_games(age_years, day_index):
    """
    Returns rotating educational games from a pool based on the day.
    """
    pool = []
    if age_years < 3:
        pool = [
            {"name": "Curious George: Monkey Face", "url": "https://pbskids.org/curiousgeorge/games/monkey-face/", "description": "Logic for toddlers."},
            {"name": "Elinor Wonders Why: Sorting", "url": "https://pbskids.org/elinor/games/elinor-wonders-why-sorting", "description": "Scientific sorting."},
            {"name": "Peg + Cat: Chicken Dance", "url": "https://pbskids.org/peg/games/chicken-dance/", "description": "Basic patterns."},
            {"name": "Sesame Street: Cookie Games", "url": "https://pbskids.org/sesame/games/cookie-monster-foodie-truck/", "description": "Healthy habits."}
        ]
    elif age_years <= 6:
        pool = [
            {"name": "Wild Kratts: Creature Power", "url": "https://pbskids.org/wildkratts/games/creature-power-suit/", "description": "Biology logic."},
            {"name": "Peg + Cat: Mega Mall", "url": "https://pbskids.org/peg/games/mega-mall/", "description": "Math logic."},
            {"name": "Arthur: Park Your Car", "url": "https://pbskids.org/arthur/games/park-your-car/", "description": "Spatial logic."},
            {"name": "Cyberchase: Railway", "url": "https://pbskids.org/cyberchase/games/railway-hero/", "description": "Advanced problem solving."}
        ]
    else:
        pool = [{"name": "PBS Kids Central", "url": "https://pbskids.org/games/", "description": "Educational portal."}]

    # Rotate by day: Pick 2 different games each day
    idx1 = day_index % len(pool)
    idx2 = (day_index + 1) % len(pool)
    
    selected = [pool[idx1]]
    if len(pool) > 1:
        selected.append(pool[idx2])
    return selected

def get_fallback_activity(child, day_index):
    """
    Rotating offline activities based on the day.
    """
    activities = [
        {"name": "Local Clay Modeling", "description": "Create shapes of local fruits."},
        {"name": "Seed Sorting", "description": "Sort different types of local seeds/grains by size."},
        {"name": "Nature Color Match", "description": "Find 5 things in nature that match specific colors."},
        {"name": "Storytelling", "description": "Tell a story about local folklore or animals."},
        {"name": "Rhythm Play", "description": "Use local utensils to create rhythmic patterns."},
        {"name": "Leaf Tracing", "description": "Trace shapes of different local leaves."},
        {"name": "Water Play", "description": "Explore floating and sinking with local objects."}
    ]
    activity = activities[day_index % len(activities)]
    activity['type'] = 'Daily Offline Activity'
    return activity

def get_validated_games(child):
    """
    Main logic for daily rotating games and activities.
    """
    from datetime import datetime
    day_index = datetime.now().weekday() # 0-6 (Mon-Sun)
    
    age_years = (datetime.now().date() - child.date_of_birth).days // 365
    games = get_pbs_kids_games(age_years, day_index)
    
    result = []
    for game in games:
        is_active = validate_game_link(game['url'])
        game['status'] = 'Online' if is_active else 'Connection Flaky'
        game['is_active'] = is_active
        result.append(game)
    
    # Add daily rotating offline fallback
    result.append(get_fallback_activity(child, day_index))
            
    return result
