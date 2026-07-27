from django.contrib import admin
from .models import (
    Category,
    Product,
    Order,
    OrderItem,
    Cart,
    Event,
    EventTicket,
    EventOrder,
    ReferralReward,
)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Cart)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "customer", "pick_up_date", "total", "payment_status", "order_status", "date")
    list_filter = ("payment_status", "order_status", "pick_up_date", "date")
    search_fields = ("order_id", "customer__username", "customer__email")


class EventTicketInline(admin.TabularInline):
    model = EventTicket
    extra = 0
    fields = ("name", "price", "tier", "combo_description", "image", "image_static", "is_purchasable", "stock")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "start_date", "end_date", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    inlines = [EventTicketInline]


@admin.register(EventTicket)
class EventTicketAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "price", "tier", "is_purchasable", "stock")
    list_filter = ("tier", "is_purchasable", "event")
    search_fields = ("name", "combo_description", "event__name")
    fields = (
        "event",
        "name",
        "price",
        "tier",
        "combo_description",
        "image",
        "image_static",
        "is_purchasable",
        "stock",
    )


@admin.register(EventOrder)
class EventOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "customer",
        "ticket",
        "total",
        "referred_by_code",
        "payment_status",
        "is_free_reward",
        "date",
    )
    list_filter = ("payment_status", "order_status", "is_free_reward", "event")
    search_fields = (
        "order_id",
        "customer__username",
        "customer__email",
        "referred_by_code",
    )


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = (
        "referrer",
        "event",
        "tier",
        "referral_count",
        "includes_shawarma",
        "status",
        "date",
    )
    list_filter = ("tier", "status", "includes_shawarma", "event")
    search_fields = ("referrer__email", "referrer__username", "reward_description")
