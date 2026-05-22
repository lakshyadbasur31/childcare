from health.models import ChildProfile
from datetime import datetime

class ChildService:
    @staticmethod
    def create_child_profile(data, parent_user, locality_id=None):
        """
        Creates a ChildProfile linked to the given parent_user.
        Ensures age validation and duplicate prevention.
        """
        child_name = data.get('child_name')
        child_date_of_birth = data.get('child_date_of_birth')
        child_gender = data.get('child_gender')
        child_weight = data.get('child_weight')
        child_height = data.get('child_height')

        if not child_name or not child_date_of_birth:
            raise ValueError("Child name and date of birth are required.")
            
        if isinstance(child_date_of_birth, str) and child_date_of_birth:
            child_date_of_birth = datetime.strptime(child_date_of_birth, '%Y-%m-%d').date()

        # Duplicate Prevention: Check if child with same name and DOB exists for this parent
        if ChildProfile.objects.filter(parent=parent_user, name=child_name, date_of_birth=child_date_of_birth).exists():
            raise ValueError(f"Child profile for {child_name} already exists.")

        child = ChildProfile.objects.create(
            parent=parent_user,
            name=child_name,
            date_of_birth=child_date_of_birth,
            gender=child_gender,
            current_weight=float(child_weight),
            current_height=float(child_height),
            locality_id=int(locality_id) if locality_id else None
        )
        return child
