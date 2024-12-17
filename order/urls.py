from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views
 

urlpatterns = [

  path('order-placed/', views.order_placed, name='order-placed'),
  path('order-confirmation/<str:order_id>/', views.order_confirmation, name='order-confirmation'),
  path('order-list/', views.admin_order_list, name='list-order'),
  path('admin-orders-details/<int:oid>', views.admin_orders_details, name='admin-orders-details'),
  path('failure/<str:order_id>/', views.order_failure, name='order-failure'),
  path('change-order-status/<int:order_id>/', views.change_order_status, name='change_order_status'),
  path('returned-orders/', views.returned_orders, name='returned-orders'),
  path('return-request/update/<int:return_request_id>/', views.update_return_request, name='update-return-request'),
  path('razorpay/callback/', views.razorpay_callback, name='razorpay-callback'),
]