from django import forms
from .models import Deed

class DeedVerificationForm(forms.ModelForm):
    class Meta:
        model = Deed
        fields = ['final_name', 'final_location', 'final_role', 'final_organization', 'final_ship_name', 'final_captain', 'final_chamber', 'final_shiptype', 'final_remarks']
