# main/admin.py
from django.contrib import admin
from .models import RawMaterial, ManufacturingPart, Product, PurchasedProduct
from django.contrib.admin import AdminSite
from .models import Order
from .models import Userprofile, RawMaterial, Order


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'quantity']
    actions = ['send_to_manufacturing']

    def send_to_manufacturing(self, request, queryset):
        # Custom action to send selected raw materials to manufacturing
        pass

@admin.register(ManufacturingPart)
class ManufacturingPartAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_raw_materials']
    actions = ['send_to_product']

    def send_to_product(self, request, queryset):
        # Custom action to send selected parts to product
        pass

    def get_raw_materials(self, obj):
        return ", ".join([raw_material.name for raw_material in obj.raw_materials.all()])
    get_raw_materials.short_description = 'Raw Materials'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "raw_materials":
            # Get IDs of raw materials associated with completed orders
            complete_order_raw_material_ids = Order.objects.filter(status='complete').values_list('raw_material_id', flat=True)
            # Filter raw materials to include only those with completed orders
            kwargs["queryset"] = RawMaterial.objects.filter(id__in=complete_order_raw_material_ids)
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'image']

    def get_manufacturing_parts(self, obj):
        return ", ".join([part.name for part in obj.parts.all()])
    get_manufacturing_parts.short_description = 'Manufacturing Parts'

@admin.register(PurchasedProduct)
class PurchasedProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'user_business', 'user_contact', 'user_location', 'purchase_date', 'quantity']

    def user_business(self, obj):
        return obj.user.userprofile.business_type
    user_business.short_description = 'Business Name'

    def user_contact(self, obj):
        return obj.user.userprofile.contact
    user_contact.short_description = 'Contact Number'

    def user_location(self, obj):
        return obj.user.userprofile.location
    user_location.short_description = 'Location'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['raw_material','user', 'quantity', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['raw_material__name']

    def has_add_permission(self, request):
        # Only allow s  uperusers or admins to add orders
        return request.user.is_superuser or request.user.is_staff

        # # Set the user field to the admin user creating the order
        # obj.user = request.user.userprofile
        # super().save_model(request, obj, form, change)

    def save_model(self, request, obj, form, change):
        if not change:  # if it's a new order
            raw_material = obj.raw_material
            if hasattr(raw_material, 'userprofile'):
                obj.user = raw_material.userprofile
        super().save_model(request, obj, form, change)

admin.site.register(Order, OrderAdmin)
