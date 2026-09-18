import datetime
from decimal import Decimal

from django.db import migrations
from django.utils import timezone


def seed_osisioma_relaunch(apps, schema_editor):
    Event = apps.get_model("store", "Event")
    EventTicket = apps.get_model("store", "EventTicket")

    # Retire whatever event was active before (e.g. the old Demo Day / event
    # night placeholder) without deleting its historical orders.
    Event.objects.filter(is_active=True).update(is_active=False)

    start_date = timezone.make_aware(datetime.datetime(2026, 9, 26, 10, 0))

    event, _ = Event.objects.update_or_create(
        name="Osisioma Relaunch",
        defaults={
            "description": (
                "Osisioma Relaunch is the Kohi Dojo relaunch and creative community "
                "experience — the activation point for the From Sketch to Scene "
                "animation workshop and the Cantaball World Cup. Grab a combo pass, "
                "share your referral code, and join us on 26 September 2026."
            ),
            "start_date": start_date,
            "is_active": True,
        },
    )

    tickets = (
        {
            "name": "1k Pass",
            "price": Decimal("1000.00"),
            "tier": "REGULAR",
            "combo_description": "1 bun and 1 small coffee",
            "image_static": "images/tickets/combo-1k.png",
            "is_purchasable": True,
            "stock": 500,
        },
        {
            "name": "1500 Pass",
            "price": Decimal("1500.00"),
            "tier": "REGULAR",
            "combo_description": "1 sandwich and 1 small coffee",
            "image_static": "images/tickets/combo-1500.png",
            "is_purchasable": True,
            "stock": 500,
        },
        {
            "name": "2000 Pass",
            "price": Decimal("2000.00"),
            "tier": "REGULAR",
            "combo_description": "1 sandwich and 1 big coffee",
            "image_static": "images/tickets/combo-2000.png",
            "is_purchasable": True,
            "stock": 500,
        },
        {
            "name": "VIP Pass",
            "price": Decimal("0.00"),
            "tier": "VIP",
            "combo_description": "VIP access - awarded via referral (bring 10+ people)",
            "image_static": "images/tickets/combo-2000.png",
            "is_purchasable": False,
            "stock": 100,
        },
    )

    for spec in tickets:
        name = spec["name"]
        defaults = {k: v for k, v in spec.items() if k != "name"}
        EventTicket.objects.update_or_create(event=event, name=name, defaults=defaults)


def unseed_osisioma_relaunch(apps, schema_editor):
    # Left as a no-op: reversing would risk detaching real ticket orders
    # from their event.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0013_workshopregistration_eventorder_attendee_name_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_osisioma_relaunch, unseed_osisioma_relaunch),
    ]
