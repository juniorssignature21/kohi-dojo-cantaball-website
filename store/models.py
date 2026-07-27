from django.db import models
from django.contrib.auth import get_user_model
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
import uuid

User = get_user_model()

PAYMENT_STATUS = (
    ("Paid","Paid"),
    ("Processing","Processing"),
    ("Failed","Failed"),
)

PAYMENT_METHOD = (
    ("Cash","Cash"),
    ("Flutterwave","Flutterwave"),
    
)

ORDER_STATUS = (
    ("Pending","Pending"),
    ("Processing","Processing"),
    ("Delivered","Delivered"),
)

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = ShortUUIDField(length=8, max_length=25, alphabet='1234567890abcdef', unique=True, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # Generate a unique slug using UUID
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    slug = ShortUUIDField(length=8, max_length=25, alphabet='1234567890abcdef', unique=True, editable=False)

    def save(self, *args, **kwargs):
        
        if not self.slug:            
            self.slug = uuid.uuid4().hex[:8]  # Generate a unique slug using UUID
        super(Product, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    

class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    qty = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True,blank=True)
    
    sub_total = models.DecimalField(decimal_places=2,max_digits=12, default=0.00, null=True, blank=True)
    
    total = models.DecimalField(decimal_places=2,max_digits=12, default=0.00, null=True, blank=True)
    
    cart_id = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.cart_id} - {self.product.name} - {self.qty}'
    
class Order(models.Model):
    
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='customer', blank=True, null=True)
    
    sub_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
   
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="Processing")
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, default=None, null=True, blank=True)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="pending")
    order_id = ShortUUIDField(length=6, max_length=25, alphabet='1234567890')
    payment_id = models.CharField(max_length=1000, null=True, blank=True)
    pick_up_date = models.DateTimeField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Order"
        ordering = ['-date']
        
    def __str__(self):
        return f"Order {self.order_id} by {self.customer.username if self.customer else 'Unknown'}"
    
    def order_items(self):
        return OrderItem.objects.filter(order=self)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.PositiveIntegerField(default=0, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True,blank=True)
    sub_total = models.DecimalField(decimal_places=2,max_digits=12, default=0.00, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date"]
            
    def __str__(self):
        return f"{self.product.name} - {self.qty} - {self.sub_total}"


TICKET_TIER = (
    ("REGULAR", "Regular"),
    ("VIP", "VIP"),
)

REFERRAL_REWARD_TIER = (
    ("TWO", "Bring 2 — 1 regular ticket free"),
    ("FIVE", "Bring 5 — 1 regular ticket + 1 shawarma"),
    ("TEN", "Bring 10+ — 1 VIP ticket + 1 shawarma"),
)

REFERRAL_REWARD_STATUS = (
    ("Pending", "Pending"),
    ("Fulfilled", "Fulfilled"),
)


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    slug = ShortUUIDField(length=8, max_length=25, alphabet='1234567890abcdef', unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class EventTicket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tier = models.CharField(max_length=20, choices=TICKET_TIER, default="REGULAR")
    combo_description = models.TextField(
        help_text="Food/drink included with this ticket, e.g. 1 bun + 1 small coffee"
    )
    image = models.ImageField(upload_to='event_tickets/', blank=True, null=True)
    # Static fallback under static/images/ when no upload is set (e.g. tickets/combo-1k.png)
    image_static = models.CharField(max_length=255, blank=True, null=True)
    is_purchasable = models.BooleanField(
        default=True,
        help_text="Uncheck for reward-only tickets (e.g. VIP referral reward)."
    )
    stock = models.PositiveIntegerField(default=0)
    slug = ShortUUIDField(length=8, max_length=25, alphabet='1234567890abcdef', unique=True, editable=False)

    class Meta:
        ordering = ['price']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} — ₦{self.price} ({self.event.name})"


class EventOrder(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='event_orders', blank=True, null=True
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='orders')
    ticket = models.ForeignKey(EventTicket, on_delete=models.PROTECT, related_name='orders')
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    referred_by_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Referral code of the user who referred this buyer.",
    )
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="Processing")
    payment_method = models.CharField(
        max_length=100, choices=PAYMENT_METHOD, default=None, null=True, blank=True
    )
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="Pending")
    order_id = ShortUUIDField(length=6, max_length=25, alphabet='1234567890')
    payment_id = models.CharField(max_length=1000, null=True, blank=True)
    is_free_reward = models.BooleanField(
        default=False,
        help_text="True when this order was granted as a referral reward.",
    )
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Event Orders"
        ordering = ['-date']

    def __str__(self):
        buyer = self.customer.username if self.customer else 'Unknown'
        return f"EventOrder {self.order_id} — {self.ticket.name} by {buyer}"


class ReferralReward(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_rewards')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='referral_rewards')
    tier = models.CharField(max_length=10, choices=REFERRAL_REWARD_TIER)
    referral_count = models.PositiveIntegerField(default=0)
    reward_description = models.CharField(max_length=255)
    includes_shawarma = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=REFERRAL_REWARD_STATUS, default="Pending")
    free_ticket_order = models.ForeignKey(
        EventOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referral_reward_source',
    )
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']
        unique_together = [('referrer', 'event', 'tier')]

    def __str__(self):
        return f"{self.referrer.email} — {self.get_tier_display()} ({self.status})"

