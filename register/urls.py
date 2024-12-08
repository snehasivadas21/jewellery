from django.urls import path
from . import views


urlpatterns = [
    path('',views.home_page,name='home_page'),
    path('', views.index, name='index'),  
    path('signup/',views.register,name='signup'),
    path('verify-otp/',views.verify_otp,name='verify_otp'),
    path('resend-otp/',views.resend_otp,name='resend_otp'),
    path('login/', views.login_view, name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('about/',views.about_us,name='about'),
    path('contact/',views.contact,name='contact'),
    path('password-reset/', views.password_reset_request, name='password-reset'),
    path('password-reset-done/', views.password_reset_done, name='password-reset-done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password-reset-confirm'),
    path('reset/done/', views.password_reset_complete, name='password-reset-complete'),
]

