from django.urls import path 
from . import views

urlpatterns = [
    path('products-list/',views.products_list,name='products-list'),
    path('create/',views.create_product,name='create-product'),
    path('edit/<int:product_id>',views.edit_product,name='edit-product'),
    path('status/<int:product_id>/',views.product_status,name='product-status'),
    path('add-images/<int:product_id>',views.add_images,name='add-images'),
    path('add-variant/<int:product_id>',views.add_variant,name='add-variant'),
    path('product_detail/<int:product_id>',views.product_detail,name='product-detail'),
    path('variant/<int:product_id>/', views.variant_detail, name='variant-detail'),
    path('add-variant-image/<int:product_variant_id>/',views.add_variant_image, name='add-variant-image'),
    path('edit-variant/<int:variant_id>/',views.edit_variant, name='edit-variant'),
    path('delete-image/<int:image_id>/',views.delete_image, name='delete-image'),
    path('variant-status/<int:variant_id>/',views.variant_status, name='variant-status'),
    path('available-product/<int:product_id>/',views.product_is_available,name='avilable_product'),
    
    path('product/<int:product_id>/', views.product_details_user, name='product-details-user'),
    path('shop-side',views.shop_side,name='shop-side'),
]