from django.contrib import admin
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

# Register your models here.
class TeamPlayerInline(admin.TabularInline):
    model = TeamPlayer
    extra = 0


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("team_name", "country", "user", "created_at")
    list_filter = ("country",)
    search_fields = ("team_name", "user__username", "user__email", "country__name")
    inlines = [TeamPlayerInline]


@admin.register(CountrySlot)
class CountrySlotAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "taken_display", "is_available", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("capacity", "is_active")

    def taken_display(self, obj):
        return f"{obj.taken_count()}/{obj.capacity}"
    taken_display.short_description = "Taken"


admin.site.register(TeamPlayer)
admin.site.register(Season)
admin.site.register(LeagueWeek)
admin.site.register(Registration)
admin.site.register(Payment)
admin.site.register(Match)
