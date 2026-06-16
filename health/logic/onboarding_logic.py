class OnboardingLogic:
    @staticmethod
    def mark_onboarding_complete(mother_profile):
        """
        Marks the mother's onboarding as completed.
        """
        if mother_profile and not mother_profile.onboarding_completed:
            mother_profile.onboarding_completed = True
            mother_profile.save(update_fields=['onboarding_completed'])

    @staticmethod
    def is_onboarding_complete(mother_profile):
        """
        Checks if the mother's onboarding is complete.
        """
        return mother_profile.onboarding_completed if mother_profile else False
