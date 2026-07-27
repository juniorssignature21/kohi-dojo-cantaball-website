from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "role", "referral_code", "is_staff", "date_joined")
    list_filter = ("role", "is_staff", "is_superuser")
    search_fields = ("email", "username", "referral_code")
    readonly_fields = ("referral_code",)
