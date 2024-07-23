from django.shortcuts import render, redirect
from .models import Product, PurchasedProduct, RawMaterial, ManufacturingPart, Product, Order, ManufacturingProduct, CartItem, ProductRawMaterial, Inventory, SoldProduct
from .forms import UserProfileForm, ManufacturingProductForm, PurchaseForm, RawMaterialForm, RawMaterialOrderForm, CartItemForm, ProductRawMaterialForm, ProductForm
from userprofile.models import Userprofile  # Correct import
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from django.urls import reverse_lazy
from urllib.parse import urlencode
from django.core.exceptions import ObjectDoesNotExist
import json
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from collections import defaultdict
from django.db import models

def index(request):
    return render(request, 'core/main_page.html')  # This line is not used anymore but ensure it points correctly

def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = Userprofile.objects.get(user=request.user)
        except Userprofile.DoesNotExist:
            profile = None
    else:
        profile = None
    return {'user_profile': profile}

def main_page(request):
    products = Product.objects.all()
    return render(request, 'core/main_page.html', {'products': products})

@login_required
def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = PurchaseForm(request.POST, product=product)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            purchase.product = product
            if purchase.quantity <= product.total_items:
                total_price = product.price * purchase.quantity
                purchase.save()
                product.total_items -= purchase.quantity
                product.save()

                # Save the sold product information
                SoldProduct.objects.create(
                    product=product,
                    user=request.user,
                    quantity=purchase.quantity,
                    price=total_price
                )

                return redirect('main_page')
            else:
                return render(request, 'core/buy_product.html', {'form': form, 'product': product, 'error': 'Not enough stock'})
    else:
        form = PurchaseForm(product=product)
    return render(request, 'core/buy_product.html', {'form': form, 'product': product})

@login_required
@csrf_protect
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
    raw_material = get_object_or_404(RawMaterial, id=raw_material_id)
    if request.method == 'POST':
        form = RawMaterialForm(request.POST, request.FILES, instance=raw_material)
        if form.is_valid(): 
            form.save()
            messages.success(request, 'Raw material updated successfully!')
            return redirect('list_raw_materials')  # Ensure this URL name is correct
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
    # Fetch orders that are complete and belong to the logged-in vendor
    orders = Order.objects.filter(vendor=request.user, status='complete').order_by('-created_at')
    return render(request, 'core/orders_recieved.html', {'orders': orders})

@login_required
def my_orders(request):
    orders = PurchasedProduct.objects.filter(user=request.user)
    return render(request, 'core/my_orders.html', {'orders': orders})

##==========================================================================================================##
##==========================================================================================================##
##==========================================================================================================##
##==========================================================================================================##
## Admin panel
# Decorator to restrict access to superusers only
def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func

@superuser_required
@login_required
def raw_materials_view(request):
    query = request.GET.get('q')
    if query:
        raw_materials = RawMaterial.objects.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(user__username__icontains=query) |
            models.Q(quantity__icontains=query) |
            models.Q(price__icontains=query)
        )
    else:
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
@login_required
def inventory_view(request):
    query = request.GET.get('q')
    if query:
        inventory = Inventory.objects.filter(
            models.Q(raw_material__name__icontains=query) |
            models.Q(raw_material__description__icontains=query) |
            models.Q(vendor__username__icontains=query) |
            models.Q(quantity__icontains=query)
        )
    else:
        inventory = Inventory.objects.all()
    return render(request, 'core/inventory.html', {'inventory': inventory})

@superuser_required
@login_required
def delete_inventory_item_view(request, item_id):
    inventory_item = get_object_or_404(Inventory, id=item_id)
    inventory_item.delete()
    messages.success(request, f'Inventory item {inventory_item.raw_material.name} has been deleted successfully!')
    return redirect('inventory')

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
        messages.success(request, f'{product.name} has been deleted.')
        return redirect('manufacturing_products')
    return render(request, 'core/delete_manufacturing_product.html', {'product': product})

@superuser_required
@login_required
def order_raw_materials_view(request):
    if request.method == 'POST':
        form = RawMaterialOrderForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            raw_materials_needed = form.get_raw_material_fields()

            materials_info = []
            cart_item_raw_material_ids = CartItem.objects.filter(user=request.user).values_list('raw_material_id', flat=True)

            for raw_material_name, quantity_needed in raw_materials_needed:
                # Use the related field 'raw_material__name' to filter by raw material name in the Order model
                available_raw_material_objs = Inventory.objects.filter(raw_material__name__iexact=raw_material_name)
                raw_material_objs = RawMaterial.objects.filter(name__iexact=raw_material_name)
                total_available = sum([obj.quantity for obj in available_raw_material_objs if obj.quantity is not None])
                quantity_needed = quantity_needed if quantity_needed is not None else 0

                print("Raw material:", raw_material_name)
                print("Total available:", total_available)
                print("Quantity needed:", quantity_needed)

                if raw_material_objs.exists():
                    for raw_material_obj in raw_material_objs:
                        vendor_available = raw_material_obj.quantity

                        if vendor_available == 0:
                            to_buy = 0
                            status = "Out of Stock"
                        elif vendor_available > quantity_needed:
                            if quantity_needed > total_available:
                                to_buy = quantity_needed - total_available
                                status = "Add to Cart"
                            else:
                                to_buy = 0
                                status = "Available in Inventory"
                        else:
                            if quantity_needed > total_available:
                                to_buy = vendor_available
                                status = "Add to Cart"
                            else:
                                to_buy = 0
                                status = "Available in Inventory"

                        materials_info.append({
                            'id': raw_material_obj.id if raw_material_obj.id is not None else 0,
                            'name': raw_material_obj.name,
                            'quantity_needed': quantity_needed,
                            'quantity_available': total_available,
                            'quantity_to_order': to_buy,
                            'status': status,
                            'vendor': raw_material_obj.user.username,
                            'vendor_available': vendor_available,
                            'price': raw_material_obj.price
                        })
                else:
                    # If no raw material objects exist, still add an entry to the materials_info
                    materials_info.append({
                        'id': None,
                        'name': raw_material_name,
                        'quantity_needed': quantity_needed,
                        'quantity_available': total_available,
                        'quantity_to_order': 0,
                        'status': "Out of Stock",
                        'vendor': "N/A",
                        'vendor_available': 0,
                        'price': 0
                    })

            print("Materials info:", materials_info)

            request.session['selected_product_id'] = product.id

            context = {
                'form': form,
                'materials_info': materials_info
            }
            return render(request, 'core/order_raw_materials.html', context)
    else:
        form = RawMaterialOrderForm()

    return render(request, 'core/order_raw_materials.html', {'form': form})

@superuser_required
@login_required
def add_to_cart_view(request, raw_material_id, quantity):
    raw_material = get_object_or_404(RawMaterial, id=raw_material_id)

    product_id = request.session.get('selected_product_id')
    product = get_object_or_404(ManufacturingProduct, id=product_id) if product_id else None

    price = raw_material.price
    if quantity:
        cart_item, created = CartItem.objects.get_or_create(
            user=raw_material.user,
            raw_material=raw_material,
            defaults={'quantity': quantity, 'price': price, 'vendor': raw_material.user}
        )
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.price = price
            cart_item.vendor = raw_material.user  # Ensure the vendor is set correctly
            cart_item.save()
        messages.success(request, f'{raw_material.name} from {raw_material.user.username} has been added to your cart!')
    else:
        messages.error(request, 'Quantity is required.')

    if product:
        raw_materials_needed = [
            (getattr(product, f'raw_material_{i}'), getattr(product, f'quantity_{i}'))
            for i in range(1, 6)
            if getattr(product, f'raw_material_{i}')
        ]

        materials_info = []
        cart_item_raw_material_ids = CartItem.objects.filter(user=request.user).values_list('raw_material_id', flat=True)

        for raw_material_name, quantity_needed in raw_materials_needed:
                # Use the related field 'raw_material__name' to filter by raw material name in the Order model
                available_raw_material_objs = Order.objects.filter(raw_material__name__iexact=raw_material_name)
                raw_material_objs = RawMaterial.objects.filter(name__iexact=raw_material_name)
                total_available = sum([obj.quantity for obj in available_raw_material_objs if obj.quantity is not None])
                quantity_needed = quantity_needed if quantity_needed is not None else 0

                print("Raw material:", raw_material_name)
                print("Total available:", total_available)
                print("Quantity needed:", quantity_needed)

                if raw_material_objs.exists():
                    for raw_material_obj in raw_material_objs:
                        vendor_available = raw_material_obj.quantity

                        if vendor_available == 0:
                            to_buy = 0
                            status = "Out of Stock"
                        elif vendor_available > quantity_needed:
                            if quantity_needed > total_available:
                                to_buy = quantity_needed - total_available
                                status = "Add to Cart"
                            else:
                                to_buy = 0
                                status = "Available in Inventory"
                        else:
                            if quantity_needed > total_available:
                                to_buy = vendor_available
                                status = "Add to Cart"
                            else:
                                to_buy = 0
                                status = "Available in Inventory"

                        materials_info.append({
                            'id': raw_material_obj.id if raw_material_obj.id is not None else 0,
                            'name': raw_material_obj.name,
                            'quantity_needed': quantity_needed,
                            'quantity_available': total_available,
                            'quantity_to_order': to_buy,
                            'status': status,
                            'vendor': raw_material_obj.user.username,
                            'vendor_available': vendor_available,
                            'price': raw_material_obj.price
                        })
                else:
                    # If no raw material objects exist, still add an entry to the materials_info
                    materials_info.append({
                        'id': None,
                        'name': raw_material_name,
                        'quantity_needed': quantity_needed,
                        'quantity_available': total_available,
                        'quantity_to_order': 0,
                        'status': "Out of Stock",
                        'vendor': "N/A",
                        'vendor_available': 0,
                        'price': 0
                    })

                print("Materials info:", materials_info)
        form = RawMaterialOrderForm(initial={'product': product})

        context = {
            'form': form,
            'materials_info': materials_info
        }
        return render(request, 'core/order_raw_materials.html', context)

    return redirect('order_raw_materials')


#######----------------------------Cart Functionality---------------------->>
@superuser_required
@login_required
def view_cart(request):
    cart_items = CartItem.objects.all()
    for item in cart_items:
        item.total_price = item.quantity * item.price
    context = {
        'cart_items': cart_items
    }
    return render(request, 'core/view_cart.html', context)

@superuser_required
@login_required
def remove_from_cart_view(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    messages.success(request, f'{cart_item.raw_material.name} has been removed from your cart!')
    return redirect('view_cart')

@superuser_required
@login_required
def order_item_from_cart_view(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if request.method == 'POST':
        # Create an order for the item
        order = Order.objects.create(
            user=request.user,  # The superuser placing the order
            raw_material=cart_item.raw_material,
            quantity=cart_item.quantity,
            vendor=cart_item.vendor
        )

        # Update the quantity in RawMaterial
        raw_material = cart_item.raw_material
        raw_material.quantity -= cart_item.quantity
        raw_material.save()

        # Check if the raw material quantity is zero or less and delete it
        if raw_material.quantity <= 0:
            raw_material.delete()

        # Update or create inventory item
        inventory_item, created = Inventory.objects.get_or_create(
            user=request.user,
            raw_material=cart_item.raw_material,
            vendor=cart_item.vendor,  # Set the vendor
            defaults={'quantity': 0}
        )
        if not created:
            inventory_item.quantity += cart_item.quantity
        else:
            inventory_item.quantity = cart_item.quantity
        inventory_item.save()
        
        # Remove the item from the cart after ordering
        cart_item.delete()

        messages.success(request, f'Order for {cart_item.raw_material.name} has been placed successfully!')
        return redirect('view_cart')
    
    context = {
        'cart_item': cart_item
    }
    return render(request, 'core/order_from_cart_confirm.html', context)

@superuser_required
@login_required
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            manufacturing_product = form.cleaned_data['manufacturing_product']
            product.save()

            raw_materials_needed = {}

            for i in range(1, 6):
                raw_material_name = getattr(manufacturing_product, f'raw_material_{i}')
                quantity_needed = getattr(manufacturing_product, f'quantity_{i}')
                if raw_material_name and quantity_needed:
                    if raw_material_name in raw_materials_needed:
                        raw_materials_needed[raw_material_name] += quantity_needed
                    else:
                        raw_materials_needed[raw_material_name] = quantity_needed

            for raw_material_name, total_quantity_needed in raw_materials_needed.items():
                raw_materials = RawMaterial.objects.filter(name=raw_material_name)
                if raw_materials.exists():
                    raw_material = raw_materials.first()
                    inventory_item = Inventory.objects.filter(raw_material=raw_material).first()
                    if inventory_item:
                        try:
                            ProductRawMaterial.objects.create(product=product, raw_material=raw_material, quantity=total_quantity_needed)
                            inventory_item.quantity -= total_quantity_needed
                            if inventory_item.quantity <= 0:
                                inventory_item.delete()
                            else:
                                inventory_item.save()
                        except Exception as e:
                            messages.error(request, f"Error processing raw material {raw_material_name}: {str(e)}")
                    else:
                        messages.error(request, f"Raw material {raw_material_name} not found in inventory.")
                else:
                    messages.error(request, f"Raw material {raw_material_name} not found.")
            return redirect('products')
    else:
        form = ProductForm()

    return render(request, 'core/add_product.html', {'form': form})

@superuser_required
@login_required
def edit_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/edit_product.html', {'form': form})

@superuser_required
@login_required
def delete_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('products')
    return render(request, 'core/delete_product_confirm.html', {'product': product})

@superuser_required
@login_required
def sold_products_view(request):
    sold_products = SoldProduct.objects.all()
    return render(request, 'core/sold_products.html', {'sold_products': sold_products})