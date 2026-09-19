import datetime
from decimal import Decimal

from django.db import migrations
from django.utils import timezone


OLD_TICKET_NAMES = ["1k Pass", "1500 Pass", "2000 Pass", "VIP Pass"]

NEW_TICKETS = (
    {
        "name": "Explorer Pass",
        "price": Decimal("0.00"),
        "tier": "EXPLORER",
        "combo_description": "Come Explore! Free entry, introductory access, and more.",
        "image_static": "images/tickets/next-frame-explorer.jpg",
        "is_purchasable": True,
        "stock": 1000,
    },
    {
        "name": "Community Pass",
        "price": Decimal("1000.00"),
        "tier": "COMMUNITY",
        "combo_description": "Come Play! Games, Kohi Village, selected experiences.",
        "image_static": "images/tickets/next-frame-community.jpg",
        "is_purchasable": True,
        "stock": 500,
    },
    {
        "name": "Creator Pass",
        "price": Decimal("2000.00"),
        "tier": "CREATOR",
        "combo_description": "Come Create! Games, Kohi Village, Animation experience, Creator/Investor access.",
        "image_static": "images/tickets/next-frame-creator.jpg",
        "is_purchasable": True,
        "stock": 300,
    },
    {
        "name": "VVIP Pass",
        "price": Decimal("10000.00"),
        "tier": "VVIP",
        "combo_description": "Go Deeper! Premium/VVIP experience and access.",
        "image_static": "images/tickets/next-frame-vvip.jpg",
        "is_purchasable": True,
        "stock": 100,
    },
)


def seed_next_frame_2026(apps, schema_editor):
    Event = apps.get_model("store", "Event")
    EventTicket = apps.get_model("store", "EventTicket")

    # Reuse the event previously seeded as "Osisioma Relaunch" (rebranded here
    # as "The Next Frame 2026") so existing tickets/orders stay attached to
    # the same row, rather than creating a second Event.
    event = (
        Event.objects.filter(name="Osisioma Relaunch").first()
        or Event.objects.filter(is_active=True).order_by("-created_at").first()
    )

    start_date = timezone.make_aware(datetime.datetime(2026, 10, 3, 10, 0))
    description = (
        "Kohi Dojo × NueLuks Studio present The Next Frame 2026 — the Osisioma "
        "Stand Relaunch & From Sketch to Scene Animation Workshop. Join us in "
        "Osisioma, Aba on 3rd October 2026 for community, games, art, food and "
        "the animation experience."
    )

    if event:
        Event.objects.filter(is_active=True).exclude(pk=event.pk).update(is_active=False)
        event.name = "The Next Frame 2026"
        event.description = description
        event.start_date = start_date
        event.is_active = True
        event.save(update_fields=["name", "description", "start_date", "is_active"])
    else:
        Event.objects.filter(is_active=True).update(is_active=False)
        event = Event.objects.create(
            name="The Next Frame 2026",
            description=description,
            start_date=start_date,
            is_active=True,
        )

    # Retire the old placeholder combo tickets without deleting any real orders.
    EventTicket.objects.filter(event=event, name__in=OLD_TICKET_NAMES).update(is_purchasable=False)

    for spec in NEW_TICKETS:
        name = spec["name"]
        defaults = {k: v for k, v in spec.items() if k != "name"}
        EventTicket.objects.update_or_create(event=event, name=name, defaults=defaults)


def unseed_next_frame_2026(apps, schema_editor):
    # Left as a no-op: reversing would risk detaching real ticket orders
    # from their event/ticket rows.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0017_alter_eventticket_tier"),
    ]

    operations = [
        migrations.RunPython(seed_next_frame_2026, unseed_next_frame_2026),
    ]
