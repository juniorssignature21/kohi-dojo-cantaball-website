from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
ROLE_CHOICES = (
    ('PLAYER', 'Player'),
    ('ADMIN', 'Admin')
)
class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='PLAYER')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
            
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.email
    
