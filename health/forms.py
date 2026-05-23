from django import forms
from .models import ChildProfile, GrowthRecord, MotherProfile, RecoveryMetric

class ChildProfileForm(forms.ModelForm):
    mother_name = forms.CharField(max_length=150, required=True, label="Mother's Name", help_text="Required to link or create maternal profile.")
    mother_delivery_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True, label="Delivery Date", help_text="Used to configure 40-day postpartum diet.")
    mother_password = forms.CharField(widget=forms.PasswordInput, required=True, label="Create Mother's Password", help_text="Password for the new account.")
    mother_phone_number = forms.CharField(max_length=15, required=False, label="Phone Number", help_text="For receiving translated SMS alerts.")

    class Meta:
        model = ChildProfile
        fields = ['mother_name', 'mother_delivery_date', 'name', 'date_of_birth', 'gender', 'locality', 'current_weight', 'weight_unit', 'current_height', 'height_unit']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class GrowthRecordForm(forms.ModelForm):
    class Meta:
        model = GrowthRecord
        fields = ['weight', 'height']

class MotherProfileForm(forms.ModelForm):
    class Meta:
        model = MotherProfile
        fields = ['delivery_date', 'delivery_type', 'diet_preference', 'allergies', 'current_weight', 'weight_unit', 'pantry_items']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'allergies': forms.TextInput(attrs={'placeholder': 'e.g., peanuts, dairy, gluten'}),
            'pantry_items': forms.Textarea(attrs={'placeholder': 'e.g., Rice, Dal, Apples (Comma separated)', 'rows': 2}),
        }

class RecoveryMetricForm(forms.ModelForm):
    SYMPTOM_CHOICES = [
        ('fever', 'High Fever'),
        ('heavy_bleeding', 'Heavy Bleeding'),
        ('severe_headache', 'Severe Headache'),
        ('vision_blurring', 'Vision Blurring'),
        ('pain', 'Severe Abdominal Pain'),
    ]
    symptoms = forms.MultipleChoiceField(choices=SYMPTOM_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    
    class Meta:
        model = RecoveryMetric
        fields = ['weight', 'systolic_bp', 'diastolic_bp', 'symptoms']
