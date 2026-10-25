import datetime
from decimal import Decimal

from django.db import migrations, models
from django.utils import timezone


PASS_SPECS = (
    ("Explorer Pass", "EXPLORER", "0.00"),
    ("Community Pass", "COMMUNITY", "1000.00"),
    ("Creator Pass", "CREATOR", "2000.00"),
    ("Couple Pass", "COUPLE", "3000.00"),
    ("Family Pass", "FAMILY", "5000.00"),
    ("VVIP Pass", "VVIP", "10000.00"),
)


def update_next_frame(apps, schema_editor):
    Event = apps.get_model("store", "Event")
    EventTicket = apps.get_model("store", "EventTicket")
    event = Event.objects.filter(name="The Next Frame 2026", is_active=True).order_by("-created_at").first()
    if not event:
        event = Event.objects.filter(is_active=True).order_by("-created_at").first()
    if not event:
        return

    event.name = "The Next Frame 2026"
    event.description = (
        "Kohi Dojo × NueLuks Studio present The Next Frame at El Dorado, Aba on "
        "Saturday, 31 October 2026. A day for art, animation and community. "
        "Registered pass holders may request a free place in a short Cantaball "
        "mini-tournament, subject to available slots."
    )
    event.start_date = timezone.make_aware(datetime.datetime(2026, 10, 31))
    event.save(update_fields=["name", "description", "start_date"])

    neutral_description = "Pass inclusions are being finalised by the organisers."
    for name, tier, price in PASS_SPECS:
        EventTicket.objects.update_or_create(
            event=event,
            name=name,
            defaults={
                "tier": tier,
                "price": Decimal(price),
                "combo_description": neutral_description,
                "is_purchasable": True,
            },
        )
    # Retire outdated tiers from sale while retaining their historical orders.
    EventTicket.objects.filter(event=event).exclude(name__in=[item[0] for item in PASS_SPECS]).update(is_purchasable=False)


class Migration(migrations.Migration):
    dependencies = [("store", "0018_seed_next_frame_2026_passes")]

    operations = [
        migrations.AlterField(
            model_name="eventticket",
            name="tier",
            field=models.CharField(
                choices=[
                    ("REGULAR", "Regular"),
                    ("VIP", "VIP"),
                    ("EXPLORER", "Explorer"),
                    ("COMMUNITY", "Community"),
                    ("CREATOR", "Creator"),
                    ("COUPLE", "Couple"),
                    ("FAMILY", "Family"),
                    ("VVIP", "VVIP"),
                ],
                default="REGULAR",
                max_length=20,
            ),
        ),
        migrations.RunPython(update_next_frame, migrations.RunPython.noop),
    ]
