from health.models import PostpartumDiet, PostpartumCareGuide

def populate_maternal_data():
    # 1. 12-Week Recovery Roadmap (Detailed)
    guides = [
        (1, "Wound Healing & Rest", "Focus on C-section/Normal wound care. Keep clean and dry. Avoid lifting heavy objects.", "Deep Breathing", "Gentle belly breathing to engage core without strain.", "Sleep when the baby sleeps. Syncing is vital for your sanity."),
        (2, "Hydration & Movement", "Drink 3-4 liters of water. Essential for milk production and preventing constipation.", "Pelvic Floor / Kegels", "Internal contractions to strengthen the base. Hold for 3s, release.", "Reach out to one friend or family member today. Connection helps heal."),
        (3, "Digestion & Posture", "Sit upright while feeding. Use pillows for support. Walk slowly indoors.", "Shoulder Rolls", "Relieve tension from breastfeeding posture.", "Acknowledge your strength. You just brought life into the world."),
        (4, "Lactation Support", "Monitor supply. Use warm compresses if engorged. Frequent feeding is key.", "Light Walking", "5-10 mins slow indoor walking. Increase circulation.", "Mood swings are normal (Baby Blues), but talk to us if they persist beyond 2 weeks."),
        (6, "Nutritional Rebuilding", "Introduce more fiber and protein. Iron-rich local greens are a must.", "Pelvic Tilts", "Gentle lower back stretches to align the spine.", "Find 5 minutes of silence today. Just breathe."),
        (8, "Strength Rebuilding", "Balanced diet. High protein for tissue repair. Start looking into postnatal yoga.", "Postnatal Yoga", "Gentle stretching, Cat-Cow pose, and spinal alignment.", "Set one small 'me-time' goal this week. Even if it's a longer shower."),
        (10, "Endurance & Energy", "Energy levels should be stabilizing. Keep up the high-calorie healthy snacks.", "Brisk Walking", "15-20 mins outdoor walk. Vitamin D exposure.", "You are doing an amazing job. Look at how far you've come."),
        (12, "Full Recovery Transition", "Return to regular activity. Maintain hydration and localized nutrition.", "Active Fitness", "Increase walking pace, gentle swimming, or core strengthening.", "Celebrate your 3-month journey! You are a Hero Mother.")
    ]
    
    for wk, title, care, ex_t, ex_d, mental in guides:
        PostpartumCareGuide.objects.update_or_create(
            week_number=wk,
            defaults={
                'title': title,
                'care_instructions': care,
                'exercise_title': ex_t,
                'exercise_desc': ex_d,
                'mental_health_tip': mental
            }
        )

    # 2. 40-Day Full Meal Plan Engine (Breakfast, Lunch, Snack, Dinner)
    
    # NORTH INDIA RECIPES
    north_veg_p1 = [
        ("Ajwain Dalia", "Carom seed wheat porridge.", "Moong Dal Khichdi", "Mashed rice and lentils with ghee.", "Roasted Makhana", "Lotus seeds with pepper.", "Lauki Soup", "Bottle gourd broth with cumin.", "Dalia, Ajwain, Moong Dal, Rice, Ghee, Makhana, Lauki", "Healing & Digestion"),
        ("Garlic Wheat Mash", "Antiseptic garlic porridge.", "Dalia & Mashed Veggies", "Fiber-rich wheat and carrots.", "Turmeric Milk", "Warm milk with fresh haldi.", "Yellow Dal & Soft Roti", "Easy protein with wheat.", "Wheat, Garlic, Carrots, Milk, Turmeric, Moong Dal", "Immunity Boost"),
    ]
    north_veg_p2 = [
        ("Methi Paratha", "Fenugreek flatbread with curd.", "Palak Paneer & Roti", "Iron-rich spinach and cheese.", "Gond Laddoos & Milk", "Energy-dense resin sweets.", "Vegetable Daliya", "Fiber-rich cracked wheat.", "Methi, Wheat, Spinach, Paneer, Gond, Dry Fruits", "Lactation Support"),
        ("Besan Chilla", "Gram flour pancakes with ginger.", "Mixed Veg Khichdi", "Nutrient-dense mash.", "Panjiri & Herbal Tea", "Wheat and nut strength mix.", "Moong Dal & Spinach", "High protein and iron.", "Besan, Moong Dal, Spinach, Mixed Veggies, Panjiri", "Strength & Milk"),
    ]
    north_veg_p3 = [
        ("Mixed Sprouts", "Steamed moong and chana.", "Soya Chunk Curry & Rice", "Plant-based protein meal.", "Paneer Tikka (Mild)", "Grilled cottage cheese cubes.", "Seasonal Saag & Roti", "Mustard/Spinach greens.", "Sprouts, Soya Chunks, Rice, Paneer, Seasonal Greens", "Muscle Rebuilding"),
        ("Almond Milk Oats", "Oatmeal with almonds & honey.", "Paneer Curry & Rice", "Calcium-rich dinner.", "Roasted Peanuts", "Healthy fats and protein.", "Mixed Veg Sabzi & Roti", "Vitamins & fiber.", "Oats, Almonds, Paneer, Rice, Peanuts, Mixed Vegetables", "Active Recovery"),
    ]

    north_nonveg_p1 = [
        ("Ajwain Dalia", "Carom seed wheat porridge.", "Moong Dal Khichdi", "Mashed rice and lentils with ghee.", "Egg Drop Soup", "Light antiseptic protein broth.", "Lauki Soup", "Bottle gourd broth with cumin.", "Dalia, Ajwain, Moong Dal, Rice, Eggs, Lauki", "Healing & Digestion"),
        ("Garlic Wheat Mash", "Antiseptic garlic porridge.", "Dalia & Mashed Veggies", "Fiber-rich wheat and carrots.", "Turmeric Milk", "Warm milk with fresh haldi.", "Chicken Broth & Soft Roti", "Lean protein soup.", "Wheat, Garlic, Carrots, Milk, Turmeric, Chicken", "Immunity Boost"),
    ]
    north_nonveg_p2 = [
        ("Egg Paratha", "Flatbread stuffed with egg & herbs.", "Chicken Keema & Roti", "Lean chicken mince and wheat flatbread.", "Gond Laddoos & Milk", "Energy-dense resin sweets.", "Vegetable Daliya", "Fiber-rich cracked wheat.", "Eggs, Chicken, Wheat, Gond, Dry Fruits", "Lactation Support"),
        ("Besan Chilla", "Gram flour pancakes.", "Egg Khichdi", "Rice, lentils, and scrambled eggs.", "Panjiri & Herbal Tea", "Wheat and nut strength mix.", "Chicken Soup & Spinach", "High protein and iron.", "Besan, Eggs, Chicken, Rice, Panjiri", "Strength & Milk"),
    ]
    north_nonveg_p3 = [
        ("Egg Bhurji", "Scrambled eggs with onions.", "Chicken Stew & Roti", "Lean protein in mild gravy.", "Roasted Peanuts", "Healthy fats and protein.", "Fish Curry & Rice", "Omega-3 rich dinner.", "Eggs, Chicken, Wheat, Peanuts, Fish, Rice", "Active Recovery"),
        ("Chicken Keema Toast", "Minced chicken toast.", "Chicken Curry & Rice", "High protein dinner.", "Boiled Eggs", "Simple protein snack.", "Paneer Curry & Roti", "Calcium and protein.", "Chicken, Bread, Eggs, Paneer, Wheat", "Muscle Rebuilding"),
    ]

    # SOUTH INDIA & COASTAL RECIPES
    south_veg_p1 = [
        ("Methi Kanji", "Fenugreek red rice porridge.", "Garlic Rasam & Mash", "Antiseptic tamarind soup.", "Pepper Decoction", "Herbal immunity drink.", "Steamed Idli & Podi", "Probiotic rice cakes.", "Red Rice, Methi, Garlic, Tamarind, Pepper, Idli", "Womb Healing"),
        ("Ragi Malt", "Finger millet drink.", "Rice & Moringa Leaves", "Iron-rich drumstick greens.", "Steamed Banana", "Natural potassium boost.", "Curd Rice & Ginger", "Cooling and digestive.", "Ragi, Rice, Moringa, Banana, Curd, Ginger", "Digestive Health"),
    ]
    south_veg_p2 = [
        ("Idiyappam & Stew", "Rice noodles with veg stew.", "Sesame Rice & Dal", "Hormone-balancing fats.", "Moringa Leaf Soup", "Intense calcium boost.", "Garlic Milk & Rasam", "Lactation support.", "Rice Flour, Veggies, Sesame, Moringa, Garlic, Milk", "Lactation Power"),
        ("Puttu & Kadala", "Steamed rice cake with chickpeas.", "Paneer Roast & Red Rice", "Protein-rich coastal meal.", "Dry Ginger Coffee", "Pain-relieving herbal coffee.", "Mashed Rice & Ghee", "High energy lactation.", "Rice, Chickpeas, Paneer, Ginger, Jaggery", "Lactation Support"),
    ]
    south_veg_p3 = [
        ("Upma & Veggies", "Semolina with carrots/peas.", "Dal Tadka & Red Rice", "Lentil protein and rice.", "Peanut Sundal", "Steamed protein snack.", "Avial & Rice", "Full vitamin spectrum.", "Semolina, Lentils, Red Rice, Peanuts, Mixed Veggies", "Tissue Repair"),
        ("Ragi Dosa", "Finger millet crepes.", "Paneer Curry & Rice", "Calcium-rich meal.", "Dry Fruits & Milk", "Nutrient dense drink.", "Curd Rice & Fruits", "Gut health and vitamins.", "Ragi, Paneer, Rice, Dry Fruits, Curd", "Vitality & Gut"),
    ]

    south_nonveg_p1 = [
        ("Chicken Kanji", "Chicken and red rice porridge.", "Garlic Rasam & Mash", "Antiseptic tamarind soup.", "Pepper Decoction", "Herbal immunity drink.", "Egg Appam", "Soft rice pancakes with egg.", "Red Rice, Chicken, Garlic, Tamarind, Pepper, Eggs", "Womb Healing"),
        ("Ragi Malt", "Finger millet drink.", "Rice & Moringa Leaves", "Iron-rich drumstick greens.", "Steamed Banana", "Natural potassium boost.", "Curd Rice & Ginger", "Cooling and digestive.", "Ragi, Rice, Moringa, Banana, Curd, Ginger", "Digestive Health"),
    ]
    south_nonveg_p2 = [
        ("Idiyappam & Stew", "Rice noodles with veg stew.", "Sesame Rice & Dal", "Hormone-balancing fats.", "Moringa Leaf Soup", "Intense calcium boost.", "Garlic Milk & Rasam", "Lactation support.", "Rice Flour, Veggies, Sesame, Moringa, Garlic, Milk", "Lactation Power"),
        ("Puttu & Kadala", "Steamed rice cake with chickpeas.", "Fish Curry & Red Rice", "DHA-rich coastal meal.", "Dry Ginger Coffee", "Pain-relieving herbal coffee.", "Mashed Rice & Ghee", "High energy lactation.", "Rice, Chickpeas, Sardines, Ginger, Jaggery", "DHA & Strength"),
    ]
    south_nonveg_p3 = [
        ("Upma & Veggies", "Semolina with carrots/peas.", "Chicken Curry & Red Rice", "Lean protein and complex carbs.", "Boiled Egg & Tea", "Quick protein snack.", "Avial & Rice", "Full vitamin spectrum.", "Semolina, Chicken, Red Rice, Eggs, Mixed Veggies", "Tissue Repair"),
        ("Ragi Dosa", "Finger millet crepes.", "Prawn Roast & Rice", "Zinc and protein boost.", "Peanut Sundal", "Steamed protein snack.", "Curd Rice & Fruits", "Gut health and vitamins.", "Ragi, Prawns, Rice, Peanuts, Curd", "Vitality & Gut"),
    ]

    def populate_region(region_tag, diet_type, p1, p2, p3):
        for day in range(1, 41):
            if day <= 10:
                recipe = p1[(day-1) % len(p1)]
                phase = 1
            elif day <= 30:
                recipe = p2[(day-11) % len(p2)]
                phase = 2
            else:
                recipe = p3[(day-31) % len(p3)]
                phase = 3
            
            PostpartumDiet.objects.update_or_create(
                day_number=day, region_tag=region_tag, diet_type=diet_type,
                defaults={
                    'phase': phase,
                    'breakfast_name': recipe[0],
                    'breakfast_details': recipe[1],
                    'lunch_name': recipe[2],
                    'lunch_details': recipe[3],
                    'snack_name': recipe[4],
                    'snack_details': recipe[5],
                    'dinner_name': recipe[6],
                    'dinner_details': recipe[7],
                    'ingredients': recipe[8],
                    'benefits': recipe[9]
                }
            )

    # Execute populations
    for d_type, n_p1, n_p2, n_p3, s_p1, s_p2, s_p3 in [
        ('veg', north_veg_p1, north_veg_p2, north_veg_p3, south_veg_p1, south_veg_p2, south_veg_p3),
        ('non-veg', north_nonveg_p1, north_nonveg_p2, north_nonveg_p3, south_nonveg_p1, south_nonveg_p2, south_nonveg_p3)
    ]:
        populate_region('NORTH_INDIA', d_type, n_p1, n_p2, n_p3)
        populate_region('SOUTH_INDIA', d_type, s_p1, s_p2, s_p3)
        populate_region('COASTAL', d_type, s_p1, s_p2, s_p3)
        # Default others to North
        populate_region('WEST_INDIA', d_type, n_p1, n_p2, n_p3)
        populate_region('EAST_INDIA', d_type, n_p1, n_p2, n_p3)
        populate_region('CENTRAL_INDIA', d_type, n_p1, n_p2, n_p3)

    print("Successfully seeded Mother Diet and Recovery data!")
