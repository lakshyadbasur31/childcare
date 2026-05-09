from health.models import Vaccine

def populate_vaccines():
    nis_vaccines = [
        # Birth
        ("BCG", "Bacillus Calmette-Guerin (Tuberculosis)", 0, "0.1ml/0.05ml Intra-dermal"),
        ("HepB Birth", "Hepatitis B Birth dose", 0, "0.5ml Intra-muscular"),
        ("OPV 0", "Oral Polio Vaccine Birth dose", 0, "2 drops Oral"),
        
        # 6 Weeks
        ("Pentavalent 1", "DPT + HepB + Hib 1st dose", 6, "0.5ml Intra-muscular"),
        ("OPV 1", "Oral Polio Vaccine 1st dose", 6, "2 drops Oral"),
        ("Rotavirus 1", "Rotavirus Vaccine 1st dose", 6, "5 drops Oral"),
        ("fIPV 1", "Fractional Inactivated Polio Vaccine 1st dose", 6, "0.1ml Intra-dermal"),
        ("PCV 1", "Pneumococcal Conjugate Vaccine 1st dose", 6, "0.5ml Intra-muscular"),
        
        # 10 Weeks
        ("Pentavalent 2", "DPT + HepB + Hib 2nd dose", 10, "0.5ml Intra-muscular"),
        ("OPV 2", "Oral Polio Vaccine 2nd dose", 10, "2 drops Oral"),
        ("Rotavirus 2", "Rotavirus Vaccine 2nd dose", 10, "5 drops Oral"),
        
        # 14 Weeks
        ("Pentavalent 3", "DPT + HepB + Hib 3rd dose", 14, "0.5ml Intra-muscular"),
        ("OPV 3", "Oral Polio Vaccine 3rd dose", 14, "2 drops Oral"),
        ("Rotavirus 3", "Rotavirus Vaccine 3rd dose", 14, "5 drops Oral"),
        ("fIPV 2", "Fractional Inactivated Polio Vaccine 2nd dose", 14, "0.1ml Intra-dermal"),
        ("PCV 2", "Pneumococcal Conjugate Vaccine 2nd dose", 14, "0.5ml Intra-muscular"),
        
        # 9-12 Months (Approx 39-52 weeks)
        ("MR 1", "Measles & Rubella 1st dose", 39, "0.5ml Subcutaneous"),
        ("Vitamin A 1", "Vitamin A 1st dose", 39, "1ml Oral"),
        ("PCV Booster", "Pneumococcal Conjugate Vaccine Booster", 39, "0.5ml Intra-muscular"),
        
        # 16-24 Months (Approx 69-104 weeks)
        ("MR 2", "Measles & Rubella 2nd dose", 69, "0.5ml Subcutaneous"),
        ("DPT Booster 1", "DPT Booster 1st dose", 69, "0.5ml Intra-muscular"),
        ("OPV Booster", "Oral Polio Vaccine Booster", 69, "2 drops Oral"),
        
        # 5-6 Years (Approx 260-312 weeks)
        ("DPT Booster 2", "DPT Booster 2nd dose", 260, "0.5ml Intra-muscular"),
    ]

    for name, desc, weeks, dosage in nis_vaccines:
        Vaccine.objects.get_or_create(
            name=name,
            defaults={
                'description': desc,
                'recommended_age_weeks': weeks,
                'dosage_info': dosage
            }
        )

def populate_food_resources():
    from health.models import Locality, LocalFoodResource
    
    # Create Localities if they don't exist
    coastal, _ = Locality.objects.get_or_create(name="Kerala Coastal", region_type="coastal")
    north_rural, _ = Locality.objects.get_or_create(name="Punjab Rural", region_type="northern_rural")
    south_plain, _ = Locality.objects.get_or_create(name="Tamil Nadu Plain", region_type="southern_plain")

    foods = [
        # Coastal Foods
        ("Coconut Milk", "fat", [coastal], 2.0, "Medium", "Fat source for infants", True, True),
        ("Sardines", "protein", [coastal], 25.0, "High", "DHA and Protein", True, False),
        ("Brown Rice (Matta)", "carbs", [coastal, south_plain], 7.0, "Vitamin B", "Energy source", True, True),
        
        # North Rural Foods
        ("Bajra (Pearl Millet)", "millet", [north_rural], 11.0, "Iron, Zinc", "High energy millet", True, True),
        ("Sarson (Mustard Greens)", "greens", [north_rural], 3.0, "Vitamin A, C", "Seasonal greens", True, False),
        ("Paneer (Local)", "protein", [north_rural], 18.0, "Calcium", "Growth support", False, False),
        
        # General/South Foods
        ("Ragi (Finger Millet)", "millet", [south_plain, coastal, north_rural], 7.0, "Calcium, Iron", "Best for weaning", True, True),
        ("Moong Dal", "protein", [south_plain, north_rural], 24.0, "Easy protein", "Complementary feeding base", True, True),
        ("Drumstick Leaves", "greens", [south_plain, coastal], 9.0, "Vitamin A, Iron", "Superfood", True, False),
    ]

    for name, cat, locs, prot, vit, desc, low_cost, comp in foods:
        food, _ = LocalFoodResource.objects.get_or_create(
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
