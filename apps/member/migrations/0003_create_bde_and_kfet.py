from django.db import migrations


def create_bde_and_kfet(apps, schema_editor):
    """
    The clubs BDE and Kfet are pre-injected.
    """
    Club = apps.get_model("member", "club")
    NoteClub = apps.get_model("note", "noteclub")
    Alias = apps.get_model("note", "alias")
    ContentType = apps.get_model('contenttypes', 'ContentType')
    polymorphic_ctype_id = ContentType.objects.get_for_model(NoteClub).id

    Club.objects.get_or_create(
        id=1,
        name="BDE",
        email="tresorerie.bde@example.com",
        require_memberships=True,
        membership_fee_paid=500,
        membership_fee_unpaid=500,
        membership_duration=396,
        membership_start="2021-08-01",
        membership_end="2022-09-30",
    )
    Club.objects.get_or_create(
        id=2,
        name="Kfet",
        parent_club_id=1,
        email="tresorerie.bde@example.com",
        require_memberships=True,
        membership_fee_paid=3500,
        membership_fee_unpaid=3500,
        membership_duration=396,
        membership_start="2021-08-01",
        membership_end="2022-09-30",
    )

    NoteClub.objects.get_or_create(
        id=5,
        club_id=1,
        polymorphic_ctype_id=polymorphic_ctype_id,
    )
    NoteClub.objects.get_or_create(
        id=6,
        club_id=2,
        polymorphic_ctype_id=polymorphic_ctype_id,
    )

    Alias.objects.get_or_create(
        id=5,
        note_id=5,
        name="BDE",
        normalized_name="bde",
    )
    Alias.objects.get_or_create(
        id=6,
        note_id=6,
        name="Kfet",
        normalized_name="kfet",
    )


class Migration(migrations.Migration):
    dependencies = [
        ('member', '0002_auto_20200904_2341'),
        ('note', '0002_create_special_notes'),
    ]

    operations = [
        migrations.RunPython(create_bde_and_kfet),
    ]
