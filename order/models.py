from django.db import models
from django.db import models
from register.models import *
from product.models import Product_Variant
from userprofile.models import *
from decimal import Decimal


# Create your models here..
class OrderAddress(models.Model):
    name = models.CharField(max_length=50, null=False)
    house_name = models.CharField(max_length=100, null=False)
    street_name = models.CharField(max_length=100, null=False)
    pin_number = models.IntegerField(null=False)
    district = models.CharField(max_length=100, null=False)
    state = models.CharField(max_length=100, null=False)
    country = models.CharField(max_length=50, null=False)
    phone_number = models.CharField(max_length=50, null=False)
    status = models.BooleanField(default=True)

class OrderMain(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Awaiting payment', 'Awaiting payment'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
        ('Returned', 'Returned'),
    ]
    user = models.ForeignKey(User,  on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(OrderAddress, on_delete=models.SET_NULL,null=True)
    total_amount = models.FloatField(null=False)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    order_status = models.CharField( max_length=100, choices=ORDER_STATUS_CHOICES, default='Pending')
    payment_option = models.CharField(max_length=100, default="Cash_on_delivery")
    order_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=50)
    
    

class OrderSub(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    main_order = models.ForeignKey(OrderMain, on_delete=models.CASCADE)
    variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, default=0)
    price = models.FloatField(null=False,default=0)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=50,null=True, blank=True)
    
    def total_cost(self):
        return Decimal(self.quantity) * Decimal(self.price)
    
    

class ReturnRequest(models.Model):
    RETURN_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    order_main = models.ForeignKey(OrderMain, on_delete=models.CASCADE)
    order_sub = models.ForeignKey(OrderSub, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=RETURN_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
