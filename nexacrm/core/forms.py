from django import forms
from django.contrib.auth.models import User
from .models import RawMaterial, Order, ManufacturingPart, Product, PurchasedProduct, Userprofile, ManufacturingProduct
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

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

HARDCODED_RAW_MATERIALS = [
    'Round Pipe',
    'Angle',
    'Flat Bar',
    'Iron Lock',
    'Sqruare Net',
    'Steel Iron Pipe',
    'Aldrop',
    'Iron Sheets',
    'Steel Pipe',
    'Iron Round Bars',
    'Iron Moulding',
    'Steel Angle'
]

class ManufacturingProductForm(forms.ModelForm):
    raw_material_1 = forms.ChoiceField(choices=[(material, material) for material in HARDCODED_RAW_MATERIALS] + [('None', 'None')], required=False)
    raw_material_2 = forms.ChoiceField(choices=[(material, material) for material in HARDCODED_RAW_MATERIALS] + [('None', 'None')], required=False)
    raw_material_3 = forms.ChoiceField(choices=[(material, material) for material in HARDCODED_RAW_MATERIALS] + [('None', 'None')], required=False)
    raw_material_4 = forms.ChoiceField(choices=[(material, material) for material in HARDCODED_RAW_MATERIALS] + [('None', 'None')], required=False)
    raw_material_5 = forms.ChoiceField(choices=[(material, material) for material in HARDCODED_RAW_MATERIALS] + [('None', 'None')], required=False)

    class Meta:
        model = ManufacturingProduct
        fields = ['name', 'raw_material_1', 'quantity_1', 'raw_material_2', 'quantity_2', 'raw_material_3', 'quantity_3', 'raw_material_4', 'quantity_4', 'raw_material_5', 'quantity_5']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(
                Column('raw_material_1', css_class='form-group col-md-6 mb-0'),
                Column('quantity_1', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('raw_material_2', css_class='form-group col-md-6 mb-0'),
                Column('quantity_2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('raw_material_3', css_class='form-group col-md-6 mb-0'),
                Column('quantity_3', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('raw_material_4', css_class='form-group col-md-6 mb-0'),
                Column('quantity_4', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('raw_material_5', css_class='form-group col-md-6 mb-0'),
                Column('quantity_5', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            )
        )

class RawMaterialOrderForm(forms.Form):
    product = forms.ModelChoiceField(queryset=ManufacturingProduct.objects.all(), label="Select Product")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].widget.attrs.update({'class': 'form-control'})

    def get_raw_material_fields(self):
        product = self.cleaned_data.get('product')
        raw_material_fields = []
        if product:
            for i in range(1, 6):
                raw_material = getattr(product, f'raw_material_{i}', None)
                quantity = getattr(product, f'quantity_{i}', None)
                if raw_material:
                    raw_material_fields.append((raw_material, quantity))
        return raw_material_fields