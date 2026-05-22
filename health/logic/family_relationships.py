from health.models import ChildProfile

class FamilyRelationships:
    @staticmethod
    def get_mother_children(mother_profile):
        """
        Safely fetches a mother's children, ensuring no orphaned records exist.
        The mother_profile.user is the parent of the ChildProfile.
        """
        if not mother_profile or not mother_profile.user:
            return ChildProfile.objects.none()
            
        return ChildProfile.objects.filter(parent=mother_profile.user).order_by('-created_at')
        
    @staticmethod
    def validate_parent_link(child, user):
        """
        Ensures a child is validly linked to a parent user.
        """
        return child.parent == user
