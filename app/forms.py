from .models import (
    Team, 
    TeamPlayer,
    Season,
    LeagueWeek,
    Registration,
    Payment,
    Match                  
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

    class Meta:
        model = Team
        fields = ['team_name', 'logo', 'team_colour', 'motto']
        

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
