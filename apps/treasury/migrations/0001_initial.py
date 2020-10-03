# Generated by Django 2.2.16 on 2020-09-04 21:41

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('note', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False, verbose_name='Invoice identifier')),
                ('bde', models.CharField(choices=[('Saperlistpopette.png', 'Saper[list]popette'), ('Finalist.png', 'Fina[list]'), ('Listorique.png', '[List]orique'), ('Satellist.png', 'Satel[list]'), ('Monopolist.png', 'Monopo[list]'), ('Kataclist.png', 'Katac[list]')], default='Saperlistpopette.png', max_length=32, verbose_name='BDE')),
                ('object', models.CharField(max_length=255, verbose_name='Object')),
                ('description', models.TextField(verbose_name='Description')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('address', models.TextField(verbose_name='Address')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='Date')),
                ('acquitted', models.BooleanField(default=False, verbose_name='Acquitted')),
                ('locked', models.BooleanField(default=False, help_text="An invoice can't be edited when it is locked.", verbose_name='Locked')),
                ('tex', models.TextField(default='', verbose_name='tex source')),
            ],
            options={
                'verbose_name': 'invoice',
                'verbose_name_plural': 'invoices',
            },
        ),
        migrations.CreateModel(
            name='Remittance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date')),
                ('comment', models.CharField(max_length=255, verbose_name='Comment')),
                ('closed', models.BooleanField(default=False, verbose_name='Closed')),
            ],
            options={
                'verbose_name': 'remittance',
                'verbose_name_plural': 'remittances',
            },
        ),
        migrations.CreateModel(
            name='SpecialTransactionProxy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remittance', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='treasury.Remittance', verbose_name='Remittance')),
                ('transaction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='note.SpecialTransaction')),
            ],
            options={
                'verbose_name': 'special transaction proxy',
                'verbose_name_plural': 'special transaction proxies',
            },
        ),
        migrations.CreateModel(
            name='SogeCredit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credit_transaction', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='note.SpecialTransaction', verbose_name='credit transaction')),
                ('transactions', models.ManyToManyField(related_name='_sogecredit_transactions_+', to='note.MembershipTransaction', verbose_name='membership transactions')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'Credit from the Société générale',
                'verbose_name_plural': 'Credits from the Société générale',
            },
        ),
        migrations.CreateModel(
            name='RemittanceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='note.NoteSpecial')),
            ],
            options={
                'verbose_name': 'remittance type',
                'verbose_name_plural': 'remittance types',
            },
        ),
        migrations.AddField(
            model_name='remittance',
            name='remittance_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='treasury.RemittanceType', verbose_name='Type'),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.CharField(max_length=255, verbose_name='Designation')),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantity')),
                ('amount', models.IntegerField(verbose_name='Unit price')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='treasury.Invoice', verbose_name='invoice')),
            ],
            options={
                'verbose_name': 'product',
                'verbose_name_plural': 'products',
            },
        ),
    ]