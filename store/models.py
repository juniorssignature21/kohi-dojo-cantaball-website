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

    
