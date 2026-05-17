from health.models import LocalFoodResource, NutritionRecommendation
import random

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

def generate_7_day_plan(child, available_foods, guidelines):
    """
    Generates a 7-day meal plan based on locality, age, and regional staples.
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plan = {}
    
    foods_list = list(available_foods)
    if not foods_list:
        return {day: "Consult healthcare worker for local resources" for day in days}

    # Market Prices Simulation (Districts)
    market_prices = {
        "Bajra (Pearl Millet)": "low", "Ragi (Finger Millet)": "low",
        "Coconut Milk": "low", "Sardines": "low", "Moong Dal": "low"
    }
    
    # Regional Staple Preference
    region = child.locality.region_tag if child.locality else "NORTH_INDIA"
    
    for day in days:
        protein_sources = [f for f in foods_list if f.category == 'protein']
        carb_sources = [f for f in foods_list if f.category in ['carbs', 'millet']]
        green_sources = [f for f in foods_list if f.category == 'greens']
        
        def get_smart_choice(sources):
            if not sources: return None
            # Filter for low cost or regional match
            regional = [s for s in sources if market_prices.get(s.name) == 'low' or s.is_low_cost]
            return random.choice(regional) if regional else random.choice(sources)
            
        smart_protein = get_smart_choice(protein_sources)
        smart_carb = get_smart_choice(carb_sources)
        smart_green = get_smart_choice(green_sources)
        
        # Alternate Smart Choice Generation
        alt_protein_sources = [p for p in protein_sources if p != smart_protein]
        alt_carb_sources = [c for c in carb_sources if c != smart_carb]
        alt_green_sources = [g for g in green_sources if g != smart_green]
        
        smart_protein_alt = get_smart_choice(alt_protein_sources) or smart_protein
        smart_carb_alt = get_smart_choice(alt_carb_sources) or smart_carb
        smart_green_alt = get_smart_choice(alt_green_sources) or smart_green
        
        texture = guidelines['texture']
        
        # Adaptive Meal Styles
        if texture == "puree":
            breakfast = f"Mashed {smart_carb.name if smart_carb else 'Grain'} with Milk"
            breakfast_alt = f"Warm {smart_carb_alt.name if smart_carb_alt else 'Grain'} Porridge"
            
            lunch = f"Pureed {smart_protein.name if smart_protein else 'Pulse'} & {smart_carb.name if smart_carb else 'Rice'}"
            lunch_alt = f"Soft Mashed {smart_protein_alt.name if smart_protein_alt else 'Millet'} & Lentils"
            
            dinner = f"Soft {smart_green.name if smart_green else 'Vegetable'} Mash"
            dinner_alt = f"Steamed Pumpkin / {smart_green_alt.name if smart_green_alt else 'Carrot'} Puree"
        elif texture == "soft_solid":
            breakfast = f"{smart_carb.name if smart_carb else 'Grain'} Upma / Porridge"
            breakfast_alt = f"Soft {smart_carb_alt.name if smart_carb_alt else 'Millet'} Pongal"
            
            lunch = f"{smart_protein.name if smart_protein else 'Pulse'} Khichdi with {smart_green.name if smart_green else 'Greens'}"
            lunch_alt = f"{smart_protein_alt.name if smart_protein_alt else 'Lentil'} Stew with {smart_carb_alt.name if smart_carb_alt else 'Soft Rice'}"
            
            dinner = f"Soft Roti with {smart_protein.name if smart_protein else 'Dal'}"
            dinner_alt = f"Mashed Vegetable Khichdi with {smart_protein_alt.name if smart_protein_alt else 'Curd'}"
        else: # Full Solid
            breakfast = f"Stuffed Paratha / Dosa with {smart_protein.name if smart_protein else 'Chutney'}"
            breakfast_alt = f"Fluffy Millets Idli with {smart_protein_alt.name if smart_protein_alt else 'Sambar'}"
            
            lunch = f"Regional {smart_carb.name if smart_carb else 'Grain'} Thali with {smart_protein.name if smart_protein else 'Curry'}"
            lunch_alt = f"{smart_carb_alt.name if smart_carb_alt else 'Rice'} Pulav with roasted {smart_protein_alt.name if smart_protein_alt else 'Paneer'}"
            
            dinner = f"{smart_carb.name if smart_carb else 'Bread'} with {smart_green.name if smart_green else 'Saag'} & {smart_protein.name if smart_protein else 'Curd'}"
            dinner_alt = f"Wheat Chapati with {smart_green_alt.name if smart_green_alt else 'Palak'} and boiled {smart_protein_alt.name if smart_protein_alt else 'Chana'}"

        plan[day] = [
            {"meal": "Breakfast", "time": "8:30 AM", "food": breakfast, "alt_food": breakfast_alt},
            {"meal": "Mid-Morning", "time": "11:30 AM", "food": "Seasonal Fruit / Local Snack", "alt_food": "Coconut Water / Dry Seeds"},
            {"meal": "Lunch", "time": "2:00 PM", "food": lunch, "alt_food": lunch_alt},
            {"meal": "Evening", "time": "5:00 PM", "food": "Roasted Grains / Milk", "alt_food": "Sprouted Sprouts / Herbal drink"},
            {"meal": "Dinner", "time": "8:00 PM", "food": dinner, "alt_food": dinner_alt}
        ]
    
    return plan

def get_nutrition_recommendation(child):
    """
    AI Recommender: Age-Adaptive and All-India Locality Aware.
    """
    import datetime
    child_age_months = (datetime.date.today() - child.date_of_birth).days // 30
    guidelines = get_age_guidelines(child_age_months)
    
    # Locality-based filtering
    available_foods = LocalFoodResource.objects.filter(localities=child.locality)
    if not available_foods.exists() and child.locality:
        # Fallback to regional tag
        available_foods = LocalFoodResource.objects.filter(localities__region_tag=child.locality.region_tag).distinct()
    
    if not available_foods.exists():
        available_foods = LocalFoodResource.objects.all()
    
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
                    f"Prioritized regional {child.locality.region_tag if child.locality else 'NORTH_INDIA'} staples."
    
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
