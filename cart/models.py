from django.db import models
from register.models import User
from product.models import Products, Product_Variant

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"Cart of {self.user}"

class CartItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def sub_total(self):
        return self.product.offer_price * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.product} in {self.cart}"