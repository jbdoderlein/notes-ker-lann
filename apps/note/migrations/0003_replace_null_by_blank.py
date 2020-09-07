from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('note', '0002_create_special_notes'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE note_note SET inactivity_reason = '' WHERE inactivity_reason IS NULL;"
        ),
        migrations.RunSQL(
            "UPDATE note_transaction SET invalidity_reason = '' WHERE invalidity_reason IS NULL;"
        ),
    ]
