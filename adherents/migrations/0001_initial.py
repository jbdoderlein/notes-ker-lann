# Generated by Django 2.2.3 on 2019-07-16 07:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, max_length=255, upload_to='', verbose_name='profile picture')),
                ('phone_number', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='phone number')),
                ('section', models.CharField(help_text='e.g. "1A0", "9A♥", "SAPHIRE"', max_length=255, verbose_name='section')),
                ('genre', models.CharField(blank=True, choices=[(None, 'ND'), ('M', 'M'), ('F', 'F')], max_length=1, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('paid', models.BooleanField(default=False, verbose_name='paid')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='is deleted')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user profile',
                'verbose_name_plural': 'user profile',
            },
        ),
        migrations.CreateModel(
            name='MembershipFee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(max_length=255, verbose_name='date')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='amount')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'membership fee',
                'verbose_name_plural': 'membership fees',
            },
        ),
    ]
