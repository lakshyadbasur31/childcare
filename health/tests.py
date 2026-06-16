from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from health.models import User, ChildProfile, MotherProfile, OfflineActivity
from health.models import validate_child_age
from health.logic.age_rules import get_medically_safe_activities, is_infant_priority_mode
from health.recovery.exercise_progression import get_exercise_guidance
from health.translation.services.translation_service import TranslationService
from django.core.cache import cache

class ChildAgeValidationTests(TestCase):
    def test_future_dob(self):
        with self.assertRaises(ValidationError):
            validate_child_age(date.today() + timedelta(days=1))

    def test_over_13_years(self):
        with self.assertRaises(ValidationError):
            validate_child_age(date.today() - timedelta(days=15*365))

    def test_valid_age(self):
        try:
            validate_child_age(date.today() - timedelta(days=5*365))
        except ValidationError:
            self.fail("validate_child_age raised ValidationError unexpectedly!")

class ExerciseProgressionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testmom")
        self.mother = MotherProfile.objects.create(
            user=self.user,
            delivery_date=date.today() - timedelta(days=30), # 1 month postpartum
            delivery_type='c-section'
        )

    def test_restricted_exercise_under_90_days(self):
        guidance = get_exercise_guidance(self.mother)
        self.assertEqual(guidance['status'], 'restricted')
        self.assertTrue(any('C-Section' in w for w in guidance['warnings']))

    def test_cleared_exercise_over_90_days(self):
        self.mother.delivery_date = date.today() - timedelta(days=100)
        self.mother.save()
        guidance = get_exercise_guidance(self.mother)
        self.assertEqual(guidance['status'], 'cleared')

class TranslationServiceTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_translation_cache(self):
        text = "Hello"
        lang = "hi"
        # Pre-seed cache to avoid network call in tests
        cache_key = TranslationService.get_cache_key(text, lang)
        cache.set(cache_key, "Namaste", 3600)
        
        result = TranslationService.translate(text, lang)
        self.assertEqual(result, "Namaste")
        
    def test_english_no_translation(self):
        result = TranslationService.translate("Hello World", "en")
        self.assertEqual(result, "Hello World")

class AgeRulesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testparent")
        self.infant = ChildProfile.objects.create(
            parent=self.user,
            name="Infant",
            date_of_birth=date.today() - timedelta(days=60), # 2 months
            gender='M',
            current_weight=4.0,
            current_height=50.0
        )
        self.toddler = ChildProfile.objects.create(
            parent=self.user,
            name="Toddler",
            date_of_birth=date.today() - timedelta(days=400), # > 1 year
            gender='F',
            current_weight=10.0,
            current_height=80.0
        )
        
        OfflineActivity.objects.create(title="Sensory Play", description="Look at lights", age_tier="sensory", materials_needed="", developmental_benefit="")
        OfflineActivity.objects.create(title="Toddler Run", description="Run around", age_tier="toddler", materials_needed="", developmental_benefit="")

    def test_infant_priority_mode(self):
        self.assertTrue(is_infant_priority_mode(self.infant))
        self.assertFalse(is_infant_priority_mode(self.toddler))

    def test_medically_safe_activities_infant(self):
        activities = get_medically_safe_activities(self.infant)
        for act in activities:
            self.assertEqual(act.age_tier, 'sensory')
            
    def test_medically_safe_activities_toddler(self):
        activities = get_medically_safe_activities(self.toddler)
        for act in activities:
            self.assertEqual(act.age_tier, 'toddler')
