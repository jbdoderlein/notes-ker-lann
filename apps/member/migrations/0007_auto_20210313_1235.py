# Generated by Django 2.2.19 on 2021-03-13 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0006_create_note_account_bde_membership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='roles',
            field=models.ManyToManyField(related_name='memberships', to='permission.Role', verbose_name='roles'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='promotion',
            field=models.PositiveSmallIntegerField(default=2021, help_text='Year of entry to the school (None if not ENS student)', null=True, verbose_name='promotion'),
        ),
    ]
