from .models import (
    Team,
    TeamPlayer,
    Season,
    LeagueWeek,
    Registration,
    Payment,
    Match,
    CountrySlot,
)

from django import forms

class TeamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'team_name': 'Enter your team name',
            'motto': 'One team. One shot.',
        }

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-input',
                'placeholder': placeholders.get(field_name, ''),
            })

        self.fields['team_colour'].widget.input_type = 'color'
        self.fields['logo'].widget.attrs.update({
            'accept': 'image/*',
            'class': '',
            'data-preview': 'logo-preview',
        })

        # Only show countries that are still open. When editing an existing
        # team, keep its already-selected country selectable too.
        available = CountrySlot.objects.filter(is_active=True)
        keep_ids = list(available.values_list('id', flat=True))
        if self.instance and self.instance.pk and self.instance.country_id:
            keep_ids.append(self.instance.country_id)
        self.fields['country'].queryset = CountrySlot.objects.filter(id__in=keep_ids)
        self.fields['country'].required = True
        self.fields['country'].empty_label = "Select a country"
        self.fields['country'].widget.attrs.update({
            'class': 'form-input',
        })
        self.fields['country'].label = "Country You Will Represent"

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country:
            raise forms.ValidationError("Please select the country you will represent.")

        already_taken = country.pk == getattr(self.instance, 'country_id', None)
        if not already_taken and not country.is_available():
            raise forms.ValidationError(
                f"{country.name} already has a representative. Please choose another country."
            )
        return country

    class Meta:
        model = Team
        fields = ['team_name', 'logo', 'team_colour', 'motto', 'country']
        

class TeamPlayerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        role_label = kwargs.pop('role_label', 'player')
        super().__init__(*args, **kwargs)
        placeholders = {
            'player_name': f'Full name of {role_label}',
            'phone': '+234 800 000 0000',
            'email': 'email@example.com',
        }

        for field_name, field in self.fields.items():
            if field_name == 'is_captain':
                continue

            field.widget.attrs.update({
                'class': 'form-input',
                'placeholder': placeholders.get(field_name, ''),
            })

    class Meta:
        model = TeamPlayer
        fields = ['player_name', 'phone', 'email', 'is_captain']


class RegisterForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ('week', 'team')
