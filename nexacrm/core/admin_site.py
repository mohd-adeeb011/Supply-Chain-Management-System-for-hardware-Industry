from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import RawMaterial, ManufacturingPart, Product, PurchasedProduct, Order  # Import the Order model
from .admin import RawMaterialAdmin, ManufacturingPartAdmin, ProductAdmin, PurchasedProductAdmin, OrderAdmin  # Import the Order admin class

class MyAdminSite(AdminSite):
    site_header = "Star Fabricator Supply Chain management"

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)
        # Order the models as desired
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        for app in app_list:
            if app['name'].lower() == 'core':
                app['models'] = sorted(app['models'], key=lambda x: (
                    0 if x['object_name'] == 'RawMaterial' else
                    1 if x['object_name'] == 'ManufacturingPart' else
                    2 if x['object_name'] == 'Product' else
                    3 if x['object_name'] == 'PurchasedProduct' else
                    4 if x['object_name'] == 'Order' else 5  # Add this line for the Order model
                ))
        return app_list

admin_site = MyAdminSite(name='myadmin')

admin_site.register(RawMaterial, RawMaterialAdmin)
admin_site.register(ManufacturingPart, ManufacturingPartAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(PurchasedProduct, PurchasedProductAdmin)
admin_site.register(Order, OrderAdmin)  # Register the Order model with its admin class
