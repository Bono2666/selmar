from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('master/user/', views.user_index, name='user-index'),
    path('master/user/add/', views.user_add, name='user-add'),
    path('master/user/view/<int:_id>/', views.user_update, name='user-view'),
    path('master/user/delete/<int:_id>/', views.user_delete, name='user-delete'),
    path('master/user/change-password/', views.change_password, name='change-password'),
    path('master/user/set-password/<int:_id>/', views.set_password, name='set-password'),
]
