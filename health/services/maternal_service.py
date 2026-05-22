from health.models import User, MotherProfile

class MaternalService:
    @staticmethod
    def create_user_and_mother_profile(data):
        """
        Creates a User (Parent) and their corresponding MotherProfile.
        Returns a tuple of (user, mother_profile).
        Expects data dict containing user and mother fields.
        """
        username = data.get('username')
        password = data.get('password')
        phone_number = data.get('phone_number')
        preferred_language = data.get('preferred_language', 'en')
        locality_id = data.get('locality')

        # 1. Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            preferred_language=preferred_language,
            is_parent=True
        )
        if locality_id:
            user.locality_id = int(locality_id)
            user.save()

        # 2. Create MotherProfile
        delivery_date = data.get('delivery_date')
        if isinstance(delivery_date, str) and delivery_date:
            from datetime import datetime
            delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
            
        delivery_type = data.get('delivery_type')
        diet_preference = data.get('diet_preference', 'veg')
        allergies = data.get('allergies', '')
        mother_weight = data.get('mother_weight')
        pantry_items = data.get('pantry_items', '')

        mother = MotherProfile.objects.create(
            user=user,
            delivery_date=delivery_date,
            delivery_type=delivery_type,
            diet_preference=diet_preference,
            allergies=allergies,
            current_weight=float(mother_weight) if mother_weight else None,
            pantry_items=pantry_items
        )

        return user, mother
