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
                    print("----------------------------------------------------################")
                    print(materials_info[0]['id'])

            context = {
                'form': form,
                'materials_info': materials_info
            }
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