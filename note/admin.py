from django.contrib import admin

from .models.notes import Alias, NoteClub, NoteSpecial, NoteUser


class AliasInlines(admin.TabularInline):
    """
    Define user and club aliases when editing their note
    """
    extra = 0
    model = Alias


class NoteClubAdmin(admin.ModelAdmin):
    """
    Admin customisation for NoteClub
    """
    inlines = (AliasInlines,)
    list_display = ('club', 'balance', 'is_active')
    list_filter = ('is_active',)
    search_fields = ['club__name']


class NoteSpecialAdmin(admin.ModelAdmin):
    """
    Admin customisation for NoteSpecial
    """
    list_display = ('special_type', 'balance', 'is_active')


class NoteUserAdmin(admin.ModelAdmin):
    """
    Admin customisation for NoteUser
    """
    inlines = (AliasInlines,)
    list_display = ('user', 'balance', 'is_active')
    list_filter = ('is_active',)
    search_fields = ['user__username']

    # Organize note by registration date
    date_hierarchy = 'user__date_joined'
    ordering = ['-user__date_joined']


# Register your models here.
admin.site.register(NoteClub, NoteClubAdmin)
admin.site.register(NoteSpecial, NoteSpecialAdmin)
admin.site.register(NoteUser, NoteUserAdmin)
