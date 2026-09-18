from django.db import migrations


def seed_school_codes(apps, schema_editor):
    SchoolCode = apps.get_model("store", "SchoolCode")

    for n in range(1, 11):
        code = f"FSS-SCHOOL{n:02d}"
        SchoolCode.objects.get_or_create(
            code=code,
            defaults={"school_name": f"Partner School {n}", "is_active": True},
        )


def unseed_school_codes(apps, schema_editor):
    SchoolCode = apps.get_model("store", "SchoolCode")
    codes = [f"FSS-SCHOOL{n:02d}" for n in range(1, 11)]
    SchoolCode.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0015_schoolcode"),
    ]

    operations = [
        migrations.RunPython(seed_school_codes, unseed_school_codes),
    ]
