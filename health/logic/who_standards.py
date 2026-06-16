import math

# Simplified WHO Weight-for-Age Data (kg) for Boys (0-60 months)
WHO_WEIGHT_BOYS = {
    0: {'p3': 2.5, 'p15': 2.9, 'p50': 3.3, 'p85': 3.9, 'p97': 4.4},
    1: {'p3': 3.4, 'p15': 3.9, 'p50': 4.5, 'p85': 5.1, 'p97': 5.8},
    2: {'p3': 4.3, 'p15': 4.9, 'p50': 5.6, 'p85': 6.3, 'p97': 7.1},
    3: {'p3': 5.0, 'p15': 5.7, 'p50': 6.4, 'p85': 7.2, 'p97': 8.0},
    4: {'p3': 5.6, 'p15': 6.2, 'p50': 7.0, 'p85': 7.8, 'p97': 8.7},
    5: {'p3': 6.0, 'p15': 6.7, 'p50': 7.5, 'p85': 8.4, 'p97': 9.3},
    6: {'p3': 6.4, 'p15': 7.1, 'p50': 7.9, 'p85': 8.8, 'p97': 9.8},
    9: {'p3': 7.1, 'p15': 8.0, 'p50': 8.9, 'p85': 9.9, 'p97': 11.0},
    12: {'p3': 7.7, 'p15': 8.6, 'p50': 9.6, 'p85': 10.8, 'p97': 12.0},
    18: {'p3': 8.8, 'p15': 9.8, 'p50': 10.9, 'p85': 12.2, 'p97': 13.7},
    24: {'p3': 9.7, 'p15': 10.8, 'p50': 12.2, 'p85': 13.6, 'p97': 15.3},
    36: {'p3': 11.3, 'p15': 12.7, 'p50': 14.3, 'p85': 16.2, 'p97': 18.3},
    48: {'p3': 12.7, 'p15': 14.3, 'p50': 16.3, 'p85': 18.6, 'p97': 21.2},
    60: {'p3': 14.1, 'p15': 16.0, 'p50': 18.3, 'p85': 21.0, 'p97': 24.2},
}

# Simplified WHO Weight-for-Age Data (kg) for Girls (0-60 months)
WHO_WEIGHT_GIRLS = {
    0: {'p3': 2.4, 'p15': 2.8, 'p50': 3.2, 'p85': 3.7, 'p97': 4.2},
    1: {'p3': 3.2, 'p15': 3.6, 'p50': 4.2, 'p85': 4.8, 'p97': 5.5},
    2: {'p3': 3.9, 'p15': 4.5, 'p50': 5.1, 'p85': 5.8, 'p97': 6.6},
    3: {'p3': 4.5, 'p15': 5.2, 'p50': 5.8, 'p85': 6.6, 'p97': 7.5},
    4: {'p3': 5.0, 'p15': 5.7, 'p50': 6.4, 'p85': 7.3, 'p97': 8.2},
    5: {'p3': 5.4, 'p15': 6.1, 'p50': 6.9, 'p85': 7.8, 'p97': 8.8},
    6: {'p3': 5.7, 'p15': 6.5, 'p50': 7.3, 'p85': 8.2, 'p97': 9.3},
    9: {'p3': 6.5, 'p15': 7.3, 'p50': 8.2, 'p85': 9.3, 'p97': 10.4},
    12: {'p3': 7.0, 'p15': 7.9, 'p50': 8.9, 'p85': 10.1, 'p97': 11.5},
    18: {'p3': 8.1, 'p15': 9.2, 'p50': 10.2, 'p85': 11.6, 'p97': 13.2},
    24: {'p3': 9.0, 'p15': 10.2, 'p50': 11.5, 'p85': 13.0, 'p97': 14.8},
    36: {'p3': 10.8, 'p15': 12.2, 'p50': 13.9, 'p85': 15.8, 'p97': 18.1},
    48: {'p3': 12.3, 'p15': 14.0, 'p50': 16.1, 'p85': 18.5, 'p97': 21.5},
    60: {'p3': 13.7, 'p15': 15.8, 'p50': 18.2, 'p85': 21.2, 'p97': 24.9},
}

def interpolate_dict(d1, d2, fraction):
    """Interpolates between two dictionaries of percentiles based on a fraction (0.0 to 1.0)."""
    return {k: round(d1[k] + (d2[k] - d1[k]) * fraction, 2) for k in d1}

def get_who_percentiles(gender, age_in_days):
    """
    Returns interpolated WHO weight percentiles for a specific gender and age.
    """
    age_months = min(max(age_in_days / 30.4375, 0), 60)
    dataset = WHO_WEIGHT_BOYS if gender == 'M' else WHO_WEIGHT_GIRLS
    
    # Extract sorted keys
    keys = sorted(dataset.keys())
    
    # If exactly matches a key or exceeds max
    if age_months in dataset:
        return dataset[age_months]
    if age_months >= keys[-1]:
        return dataset[keys[-1]]
        
    # Find bounding months
    lower_month = 0
    upper_month = 1
    for i in range(len(keys) - 1):
        if keys[i] <= age_months < keys[i+1]:
            lower_month = keys[i]
            upper_month = keys[i+1]
            break
            
    fraction = (age_months - lower_month) / (upper_month - lower_month)
    return interpolate_dict(dataset[lower_month], dataset[upper_month], fraction)
