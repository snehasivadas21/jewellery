from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views
 

urlpatterns = [

  path('order-placed/', views.order_placed, name='order-placed'),
  path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order-confirmation'),
  path('order-list/', views.admin_order_list, name='list-order'),
  path('admin-orders-details/<int:oid>', views.admin_orders_details, name='admin-orders-details'),
  path('failure/<int:order_id>/', views.order_failure, name='order-failure'),
  path('change-order-status/<int:order_id>/', views.change_order_status, name='change_order_status'),
  
  
]