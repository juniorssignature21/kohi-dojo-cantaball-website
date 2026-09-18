from django.utils import timezone

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Countries that qualified for the 2026 FIFA World Cup — used for Cantaball
# World Cup's "Country You Will Represent" selection.
WORLD_CUP_2026_COUNTRIES = [
    "Algeria", "Argentina", "Australia", "Austria", "Belgium",
    "Bosnia and Herzegovina", "Brazil", "Cabo Verde", "Canada", "Colombia",
    "Congo DR", "Croatia", "Curaçao", "Côte d'Ivoire", "Czechia",
    "Ecuador", "Egypt", "England", "France", "Germany", "Ghana", "Haiti",
    "IR Iran", "Iraq", "Japan", "Jordan", "Korea Republic", "Mexico",
    "Morocco", "Netherlands", "New Zealand", "Norway", "Panama",
    "Paraguay", "Portugal", "Qatar", "Saudi Arabia", "Scotland",
    "Senegal", "South Africa", "Spain", "Sweden", "Switzerland",
    "Tunisia", "Türkiye", "United States", "Uruguay", "Uzbekistan",
]


class CountrySlot(models.Model):
    """
    One slot per 2026 World Cup-qualified country a Cantaball World Cup
    participant can represent. Capacity defaults to 1 (one representative
    per country) but stays admin-editable.
    """

    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to manually close this country even if capacity remains.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def taken_count(self):
        return self.teams.count()

    def is_available(self):
        return self.is_active and self.taken_count() < self.capacity


# Create your models here.
class Season(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    

class LeagueWeek(models.Model):

    STATUS = (
        ("OPEN", "Open"),
        ("FULL", "Full"),
        ("CLOSED", "Closed"),
    )

    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="weeks"
    )

    week_number = models.PositiveIntegerField()

    registration_open = models.DateTimeField()

    registration_close = models.DateTimeField()

    max_teams = models.PositiveIntegerField(default=20)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="OPEN"
    )

    def registered_count(self):
        return self.registrations.filter(
            payment__status="SUCCESS"
        ).count()
        
        
class Team(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    
    team_name = models.CharField(max_length=100)

    team_colour = models.CharField(max_length=7, default="#FFFFFF")
    
    motto = models.CharField(max_length=255, blank=True, null=True)

    logo = models.ImageField(
        upload_to="logos/",
        blank=True,
        null=True
    )

    country = models.ForeignKey(
        CountrySlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teams",
        help_text="Country this team represents in the Cantaball World Cup.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    

class TeamPlayer(models.Model):

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="players"
    )

    player_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)

    email = models.EmailField(blank=True)

    is_captain = models.BooleanField(default=False)
    

class Registration(models.Model):

    STATUS = (
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    )

    week = models.ForeignKey(
        LeagueWeek,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("week", "team")
        
        
class Payment(models.Model):

    STATUS = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE
    )

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5000
    )

    reference = models.CharField(
        max_length=150,
        unique=True
    )

    gateway = models.CharField(max_length=30)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="PENDING"
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    def save(self, *args, **kwargs):
        if not self.paid_at:
            self.paid_at = timezone.now()
            
        super().save(*args, **kwargs)
    
    
class Match(models.Model):

    week = models.ForeignKey(
        LeagueWeek,
        on_delete=models.CASCADE
    )

    team1 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="team1"
    )

    team2 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="team2"
    )

    team1_score = models.IntegerField(default=0)

    team2_score = models.IntegerField(default=0)

    winner = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="wins"
    )
    
    played = models.BooleanField(default=False)
    

    played_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    