# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User
from django.core.exceptions import ValidationError
import re

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']

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
        email =self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")   
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Password strength validation
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character.")

        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return confirm_password
    
    def clean_phone_number(self):
       phone_number = self.cleaned_data.get('phone_number')

    # Ensure phone number is not empty
       if not phone_number:
        raise ValidationError("Phone number is required.")
    
    # Remove spaces and special characters for validation
       cleaned_phone_number = ''.join(filter(str.isdigit, phone_number))
    
    # Length validation
       if len(cleaned_phone_number) != 10:
        raise ValidationError("Phone number must be exactly 10 digits.")
    
    # Ensure phone number is not all zeros
       if cleaned_phone_number == "0000000000":
        raise ValidationError("Phone number cannot be all zeros.")
    
       return cleaned_phone_number


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                "This account is inactive. Please contact support.",
            )
        