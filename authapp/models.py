import secrets
import string

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
ROLE_CHOICES = (
    ('PLAYER', 'Player'),
    ('ADMIN', 'Admin')
)


def generate_referral_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    is_marketer = models.BooleanField(default=False)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='PLAYER')
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.username and self.email:
            self.username = self.email.split('@')[0]

        if not self.referral_code and self.is_marketer:
            code = generate_referral_code()
            while User.objects.filter(referral_code=code).exclude(pk=self.pk).exists():
                code = generate_referral_code()
            self.referral_code = code

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
    
