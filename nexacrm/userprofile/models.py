from django.db import models
from django.contrib.auth.models import User

class Userprofile(models.Model):
    USER_TYPES = [
        ('supplier', 'Raw Material Supplier'),
        ('customer', 'Customer')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    shop = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    business_type = models.CharField(max_length=50, choices=USER_TYPES, default='customer')

    
    def __str__(self):
        return self.name