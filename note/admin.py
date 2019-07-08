from django.contrib import admin

from .models import NoteClub,NoteSpec,NoteUser
from .models import Alias
# Register your models here.
admin.site.register(NoteClub)
admin.site.register(NoteSpec)
admin.site.register(NoteUser)
admin.site.register(Alias)
