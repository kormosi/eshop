import re
from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "postal_code",
            "country",
        ]

    def clean_postal_code(self):
        postal_code = self.cleaned_data["postal_code"]
        if not re.fullmatch(r"\d{3}\s?\d{2}", postal_code):
            raise forms.ValidationError("Enter a valid postal code (format: 123 45).")
        return postal_code

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not re.fullmatch(r"[0-9+ ]{6,}", phone):
            raise forms.ValidationError("Enter a valid phone number, e.g. +421 919 123 456.")
        return phone

    def clean_country(self):
        country = self.cleaned_data["country"]
        if country not in ("SK", "CZ"):
            raise forms.ValidationError("Unsupported country.")
        return country
