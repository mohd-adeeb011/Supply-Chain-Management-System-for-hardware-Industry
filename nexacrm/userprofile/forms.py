from django import forms
from django.contrib.auth.models import User
from .models import Userprofile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Userprofile
        fields = ['name', 'shop', 'contact', 'location', 'business_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initially set the shop field as required
        self.fields['shop'].required = False