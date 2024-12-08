from django.urls import path
from . import views

urlpatterns = [
    path('profile/',views.user_profile,name='user-profile'),
    path('user-address/',views.user_address,name='user-address'),
    path('edit-address/<int:address_id>/',views.add_or_edit_address, name='edit-address'),
    path('useradd-address/',views.add_or_edit_address, name='useradd-address'),
    path('delete-address/<int:address_id>/',views.delete_address, name='delete-address'),
    path('order-list/',views.user_orders_view,name='order-list'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel-order'),
    path('cancel-order-item/', views.cancel_order_item, name='cancel-order-item'),
    path('password-change/', views.password_change_view, name='password-change'),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
   
]