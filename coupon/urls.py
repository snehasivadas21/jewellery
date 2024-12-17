from django.urls import path ,include
from . import views

urlpatterns = [
    path('list-coupon/', views.list_coupon, name='list-coupon'),
    path('create/', views.create_coupon, name='create-coupon'),
    path('edit/<int:pk>/', views.edit_coupon, name='edit-coupon'),
    path('coupon-status/<int:pk>/', views.coupon_status, name='coupon-status'),
    path('apply-coupon/', views.apply_coupon, name='apply-coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove-coupon'),
    path('generate-coupon-code/', views.generate_coupon_code, name='generate-coupon-code'),
 

]
