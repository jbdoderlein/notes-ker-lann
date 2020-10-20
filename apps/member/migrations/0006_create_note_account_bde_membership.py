import sys

from django.db import migrations


def give_note_account_permissions(apps, schema_editor):
    """
    Automatically manage the membership of the Note account.
    """
    User = apps.get_model("auth", "user")
    Membership = apps.get_model("member", "membership")
    Role = apps.get_model("permission", "role")

    note = User.objects.filter(username="note")
    if not note.exists():
        # We are in a test environment, don't log error message
        if len(sys.argv) > 1 and sys.argv[1] == 'test':
            return
        print("Warning: Note account was not found. The note account was not imported.")
        print("Make sure you have imported the NK15 database. The new import script handles correctly the permissions.")
        print("This migration will be ignored, you can re-run it if you forgot the note account or ignore it if you "
              "don't want this account.")
        return

    note = note.get()

    # Set for the two clubs a large expiration date and the correct role.
    for m in Membership.objects.filter(user_id=note.id).all():
        m.date_end = "3142-12-12"
        m.roles.set(Role.objects.filter(name="PC Kfet").all())
        m.save()
    # By default, the note account is only authorized to be logged from localhost.
    note.password = "ipbased$127.0.0.1"
    note.is_active = True
    note.save()
    # Ensure that the note of the account is disabled
    note.note.inactivity_reason = 'forced'
    note.note.is_active = False
    note.save()


class Migration(migrations.Migration):
    dependencies = [
        ('member', '0005_remove_null_tag_on_charfields'),
        ('permission', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(give_note_account_permissions),
    ]
