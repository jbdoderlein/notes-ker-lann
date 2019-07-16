from django.contrib import admin

from .models.notes import NoteClub, NoteUser, NoteSpecial, Alias

# Register your models here.
admin.site.register(NoteClub)
admin.site.register(NoteUser)
admin.site.register(NoteSpecial)
admin.site.register(Alias)
