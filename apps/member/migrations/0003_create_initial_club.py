"""Migration member default BDE BDA"""

from django.db import migrations


def create_initial_club(apps, schema_editor):
    """
    The clubs BDE BDA BDS are pre-injected.
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
        membership_fee_paid=3500,
        membership_fee_unpaid=2800,
        membership_duration=396,
        membership_start="2022-08-01",
        membership_end="2023-09-30",
    )

    Club.objects.get_or_create(
        id=2,
        name="BDA",
        email="tresorerie.bda@example.com",
        require_memberships=True,
        membership_fee_paid=2500,
        membership_fee_unpaid=1700,
        membership_duration=396,
        membership_start="2022-08-01",
        membership_end="2023-09-30",
    )

    Club.objects.get_or_create(
        id=3,
        name="BDS",
        email="tresorerie.bds@example.com",
        require_memberships=True,
        membership_fee_paid=3000,
        membership_fee_unpaid=2300,
        membership_duration=396,
        membership_start="2022-08-01",
        membership_end="2023-09-30",
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
    NoteClub.objects.get_or_create(
        id=7,
        club_id=3,
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
        name="BDA",
        normalized_name="bda",
    )
    Alias.objects.get_or_create(
        id=7,
        note_id=7,
        name="BDS",
        normalized_name="bds",
    )


class Migration(migrations.Migration):
    dependencies = [
        ('member', '0002_auto_20220817_2253'),
        ('note', '0002_special_note'),
    ]

    operations = [
        migrations.RunPython(create_initial_club),
    ]
