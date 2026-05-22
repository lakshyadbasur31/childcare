from django.test import TestCase
from health.models import User, MotherProfile, ChildProfile
from health.services.onboarding_service import OnboardingService
from health.logic.onboarding_logic import OnboardingLogic

class OnboardingServiceTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'testmother',
            'password': 'password123',
            'delivery_date': '2023-01-01',
            'delivery_type': 'normal',
            'child_name': 'Test Baby',
            'child_date_of_birth': '2023-01-05',
            'child_gender': 'F',
            'child_weight': '3.5',
            'child_height': '50',
        }

    def test_successful_onboarding(self):
        user = OnboardingService.process_onboarding(self.valid_data)
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testmother')
        self.assertTrue(hasattr(user, 'mother_profile'))
        self.assertTrue(OnboardingLogic.is_onboarding_complete(user.mother_profile))
        
        child = ChildProfile.objects.filter(parent=user).first()
        self.assertIsNotNone(child)
        self.assertEqual(child.name, 'Test Baby')

    def test_rollback_on_child_error(self):
        invalid_data = self.valid_data.copy()
        invalid_data['child_date_of_birth'] = None # Missing DOB should raise ValueError

        with self.assertRaises(ValueError):
            OnboardingService.process_onboarding(invalid_data)

        # Ensure Mother was NOT created (rollback successful)
        self.assertFalse(User.objects.filter(username='testmother').exists())
        self.assertFalse(MotherProfile.objects.exists())

    def test_duplicate_child_prevention(self):
        # First onboarding
        user = OnboardingService.process_onboarding(self.valid_data)
        self.assertIsNotNone(user)
        
        # Second attempt to add same child manually to trigger duplicate
        from health.services.child_service import ChildService
        with self.assertRaises(ValueError):
            ChildService.create_child_profile(self.valid_data, user)
