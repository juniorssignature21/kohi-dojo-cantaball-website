from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'Choose a username',
            'email': 'you@example.com',
            'password1': 'Create a password',
            'password2': 'Confirm your password',
        }

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-input',
                'placeholder': placeholders.get(field_name, ''),
            })

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

