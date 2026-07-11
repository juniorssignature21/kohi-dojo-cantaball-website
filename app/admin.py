from django.contrib import admin
from .models import (
    Team, 
    TeamPlayer,
    Season,
    LeagueWeek,
    Registration,
    Payment,
    Match                  
)

# Register your models here.
admin.site.register(Team)
admin.site.register(TeamPlayer)
admin.site.register(Season)
admin.site.register(LeagueWeek)
admin.site.register(Registration)
admin.site.register(Payment)
admin.site.register(Match)
