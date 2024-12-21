from django.urls import path
from . import views

urlpatterns = [
    path('admin-login/', views.admin_login,name='admin_login'),
    path('admin-dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('sales-report/',views.sales_report,name='sales-report'),
    path('sales-report/filter/',views.order_date_filter,name='order_date_filter'),
    path('user-list/',views.user_list,name='user-list'),
    path('user-block/<int:user_id>/',views.user_block,name='user-block'),
    path('user-unblock/<int:user_id>/',views.user_unblock,name='user-unblock'),
    path('best-selling-products/',views.best_selling_products,name='best-products'),
    path('best-selling-categories/',views.best_selling_categories,name='best-categories'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
]
