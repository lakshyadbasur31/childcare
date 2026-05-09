from django.db import models
from django.contrib.auth.models import AbstractUser, User as DjangoUser
from django.conf import settings

class User(AbstractUser):
    """
    Custom User model to distinguish between Parents and Vaccination Admins.
    """
    is_parent = models.BooleanField(default=False)
    is_vaccination_admin = models.BooleanField(default=False)
    locality = models.ForeignKey('Locality', on_delete=models.SET_NULL, null=True, blank=True)

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

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

# Re-link existing models to the new User model

class Locality(models.Model):
    """
    Represents a geographic area and its regional characteristics
    to drive locality-specific resource filtering.
    """
    REGION_CHOICES = [
        ('coastal', 'Coastal Region'),
        ('northern_rural', 'Northern Rural Belt'),
        ('southern_plain', 'Southern Plain'),
        ('hilly_terrain', 'Hilly Terrain'),
    ]
    name = models.CharField(max_length=100)
    region_type = models.CharField(max_length=50, choices=REGION_CHOICES)
    
    def __str__(self):
        return f"{self.name} ({self.get_region_type_display()})"
    
    class Meta:
        verbose_name_plural = "Localities"

class ChildProfile(models.Model):
    """
    Core profile for children aged 0-6 years.
    """
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='children', null=True)
    name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    locality = models.ForeignKey(Locality, on_delete=models.SET_NULL, null=True)
    
    # Biometric tracking
    current_weight = models.FloatField(help_text="Weight in kg")
    current_height = models.FloatField(help_text="Height in cm")
    
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
