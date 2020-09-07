from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0003_create_bde_and_kfet'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE member_profile SET address = '' WHERE address IS NULL;",
        ),
        migrations.RunSQL(
            "UPDATE member_profile SET ml_events_registration = '' WHERE ml_events_registration IS NULL;",
        ),
        migrations.RunSQL(
            "UPDATE member_profile SET section = '' WHERE section IS NULL;",
        ),
    ]
