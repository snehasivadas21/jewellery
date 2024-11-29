from django.urls import path
from . import views

urlpatterns = [
    path('list-category',views.list_category,name='list_category'),
    path('create-category',views.create_category,name='create_category'),
    path('edit-category/<int:category_id>/',views.edit_category,name='edit_category'),
    path('available-category/<int:category_id>/',views.category_is_available,name='avilable_category'),
]