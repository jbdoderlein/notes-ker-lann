from django.contrib import admin

from .models.notes import Alias, NoteClub, NoteSpecial, NoteUser

# Register your models here.
admin.site.register(Alias)
admin.site.register(NoteClub)
admin.site.register(NoteSpecial)
admin.site.register(NoteUser)
