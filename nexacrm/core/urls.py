# main/urls.py
from django.urls import path
from . import views
from .views import edit_raw_material, list_raw_materials  # Import your views


urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('buy/<int:product_id>/', views.buy_product, name='buy_product'),
    path('add_raw_material/', views.add_raw_material, name='add_raw_material'),
    path('list_raw_materials/', list_raw_materials, name='list_raw_materials'),
    path('raw-materials/edit/<int:raw_material_id>/', edit_raw_material, name='edit_raw_material'),
    path('my-account/', views.my_account, name='my_account'),
    path('orders-recieved/', views.orders_recieved, name='orders_recieved'),
    path('admin/orders/', views.orders_recieved, name='admin_orders'),    
    path('my-orders/', views.my_orders, name='my_orders'),
]

