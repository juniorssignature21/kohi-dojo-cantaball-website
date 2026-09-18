from django.db import migrations


def seed_country_slots(apps, schema_editor):
    CountrySlot = apps.get_model("app", "CountrySlot")
    from app.models import WORLD_CUP_2026_COUNTRIES

    for name in WORLD_CUP_2026_COUNTRIES:
        CountrySlot.objects.get_or_create(name=name, defaults={"capacity": 1, "is_active": True})


def unseed_country_slots(apps, schema_editor):
    CountrySlot = apps.get_model("app", "CountrySlot")
    from app.models import WORLD_CUP_2026_COUNTRIES

    CountrySlot.objects.filter(name__in=WORLD_CUP_2026_COUNTRIES, teams__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_countryslot_team_country"),
    ]

    operations = [
        migrations.RunPython(seed_country_slots, unseed_country_slots),
    ]
