from django import forms
from django.core.exceptions import ValidationError

def validate_password(value):
    length_ok = len(value) >= 9 and len(value) <= 40
    number = 0
    lcase = 0
    ucase = 0
    symbol = 0
    for c in value:
        if c.isdigit():
            number += 1
        elif c.islower():
            lcase += 1
        elif c.isupper():
            ucase += 1
        elif not c.isalpha():
            symbol += 1
    if length_ok and number > 0 and lcase > 0 and ucase > 0 and symbol > 0:
        return True
    else:
        raise ValidationError("Choose a password that conforms with the stated requirements.")

class FinishRegistrationForm(forms.Form):
    email = forms.EmailField(label="Email address", help_text="Please provide a valid email address for service annoucements.", required=False)
    password = forms.CharField(label="Trading password", help_text="Your chosen password must consist of at least 9 characters including 1 number, 1 lowercase character, 1 uppercase character, and 1 symbol.", widget=forms.PasswordInput, validators=[validate_password])