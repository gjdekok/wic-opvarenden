import os
import django
import sys
import csv
import pickle

# Setting up the Django environment
project_path = '/home/gerhard/programming/python/wic-opvarenden/webapp'
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
django.setup()

# Importing models
from validator.models import Deed

with open('validator/scripts/organizations.pickle', 'rb') as handle:
    organizations = pickle.load(handle)

with open('validator/scripts/ship_roles.pickle', 'rb') as handle:
    ship_roles = pickle.load(handle)

def set_suggested_field(row, field_name, field_name_htr):
    if row[field_name]:
        return row[field_name]
    else:
        return row[field_name_htr]
    
def update_database_from_csv(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Get the deed by URI
                deed = Deed.objects.get(deed_uri=row['deed_uri'])

                # Update fields for both validated and non-validated deeds
                deed.creditor_name = row['creditor_name']
                deed.debt_amount = row['debt_amount']
                deed.creditor_uri = row['creditor_uri']
                deed.suggested_creditor_name = row['creditor_name'] 
                deed.suggested_debt_amount = row['debt_amount']
                deed.final_creditor_name = row['creditor_name']
                deed.final_debt_amount = row['debt_amount']

                # Additional updates for non-validated deeds
                if not deed.validation_complete:
                    normal_role = set_suggested_field(row, 'role', 'role_htr')
                    if normal_role in ship_roles:
                        normal_role = ship_roles[normal_role]

                    normal_org = set_suggested_field(row, 'organization', 'organization_htr')
                    if normal_org in organizations:
                        normal_org = organizations[normal_org]

                    deed.name = row['name']
                    deed.location = row['location']
                    deed.role = row['role']
                    deed.organization = row['organization']
                    deed.ship_name = row['ship_name']
                    deed.location_htr = row['location_htr']
                    deed.role_htr = row['role_htr']
                    deed.organization_htr = row['organization_htr']
                    deed.ship_name_htr = row['ship_name_htr']
                    deed.sailor_uri = row['sailor_uri']
                    deed.location_uri = row['location_uri']
                    deed.interesting_text = row['interesting_text']
                    deed.interesting_text_after = row['interesting_text_after']
                    deed.possible_names = row['possible_names']
                    deed.possible_locations = row['possible_locations']
                    deed.subject = row['subject']
                    deed.text = row['text']
                    deed.full_coords = row['full_coords']
                    deed.dimensions = row['dimensions']

                    # Set suggestions (and save them separately so user can revert to them if needed)
                    deed.suggested_name=row['name']
                    deed.suggested_location=set_suggested_field(row, 'location', 'location_htr')
                    deed.suggested_role=normal_role
                    deed.suggested_organization=normal_org
                    deed.suggested_ship_name=set_suggested_field(row, 'ship_name', 'ship_name_htr')
                    deed.suggested_creditor_name=row['creditor_name']
                    deed.suggested_debt_amount=row['debt_amount']
                    
                    # For now, set final fields to the same as suggested fields (user may change these)
                    deed.final_name=row['name']
                    deed.final_location=set_suggested_field(row, 'location', 'location_htr')
                    deed.final_role=normal_role
                    deed.final_organization=normal_org
                    deed.final_ship_name=set_suggested_field(row, 'ship_name', 'ship_name_htr')
                    deed.final_creditor_name=row['creditor_name']
                    deed.final_debt_amount=row['debt_amount']

                deed.save()

            except Deed.DoesNotExist:
                print(f"Deed with URI {row['deed_uri']} not found in database.")
            except KeyError as e:
                print(f"Column {e} missing in CSV.")

if __name__ == "__main__":
    csv_file_path = '../notebooks/sailors-20231025-162347.csv'  
    update_database_from_csv(csv_file_path)
