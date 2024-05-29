from django.shortcuts import render, redirect
from .models import Product, PurchasedProduct
from .forms import PurchaseForm
from userprofile.models import Userprofile  # Correct import
from .models import RawMaterial
from .forms import RawMaterialForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import UserProfileForm
from .models import Order

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