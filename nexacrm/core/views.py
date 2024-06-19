from django.shortcuts import render, redirect
from .models import Product, PurchasedProduct, RawMaterial, ManufacturingPart, Product, Order, ManufacturingProduct
from userprofile.models import Userprofile  # Correct import
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import UserProfileForm, ManufacturingProductForm, PurchaseForm, RawMaterialForm, RawMaterialOrderForm
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from django.urls import reverse_lazy
from urllib.parse import urlencode
from django.core.exceptions import ObjectDoesNotExist
import json

def index(request):
    return render(request, 'core/main_page.html')  # This line is not used anymore but ensure it points correctly

def main_page(request):
    products = Product.objects.all()
    return render(request, 'core/main_page.html', {'products': products})

@login_required
def buy_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            purchase.product = product
            if purchase.quantity <= product.total_items:
                purchase.save()
                product.total_items -= purchase.quantity
                product.save()
                return redirect('main_page')
            else:
                return render(request, 'core/buy_product.html', {'form': form, 'error': 'Not enough stock'})
    else:
        form = PurchaseForm()
    return render(request, 'core/buy_product.html', {'form': form, 'product': product})


@login_required
def add_raw_material(request):
    if request.method == 'POST':
        form = RawMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            raw_material = form.save(commit=False)
            raw_material.user = request.user
            raw_material.save()
            return redirect('list_raw_materials')
    else:
        form = RawMaterialForm()
    return render(request, 'core/add_raw_material.html', {'form': form})

@login_required
def list_raw_materials(request):
    raw_materials = RawMaterial.objects.filter(user=request.user)
    return render(request, 'core/list_raw_materials.html', {'raw_materials': raw_materials})



@login_required
def edit_raw_material(request, raw_material_id):
    raw_material = get_object_or_404(RawMaterial, pk=raw_material_id)
    if request.method == "POST":
        form = RawMaterialForm(request.POST, instance=raw_material)
        if form.is_valid():
            form.save()
            return redirect('core/list_raw_materials')
    else:
        form = RawMaterialForm(instance=raw_material)
    return render(request, 'core/edit_raw_material.html', {'form': form})

@login_required
def my_account(request):
    user_profile, created = Userprofile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('my_account')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'core/my_account.html', {'form': form})

@login_required
def orders_recieved(request):
    # Fetch all orders that are complete
    orders = Order.objects.filter(status='complete').order_by('-created_at')
    return render(request, 'core/orders_recieved.html', {'orders': orders})

@login_required
def my_orders(request):
    orders = PurchasedProduct.objects.filter(user=request.user)
    return render(request, 'core/my_orders.html', {'orders': orders})


## Admin panel
# Decorator to restrict access to superusers only
def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func

@superuser_required
def raw_materials_view(request):
    raw_materials = RawMaterial.objects.all()
    return render(request, 'core/raw_materials.html', {'raw_materials': raw_materials})

@superuser_required
def manufacturing_parts_view(request):
    parts = ManufacturingPart.objects.all()
    return render(request, 'core/manufacturing_parts.html', {'parts': parts})

@superuser_required
def products_view(request):
    products = Product.objects.all()
    return render(request, 'core/products.html', {'products': products})

@superuser_required
def orders_view(request):
    orders = Order.objects.all()
    return render(request, 'core/orders.html', {'orders': orders})

@superuser_required
def add_manufacturing_product(request):
    if request.method == 'POST':
        form = ManufacturingProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manufacturing_products')
    else:
        form = ManufacturingProductForm()
    return render(request, 'core/add_manufacturing_product.html', {'form': form})

@superuser_required
def manufacturing_products(request):
    products = ManufacturingProduct.objects.all()
    return render(request, 'core/manufacturing_products.html', {'manufacturing_products': products})

@superuser_required
def edit_manufacturing_product(request, pk):
    product = get_object_or_404(ManufacturingProduct, pk=pk)
    if request.method == 'POST':
        form = ManufacturingProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('manufacturing_products')
    else:
        form = ManufacturingProductForm(instance=product)
    return render(request, 'core/edit_manufacturing_product.html', {'form': form, 'product': product})

@superuser_required
def delete_manufacturing_product(request, pk):
    product = get_object_or_404(ManufacturingProduct, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('manufacturing_products')
    return render(request, 'core/delete_manufacturing_product.html', {'product': product})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def order_raw_materials_view(request):
    if request.method == 'POST':
        form = RawMaterialOrderForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            raw_materials_needed = form.get_raw_material_fields()

            materials_info = []

            for raw_material_name, quantity_needed in raw_materials_needed:
                raw_material_obj = RawMaterial.objects.filter(name__iexact=raw_material_name).first()
                if raw_material_obj:
                    total_available = Order.objects.filter(raw_material=raw_material_obj, status='complete').aggregate(total=Sum('quantity'))['total'] or 0
                    needed_quantity = max(quantity_needed - total_available, 0)
                    materials_info.append({
                        'id': raw_material_obj.id,
                        'name': raw_material_name,
                        'quantity_needed': quantity_needed,
                        'quantity_available': total_available,
                        'quantity_to_order': needed_quantity
                    })
            ids_to_order = [item['id'] for item in materials_info]

            url_name = reverse_lazy('finalize_order')

            # Encode the query parameters
            query_params = urlencode({'ids_to_order': ','.join(map(str, ids_to_order))})

            # Construct the full URL with query parameters
            full_url = f'{url_name}?{query_params}'

            # Use redirect with the constructed URL
            return redirect(full_url)
        else:
            context = {'form': form}
            return render(request, 'core/order_raw_materials.html', context)
    else:
        form = RawMaterialOrderForm()

    return render(request, 'core/order_raw_materials.html', {'form': form})


def finalize_order_view(request, material_id):
    # Retrieve IDs from the query parameters
    ids_to_order = request.GET.getlist('ids_to_order')

    # Fetch the corresponding items from the database
    materials_info = []
    for id in ids_to_order:
        try:
            raw_material = RawMaterial.objects.get(pk=id)
            materials_info.append({
                'id': raw_material.id,
                'name': raw_material.name,
                'quantity_needed': 0,  # Example, adjust according to your logic
                'quantity_available': 0,  # Example, adjust according to your logic
                'quantity_to_order': 0  # Example, adjust according to your logic
            })
        except ObjectDoesNotExist:
            pass  # Handle case where ID does not exist
    if request.method == 'POST':
        PrintFunction(2)
        quantity_to_order = int(request.POST.get('quantity_to_order'))
        raw_material = get_object_or_404(RawMaterial, pk=material_id)

        # Create a new Order for the required raw material
        Order.objects.create(
            user=request.user,
            raw_material=raw_material,
            quantity=quantity_to_order,
            status='complete'
        )
        PrintFunction(3)
        return redirect('order_raw_materials')
    else:
        PrintFunction(4)
        # Extract the materials_info JSON string from the query parameters
        materials_info_json = request.GET.get('materials_info', '{}')
        
        # Parse the JSON string back into a Python object
        materials_info = json.loads(materials_info_json)
        
        # Assuming you want to access the materials_info in the template or elsewhere
        # You can now work with materials_info as a list of dictionaries
        
        raw_material = get_object_or_404(RawMaterial, pk=material_id)
        context = {
            'material': raw_material,
            'quantity_to_order': request.GET.get('quantity_to_order'),
            'materials_info': materials_info  # Pass materials_info to the template
        }
        return render(request, 'core/finalize_order.html', context)

def PrintFunction(n):
    print(f"Hello {n}")