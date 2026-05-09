from datetime import timedelta
from health.models import Vaccine, VaccinationSchedule

def generate_schedule(child):
    """
    Generates a personalized vaccination schedule for a child
    based on their date of birth and the NIS.
    """
    vaccines = Vaccine.objects.all()
    schedules = []
    
    for vaccine in vaccines:
        due_date = child.date_of_birth + timedelta(weeks=vaccine.recommended_age_weeks)
        
        # Check if schedule already exists to avoid duplicates
        schedule, created = VaccinationSchedule.objects.get_or_create(
            child=child,
            vaccine=vaccine,
            defaults={'due_date': due_date}
        )
        if created:
            schedules.append(schedule)
            
    return schedules
