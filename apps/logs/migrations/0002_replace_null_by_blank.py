from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE logs_changelog SET previous = '' WHERE previous IS NULL;"
        ),
        migrations.RunSQL(
            "UPDATE logs_changelog SET data = '' WHERE data IS NULL;"
        ),
    ]
