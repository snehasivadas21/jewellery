from django.db import models
from category.models import Category
from register.models import User
from django.apps import apps 
from django.db.models import Avg, Count
# Create your models here.



class Products(models.Model):
    product_name = models.CharField(max_length=100, null=False)
    product_description = models.TextField(max_length=5000, null=False)
    product_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    offer_price = models.DecimalField(max_digits=8, decimal_places=2)
    thumbnail = models.ImageField(upload_to="thumbnail_images", null=True)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def percentage_discount(self):
        return int(((self.price - self.offer_price) / self.price) * 100)
    
    def get_average_rating(self):
        average = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return average if average else 0
    
    def get_star_rating_distribution(self):
        total_reviews = self.reviews.count()
        distribution = self.reviews.values('rating').annotate(rating_count=Count('rating'))
        
        star_ratings = {str(i): 0 for i in range(1, 6)}
        for item in distribution:
            star_ratings[str(item['rating'])] = (item['rating_count'] / total_reviews) * 100
        
        return star_ratings
    
    def user_has_purchased(self, user):
        OrderSub = apps.get_model('orders', 'OrderSub')  
        return OrderSub.objects.filter(
            variant__product=self,
            user=user,
            is_active=True
        ).exists()

    def __str__(self):
        return f"-{self.product_name}"

   
class Product_Variant(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    gemstone =models.CharField(max_length=10,null=True)
    variant_stock = models.BigIntegerField(null=False, default=0)
    variant_status = models.BooleanField(default=True)
    weight = models.CharField(max_length=20,null=True)


class Product_images(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE,null=True)
    images = models.ImageField(
        upload_to="product_images"
    )

    def __str__(self):
        return f"Image for {self.product.product_name}"

class Product_variant_images(models.Model):
    product_variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
    images = models.ImageField(
        upload_to="product_images"
    )

    def __str__(self):
        return f"Image for {self.product_variant.product.product_name} - {self.product_variant.colour_name}"
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.CharField( max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)    
    
    def __str__(self):
        return f'{self.user} - {self.product}'
























































