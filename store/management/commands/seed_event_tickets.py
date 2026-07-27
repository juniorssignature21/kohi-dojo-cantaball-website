from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from store.models import Event, EventTicket


TICKETS = (
    {
        "name": "1k Ticket",
        "price": Decimal("1000.00"),
        "tier": "REGULAR",
        "combo_description": "1 bun and 1 small coffee",
        "image_static": "images/tickets/combo-1k.png",
        "is_purchasable": True,
        "stock": 500,
    },
    {
        "name": "1500 Ticket",
        "price": Decimal("1500.00"),
        "tier": "REGULAR",
        "combo_description": "1 sandwich and 1 small coffee",
        "image_static": "images/tickets/combo-1500.png",
        "is_purchasable": True,
        "stock": 500,
    },
    {
        "name": "2000 Ticket",
        "price": Decimal("2000.00"),
        "tier": "REGULAR",
        "combo_description": "1 sandwich and 1 big coffee",
        "image_static": "images/tickets/combo-2000.png",
        "is_purchasable": True,
        "stock": 500,
    },
    {
        "name": "VIP Ticket",
        "price": Decimal("0.00"),
        "tier": "VIP",
        "combo_description": "VIP access - awarded via referral (bring 10+ people)",
        "image_static": "images/tickets/combo-2000.png",
        "is_purchasable": False,
        "stock": 100,
    },
)


class Command(BaseCommand):
    help = "Create the default event and combo tickets (1k / 1500 / 2000 + VIP reward)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--event-name",
            default="Kohi Dojo Event Night",
            help="Name of the event to create or update.",
        )

    def handle(self, *args, **options):
        event_name = options["event_name"]
        event, created = Event.objects.get_or_create(
            name=event_name,
            defaults={
                "description": (
                    "Buy a combo ticket. Share your referral code — "
                    "bring 2 people for a free regular ticket, "
                    "5 for a regular ticket + shawarma, "
                    "10+ for a VIP ticket + shawarma."
                ),
                "start_date": timezone.now(),
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created event: {event.name}"))
        else:
            self.stdout.write(f"Using existing event: {event.name}")

        for spec in TICKETS:
            ticket, ticket_created = EventTicket.objects.update_or_create(
                event=event,
                name=spec["name"],
                defaults={
                    "price": spec["price"],
                    "tier": spec["tier"],
                    "combo_description": spec["combo_description"],
                    "image_static": spec.get("image_static"),
                    "is_purchasable": spec["is_purchasable"],
                    "stock": spec["stock"],
                },
            )
            action = "Created" if ticket_created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"  {action}: {ticket.name} - NGN {ticket.price} ({ticket.combo_description})"
                )
            )

        self.stdout.write(self.style.SUCCESS("Done."))
