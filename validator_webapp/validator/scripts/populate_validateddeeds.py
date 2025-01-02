import os
import django
import sys

# Setting up the Django environment
project_path = '/home/gerhard/programming/python/wic-opvarenden/webapp'
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
django.setup()

# Importing models
from validator.models import Deed, ValidatedDeed

# Script logic
def populate_validateddeeds():
    # Update validation_complete for deeds from 1638
    Deed.objects.filter(deed_date__year=1638).update(validation_complete=True)

    # Create entries in ValidatedDeed only if final_name is not empty
    for deed in Deed.objects.filter(validation_complete=True, deed_date__year=1638):
        if deed.final_name:  # Checks if final_name is not empty
            ValidatedDeed.objects.create(
                deed_uri=deed.deed_uri,
                deed_date=deed.deed_date,
                name=deed.final_name,
                location=deed.final_location,
                ship_name=deed.final_ship_name,
                role=deed.final_role,
                organization=deed.final_organization,
                captain=deed.final_captain,
                chamber=deed.final_chamber,
                shiptype=deed.final_shiptype,
                remarks=deed.final_remarks,
                sailor_uri=deed.sailor_uri,
                location_uri=deed.location_uri
            )

if __name__ == "__main__":
    populate_validateddeeds()
