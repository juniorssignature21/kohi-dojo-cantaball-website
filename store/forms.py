from django import forms

from .models import Product, Category, WorkshopRegistration


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={"class": "form-control frontdesk-category-select"}),
    )

    class Meta:
        model = Product
        fields = ["name", "description", "image", "price", "category", "stock"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
        }


class WorkshopRegistrationForm(forms.ModelForm):
    class Meta:
        model = WorkshopRegistration
        fields = [
            "parent_name",
            "parent_phone",
            "parent_email",
            "student_name",
            "student_age",
            "pricing_tier",
            "interested_in_fellowship",
            "school_code",
        ]
        widgets = {
            "parent_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
            "parent_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+234 800 000 0000"}),
            "parent_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com"}),
            "student_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Student's full name"}),
            "student_age": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 25}),
            "pricing_tier": forms.Select(attrs={"class": "form-control"}),
            "interested_in_fellowship": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "school_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. FSS-SCHOOL01 (optional)"}),
        }
        labels = {
            "interested_in_fellowship": "I'm interested in the 1-year Fellowship pathway",
            "school_code": "School / Referral code",
        }
