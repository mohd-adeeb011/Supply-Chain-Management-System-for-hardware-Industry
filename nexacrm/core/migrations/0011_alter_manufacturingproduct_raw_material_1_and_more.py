# Generated by Django 5.0.6 on 2024-07-21 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_manufacturingproduct_quantity_1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manufacturingproduct',
            name='raw_material_1',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='manufacturingproduct',
            name='raw_material_2',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='manufacturingproduct',
            name='raw_material_3',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='manufacturingproduct',
            name='raw_material_4',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='manufacturingproduct',
            name='raw_material_5',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
