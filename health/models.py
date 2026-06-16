from django.db import models
from django.contrib.auth.models import AbstractUser, User as DjangoUser
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date

def validate_child_age(value):
    today = date.today()
    if value > today:
        raise ValidationError("Date of birth cannot be in the future.")
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age > 13:
        raise ValidationError("Child age cannot exceed 13 years.")

class User(AbstractUser):
    """
    Custom User model to distinguish between Parents and Vaccination Admins.
    """
    is_parent = models.BooleanField(default=False)
    is_vaccination_admin = models.BooleanField(default=False)
    locality = models.ForeignKey('Locality', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Added per blueprint specification
    location_district = models.CharField(max_length=100, blank=True)
    password_hash = models.CharField(max_length=255, blank=True)
    
    # Custom fields for notification and language support
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('kn', 'Kannada'),
            ('hi', 'Hindi'),
            ('te', 'Telugu'),
            ('ta', 'Tamil')
        ],
        default='en'
    )


class Notification(models.Model):
    """
    Automated alerts for parents regarding upcoming or overdue vaccinations.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False, help_text="Triggers Red Alert badge")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Trigger SMS if it's a newly created notification
        if is_new:
            import threading
            from health.services.sms_service import SMSService
            
            # Run in a separate thread so we don't block the web request while hitting translation APIs
            threading.Thread(
                target=SMSService.send_alert, 
                args=(self.user, f"BHG Alert: {self.title} - {self.message}")
            ).start()

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

class Locality(models.Model):
    """
    Represents a geographic area and its regional characteristics
    to drive locality-specific resource filtering.
    """
    REGION_CHOICES = [
        ('NORTH_INDIA', 'North India (Plains/Hills)'),
        ('SOUTH_INDIA', 'South India (Peninsular)'),
        ('WEST_INDIA', 'West India (Arid/Coastal)'),
        ('EAST_INDIA', 'East India (Plains)'),
        ('CENTRAL_INDIA', 'Central India (Plateau)'),
        ('COASTAL', 'Coastal Belt'),
    ]
    name = models.CharField(max_length=100, help_text="Village/Tehsil Name")
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    region_tag = models.CharField(max_length=50, choices=REGION_CHOICES, default='NORTH_INDIA')
    
    # GPS Coordinates for Auto-Detection
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_region_tag_display()})"
    
    class Meta:
        verbose_name_plural = "Localities"

class MotherProfile(models.Model):
    """
    Profile for mothers tracking postpartum recovery.
    """
    DELIVERY_CHOICES = [('normal', 'Normal Delivery'), ('c-section', 'C-Section')]
    DIET_CHOICES = [('veg', 'Vegetarian'), ('non-veg', 'Non-Vegetarian')]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mother_profile')
    delivery_date = models.DateField()
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    diet_preference = models.CharField(max_length=20, choices=DIET_CHOICES, default='veg')
    allergies = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of allergies (e.g., peanuts, dairy)")
    
    # Biometrics
    current_weight = models.FloatField(null=True, blank=True, help_text="Stored in KG")
    weight_unit = models.CharField(max_length=5, choices=[('kg', 'kg'), ('g', 'g')], default='kg')
    
    # Health Flags for Red Alert System
    last_systolic_bp = models.IntegerField(null=True, blank=True)
    last_diastolic_bp = models.IntegerField(null=True, blank=True)
    
    # Blueprint appended fields
    bp_reading = models.CharField(max_length=50, blank=True, help_text="Historical string format BP e.g. 120/80")
    symptoms_log = models.TextField(blank=True, help_text="Raw symptom entry log")
    postpartum_day = models.IntegerField(null=True, blank=True, help_text="Explicit tracked day of recovery")
    epds_score = models.IntegerField(null=True, blank=True, help_text="Edinburgh Postnatal Depression Scale score")
    pantry_items = models.TextField(blank=True, help_text="Comma-separated list of items available at home for the shopping list")
    postpartum_metadata = models.JSONField(default=dict, blank=True)
    priority_mode_metadata = models.JSONField(default=dict, blank=True)
    
    # Onboarding and Relationship State
    onboarding_completed = models.BooleanField(default=False, help_text="Flags if the mother finished the 4-step onboarding")
    relationship_metadata = models.JSONField(default=dict, blank=True, help_text="Stores hierarchy mapping and linkage rules")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mother: {self.user.username}"

class PostpartumDiet(models.Model):
    """
    Regional 40-day recovery meal plans for mothers.
    """
    day_number = models.IntegerField(help_text="Day 1 to 40 of recovery")
    phase = models.IntegerField(choices=[(1, 'Phase 1: Healing'), (2, 'Phase 2: Lactation'), (3, 'Phase 3: Strength')])
    region_tag = models.CharField(max_length=50, choices=Locality.REGION_CHOICES)
    diet_type = models.CharField(max_length=20, choices=[('veg', 'Vegetarian'), ('non-veg', 'Non-Vegetarian')], default='veg')
    
    # Breakfast
    breakfast_name = models.CharField(max_length=200)
    breakfast_details = models.TextField()
    
    # Lunch
    lunch_name = models.CharField(max_length=200)
    lunch_details = models.TextField()
    
    # Evening Snack
    snack_name = models.CharField(max_length=200)
    snack_details = models.TextField()
    
    # Dinner
    dinner_name = models.CharField(max_length=200)
    dinner_details = models.TextField()
    
    ingredients = models.TextField(help_text="Consolidated market items for the day")
    benefits = models.TextField()

    def __str__(self):
        return f"Day {self.day_number} ({self.region_tag}) Plan"

class RecoveryMetric(models.Model):
    """
    Daily health tracking for the Red Flag system.
    """
    mother = models.ForeignKey(MotherProfile, on_delete=models.CASCADE, related_name='metrics')
    weight = models.FloatField(null=True, blank=True)
    systolic_bp = models.IntegerField(null=True, blank=True)
    diastolic_bp = models.IntegerField(null=True, blank=True)
    symptoms = models.JSONField(default=list, help_text="List of symptoms like ['fever', 'bleeding']")
    recorded_at = models.DateTimeField(auto_now_add=True)

class PostpartumCareGuide(models.Model):
    """
    The Healing Journey roadmap and exercises.
    """
    week_number = models.IntegerField()
    title = models.CharField(max_length=100)
    care_instructions = models.TextField()
    exercise_title = models.CharField(max_length=100)
    exercise_desc = models.TextField()
    mental_health_tip = models.TextField()

    def __str__(self):
        return f"Week {self.week_number}: {self.title}"

# Re-link existing models to the new User model

# Re-link existing models to the new User model

class ChildProfile(models.Model):
    """
    Core profile for children aged 0-6 years.
    """
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='children', null=True)
    name = models.CharField(max_length=200)
    date_of_birth = models.DateField(validators=[validate_child_age])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    locality = models.ForeignKey(Locality, on_delete=models.SET_NULL, null=True)
    
    # Biometric tracking
    current_weight = models.FloatField(help_text="Weight (Stored in KG)")
    current_height = models.FloatField(help_text="Height (Stored in CM)")
    birth_weight = models.FloatField(null=True, blank=True, help_text="Birth Weight (Stored in KG)")
    
    # Unit preferences
    height_unit = models.CharField(max_length=5, choices=[('cm', 'cm'), ('m', 'm')], default='cm')
    weight_unit = models.CharField(max_length=5, choices=[('kg', 'kg'), ('g', 'g')], default='kg')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.date_of_birth})"

class GrowthRecord(models.Model):
    """
    Periodic biometric tracking for growth monitoring.
    """
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='growth_records')
    weight = models.FloatField(help_text="Weight in kg")
    height = models.FloatField(help_text="Height in cm")
    head_cm = models.FloatField(null=True, blank=True, help_text="Head Circumference in cm")
    recorded_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['recorded_at']
        
    def __str__(self):
        return f"{self.child.name} - {self.recorded_at}"

class Vaccine(models.Model):
    """
    Master list of vaccines based on India National Immunization Schedule (NIS).
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    recommended_age_weeks = models.IntegerField(help_text="Recommended age in weeks from birth")
    dosage_info = models.CharField(max_length=100, blank=True)
    
    # Mentor Data
    why_it_matters = models.TextField(blank=True, help_text="Educational insight for parents")
    consequence_text = models.TextField(blank=True, help_text="Specific risk if missed (e.g., Paralysis)")
    
    def __str__(self):
        return self.name

class VaccinationSchedule(models.Model):
    """
    Personalized schedule for a specific child.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    due_date = models.DateField()
    administered_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Blueprint appended fields
    given_date = models.DateField(null=True, blank=True, help_text="Explicit blueprint alias for administered_date")
    vaccine_name = models.CharField(max_length=100, blank=True, help_text="Denormalized name for blueprint matching")

    def __str__(self):
        return f"{self.vaccine.name} for {self.child.name}"

class LocalFoodResource(models.Model):
    """
    Nutritional database filtered by locality.
    """
    CATEGORY_CHOICES = [
        ('protein', 'Protein-Rich'),
        ('vitamin', 'Vitamin-Rich'),
        ('mineral', 'Mineral-Rich'),
        ('carbs', 'Carbohydrates'),
        ('fat', 'Healthy Fats'),
        ('millet', 'Millets/Grains'),
        ('greens', 'Seasonal Greens'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    localities = models.ManyToManyField(Locality, related_name='available_foods')
    
    # Nutritional density per 100g
    protein_content = models.FloatField(default=0.0)
    vitamin_content = models.TextField(blank=True, help_text="List of vitamins provided")
    mineral_content = models.TextField(blank=True, help_text="List of minerals provided")
    nutritional_description = models.TextField(blank=True)
    
    is_low_cost = models.BooleanField(default=True)
    is_complementary_base = models.BooleanField(default=False, help_text="Suitable for transition from breastfeeding")

    def __str__(self):
        return self.name

class NutritionRecommendation(models.Model):
    """
    AI-generated nutritional plans.
    """
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='recommendations')
    recommended_foods = models.ManyToManyField(LocalFoodResource)
    
    nutritional_gap_addressed = models.TextField(help_text="Gaps in protein, vitamins, or minerals identified")
    logic_summary = models.TextField(help_text="Explanation of locality-based logic used")
    seven_day_plan = models.JSONField(null=True, blank=True, help_text="Generated 7-day meal plan")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Review workflow
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_plans',
        limit_choices_to={'is_vaccination_admin': True}
    )
    review_comments = models.TextField(blank=True)

    def __str__(self):
        return f"AI Recommendation for {self.child.name} ({self.created_at.date()})"

class Achievement(models.Model):
    """
    Story-driven milestones representing the child's journey.
    """
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=100, help_text='e.g., "Shield of BCG"')
    story_text = models.TextField(help_text='e.g., "The hero is now protected against the invisible cough."')
    is_unlocked = models.BooleanField(default=False)
    date_unlocked = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} for {self.child.name}"

class OfflineActivity(models.Model):
    """
    Daily-refreshing 100% offline activities for brain development.
    """
    AGE_TIERS = [
        ('infant', 'Infant (0-2y)'),
        ('early', 'Early Childhood (3-6y)'),
        ('preteen', 'Pre-Teen (7-11y)'),
        ('sensory', 'Sensory/Tracking (<6m)'),
        ('grasping', 'Object Permanence (6-12m)'),
        ('toddler', 'Toddler/Sorting (1-3y)'),
        ('preschool', 'Pre-schooler/Modeling (3-6y)'),
        ('school', 'School Support/Logic (6-11y)'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    age_tier = models.CharField(max_length=20, choices=AGE_TIERS)
    materials_needed = models.TextField(help_text="Common household items in rural India")
    developmental_benefit = models.TextField()
    risk_if_missed = models.TextField(blank=True, help_text="Developmental risk alert")
    
    def __str__(self):
        return f"{self.title} ({self.get_age_tier_display()})"

class BedtimeStory(models.Model):
    """
    Personalized Hero stories integrated with locality data.
    """
    title = models.CharField(max_length=200)
    template_text = models.TextField(help_text="Use [Name] and [Locality] as placeholders")
    region_tag = models.CharField(max_length=50, choices=Locality.REGION_CHOICES)
    moral_lesson = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title

class ActivityCompletion(models.Model):
    """
    Tracks completed offline activities for the Memory Page.
    """
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='completions')
    activity = models.ForeignKey(OfflineActivity, on_delete=models.CASCADE)
    completed_at = models.DateField(auto_now_add=True)
    parent_note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.child.name} completed {self.activity.title}"

class NutritionLog(models.Model):
    """
    Blueprint Required Model: Logs daily nutrition entries.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='nutrition_logs')
    date = models.DateField(auto_now_add=True)
    meal_type = models.CharField(max_length=50)
    food_items = models.TextField()
    iron_score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Nutrition Log for {self.user.username} on {self.date}"

class MotherExerciseMoodLog(models.Model):
    """
    Blueprint Required Model: Daily tracking of exercise and mood for mothers.
    """
    MOOD_CHOICES = [
        ('great', 'Great - Energized and Positive'),
        ('good', 'Good - Stable and Calm'),
        ('tired', 'Tired - Needs rest'),
        ('overwhelmed', 'Overwhelmed - Needing support'),
    ]
    mother = models.ForeignKey(MotherProfile, on_delete=models.CASCADE, related_name='mood_logs')
    date = models.DateField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default='good')
    exercise_done = models.BooleanField(default=False, help_text="Did the mother complete her daily exercise/walk?")
    affirmation_done = models.BooleanField(default=False, help_text="Did the mother complete her daily affirmation?")
    notes = models.TextField(blank=True, help_text="Optional journal entry")

    class Meta:
        unique_together = ('mother', 'date')
        
    def __str__(self):
        return f"{self.mother.user.username} - {self.date} - {self.get_mood_display()}"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Notification)
def send_notification_sms(sender, instance, created, **kwargs):
    if created and instance.user and instance.user.phone_number:
        from health.notifications.services.messaging_service import dispatch_sms_async
        message = f"{instance.title}: {instance.message}"
        dispatch_sms_async(instance.user.phone_number, message)

