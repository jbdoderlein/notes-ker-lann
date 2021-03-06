# Generated by Django 2.2.19 on 2021-03-21 09:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('treasury', '0002_invoice_remove_png_extension'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Quantity'),
        ),
        migrations.AlterField(
            model_name='specialtransactionproxy',
            name='remittance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transaction_proxies', to='treasury.Remittance', verbose_name='Remittance'),
        ),
    ]
