# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.utils.translation import gettext_lazy as _
from django_tables2.views import SingleTableView
from note.models import NoteUser, Alias, NoteSpecial
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms import ActivityForm, GuestForm
from .models import Activity, Guest, Entry
from .tables import ActivityTable, GuestTable, EntryTable


class ActivityCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    model = Activity
    form_class = ActivityForm

    def form_valid(self, form):
        form.instance.creater = self.request.user
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        self.object.refresh_from_db()
        return reverse_lazy('activity:activity_detail', kwargs={"pk": self.object.pk})


class ActivityListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    model = Activity
    table_class = ActivityTable

    def get_queryset(self):
        return super().get_queryset().reverse()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Activities")

        upcoming_activities = Activity.objects.filter(date_end__gt=datetime.now())
        context['upcoming'] = ActivityTable(
            data=upcoming_activities.filter(PermissionBackend.filter_queryset(self.request.user, Activity, "view")))

        return context


class ActivityDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    model = Activity
    context_object_name = "activity"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        table = GuestTable(data=Guest.objects.filter(activity=self.object)
                           .filter(PermissionBackend.filter_queryset(self.request.user, Guest, "view")))
        context["guests"] = table

        context["activity_started"] = datetime.now(timezone.utc) > self.object.date_start

        return context


class ActivityUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    model = Activity
    form_class = ActivityForm

    def get_success_url(self, **kwargs):
        return reverse_lazy('activity:activity_detail', kwargs={"pk": self.kwargs["pk"]})


class ActivityInviteView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    model = Guest
    form_class = GuestForm
    template_name = "activity/activity_invite.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.activity = Activity.objects.filter(PermissionBackend.filter_queryset(self.request.user, Activity, "view"))\
            .get(pk=self.kwargs["pk"])
        return form

    def form_valid(self, form):
        form.instance.activity = Activity.objects\
            .filter(PermissionBackend.filter_queryset(self.request.user, Activity, "view")).get(pk=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('activity:activity_detail', kwargs={"pk": self.kwargs["pk"]})


class ActivityEntryView(LoginRequiredMixin, TemplateView):
    template_name = "activity/activity_entry.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        activity = Activity.objects.filter(PermissionBackend.filter_queryset(self.request.user, Activity, "view"))\
            .get(pk=self.kwargs["pk"])
        context["activity"] = activity

        matched = []

        pattern = "^$"
        if "search" in self.request.GET:
            pattern = self.request.GET["search"]

        if not pattern:
            pattern = "^$"

        if pattern[0] != "^":
            pattern = "^" + pattern

        guest_qs = Guest.objects\
            .annotate(balance=F("inviter__balance"), note_name=F("inviter__user__username"))\
            .filter(Q(first_name__regex=pattern) | Q(last_name__regex=pattern)
                    | Q(inviter__alias__name__regex=pattern)
                    | Q(inviter__alias__normalized_name__regex=Alias.normalize(pattern))) \
            .filter(PermissionBackend.filter_queryset(self.request.user, Guest, "view"))\
            .distinct()[:20]
        for guest in guest_qs:
            guest.type = "Invité"
            matched.append(guest)

        note_qs = Alias.objects.annotate(last_name=F("note__noteuser__user__last_name"),
                                         first_name=F("note__noteuser__user__first_name"),
                                         username=F("note__noteuser__user__username"),
                                         note_name=F("name"),
                                         balance=F("note__balance"))\
            .filter(Q(note__polymorphic_ctype__model="noteuser")
                    & (Q(note__noteuser__user__first_name__regex=pattern)
                    | Q(note__noteuser__user__last_name__regex=pattern)
                    | Q(name__regex=pattern)
                    | Q(normalized_name__regex=Alias.normalize(pattern)))) \
            .filter(PermissionBackend.filter_queryset(self.request.user, Alias, "view"))\
            .distinct()[:20]
        for note in note_qs:
            note.type = "Adhérent"
            note.activity = activity
            matched.append(note)

        table = EntryTable(data=matched)
        context["table"] = table

        context["entries"] = Entry.objects.filter(activity=activity)

        context["title"] = _('Entry for activity "{}"').format(activity.name)
        context["noteuser_ctype"] = ContentType.objects.get_for_model(NoteUser).pk
        context["notespecial_ctype"] = ContentType.objects.get_for_model(NoteSpecial).pk

        context["activities_open"] = Activity.objects.filter(open=True).filter(
            PermissionBackend.filter_queryset(self.request.user, Activity, "view")).filter(
            PermissionBackend.filter_queryset(self.request.user, Activity, "change")).all()

        return context
