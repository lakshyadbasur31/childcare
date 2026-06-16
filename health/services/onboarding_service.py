from django.db import transaction
from health.services.maternal_service import MaternalService
from health.services.child_service import ChildService
from health.logic.vaccination_initializer import VaccinationInitializer
from health.logic.onboarding_logic import OnboardingLogic

class OnboardingService:
    @staticmethod
    def process_onboarding(data):
        """
        Orchestrates the entire onboarding flow safely within a transaction.
        Returns the created User object if successful.
        Raises ValueError or RuntimeError on failure, safely rolling back.
        """
        with transaction.atomic():
            # 1 & 2: Mother & Account registration
            user, mother = MaternalService.create_user_and_mother_profile(data)

            # 3: Child registration (if child data is provided)
            child_name = data.get('child_name')
            if child_name:
                child = ChildService.create_child_profile(data, user, data.get('locality'))
                
                # 4: Initialize Vaccination Schedule & Nutrition
                VaccinationInitializer.initialize_for_child(child)
            
            # Mark onboarding as complete
            OnboardingLogic.mark_onboarding_complete(mother)
            
            return user
