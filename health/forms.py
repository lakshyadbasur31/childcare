from django import forms
from .models import ChildProfile, GrowthRecord

class ChildProfileForm(forms.ModelForm):
    class Meta:
        model = ChildProfile
        fields = ['name', 'date_of_birth', 'gender', 'locality', 'current_weight', 'current_height']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class GrowthRecordForm(forms.ModelForm):
    class Meta:
        model = GrowthRecord
        fields = ['weight', 'height']
