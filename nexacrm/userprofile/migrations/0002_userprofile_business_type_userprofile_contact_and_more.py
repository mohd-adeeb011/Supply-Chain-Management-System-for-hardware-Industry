# Generated by Django 5.0.6 on 2024-05-27 20:24

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='business_type',
            field=models.CharField(choices=[('supplier', 'Raw Material Supplier'), ('dealer', 'Product Dealer')], default='dealer', max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='contact',
            field=models.CharField(default=123, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='location',
            field=models.CharField(default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='name',
            field=models.CharField(default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]