# main/models.py
from django.db import models
from django.contrib.auth.models import User
from userprofile.models import Userprofile

class RawMaterial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='raw_materials/')
    quantity = models.IntegerField()
    price = models.IntegerField(default=1000)
    def __str__(self):
        return self.name
    
class ManufacturingPart(models.Model):
    name = models.CharField(max_length=255)
    raw_materials = models.ManyToManyField(RawMaterial)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    parts = models.ManyToManyField(ManufacturingPart)
    image = models.ImageField(upload_to='products/')
    total_items = models.IntegerField()
    price = models.IntegerField(default=2000)
    def __str__(self):
        return self.name

class PurchasedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()
    price = models.IntegerField(default=3000)
    

##This is the raw material we have.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        delete_raw_material = False
        
        if self.pk is not None:  # Check if this is an update to an existing order
            previous_order = Order.objects.get(pk=self.pk)
            if previous_order.status != 'complete' and self.status == 'complete':
                self.update_raw_material_quantity()
                if self.raw_material.quantity <= 0:
                    delete_raw_material = True
        elif self.status == 'complete':  # Check if this is a new order with status 'complete'
            self.update_raw_material_quantity()
            if self.raw_material.quantity <= 0:
                delete_raw_material = True

        super().save(*args, **kwargs)

        if delete_raw_material:
            self.raw_material.delete()

    def update_raw_material_quantity(self):
        raw_material = self.raw_material
        raw_material.quantity -= self.quantity
        raw_material.save()

class BillOfMaterials(models.Model):
    name = models.CharField(max_length=255)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    required_quantity = models.IntegerField()

    def __str__(self):
        return f'{self.product.name} - {self.raw_material.name}'


class ManufacturingProduct(models.Model):
    name = models.CharField(max_length=255)
    raw_material_1 = models.CharField(max_length=255, null=True, blank=True)
    quantity_1 = models.IntegerField(null=True, blank=True)
    raw_material_2 = models.CharField(max_length=255, null=True, blank=True)
    quantity_2 = models.IntegerField(null=True, blank=True)
    raw_material_3 = models.CharField(max_length=255, null=True, blank=True)
    quantity_3 = models.IntegerField(null=True, blank=True)
    raw_material_4 = models.CharField(max_length=255, null=True, blank=True)
    quantity_4 = models.IntegerField(null=True, blank=True)
    raw_material_5 = models.CharField(max_length=255, null=True, blank=True)
    quantity_5 = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.raw_material.name} - {self.quantity}"