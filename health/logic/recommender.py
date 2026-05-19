from health.models import LocalFoodResource, NutritionRecommendation
import random
import datetime

def get_age_guidelines(age_months):
    """
    Age-adaptive logic for Bharat-Health Guardian (0-11 years).
    """
    if age_months < 6:
        return {"protein": 0, "energy": 0, "desc": "Foundations (Exclusive Breastfeeding)", "texture": "liquid"}
    elif age_months <= 12:
        return {"protein": 11, "energy": 700, "desc": "Weaning (Complementary Feeding)", "texture": "puree"}
    elif age_months <= 36:
        return {"protein": 13, "energy": 1000, "desc": "Toddler Nutrition", "texture": "soft_solid"}
    elif age_months <= 72:
        return {"protein": 19, "energy": 1400, "desc": "Pre-School Nutrition", "texture": "solid"}
    else:
        return {"protein": 30, "energy": 1800, "desc": "Growth & School Support", "texture": "solid"}

def apply_allergy_substitution(text, allergens):
    """
    Dynamically substitutes allergen ingredients with safe regional alternatives.
    """
    if not text or not allergens:
        return text
    
    substitutes = {
        'dairy': 'Almond Milk',
        'milk': 'Almond Milk',
        'paneer': 'Tofu',
        'ghee': 'Sesame Oil',
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
    
    import re
    for a in allergens:
        a_clean = a.strip().lower()
        if a_clean in substitutes:
            sub_text = substitutes[a_clean]
            pattern = re.compile(re.escape(a_clean), re.IGNORECASE)
            text = pattern.sub(sub_text, text)
            
            # Singular/plural forms
            if a_clean.endswith('s'):
                pattern_sing = re.compile(re.escape(a_clean[:-1]), re.IGNORECASE)
                text = pattern_sing.sub(sub_text, text)
            else:
                pattern_plur = re.compile(re.escape(a_clean + 's'), re.IGNORECASE)
                text = pattern_plur.sub(sub_text, text)
    return text

def generate_7_day_plan(child, available_foods, guidelines):
    """
    Generates a 7-day meal plan containing 7 completely distinct daily recommendations.
    Highlights low-cost regional staples and Anaemia interventions (Spinach, Jaggery, Ragi).
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plan = {}
    
    age_months = (datetime.date.today() - child.date_of_birth).days // 30
    
    # Retrieve Mother's allergies to perform active substitution
    allergens = []
    try:
        mother_profile = child.parent.mother_profile
        if mother_profile.allergies:
            allergens = [a.strip().lower() for a in mother_profile.allergies.split(',') if a.strip()]
    except Exception:
        pass
        
    # --- CHILD Milestone 7-Day Matrix ---
    
    # Weaning/Puree Bracket (6-12 Months)
    puree_matrix = {
        "Monday": {
            "breakfast": "Apple ragi porridge with warm water", "breakfast_alt": "Sujii dalia porridge",
            "lunch": "Mashed red rice & yellow moong dal water", "lunch_alt": "Soft boiled rice water",
            "dinner": "Pureed spinach & pumpkin mash", "dinner_alt": "Steamed carrot mash"
        },
        "Tuesday": {
            "breakfast": "Warm bajra porridge with jaggery syrup", "breakfast_alt": "Warm oats porridge",
            "lunch": "Mashed yellow moong dal & potato mash", "lunch_alt": "Soft boiled lentil broth",
            "dinner": "Steamed sweet potato & carrot puree", "dinner_alt": "Soft pumpkin puree"
        },
        "Wednesday": {
            "breakfast": "Finger millet (ragi) malt porridge", "breakfast_alt": "Warm suji kheer with jaggery",
            "lunch": "Pureed green dal & rice mash", "lunch_alt": "Soft boiled rice with dal water",
            "dinner": "Stewed apple and pear mash", "dinner_alt": "Steamed green pea mash"
        },
        "Thursday": {
            "breakfast": "Mashed ripe banana with ragi flour", "breakfast_alt": "Mashed papaya porridge",
            "lunch": "Soft boiled yellow dal khichdi mash", "lunch_alt": "Mashed rice with ghee water",
            "dinner": "Pumpkin & sweet potato puree", "dinner_alt": "Carrot & spinach mash"
        },
        "Friday": {
            "breakfast": "Oats porridge sweetened with jaggery", "breakfast_alt": "Wheat dalia porridge",
            "lunch": "Moong dal water with mashed spinach and rice", "lunch_alt": "Pureed lentil stew",
            "dinner": "Steamed pear & apple puree", "dinner_alt": "Pureed pumpkin mash"
        },
        "Saturday": {
            "breakfast": "Ragi porridge with soft banana mash", "breakfast_alt": "Warm bajra porridge",
            "lunch": "Mashed potato & split pea broth", "lunch_alt": "Soft rice with yellow dal water",
            "dinner": "Pureed bottle gourd (lauki) & carrot mash", "dinner_alt": "Steamed sweet potato mash"
        },
        "Sunday": {
            "breakfast": "Wheat dalia porridge with jaggery", "breakfast_alt": "Ragi malt with warm water",
            "lunch": "Yellow dal khichdi mashed smoothly", "lunch_alt": "Soft mashed rice with green dal broth",
            "dinner": "Carrot & beetroot smooth mash", "dinner_alt": "Steamed pumpkin puree"
        }
    }
    
    # Toddler Bracket (1-3 Years)
    soft_solid_matrix = {
        "Monday": {
            "breakfast": "Soft ragi upma with crushed peanuts", "breakfast_alt": "Wheat dalia porridge",
            "lunch": "Soft moong dal khichdi with spinach & ghee", "lunch_alt": "Mashed paneer with rice",
            "dinner": "Soft wheat roti mashed in warm dal", "dinner_alt": "Mashed vegetable soup with soft rice"
        },
        "Tuesday": {
            "breakfast": "Soft millet pongal with carrots", "breakfast_alt": "Sooji upma with peas",
            "lunch": "Yellow split lentil stew with soft red rice", "lunch_alt": "Mashed moong dal & soft khichdi",
            "dinner": "Soft mashed vegetable khichdi with fresh curd", "dinner_alt": "Soft dalia with ghee"
        },
        "Wednesday": {
            "breakfast": "Sooji kheer sweetened with dark jaggery", "breakfast_alt": "Oats porridge with banana",
            "lunch": "Mashed paneer with soft boiled rice & dal", "lunch_alt": "Soft idli mashed in warm sambar",
            "dinner": "Soft wheat dalia with boiled pumpkin", "dinner_alt": "Soft curd rice with carrot mash"
        },
        "Thursday": {
            "breakfast": "Oats porridge with ripe banana slices", "breakfast_alt": "Ragi upma with ghee",
            "lunch": "Soft red rice with spinach soup & boiled dal", "lunch_alt": "Moong dal khichdi with peas",
            "dinner": "Soft paneer bhurji with warm milk", "dinner_alt": "Mashed potato & carrot with soft roti"
        },
        "Friday": {
            "breakfast": "Soft ragi idli with ghee brush", "breakfast_alt": "Sooji kheer with jaggery",
            "lunch": "Moong dal khichdi with soft diced carrots", "lunch_alt": "Lentil soup with soft red rice",
            "dinner": "Soft dalia with yellow pumpkin & ghee", "dinner_alt": "Mashed paneer with warm milk"
        },
        "Saturday": {
            "breakfast": "Warm bajra upma with soft cooked beans", "breakfast_alt": "Oats upma with carrots",
            "lunch": "Soft rice with tomato rasam & boiled moong dal", "lunch_alt": "Red rice with yellow dal",
            "dinner": "Mashed paneer & soft wheat chapati", "dinner_alt": "Soft curd rice with ginger touch"
        },
        "Sunday": {
            "breakfast": "Semolina (sooji) upma with carrots & peas", "breakfast_alt": "Wheat halwa with jaggery",
            "lunch": "Red rice with steamed spinach & curd", "lunch_alt": "Soft moong dal khichdi",
            "dinner": "Soft wheat halwa with warm jaggery water", "dinner_alt": "Soft roti in yellow lentil curry"
        }
    }
    
    # Preschool / School Bracket (3-6 & 6-11 Years)
    solid_matrix = {
        "Monday": {
            "breakfast": "Stuffed palak paratha with fresh curd", "breakfast_alt": "Wheat dosa with coconut chutney",
            "lunch": "Regional red rice with dal curry & cooked spinach", "lunch_alt": "Vegetable pulao with paneer cubes",
            "dinner": "Wheat chapati with saag & fresh curd", "dinner_alt": "Boiled chana with soft roti"
        },
        "Tuesday": {
            "breakfast": "Fluffy ragi idli with mixed vegetable sambar", "breakfast_alt": "Moong dal chilla",
            "lunch": "Bajra khichdi with regional winter greens", "lunch_alt": "Dal tadka with boiled rice",
            "dinner": "Wheat chapati with boiled chana & spinach saag", "dinner_alt": "Vegetable khichdi with ghee"
        },
        "Wednesday": {
            "breakfast": "Besan chilla with ginger and coriander", "breakfast_alt": "Ragi dosa with curd",
            "lunch": "Soya chunk curry with regional red rice", "lunch_alt": "Paneer curry with soft rice",
            "dinner": "Soft paneer curry with wheat roti", "dinner_alt": "Mixed veg sabzi with paratha"
        },
        "Thursday": {
            "breakfast": "Oats upma with green peas & carrots", "breakfast_alt": "Wheat dalia upma",
            "lunch": "Red rice pulav with roasted paneer chunks", "lunch_alt": "Sambar rice with roasted papad",
            "dinner": "Wheat roti with palak dal & lemon squeeze", "dinner_alt": "Paneer bhurji with soft chapati"
        },
        "Friday": {
            "breakfast": "Vegetable poha with roasted peanuts & curry leaves", "breakfast_alt": "Ragi porridge with jaggery",
            "lunch": "Moong dal tadka with hot wheat chapati", "lunch_alt": "Red rice with yellow split dal",
            "dinner": "Steamed banana with jaggery & wheat roti", "dinner_alt": "Palak paneer with soft paratha"
        },
        "Saturday": {
            "breakfast": "Stuffed paneer paratha with mild pickle", "breakfast_alt": "Besan chilla",
            "lunch": "Lentil dal makhani with steamed white rice", "lunch_alt": "Vegetable khichdi with ghee",
            "dinner": "Chapati with boiled egg curry / paneer curry for veg", "dinner_alt": "Soya curry with rice"
        },
        "Sunday": {
            "breakfast": "Millets dosa with tomato sambar", "breakfast_alt": "Wheat paratha with curd",
            "lunch": "Vegetable pulao with roasted paneer & curd", "lunch_alt": "Dal tadka with red rice",
            "dinner": "Wheat roti with saag, jaggery & curd", "dinner_alt": "Ragi roti with boiled dal"
        }
    }
    
    texture = guidelines['texture']
    
    for day in days:
        if texture == "puree":
            day_meals = puree_matrix[day]
            breakfast = day_meals["breakfast"]
            breakfast_alt = day_meals["breakfast_alt"]
            lunch = day_meals["lunch"]
            lunch_alt = day_meals["lunch_alt"]
            dinner = day_meals["dinner"]
            dinner_alt = day_meals["dinner_alt"]
        elif texture == "soft_solid":
            day_meals = soft_solid_matrix[day]
            breakfast = day_meals["breakfast"]
            breakfast_alt = day_meals["breakfast_alt"]
            lunch = day_meals["lunch"]
            lunch_alt = day_meals["lunch_alt"]
            dinner = day_meals["dinner"]
            dinner_alt = day_meals["dinner_alt"]
        else: # solid
            day_meals = solid_matrix[day]
            breakfast = day_meals["breakfast"]
            breakfast_alt = day_meals["breakfast_alt"]
            lunch = day_meals["lunch"]
            lunch_alt = day_meals["lunch_alt"]
            dinner = day_meals["dinner"]
            dinner_alt = day_meals["dinner_alt"]
            
        # Apply active allergy substitutions dynamically
        breakfast = apply_allergy_substitution(breakfast, allergens)
        breakfast_alt = apply_allergy_substitution(breakfast_alt, allergens)
        lunch = apply_allergy_substitution(lunch, allergens)
        lunch_alt = apply_allergy_substitution(lunch_alt, allergens)
        dinner = apply_allergy_substitution(dinner, allergens)
        dinner_alt = apply_allergy_substitution(dinner_alt, allergens)
        
        plan[day] = [
            {"meal": "Breakfast", "time": "8:30 AM", "food": breakfast, "alt_food": breakfast_alt},
            {"meal": "Mid-Morning", "time": "11:30 AM", "food": "Seasonal Fruit / Mashed Papaya", "alt_food": "Coconut Water / Jaggery treat"},
            {"meal": "Lunch", "time": "2:00 PM", "food": lunch, "alt_food": lunch_alt},
            {"meal": "Evening", "time": "5:00 PM", "food": "Roasted Grains / Milk (Almond Milk if Dairy-free)", "alt_food": "Roasted Makhana / Sprouted seeds"},
            {"meal": "Dinner", "time": "8:00 PM", "food": dinner, "alt_food": dinner_alt}
        ]
        
    return plan

def get_nutrition_recommendation(child):
    """
    AI Recommender: Age-Adaptive and All-India Locality Aware.
    """
    child_age_months = (datetime.date.today() - child.date_of_birth).days // 30
    guidelines = get_age_guidelines(child_age_months)
    
    # Locality-based filtering
    available_foods = LocalFoodResource.objects.filter(localities=child.locality)
    if not available_foods.exists() and child.locality:
        available_foods = LocalFoodResource.objects.filter(localities__region_tag=child.locality.region_tag).distinct()
    
    if not available_foods.exists():
        available_foods = LocalFoodResource.objects.all()
        
    # Filter out allergens based on Mother's profile (retained for database compatibility)
    allergy_summary = ""
    try:
        mother_profile = child.parent.mother_profile
        if mother_profile.allergies:
            allergens = [a.strip().lower() for a in mother_profile.allergies.split(',') if a.strip()]
            if allergens:
                for allergen in allergens:
                    available_foods = available_foods.exclude(name__icontains=allergen)
                    available_foods = available_foods.exclude(nutritional_description__icontains=allergen)
                allergy_summary = f" (Excluded allergens: {', '.join(allergens)})"
    except Exception:
        pass
    
    if child_age_months < 6:
        recommendation = NutritionRecommendation.objects.create(
            child=child,
            logic_summary="Foundations Mode: WHO guidelines strictly mandate exclusive breastfeeding.",
            nutritional_gap_addressed="N/A (Immunity focused)",
            seven_day_plan={"All Days": [{"meal": "Nutrition", "time": "Anytime", "food": "Exclusive Breastfeeding"}]}
        )
        return recommendation

    diet_plan = generate_7_day_plan(child, available_foods, guidelines)
    
    logic_summary = f"{guidelines['desc']} Plan for {child.locality.name if child.locality else 'Local Area'}. " \
                    f"Prioritized regional {child.locality.region_tag if child.locality else 'NORTH_INDIA'} staples.{allergy_summary}"
    
    # Highlight Iron & Folate priority resources based on District
    district = child.locality.district if child.locality and child.locality.district else 'Local District'
    iron_folate_priorities = "Spinach, Jaggery, Lentils, Ragi"
    logic_summary += f"\n*** IRON & FOLATE PRIORITY: Ensure {iron_folate_priorities} are included for {district} to combat rural anaemia deficits. ***"
    
    recommendation = NutritionRecommendation.objects.create(
        child=child,
        logic_summary=logic_summary,
        nutritional_gap_addressed="Protein, Energy, Regional Micronutrients",
        seven_day_plan=diet_plan
    )
    
    # Top 6 Regional Foods for the Shopping List
    proteins = available_foods.filter(category='protein').order_by('-protein_content')[:2]
    carbs = available_foods.filter(category__in=['carbs', 'millet'])[:2]
    greens = available_foods.filter(category='greens')[:2]
    
    shopping_list_foods = list(proteins) + list(carbs) + list(greens)
    if not shopping_list_foods:
        shopping_list_foods = available_foods[:6]
        
    recommendation.recommended_foods.set(shopping_list_foods)
    return recommendation

def generate_maternal_7_day_plan(mother, phase):
    """
    Creates a dynamic, 7-day-indexed matrix (Days 1 to 7) for Monday through Sunday.
    Completely distinct regional, allergy-safe meal ideas for each postpartum phase.
    """
    region = mother.user.locality.region_tag if mother.user.locality else 'SOUTH_INDIA'
    pref = mother.diet_preference
    allergens = [a.strip().lower() for a in mother.allergies.split(',') if a.strip()] if mother.allergies else []
    
    # Programmatic 7-Day Regional Meal Ideas Matrix
    maternal_matrix = {
        'NORTH_INDIA': {
            'veg': {
                1: [ # Phase 1: Healing
                    ("Ajwain Dalia", "Carom seed wheat porridge with warm herbs.", "Moong Dal Khichdi", "Mashed rice and split green lentils with cow ghee.", "Roasted Makhana", "Lotus seeds roasted with black pepper.", "Lauki Soup", "Bottle gourd broth infused with roasted cumin.", "Dalia, Ajwain, Moong Dal, Rice, Ghee, Makhana, Lauki", "Wound healing & active digestion"),
                    ("Garlic Wheat Mash", "Antiseptic fresh garlic porridge.", "Dalia & Mashed Veggies", "Fiber-rich broken wheat, carrots, and peas.", "Turmeric Milk", "Warm milk (or almond milk) with organic fresh haldi.", "Yellow Dal & Soft Roti", "Easy plant protein with soft whole wheat bread.", "Wheat, Garlic, Carrots, Milk, Turmeric, Moong Dal", "Postnatal immunity boost"),
                    ("Ghee-roasted Sooji Dalia", "Digestive semolina porridge.", "Mashed Rice & Moringa Dal", "Iron-rich drumstick greens dal with rice.", "Dry Fruit Ladoo", "Energy-dense cashew and resin round sweet.", "Spinach Soup", "Pureed fresh baby spinach broth.", "Sooji, Moringa, Rice, Ghee, Dry Fruits, Spinach", "Lactation preparation"),
                    ("Ajwain Rice & Ghee", "Stomach-soothing herb rice.", "Green Moong Khichdi", "Easy digesting whole green lentils and soft rice.", "Warm Ginger Water", "Pain-relieving ginger decoction.", "Lauki Ki Sabzi & Roti", "Light gourd curry with soft chapati.", "Rice, Ajwain, Moong Dal, Ginger, Lauki, Wheat", "Stomach gas relief"),
                    ("Cumin Dalia", "Roasted cumin seed cracked wheat.", "Soft Palak Dal & Rice", "Iron-heavy spinach cooked with yellow dal and rice.", "Roasted Makhana", "Crunchy roasted lotus seeds.", "Yellow Pumpkin Soup", "Boiled sweet pumpkin broth.", "Dalia, Cumin, Spinach, Moong Dal, Pumpkin", "Iron replenishment"),
                    ("Cardamom Suji Halwa", "Fragrant semolina porridge.", "Dalia & Mashed Carrots", "Soft cracked wheat with carrots.", "Turmeric Almond Drink", "Warm almond beverage with fresh turmeric.", "Moong Dal & Soft Roti", "Comforting protein meal.", "Suji, Cardamom, Carrots, Almonds, Moong Dal", "Tissue repair support"),
                    ("Fenugreek (Methi) Kanji", "Postnatal fenugreek rice porridge.", "Gourd Khichdi", "Fiber-loaded bottle gourd and rice mash with ghee.", "Dry Fruits Mix", "Crushed almonds, cashews, and dates.", "Dal Soup", "Clear strained lentil broth.", "Rice, Methi, Gourd, Ghee, Dry Fruits, Lentils", "Uterus contraction & cleansing")
                ],
                2: [ # Phase 2: Lactation
                    ("Methi Paratha", "Fenugreek leaf flatbread with fresh curd.", "Palak Paneer & Roti", "Iron-rich fresh spinach and cottage cheese with soft roti.", "Gond Laddoos & Milk", "Energy-dense edible resin sweets with warm milk.", "Vegetable Daliya", "Fiber-rich broken cracked wheat with carrot cubes.", "Methi, Wheat, Spinach, Paneer, Gond, Milk", "Lactation support & milk supply"),
                    ("Besan Chilla", "Gram flour pancakes seasoned with ginger.", "Mixed Veg Khichdi", "Nutrient-dense vegetable and lentil rice mash.", "Panjiri & Herbal Tea", "Whole wheat and nut strength mix with herbal tea.", "Moong Dal & Spinach Saag", "High protein and iron rich dinner.", "Besan, Moong Dal, Spinach, Mixed Veggies, Panjiri", "Bone density & breastmilk quality"),
                    ("Ragi Malt Porridge", "Finger millet milk drink.", "Paneer Bhurji & Soft Roti", "Scrambled cottage cheese with whole wheat rotis.", "Gond Ladoo", "Lactation resin sweet.", "Dalia & Green Beans", "High fiber cracked wheat.", "Ragi, Paneer, Gond, Dalia, Green Beans", "Calcium boost for bone support"),
                    ("Oats Porridge with Jaggery", "Iron-sweetened oat porridge.", "Palak Paneer with Red Rice", "Cottage cheese in creamy spinach sauce.", "Panjiri & Milk", "Wheat and nut strength mix.", "Yellow Dal & Spinach", "Double iron priority soup.", "Oats, Spinach, Paneer, Red Rice, Panjiri", "Anaemia intervention"),
                    ("Methi Roti & Curd", "Fenugreek flatbread.", "Mixed Veg Pulao", "Millet and rice mixed vegetable pulav.", "Gond Ladoo", "Energy booster sweet.", "Lauki Dal & Chapati", "Gourd cooked with yellow split lentils.", "Methi, Rice, Veggies, Gond, Lauki, Lentils", "Digestive balance"),
                    ("Besan Chilla with Tomatoes", "Savory chickpea pancakes.", "Moong Dal Khichdi", "Soft cooked split green lentils.", "Panjiri & Tea", "Traditional postnatal strength mix.", "Paneer Tikka (Mild) & Roti", "Grilled paneer cubes with soft wheat chapati.", "Besan, Paneer, Moong Dal, Panjiri", "Muscle rebuilding"),
                    ("Sprouted Moong Dosa", "Probiotic green gram crepes.", "Spinach Rice & Dal", "Iron-heavy spinach rice with yellow split dal.", "Dry Fruit Ladoo", "Nut and seed sweet ball.", "Vegetable Dalia", "Fiber-rich cracked wheat.", "Moong, Spinach, Rice, Dry Fruits, Dalia", "Lactation milk supply boost")
                ],
                3: [ # Phase 3: Strength
                    ("Mixed Sprouts", "Steamed whole moong and chana with lemon.", "Soya Chunk Curry & Rice", "Plant-based high protein meal with basmati rice.", "Paneer Tikka (Mild)", "Grilled cottage cheese cubes with mild herbs.", "Seasonal Saag & Roti", "Iron-heavy mustard/spinach greens with chapati.", "Sprouts, Soya Chunks, Rice, Paneer, Greens", "Muscle & tissue rebuilding"),
                    ("Almond Milk Oats", "Oatmeal cooked in almond milk with honey.", "Paneer Curry & Rice", "Calcium-rich cottage cheese curry and basmati rice.", "Roasted Peanuts", "Healthy fats and high protein peanut snack.", "Mixed Veg Sabzi & Roti", "Multi-vitamin rich vegetables with soft roti.", "Oats, Almonds, Paneer, Rice, Peanuts, Veggies", "Full restoration & strength"),
                    ("Methi Paratha & Curd", "Fenugreek flatbread.", "Rajma (Red Kidney Beans) & Rice", "Iron-heavy red kidney beans in thick gravy with rice.", "Roasted Makhana", "Crunchy roasted lotus seeds.", "Palak Saag & Roti", "Creamy spinach curry with soft bread.", "Methi, Rajma, Rice, Makhana, Spinach", "Haemoglobin recovery"),
                    ("Sprouted Chana Upma", "Semolina upma with sprouted chickpeas.", "Lauki Dal & Red Rice", "Bottle gourd and dal with red rice.", "Gond Ladoo & Milk", "Energy-dense postpartum sweet.", "Soya Chunk Pulao", "High-protein soya chunks cooked with rice.", "Chana, Dalia, Gond, Soya, Rice", "Amino acid support"),
                    ("Ragi Dosa & Chutney", "Calcium-heavy finger millet crepes.", "Paneer Bhurji & Chapati", "Scrambled paneer with whole wheat roti.", "Roasted Peanuts", "Energy snack.", "Moong Dal & Palak", "Yellow split lentils with spinach.", "Ragi, Paneer, Peanuts, Moong Dal, Spinach", "Bone density enhancement"),
                    ("Oats upma with peas", "Semolina and oats with carrots.", "Chana Masala & Rice", "Protein-dense chickpea curry with rice.", "Dry Fruit Ladoo", "Cashew, almond and date ball.", "Paneer Curry & Roti", "Calcium-heavy cottage cheese.", "Oats, Chickpeas, Dry Fruits, Paneer", "Active restoration"),
                    ("Mixed Sprouts Salad", "Steamed grains and lentils.", "Soya chunk Curry & Roti", "High-protein soya curry.", "Paneer Cubes (Raw)", "Fresh calcium snack.", "Spinach Saag & Rice", "Iron-rich spinach dinner.", "Sprouts, Soya, Paneer, Spinach, Rice", "Muscle recovery")
                ]
            },
            'non-veg': {
                1: [
                    ("Ajwain Dalia", "Carom seed wheat porridge.", "Moong Dal Khichdi", "Mashed rice and lentils with ghee.", "Egg Drop Soup", "Light antiseptic protein egg white broth.", "Lauki Soup", "Bottle gourd broth with cumin.", "Dalia, Ajwain, Moong Dal, Eggs, Lauki", "Healing & Digestion"),
                    ("Garlic Wheat Mash", "Antiseptic garlic porridge.", "Dalia & Mashed Veggies", "Fiber-rich wheat and carrots.", "Turmeric Milk", "Warm milk with fresh haldi.", "Chicken Broth & Soft Roti", "Lean chicken protein soup.", "Wheat, Garlic, Milk, Chicken, Wheat", "Immunity Boost"),
                    ("Cardamom Oats", "Warm oats porridge.", "Egg Khichdi", "Lentils, rice and scrambled eggs.", "Ginger Tea", "Warm pain-relieving tea.", "Chicken Soup & Soft Bread", "High protein chicken broth.", "Oats, Eggs, Chicken, Rice", "Tissue repair"),
                    ("Ajwain Rice & Ghee", "Herb digestion rice.", "Moong Dal & Fish Soup", "Light fish soup and rice.", "Turmeric Milk", "Warm haldi drink.", "Mashed Potato & Soft Chicken", "Easy lean protein.", "Rice, Fish, Chicken, Milk", "Stomach recovery"),
                    ("Egg white toast", "Toasted wheat bread with egg whites.", "Dalia & Mashed Veggies", "Cracked wheat and carrots.", "Makhana", "Lotus seeds.", "Yellow Chicken Broth", "Healing bone broth.", "Eggs, Dalia, Chicken, Makhana", "Protein replenishment"),
                    ("Garlic Mash", "Garlic porridge.", "Moong Dal Khichdi", "Split green lentils and rice.", "Boiled Egg", "Simple protein.", "Clear Chicken Soup", "Light lean chicken soup.", "Garlic, Moong Dal, Eggs, Chicken", "Wound healing"),
                    ("Fenugreek Kanji", "Red rice porridge.", "Egg Drop Soup", "Easy digesting egg soup.", "Ginger Decoction", "Herbal drink.", "Mashed fish & Rice", "Soft coastal fish mash.", "Red Rice, Eggs, Fish, Ginger", "Cleansing & healing")
                ],
                2: [
                    ("Egg Paratha", "Flatbread stuffed with egg & herbs.", "Chicken Keema & Roti", "Lean chicken mince and wheat flatbread.", "Gond Laddoos & Milk", "Energy-dense resin sweets.", "Vegetable Daliya", "Fiber-rich cracked wheat.", "Eggs, Chicken, Wheat, Gond, Milk", "Lactation Support"),
                    ("Besan Chilla", "Gram flour pancakes.", "Egg Khichdi", "Rice, lentils, and scrambled eggs.", "Panjiri & Herbal Tea", "Wheat and nut strength mix.", "Chicken Soup & Spinach", "High protein and iron.", "Besan, Eggs, Chicken, Panjiri, Spinach", "Strength & Milk"),
                    ("Ragi Malt Porridge", "Finger millet milk drink.", "Chicken Keema & Roti", "Lean chicken mince and roti.", "Gond Ladoo", "Postnatal sweet.", "Egg Bhurji & Chapati", "Scrambled eggs and whole wheat chapati.", "Ragi, Chicken, Gond, Eggs", "DHA & Calcium supply"),
                    ("Egg Toast & Tea", "Whole wheat egg toast.", "Chicken Curry & Red Rice", "Lean chicken curry with red rice.", "Panjiri & Milk", "Traditional strength mix.", "Fish Broth & Rice", "DHA-heavy fish soup.", "Eggs, Chicken, Red Rice, Panjiri, Fish", "Anaemia intervention"),
                    ("Methi Paratha", "Fenugreek flatbread.", "Egg Khichdi & Curd", "Rice, lentils and egg mash.", "Gond Ladoo", "Energy sweet.", "Chicken Soup & Spinach", "Lean chicken and iron greens.", "Methi, Eggs, Gond, Chicken, Spinach", "Lactation support"),
                    ("Besan Chilla", "Savory pancakes.", "Chicken Keema & Roti", "Lean chicken mince.", "Panjiri & Milk", "Wheat and nut strength mix.", "Egg Bhurji & Spinach", "High protein scrambled eggs.", "Besan, Chicken, Panjiri, Eggs, Spinach", "Muscle building"),
                    ("Oats upma with egg", "Semolina and scrambled egg.", "Fish Curry & Red Rice", "Rich fish curry.", "Dry Fruit Ladoo", "Postnatal sweet.", "Chicken Broth & Roti", "Lean protein dinner.", "Oats, Eggs, Fish, Red Rice, Chicken", "Lactation milk boost")
                ],
                3: [
                    ("Egg Bhurji", "Scrambled eggs with onions.", "Chicken Stew & Roti", "Lean protein in mild gravy.", "Roasted Peanuts", "Healthy fats and protein.", "Fish Curry & Rice", "Omega-3 rich dinner.", "Eggs, Chicken, Wheat, Peanuts, Fish, Rice", "Active Recovery"),
                    ("Chicken Keema Toast", "Minced chicken toast.", "Chicken Curry & Rice", "High protein dinner.", "Boiled Eggs", "Simple protein snack.", "Paneer Curry & Roti", "Calcium and protein.", "Chicken, Eggs, Paneer, Wheat", "Muscle Rebuilding"),
                    ("Scrambled Eggs on Toast", "Eggs on wheat bread.", "Fish Roast & Red Rice", "High DHA seafood meal.", "Roasted Makhana", "Lotus seeds.", "Chicken Curry & Chapati", "Protein rich dinner.", "Eggs, Fish, Red Rice, Chicken", "Heart & brain health"),
                    ("Egg Paratha", "Egg flatbread.", "Chicken Keema & Rice", "Mince chicken with basmati rice.", "Gond Ladoo & Milk", "Energy sweet.", "Fish Curry & Roti", "DHA-rich coastal dinner.", "Eggs, Chicken, Rice, Gond, Fish", "Tissue repair"),
                    ("Ragi Dosa & Egg", "Millets crepe with scrambled egg.", "Chicken Stew & Chapati", "Lean chicken curry.", "Roasted Peanuts", "Healthy fats.", "Fish Fry (Mild) & Rice", "Omega-3 rich fish.", "Ragi, Eggs, Chicken, Fish, Rice", "Bone & heart support"),
                    ("Oats Upma & Chicken", "Oats with chicken chunks.", "Chicken Curry & Rice", "High protein meal.", "Boiled Egg", "Simple protein.", "Egg Bhurji & Chapati", "Scrambled egg dinner.", "Oats, Chicken, Eggs, Rice", "Active restoration"),
                    ("Mixed Sprouts & Egg", "Steamed sprouts with boiled egg.", "Fish Curry & Red Rice", "Omega-3 rich dinner.", "Dry Fruit Ladoo", "Postnatal sweet.", "Chicken Stew & Roti", "Lean chicken breast curry.", "Sprouts, Eggs, Fish, Chicken, Rice", "Full physical recovery")
                ]
            }
        },
        'SOUTH_INDIA': {
            'veg': {
                1: [
                    ("Methi Kanji", "Fenugreek red rice porridge.", "Garlic Rasam & Mash", "Antiseptic tamarind soup.", "Pepper Decoction", "Herbal immunity drink.", "Steamed Idli & Podi", "Probiotic rice cakes.", "Red Rice, Methi, Garlic, Tamarind, Pepper, Idli", "Womb Healing"),
                    ("Ragi Malt", "Finger millet drink.", "Rice & Moringa Leaves", "Iron-rich drumstick greens.", "Steamed Banana", "Natural potassium boost.", "Curd Rice & Ginger", "Cooling and digestive.", "Ragi, Rice, Moringa, Banana, Curd, Ginger", "Digestive Health"),
                    ("Idli & Sambar (Mild)", "Steamed soft rice cakes.", "Moringa Leaf Dal & Rice", "Iron-heavy drumstick greens dal.", "Pepper water", "Immunity water.", "Ragi Malt", "Finger millet drink.", "Idli, Moringa, Ragi", "Lactation preparation"),
                    ("Methi Kanji", "Postnatal red rice gruel.", "Garlic Rasam & Mash", "Spicy tamarind digestive soup.", "Banana steam", "Potassium boost.", "Curd Rice", "Gut cooling mash.", "Red Rice, Garlic, Banana, Curd", "Stomach gas relief"),
                    ("Ragi Malt", "Finger millet drink.", "Rice & Moringa Leaves", "Iron-rich drumstick leaves.", "Makhana", "Lotus seeds.", "Dal Soup", "Lentil broth.", "Ragi, Rice, Moringa, Makhana", "Iron replenishment"),
                    ("Idli & Podi", "Soft probiotic rice cakes.", "Moringa Leaf Dal", "Iron-rich drumstick leaf dal.", "Turmeric Drink", "Haldi water.", "Curd Rice", "Cooling digestion.", "Idli, Moringa, Curd", "Wound healing"),
                    ("Fenugreek Kanji", "Fenugreek red rice porridge.", "Garlic Rasam & Rice", "Tamarind digestive soup.", "Dry Fruits Mix", "Crushed nuts.", "Dal Soup", "Lentil soup.", "Red Rice, Garlic, Dry Fruits", "Cleansing & healing")
                ],
                2: [
                    ("Idiyappam & Stew", "Rice noodles with veg stew.", "Sesame Rice & Dal", "Hormone-balancing fats.", "Moringa Leaf Soup", "Intense calcium boost.", "Garlic Milk & Rasam", "Lactation support.", "Rice Flour, Veggies, Sesame, Moringa, Garlic, Milk", "Lactation Power"),
                    ("Puttu & Kadala", "Steamed rice cake with chickpeas.", "Paneer Roast & Red Rice", "Protein-rich coastal meal.", "Dry Ginger Coffee", "Pain-relieving herbal coffee.", "Mashed Rice & Ghee", "High energy lactation.", "Rice, Chickpeas, Paneer, Ginger, Ghee", "Lactation Support"),
                    ("Ragi Dosa & Chutney", "Finger millet crepes.", "Sesame Rice & Dal", "Hormone-balancing.", "Garlic Milk", "Lactation booster.", "Vegetable Idiyappam", "Rice noodles with stew.", "Ragi, Sesame, Garlic, Milk, Rice", "Calcium boost"),
                    ("Puttu & Kadala", "Steamed rice cake.", "Moringa Leaf Rice & Dal", "Iron-rich greens and dal.", "Ginger Coffee", "Postnatal herb coffee.", "Steamed Banana & Ghee", "Energy boost.", "Rice, Chickpeas, Moringa, Ginger, Ghee", "Lactation milk supply"),
                    ("Idiyappam & Stew", "Rice noodles and vegetable curry.", "Sesame Rice & Dal", "Lentils and rice.", "Garlic Milk", "Postnatal milk drink.", "Paneer Roast & Rice", "Cottage cheese dinner.", "Rice, Sesame, Garlic, Paneer", "Digestive balance"),
                    ("Ragi Dosa", "Finger millet pancakes.", "Paneer Curry & Rice", "Calcium-rich curry.", "Ginger Coffee", "Postnatal coffee.", "Idli & Sambar", "Soft rice cakes.", "Ragi, Paneer, Rice, Ginger", "Muscle rebuilding"),
                    ("Puttu & Kadala", "Steamed rice cake with chickpeas.", "Sesame Rice & Dal", "Balanced dal and rice.", "Garlic Milk", "Lactation support.", "Moringa Dal & Rice", "Iron-heavy drumstick greens.", "Rice, Chickpeas, Sesame, Garlic, Moringa", "Lactation milk boost")
                ],
                3: [
                    ("Upma & Veggies", "Semolina with carrots/peas.", "Dal Tadka & Red Rice", "Lentil protein and rice.", "Peanut Sundal", "Steamed protein snack.", "Avial & Rice", "Full vitamin spectrum.", "Semolina, Lentils, Red Rice, Peanuts, Veggies", "Tissue Repair"),
                    ("Ragi Dosa", "Finger millet crepes.", "Paneer Curry & Rice", "Calcium-rich meal.", "Dry Fruits & Milk", "Nutrient dense drink.", "Curd Rice & Fruits", "Gut health and vitamins.", "Ragi, Paneer, Rice, Dry Fruits, Curd", "Vitality & Gut"),
                    ("Upma with Carrots", "Savory semolina.", "Dal Tadka & Red Rice", "Lentil protein.", "Peanut Sundal", "Steamed protein.", "Avial & Red Rice", "Mixed vegetable curry.", "Semolina, Lentils, Red Rice, Peanuts", "Haemoglobin recovery"),
                    ("Ragi Dosa", "Millet crepes.", "Paneer Curry & Rice", "Cottage cheese dinner.", "Dry Fruits & Milk", "Nutrient milk.", "Curd Rice & Fruits", "Gut soothing dinner.", "Ragi, Paneer, Rice, Dry Fruits, Curd", "Amino acid support"),
                    ("Upma & Peas", "Semolina breakfast.", "Dal Tadka & Red Rice", "Lentils and red rice.", "Peanut Sundal", "Steamed snack.", "Avial & Rice", "Multi-vegetable stew.", "Semolina, Lentils, Red Rice, Peanuts", "Bone density enhancement"),
                    ("Ragi Dosa", "Finger millet crepes.", "Paneer Curry & Rice", "Calcium cottage cheese.", "Dry Fruits & Milk", "Postnatal milk.", "Curd Rice & Fruits", "Cooling digestion.", "Ragi, Paneer, Rice, Dry Fruits, Curd", "Active restoration"),
                    ("Upma & Veggies", "Semolina with carrots.", "Dal Tadka & Red Rice", "High protein lentils.", "Peanut Sundal", "Steamed peanut snack.", "Avial & Rice", "Full vitamin spectrum.", "Semolina, Lentils, Red Rice, Peanuts", "Muscle recovery")
                ]
            },
            'non-veg': {
                1: [
                    ("Chicken Kanji", "Chicken and red rice porridge.", "Garlic Rasam & Mash", "Antiseptic tamarind soup.", "Pepper Decoction", "Herbal immunity drink.", "Egg Appam", "Soft rice pancakes with egg.", "Red Rice, Chicken, Garlic, Tamarind, Pepper, Eggs", "Womb Healing"),
                    ("Ragi Malt", "Finger millet drink.", "Rice & Moringa Leaves", "Iron-rich drumstick greens.", "Steamed Banana", "Natural potassium boost.", "Curd Rice & Ginger", "Cooling and digestive.", "Ragi, Rice, Moringa, Banana, Curd, Ginger", "Digestive Health"),
                    ("Chicken Kanji", "Postnatal chicken red rice gruel.", "Garlic Rasam & Mash", "Tamarind digestive soup.", "Pepper Decoction", "Herbal drink.", "Egg Appam", "Soft pancakes with egg.", "Red Rice, Chicken, Garlic, Eggs", "Lactation preparation"),
                    ("Ragi Malt", "Finger millet drink.", "Rice & Moringa Leaves", "Iron-heavy drumstick greens.", "Banana steam", "Potassium boost.", "Curd Rice", "Gut cooling mash.", "Ragi, Rice, Moringa, Curd", "Stomach gas relief"),
                    ("Chicken Kanji", "Chicken and red rice porridge.", "Garlic Rasam", "Tamarind soup.", "Pepper water", "Postnatal immunity drink.", "Egg Appam", "Soft egg pancake.", "Red Rice, Chicken, Garlic, Eggs", "Iron replenishment"),
                    ("Ragi Malt", "Finger millet drink.", "Rice & Moringa Leaves", "Iron-rich greens.", "Steamed Banana", "Potassium boost.", "Curd Rice & Ginger", "Cooling gut check.", "Ragi, Rice, Moringa, Banana, Curd", "Wound healing"),
                    ("Chicken Kanji", "Chicken and red rice porridge.", "Garlic Rasam", "Tamarind soup.", "Pepper Decoction", "Herbal drink.", "Egg Appam", "Soft egg pancake.", "Red Rice, Chicken, Garlic, Eggs", "Cleansing & healing")
                ],
                2: [
                    ("Idiyappam & Stew", "Rice noodles with veg stew.", "Sesame Rice & Dal", "Hormone-balancing fats.", "Moringa Leaf Soup", "Intense calcium boost.", "Garlic Milk & Rasam", "Lactation support.", "Rice Flour, Veggies, Sesame, Moringa, Garlic, Milk", "Lactation Power"),
                    ("Puttu & Kadala", "Steamed rice cake with chickpeas.", "Fish Curry & Red Rice", "DHA-rich coastal meal.", "Dry Ginger Coffee", "Pain-relieving herbal coffee.", "Mashed Rice & Ghee", "High energy lactation.", "Rice, Chickpeas, Sardines, Ginger, Ghee", "DHA & Strength"),
                    ("Idiyappam & Stew", "Rice noodles and curry.", "Fish Curry & Red Rice", "DHA-rich seafood meal.", "Moringa Soup", "Calcium booster.", "Garlic Milk", "Postnatal milk.", "Rice Flour, Fish, Red Rice, Moringa, Garlic", "Calcium boost"),
                    ("Puttu & Kadala", "Steamed rice cake.", "Sesame Rice & Dal", "Balanced dal and rice.", "Ginger Coffee", "Postnatal coffee.", "Mashed Rice & Ghee", "Energy boost.", "Rice, Chickpeas, Sesame, Ginger, Ghee", "Lactation milk supply"),
                    ("Idiyappam & Stew", "Rice noodles and vegetable stew.", "Fish Curry & Red Rice", "Omega-3 seafood dinner.", "Moringa Soup", "Calcium booster.", "Garlic Milk & Rasam", "Postnatal milk.", "Rice Flour, Fish, Red Rice, Moringa, Garlic", "Digestive balance"),
                    ("Ragi Dosa", "Finger millet crepes.", "Fish Curry & Red Rice", "DHA-rich coastal meal.", "Ginger Coffee", "Postnatal coffee.", "Curd Rice", "Gut cooling dinner.", "Ragi, Fish, Red Rice, Ginger, Curd", "Muscle rebuilding"),
                    ("Puttu & Kadala", "Steamed rice cake.", "Fish Curry & Red Rice", "Zinc and protein boost.", "Garlic Milk", "Lactation support.", "Curd Rice", "Cooling digestion.", "Rice, Chickpeas, Fish, Red Rice, Garlic", "Lactation milk boost")
                ],
                3: [
                    ("Upma & Veggies", "Semolina with carrots/peas.", "Chicken Curry & Red Rice", "Lean protein and complex carbs.", "Boiled Egg & Tea", "Quick protein snack.", "Avial & Rice", "Full vitamin spectrum.", "Semolina, Chicken, Red Rice, Eggs, Veggies", "Tissue Repair"),
                    ("Ragi Dosa", "Finger millet crepes.", "Prawn Roast & Rice", "Zinc and protein boost.", "Peanut Sundal", "Steamed protein snack.", "Curd Rice & Fruits", "Gut health and vitamins.", "Ragi, Prawns, Rice, Peanuts, Curd", "Vitality & Gut"),
                    ("Upma & Veggies", "Savory semolina.", "Chicken Curry & Red Rice", "Lean protein.", "Boiled Egg & Tea", "Quick protein.", "Avial & Rice", "Mixed vegetable stew.", "Semolina, Chicken, Red Rice, Eggs", "Haemoglobin recovery"),
                    ("Ragi Dosa", "Millet crepes.", "Prawn Roast & Rice", "Zinc and protein dinner.", "Peanut Sundal", "Steamed protein.", "Curd Rice & Fruits", "Gut health.", "Ragi, Prawns, Rice, Peanuts, Curd", "Amino acid support"),
                    ("Upma & Veggies", "Semolina breakfast.", "Chicken Curry & Red Rice", "Lean protein curry.", "Boiled Egg", "Simple protein.", "Avial & Rice", "Full vitamin spectrum.", "Semolina, Chicken, Red Rice, Eggs", "Bone density enhancement"),
                    ("Ragi Dosa", "Finger millet crepes.", "Prawn Roast & Rice", "Zinc seafood meal.", "Peanut Sundal", "Steamed snack.", "Curd Rice & Fruits", "Cooling digestion.", "Ragi, Prawns, Rice, Peanuts, Curd", "Active restoration"),
                    ("Upma & Veggies", "Semolina with carrots.", "Chicken Curry & Red Rice", "Lean protein dinner.", "Boiled Egg & Tea", "Quick protein.", "Avial & Rice", "Full vitamin spectrum.", "Semolina, Chicken, Red Rice, Eggs", "Muscle recovery")
                ]
            }
        }
    }
    
    # Fallback to NORTH_INDIA if region is not present, or veg if preference is veg
    region_key = region if region in maternal_matrix else 'NORTH_INDIA'
    pref_key = pref if pref in ['veg', 'non-veg'] else 'veg'
    
    phase_data = maternal_matrix[region_key][pref_key][phase]
    
    plan = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for i, day in enumerate(days):
        recipe = phase_data[i % len(phase_data)]
        
        # Extract fields
        breakfast_name = recipe[0]
        breakfast_details = recipe[1]
        lunch_name = recipe[2]
        lunch_details = recipe[3]
        snack_name = recipe[4]
        snack_details = recipe[5]
        dinner_name = recipe[6]
        dinner_details = recipe[7]
        ingredients = recipe[8]
        benefits = recipe[9]
        
        # Apply active allergy substitutions dynamically
        breakfast_name = apply_allergy_substitution(breakfast_name, allergens)
        breakfast_details = apply_allergy_substitution(breakfast_details, allergens)
        lunch_name = apply_allergy_substitution(lunch_name, allergens)
        lunch_details = apply_allergy_substitution(lunch_details, allergens)
        snack_name = apply_allergy_substitution(snack_name, allergens)
        snack_details = apply_allergy_substitution(snack_details, allergens)
        dinner_name = apply_allergy_substitution(dinner_name, allergens)
        dinner_details = apply_allergy_substitution(dinner_details, allergens)
        ingredients = apply_allergy_substitution(ingredients, allergens)
        
        plan[day] = {
            'day_name': day,
            'breakfast_name': breakfast_name,
            'breakfast_details': breakfast_details,
            'lunch_name': lunch_name,
            'lunch_details': lunch_details,
            'snack_name': snack_name,
            'snack_details': snack_details,
            'dinner_name': dinner_name,
            'dinner_details': dinner_details,
            'ingredients': ingredients,
            'benefits': benefits
        }
        
    return plan
