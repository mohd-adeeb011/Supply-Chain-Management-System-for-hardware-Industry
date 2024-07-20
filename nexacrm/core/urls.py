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
    path('raw-materials/', views.raw_materials_view, name='raw_materials'),
    path('manufacturing-parts/', views.manufacturing_parts_view, name='manufacturing_parts'),
    path('products/', views.products_view, name='products'),
    path('orders/', views.orders_view, name='orders'),
    path('add_manufacturing_product/', views.add_manufacturing_product, name='add_manufacturing_product'),
    path('manufacturing_products/', views.manufacturing_products, name='manufacturing_products'), # Add this line
    path('edit_manufacturing_product/<int:pk>/', views.edit_manufacturing_product, name='edit_manufacturing_product'),
    path('delete_manufacturing_product/<int:pk>/', views.delete_manufacturing_product, name='delete_manufacturing_product'),
    path('order_raw_materials', views.order_raw_materials_view, name='order_raw_materials'),
    path('add_to_cart/<int:raw_material_id>/<int:quantity>/', views.add_to_cart_view, name='add_to_cart_view'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    # path('finalize_order/<int:material_id>/', views.finalize_order_view, name='finalize_order'),
]
