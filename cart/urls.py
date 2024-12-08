from django.urls import path 
from . import views

urlpatterns = [
    
    path('cart/',views.cart_view,name='cart-view'),
    path('add-to-cart/',views.add_to_cart,name='add-to-cart'),
    path('remove-item/<int:item_id>/',views.remove_item, name='remove-item'),
    path('update-cart-quantity/',views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('check_cart_status/',views.check_cart_status, name='check_cart_status'),
    path('add-address/',views.add_address, name='add-address'),
    path('update-counts/',views.update_counts, name='update-counts'),
    
]
