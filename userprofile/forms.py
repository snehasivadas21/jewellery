from django import forms
from django.core.exceptions import ValidationError
from .models import User ,UserAddress
import re


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = [
            'name', 'house_name', 'street_name', 'pin_number', 
            'district', 'state', 'country', 'phone_number', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'house_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'street_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'pin_number': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_pin_number(self):
        pin_number = self.cleaned_data.get('pin_number')
        if len(str(pin_number)) != 6:
            raise ValidationError("Pin number must be 6 digits long.")
        return pin_number

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and len(phone_number) < 10 or len(phone_number) > 15:
            raise ValidationError("Phone number must be between 10 to 15 digits.")
        if not phone_number.isdigit():
            raise ValidationError("Phone number must contain only digits.")
        return phone_number

    def clean_name(self):
        name = self.cleaned_data.get('name')
    # Regex: ^[A-Za-z]+$ ensures the name contains only letters
        if not re.match(r'^[A-Za-z\s]+$', name):
          raise ValidationError("Name should only contain letters and spaces.")
        return name

    def clean_district(self):
        district = self.cleaned_data.get('district')
        if not re.match(r'^[A-Za-z]+$', district):
            raise ValidationError("District should only contain letters.")
        return district

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not re.match(r'^[A-Za-z]+$', state):
            raise ValidationError("State should only contain letters.")
        return state

    def save(self, commit=True):
        if self.cleaned_data.get('status'):
            UserAddress.objects.filter(user=self.instance.user, status=True).update(status=False)

        return super().save(commit=commit)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True 

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()

        # Check length constraints
        if len(first_name) < 2 or len(first_name) > 50:
            raise forms.ValidationError("First name must be between 2 and 50 characters.")

        # Check for valid characters
        if not re.match(r"^[a-zA-Z0-9_.]+$", first_name):
            raise forms.ValidationError(
                "First name can only contain letters, numbers, underscores, and periods. Spaces are not allowed."
            )

        # Prevent numeric-only names
        if first_name.isdigit():
            raise forms.ValidationError("First name cannot be numeric-only.")

        # Disallow leading/trailing underscores or periods
        if first_name.startswith(('_', '.')) or first_name.endswith(('_', '.')):
            raise forms.ValidationError("First name cannot start or end with an underscore or period.")

        # Prevent consecutive underscores or periods
        if "__" in first_name or ".." in first_name or "._" in first_name or "._" in first_name:
            raise forms.ValidationError("First name cannot contain consecutive underscores or periods.")

        # Normalize casing
        return first_name.title()  # Capitalizes the first letter of each word

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()

        # Apply the same validation as for first name
        if len(last_name) < 2 or len(last_name) > 50:
            raise forms.ValidationError("Last name must be between 2 and 50 characters.")

        if not re.match(r"^[a-zA-Z0-9_.]+$", last_name):
            raise forms.ValidationError(
                "Last name can only contain letters, numbers, underscores, and periods. Spaces are not allowed."
            )

        if last_name.isdigit():
            raise forms.ValidationError("Last name cannot be numeric-only.")

        if last_name.startswith(('_', '.')) or last_name.endswith(('_', '.')):
            raise forms.ValidationError("Last name cannot start or end with an underscore or period.")

        if "__" in last_name or ".." in last_name or "._" in last_name or "._" in last_name:
            raise forms.ValidationError("Last name cannot contain consecutive underscores or periods.")

        return last_name.title()  # Normalize casing
    
    
    def clean_email(self):
        return self.instance.email
    
    def clean_phone_number(self):
       phone_number = self.cleaned_data.get('phone_number')

    # Ensure phone number is not empty
       if not phone_number:
        raise ValidationError("Phone number is required.")
    
    # Remove spaces and special characters for validation
       cleaned_phone_number = ''.join(filter(str.isdigit, phone_number))
    
    # Length validation
       if len(cleaned_phone_number) != 11:
        raise ValidationError("Phone number must be exactly 10 digits.")
    
    # Ensure phone number is not all zeros
       if cleaned_phone_number == "0000000000":
        raise ValidationError("Phone number cannot be all zeros.")
    
       return cleaned_phone_number
    
    

class OrderActionForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, required=True, label="Reason for action")