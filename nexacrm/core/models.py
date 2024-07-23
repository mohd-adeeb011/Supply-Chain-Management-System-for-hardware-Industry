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
    
    def save(self, *args, **kwargs):
        if self.quantity < 0:
            self.quantity = 0  # Prevent saving negative quantity
        super().save(*args, **kwargs)

class ManufacturingPart(models.Model):
    name = models.CharField(max_length=255)
    raw_materials = models.ManyToManyField(RawMaterial)

    def __str__(self):
        return self.name

class ManufacturingProduct(models.Model):
    name = models.CharField(max_length=255)
    raw_material_1 = models.CharField(max_length=255, null=True, blank=True, default=None)
    quantity_1 = models.IntegerField(null=True, blank=True, default=0)
    raw_material_2 = models.CharField(max_length=255, null=True, blank=True, default=None)
    quantity_2 = models.IntegerField(null=True, blank=True, default=0)
    raw_material_3 = models.CharField(max_length=255, null=True, blank=True, default=None)
    quantity_3 = models.IntegerField(null=True, blank=True, default=0)
    raw_material_4 = models.CharField(max_length=255, null=True, blank=True, default=None)
    quantity_4 = models.IntegerField(null=True, blank=True, default=0)
    raw_material_5 = models.CharField(max_length=255, null=True, blank=True, default=None)
    quantity_5 = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    raw_materials = models.ManyToManyField(RawMaterial, through='ProductRawMaterial')
    image = models.ImageField(upload_to='products/')
    total_items = models.IntegerField(default=0)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_orders', null=True)
    status = models.CharField(max_length=20, default='complete')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Inventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_inventories', null=True)  # updated related_name
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BillOfMaterials(models.Model):
    name = models.CharField(max_length=255)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    required_quantity = models.IntegerField()

    def __str__(self):
        return f'{self.product.name} - {self.raw_material.name}'
    

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # def __str__(self):
    #     return f"{self.raw_material.name} - {self.quantity} from {self.raw_material.user.username}"

class ProductRawMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    
    class Meta:
        unique_together = ('product', 'raw_material')

class SoldProduct(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.product.name} sold to {self.user.username} on {self.purchase_date}'