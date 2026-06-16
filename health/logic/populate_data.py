from health.models import Vaccine, Locality, LocalFoodResource

def populate_vaccines():
    nis_vaccines = [
        # Birth
        ("BCG", "Bacillus Calmette-Guerin (Tuberculosis)", 0, "0.1ml/0.05ml Intra-dermal",
         "The foundation of immunity against TB, crucial for newborns in India.",
         "High risk of severe Tuberculosis and brain infections (Meningitis)."),
        ("HepB Birth", "Hepatitis B Birth dose", 0, "0.5ml Intra-muscular",
         "Prevents mother-to-child transmission of Hepatitis B.",
         "Risk of chronic liver disease and liver cancer later in life."),
        ("OPV 0", "Oral Polio Vaccine Birth dose", 0, "2 drops Oral",
         "First step in the journey to a Polio-free life.",
         "Vulnerability to Polio virus which causes irreversible paralysis."),
        
        # 6-14 Weeks
        ("Pentavalent 1", "DPT + HepB + Hib 1st dose", 6, "0.5ml Intra-muscular",
         "Shields against 5 deadly diseases including Diphtheria and Tetanus.",
         "Risk of Whooping Cough, Tetanus, and severe Pneumonia."),
        ("Rotavirus 1", "Rotavirus Vaccine 1st dose", 6, "5 drops Oral",
         "Protects against severe diarrhea, the leading cause of infant hospitalization.",
         "Severe dehydration due to uncontrollable diarrhea."),
        ("PCV 1", "Pneumococcal Conjugate Vaccine 1st dose", 6, "0.5ml Intra-muscular",
         "A powerful defense against Pneumonia and ear infections.",
         "Risk of severe Pneumonia and permanent hearing loss from ear infections."),
        
        # 9-12 Months
        ("MR 1", "Measles & Rubella 1st dose", 39, "0.5ml Subcutaneous",
         "Prevents Measles outbreaks which can lead to blindness.",
         "Risk of Measles, blindness, and severe lung infections."),
        ("PCV Booster", "Pneumococcal Conjugate Vaccine Booster", 39, "0.5ml Intra-muscular",
         "Reinforces the child's defense against respiratory bacteria.",
         "Vulnerability to recurring respiratory infections."),
        
        # Boosters (16-24 Months)
        ("DPT Booster 1", "DPT Booster 1st dose", 69, "0.5ml Intra-muscular",
         "Critical booster to maintain Diphtheria and Tetanus immunity.",
         "Waning immunity leads to high risk of lockjaw (Tetanus) and respiratory distress."),
        
        # 5-6 Years
        ("DPT Booster 2", "DPT Booster 2nd dose", 260, "0.5ml Intra-muscular",
         "Strengthens immunity as the child starts school and interacts with more people.",
         "Increased risk of Whooping Cough outbreaks in school environments."),
         
        # Pre-Teen (10-11 Years)
        ("Tdap", "Tetanus, Diphtheria, & Acellular Pertussis", 520, "0.5ml Intra-muscular",
         "A vital booster for pre-teens to prevent whooping cough transmission to infants.",
         "Risk of severe cough and respiratory failure."),
        ("HPV 1", "Human Papillomavirus Vaccine 1st dose", 520, "0.5ml Intra-muscular",
         "A breakthrough vaccine that prevents certain types of cancers later in life.",
         "Increased risk of cervical and other cancers in adulthood."),
        ("HPV 2", "Human Papillomavirus Vaccine 2nd dose", 546, "0.5ml Intra-muscular",
         "Completes the primary series for long-term cancer protection.",
         "Incomplete immunity against high-risk virus strains.")
    ]

    for name, desc, weeks, dosage, why, cons in nis_vaccines:
        Vaccine.objects.update_or_create(
            name=name,
            defaults={
                'description': desc,
                'recommended_age_weeks': weeks,
                'dosage_info': dosage,
                'why_it_matters': why,
                'consequence_text': cons
            }
        )

def populate_food_resources():
    # Create Localities with regional mapping
    coastal_ker, _ = Locality.objects.update_or_create(
        name="Kerala Coastal", 
        defaults={"district": "Alappuzha", "state": "Kerala", "region_tag": "COASTAL"}
    )
    north_punjab, _ = Locality.objects.update_or_create(
        name="Punjab Rural", 
        defaults={"district": "Amritsar", "state": "Punjab", "region_tag": "NORTH_INDIA"}
    )
    south_tn, _ = Locality.objects.update_or_create(
        name="Tamil Nadu Plain", 
        defaults={"district": "Madurai", "state": "Tamil Nadu", "region_tag": "SOUTH_INDIA"}
    )
    west_raj, _ = Locality.objects.update_or_create(
        name="Jodhpur Tehsil", 
        defaults={"district": "Jodhpur", "state": "Rajasthan", "region_tag": "WEST_INDIA"}
    )
    south_kar, _ = Locality.objects.update_or_create(
        name="Karnataka", 
        defaults={"district": "Mysuru", "state": "Karnataka", "region_tag": "SOUTH_INDIA"}
    )

    foods = [
        # Coastal (South)
        ("Coconut Milk", "fat", [coastal_ker], 2.0, "Medium", "Essential fat source for coastal infants.", True, True),
        ("Sardines", "protein", [coastal_ker], 25.0, "High", "Rich in DHA for brain development.", True, False),
        ("Brown Rice (Matta)", "carbs", [coastal_ker, south_tn], 7.0, "Vitamin B", "Regional staple with high fiber.", True, True),
        
        # North India
        ("Bajra (Pearl Millet)", "millet", [north_punjab, west_raj], 11.0, "Iron, Zinc", "High energy winter staple.", True, True),
        ("Whole Wheat (Atta)", "carbs", [north_punjab], 12.0, "Fiber, B6", "Primary energy source in the North.", True, True),
        ("Sarson (Mustard Greens)", "greens", [north_punjab], 3.0, "Vitamin A, C", "Traditional seasonal superfood.", True, False),
        ("Paneer (Local)", "protein", [north_punjab], 18.0, "Calcium", "High quality local protein.", False, False),
        
        # South India
        ("Ragi (Finger Millet)", "millet", [south_tn, coastal_ker, south_kar], 7.0, "Calcium, Iron", "Best weaning food for strong bones.", True, True),
        ("Drumstick Leaves", "greens", [south_tn, coastal_ker, south_kar], 9.0, "Vitamin A, Iron", "Drought-resistant superfood.", True, False),
        ("Jaggery", "carbs", [south_tn, south_kar], 0.5, "Iron", "Natural iron-rich sweetener.", True, False),
        
        # West India (Arid)
        ("Moong Dal", "protein", [west_raj, north_punjab], 24.0, "Easy protein", "Versatile and easy to digest.", True, True),
        ("Kair-Sangri", "greens", [west_raj], 5.0, "Minerals", "Desert superfood with unique nutrients.", True, False),
        ("Jowar (Sorghum)", "millet", [west_raj], 10.0, "Copper, Magnesium", "Gluten-free regional grain.", True, True),
        
        # East India (Plains)
        ("Hilsa / Local Fish", "protein", [], 20.0, "Omega-3", "High-quality protein for brain growth.", False, False),
        ("Puffed Rice (Muri)", "carbs", [], 6.0, "Light", "Easy to digest regional snack.", True, True),
        ("Sweet Potato", "carbs", [], 1.6, "Beta-Carotene", "Rich in vitamins for eye health.", True, True),
    ]

    for name, cat, locs, prot, vit, desc, low_cost, comp in foods:
        food, _ = LocalFoodResource.objects.update_or_create(
            name=name,
            defaults={
                'category': cat,
                'protein_content': prot,
                'vitamin_content': vit,
                'nutritional_description': desc,
                'is_low_cost': low_cost,
                'is_complementary_base': comp
            }
        )
        food.localities.set(locs)
