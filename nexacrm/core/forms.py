# from django import forms
# from django.contrib.auth.models import User
# from .models import PurchasedProduct
# from userprofile.models import Userprofile
# from .models import RawMaterial, Order, ManufacturingPart

# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'password', 'email']

# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = Userprofile
#         fields = ['name', 'contact', 'location', 'business_type']

# class PurchaseForm(forms.ModelForm):
#     class Meta:
#         model = PurchasedProduct
#         fields = ['quantity']

# class RawMaterialForm(forms.ModelForm):
#     class Meta:
#         model = RawMaterial
#         fields = ['name', 'description', 'image', 'quantity']

# class ManufacturingPartForm(forms.ModelForm):
#     class Meta:
#         model = ManufacturingPart
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Filter raw materials to show only those that are in orders or have a quantity > 0
#         ordered_raw_material_ids = Order.objects.values_list('raw_material_id', flat=True).distinct()
#         available_raw_material_ids = RawMaterial.objects.filter(
#             id__in=ordered_raw_material_ids,
#             quantity__gt=0
#         ).values_list('id', flat=True)
#         self.fields['raw_materials'].queryset = RawMaterial.objects.filter(id__in=available_raw_material_ids)

from django import forms
from django.contrib.auth.models import User
from.models import RawMaterial, Order, ManufacturingPart, Product, PurchasedProduct, Userprofile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Userprofile
        exclude = ['user']  # Exclude the foreign key to User since it's auto-created

class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterial
        fields = ['name', 'description', 'image', 'quantity']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['raw_material', 'quantity', 'status']

class ManufacturingPartForm(forms.ModelForm):
    class Meta:
        model = ManufacturingPart
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define a property for the raw materials queryset
        @property
        def raw_material_queryset(self):
            ordered_raw_material_ids = Order.objects.values_list('raw_material_id', flat=True).distinct()
            available_raw_material_ids = RawMaterial.objects.filter(
                id__in=ordered_raw_material_ids,
                quantity__gt=0
            ).values_list('id', flat=True)
            return RawMaterial.objects.filter(id__in=available_raw_material_ids)
        
        self.fields['raw_materials'].queryset = self.raw_material_queryset

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'parts', 'image', 'total_items']

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = PurchasedProduct
        fields = ['product', 'quantity']
