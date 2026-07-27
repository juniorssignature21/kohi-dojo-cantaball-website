"""Referral reward evaluation for completed event orders."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count

from store import models as store_models

User = get_user_model()

# Threshold -> (tier key, description, includes_shawarma, ticket_tier)
REFERRAL_TIERS = (
    (2, "TWO", "1 regular ticket free", False, "REGULAR"),
    (5, "FIVE", "1 regular ticket and 1 shawarma", True, "REGULAR"),
    (10, "TEN", "1 VIP ticket and 1 shawarma", True, "VIP"),
)


def count_successful_referrals(event, referral_code):
    """Count distinct buyers who completed a paid (non-reward) order with this code."""
    return (
        store_models.EventOrder.objects.filter(
            event=event,
            referred_by_code__iexact=referral_code,
            payment_status="Paid",
            is_free_reward=False,
        )
        .exclude(customer__isnull=True)
        .values("customer")
        .annotate(n=Count("id"))
        .count()
    )


def _pick_reward_ticket(event, ticket_tier):
    qs = store_models.EventTicket.objects.filter(event=event, tier=ticket_tier)
    if ticket_tier == "REGULAR":
        purchasable = qs.filter(is_purchasable=True).order_by("price").first()
        if purchasable:
            return purchasable
    return qs.order_by("price").first()


def _create_free_ticket_order(referrer, event, ticket):
    return store_models.EventOrder.objects.create(
        customer=referrer,
        event=event,
        ticket=ticket,
        qty=1,
        unit_price=Decimal("0.00"),
        total=Decimal("0.00"),
        payment_status="Paid",
        payment_method="Cash",
        order_status="Pending",
        is_free_reward=True,
    )


def evaluate_referral_rewards(event_order):
    """
    After an event order is paid, check if the referred_by_code owner
    has hit a referral reward tier for this event.
    """
    code = (event_order.referred_by_code or "").strip()
    if not code or event_order.is_free_reward:
        return []

    referrer = User.objects.filter(referral_code__iexact=code).first()
    if not referrer:
        return []

    # Block self-referral from earning
    if event_order.customer_id and event_order.customer_id == referrer.id:
        return []

    count = count_successful_referrals(event_order.event, code)
    created_rewards = []

    for threshold, tier_key, description, includes_shawarma, ticket_tier in REFERRAL_TIERS:
        if count < threshold:
            continue

        reward, created = store_models.ReferralReward.objects.get_or_create(
            referrer=referrer,
            event=event_order.event,
            tier=tier_key,
            defaults={
                "referral_count": count,
                "reward_description": description,
                "includes_shawarma": includes_shawarma,
                "status": "Pending",
            },
        )
        if not created:
            if reward.referral_count != count:
                reward.referral_count = count
                reward.save(update_fields=["referral_count"])
            continue

        ticket = _pick_reward_ticket(event_order.event, ticket_tier)
        if ticket:
            free_order = _create_free_ticket_order(referrer, event_order.event, ticket)
            reward.free_ticket_order = free_order
            reward.save(update_fields=["free_ticket_order"])

        created_rewards.append(reward)

    return created_rewards
