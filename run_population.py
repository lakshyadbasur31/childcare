import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'childcare_project.settings')
django.setup()

from health.models import Locality, User, Vaccine, LocalFoodResource
from health.logic.populate_data import populate_vaccines, populate_food_resources

def create_test_users():
    print("Creating test users...")
    # Locality for admin
    loc, _ = Locality.objects.get_or_create(name="District Health HQ", region_type="southern_plain")
    
    # Admin
    if not User.objects.filter(username="admin_test").exists():
        admin = User.objects.create_user("admin_test", "admin@test.com", "pass123")
        admin.is_vaccination_admin = True
        admin.locality = loc
        admin.save()
        print("- Created Admin: admin_test / pass123")
    
    # Parent
    if not User.objects.filter(username="parent_test").exists():
        parent = User.objects.create_user("parent_test", "parent@test.com", "pass123")
        parent.is_parent = True
        parent.save()
        print("- Created Parent: parent_test / pass123")

if __name__ == "__main__":
    print("Populating Vaccines...")
    populate_vaccines()
    print("Populating Food Resources and Localities...")
    populate_food_resources()
    create_test_users()
    print("Population complete.")
