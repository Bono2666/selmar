from django.urls import path
from . import views

urlpatterns = [
     path('', views.home, name='home'),
     path('master/user/', views.user_index, name='user-index'),
     path('master/user/add/', views.user_add, name='user-add'),
     path('master/user/view/<str:_id>/', views.user_view, name='user-view'),
     path('master/user/update/<str:_id>/', views.user_update, name='user-update'),
     path('master/user/delete/<str:_id>/', views.user_delete, name='user-delete'),
     path('master/user/change-password/', views.change_password, name='change-password'),
     path('master/user/set-password/<str:_id>/', views.set_password, name='set-password'),
     path('master/distributor/', views.distributor_index, name='distributor-index'),
     path('master/distributor/add/', views.distributor_add, name='distributor-add'),
     path('master/distributor/view/<str:_id>/', views.distributor_view, name='distributor-view'),
     path('master/distributor/update/<str:_id>/', views.distributor_update, name='distributor-update'),
     path('master/distributor/delete/<str:_id>/', views.distributor_delete, name='distributor-delete'),
     path('master/area-sales/', views.area_sales_index, name='area-sales-index'),
     path('master/area-sales/add/', views.area_sales_add, name='area-sales-add'),
     path('master/area-sales/view/<str:_id>/', views.area_sales_view, name='area-sales-view'),
     path('master/area-sales/update/<str:_id>/', views.area_sales_update, name='area-sales-update'),
     path('master/area-sales/delete/<str:_id>/', views.area_sales_delete, name='area-sales-delete'),
     path('master/position/', views.position_index, name='position-index'),
     path('master/position/add/', views.position_add, name='position-add'),
     path('master/position/view/<str:_id>/', views.position_view, name='position-view'),
     path('master/position/update/<str:_id>/', views.position_update, name='position-update'),
     path('master/position/delete/<str:_id>/', views.position_delete, name='position-delete'),
]
