from datetime import date
from django.utils import timezone

def get_exercise_guidance(mother):
    """
    Evaluates postpartum exercise suitability based on days since delivery and delivery type.
    Restricts activities to gentle rest/nutrition under 3 months (90 days).
    Allows walking/stretching after 3 months.
    Adds C-section warnings.
    """
    if not mother or not mother.delivery_date:
        return None
        
    today = timezone.now().date()
    days_since_delivery = (today - mother.delivery_date).days
    
    guidance = {
        'status': 'cleared',
        'recommendation': '',
        'warnings': [],
        'days_postpartum': days_since_delivery
    }
    
    if days_since_delivery < 90:
        guidance['status'] = 'restricted'
        guidance['recommendation'] = 'Gentle rest and focused nutrition are your priorities. Avoid strenuous physical activity.'
        if mother.delivery_type == 'c-section':
            guidance['warnings'].append('C-Section Recovery: Your incision needs complete rest. Do not lift anything heavier than your baby.')
        else:
            guidance['warnings'].append('Early Postpartum: Your pelvic floor and core need time to heal before starting any exercise regimen.')
    else:
        guidance['status'] = 'cleared'
        guidance['recommendation'] = 'You may begin gentle walking and light stretching. Gradually increase activity as tolerated.'
        if mother.delivery_type == 'c-section':
            guidance['warnings'].append('C-Section Precaution: Stop any exercise that causes pulling or pain near your incision site.')
            
    return guidance
