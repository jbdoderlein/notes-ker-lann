from django.db import migrations


def create_special_notes(apps, schema_editor):
    """
    We create the four special note to make transfers.
    """
    NoteSpecial = apps.get_model("note", "notespecial")
    ContentType = apps.get_model('contenttypes', 'ContentType')
    polymorphic_ctype_id = ContentType.objects.get_for_model(NoteSpecial).id

    NoteSpecial.objects.get_or_create(id=1, special_type="Espèces", polymorphic_ctype_id=polymorphic_ctype_id)
    NoteSpecial.objects.get_or_create(id=2, special_type="Carte bancaire", polymorphic_ctype_id=polymorphic_ctype_id)
    NoteSpecial.objects.get_or_create(id=3, special_type="Chèque", polymorphic_ctype_id=polymorphic_ctype_id)
    NoteSpecial.objects.get_or_create(id=4, special_type="Virement bancaire", polymorphic_ctype_id=polymorphic_ctype_id)


class Migration(migrations.Migration):
    dependencies = [
        ('note', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_special_notes),
    ]
