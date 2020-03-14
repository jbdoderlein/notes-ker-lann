# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, UpdateView, TemplateView
from django_tables2 import SingleTableView

from .forms import TransactionTemplateForm
from .models import Transaction, TransactionTemplate, Alias, TemplateTransaction, NoteSpecial
from .models.transactions import SpecialTransaction
from .tables import HistoryTable


class TransactionCreate(LoginRequiredMixin, TemplateView):
    """
    Show transfer page

    TODO: If user have sufficient rights, they can transfer from an other note
    """
    template_name = "note/transaction_form.html"

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('Transfer money')
        context['polymorphic_ctype'] = ContentType.objects.get_for_model(Transaction).pk
        context['special_polymorphic_ctype'] = ContentType.objects.get_for_model(SpecialTransaction).pk
        context['special_types'] = NoteSpecial.objects.order_by("special_type").all()

        return context


class NoteAutocomplete(autocomplete.Select2QuerySetView):
    """
    Auto complete note by aliases
    """

    def get_queryset(self):
        """
        Quand une personne cherche un alias, une requête est envoyée sur l'API dédiée à l'auto-complétion.
        Cette fonction récupère la requête, et renvoie la liste filtrée des aliases.
        """
        #  Un utilisateur non connecté n'a accès à aucune information
        if not self.request.user.is_authenticated:
            return Alias.objects.none()

        qs = Alias.objects.all()

        # self.q est le paramètre de la recherche
        if self.q:
            qs = qs.filter(Q(name__regex="^" + self.q) | Q(normalized_name__regex="^" + Alias.normalize(self.q))) \
                .order_by('normalized_name').distinct()

        # Filtrage par type de note (user, club, special)
        note_type = self.forwarded.get("note_type", None)
        if note_type:
            types = str(note_type).lower()
            if "user" in types:
                qs = qs.filter(note__polymorphic_ctype__model="noteuser")
            elif "club" in types:
                qs = qs.filter(note__polymorphic_ctype__model="noteclub")
            elif "special" in types:
                qs = qs.filter(note__polymorphic_ctype__model="notespecial")
            else:
                qs = qs.none()

        return qs

    def get_result_label(self, result):
        # Gère l'affichage de l'alias dans la recherche
        res = result.name
        note_name = str(result.note)
        if res != note_name:
            res += " (aka. " + note_name + ")"
        return res

    def get_result_value(self, result):
        # Le résultat renvoyé doit être l'identifiant de la note, et non de l'alias
        return str(result.note.pk)


class TransactionTemplateCreateView(LoginRequiredMixin, CreateView):
    """
    Create TransactionTemplate
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm


class TransactionTemplateListView(LoginRequiredMixin, ListView):
    """
    List TransactionsTemplates
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm


class TransactionTemplateUpdateView(LoginRequiredMixin, UpdateView):
    """
    """
    model = TransactionTemplate
    form_class = TransactionTemplateForm


class ConsoView(LoginRequiredMixin, SingleTableView):
    """
    Consume
    """
    queryset = Transaction.objects.order_by("-id").all()[:50]
    template_name = "note/conso_form.html"

    # Transaction history table
    table_class = HistoryTable
    table_pagination = {"per_page": 50}

    def get_context_data(self, **kwargs):
        """
        Add some context variables in template such as page title
        """
        context = super().get_context_data(**kwargs)
        from django.db.models import Count
        buttons = TransactionTemplate.objects.filter(display=True) \
            .annotate(clicks=Count('templatetransaction')).order_by('category__name', 'name')
        context['transaction_templates'] = buttons
        context['most_used'] = buttons.order_by('-clicks', 'name')[:10]
        context['title'] = _("Consumptions")
        context['polymorphic_ctype'] = ContentType.objects.get_for_model(TemplateTransaction).pk

        # select2 compatibility
        context['no_cache'] = True

        return context
