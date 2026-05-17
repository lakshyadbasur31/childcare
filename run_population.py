import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'childcare_project.settings')
django.setup()

from health.logic.populate_data import populate_vaccines, populate_food_resources
from health.logic.populate_maternal import populate_maternal_data

print("Populating vaccines...")
populate_vaccines()
print("Populating food resources...")
populate_food_resources()
print("Populating maternal health data...")
populate_maternal_data()
print("Done!")
