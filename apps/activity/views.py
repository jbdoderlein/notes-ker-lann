# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import F, Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, TemplateView, UpdateView
from django_tables2.views import SingleTableView
from note.models import Alias, NoteSpecial, NoteUser
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin, ProtectedCreateView

from .forms import ActivityForm, GuestForm
from .models import Activity, Entry, Guest
from .tables import ActivityTable, EntryTable, GuestTable


class ActivityCreateView(ProtectQuerysetMixin, ProtectedCreateView):
    """
    View to create a new Activity
    """
    model = Activity
    form_class = ActivityForm
    extra_context = {"title": _("Create new activity")}

    def get_sample_object(self):
        return Activity(
            name="",
            description="",
            creater=self.request.user,
            activity_type_id=1,
            organizer_id=1,
            attendees_club_id=1,
            date_start=timezone.now(),
            date_end=timezone.now(),
        )

    def form_valid(self, form):
        form.instance.creater = self.request.user
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        self.object.refresh_from_db()
        return reverse_lazy('activity:activity_detail', kwargs={"pk": self.object.pk})


class ActivityListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    Displays all Activities, and classify if they are on-going or upcoming ones.
    """
    model = Activity
    table_class = ActivityTable
    ordering = ('-date_start',)
    extra_context = {"title": _("Activities")}

    def get_queryset(self):
        return super().get_queryset().distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        upcoming_activities = Activity.objects.filter(date_end__gt=timezone.now())
        context['upcoming'] = ActivityTable(
            data=upcoming_activities.filter(PermissionBackend.filter_queryset(self.request.user, Activity, "view")),
            prefix='upcoming-',
        )

        started_activities = Activity.objects\
            .filter(PermissionBackend.filter_queryset(self.request.user, Activity, "view"))\
            .filter(open=True, valid=True).all()
        context["started_activities"] = started_activities

        return context


class ActivityDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Shows details about one activity. Add guest to context
    """
    model = Activity
    context_object_name = "activity"
    extra_context = {"title": _("Activity detail")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        table = GuestTable(data=Guest.objects.filter(activity=self.object)
                           .filter(PermissionBackend.filter_queryset(self.request.user, Guest, "view")))
        context["guests"] = table

        context["activity_started"] = timezone.now() > timezone.localtime(self.object.date_start)

        return context


class ActivityUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Updates one Activity
    """
    model = Activity
    form_class = ActivityForm
    extra_context = {"title": _("Update activity")}

    def get_success_url(self, **kwargs):
        return reverse_lazy('activity:activity_detail', kwargs={"pk": self.kwargs["pk"]})


class ActivityInviteView(ProtectQuerysetMixin, ProtectedCreateView):
    """
    Invite a Guest, The rules to invites someone are defined in `forms:activity.GuestForm`
    """
    model = Guest
    form_class = GuestForm
    template_name = "activity/activity_form.html"

    def get_sample_object(self):
        """ Creates a standart Guest binds to the Activity"""
        activity = Activity.objects.get(pk=self.kwargs["pk"])
        return Guest(
            activity=activity,
            first_name="",
            last_name="",
            inviter=self.request.user.note,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = context["form"].activity
        context["title"] = _('Invite guest to the activity "{}"').format(activity.name)
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.activity = Activity.objects.filter(PermissionBackend.filter_queryset(self.request.user, Activity, "view"))\
            .get(pk=self.kwargs["pk"])
        form.fields["inviter"].initial = self.request.user.note
        return form

    def form_valid(self, form):
        form.instance.activity = Activity.objects\
            .filter(PermissionBackend.filter_queryset(self.request.user, Activity, "view")).get(pk=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('activity:activity_detail', kwargs={"pk": self.kwargs["pk"]})


class ActivityEntryView(LoginRequiredMixin, TemplateView):
    """
    Manages entry to an activity
    """
    template_name = "activity/activity_entry.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Don't display the entry interface if the user has no right to see it (no right to add an entry for itself),
        it is closed or doesn't manage entries.
        """
        activity = Activity.objects.get(pk=self.kwargs["pk"])

        sample_entry = Entry(activity=activity, note=self.request.user.note)
        if not PermissionBackend.check_perm(self.request.user, "activity.add_entry", sample_entry):
            raise PermissionDenied(_("You are not allowed to display the entry interface for this activity."))

        if not activity.activity_type.manage_entries:
            raise PermissionDenied(_("This activity does not support activity entries."))

        if not activity.open:
            raise PermissionDenied(_("This activity is closed."))
        return super().dispatch(request, *args, **kwargs)

    def get_invited_guest(self, activity):
        """
        Retrieves all Guests to the activity
        """

        guest_qs = Guest.objects\
            .annotate(balance=F("inviter__balance"), note_name=F("inviter__user__username"))\
            .filter(activity=activity)\
            .filter(PermissionBackend.filter_queryset(self.request.user, Guest, "view"))\
            .order_by('last_name', 'first_name').distinct()

        if "search" in self.request.GET and self.request.GET["search"]:
            pattern = self.request.GET["search"]
            if pattern[0] != "^":
                pattern = "^" + pattern
            guest_qs = guest_qs.filter(
                Q(first_name__regex=pattern)
                | Q(last_name__regex=pattern)
                | Q(inviter__alias__name__regex=pattern)
                | Q(inviter__alias__normalized_name__regex=Alias.normalize(pattern))
            )
        else:
            guest_qs = guest_qs.none()
        return guest_qs

    def get_invited_note(self, activity):
        """
        Retrieves all Note that can attend the activity,
        they need to have an up-to-date membership in the attendees_club.
        """
        note_qs = Alias.objects.annotate(last_name=F("note__noteuser__user__last_name"),
                                         first_name=F("note__noteuser__user__first_name"),
                                         username=F("note__noteuser__user__username"),
                                         note_name=F("name"),
                                         balance=F("note__balance"))

        # Keep only users that have a note
        note_qs = note_qs.filter(note__noteuser__isnull=False)

        # Keep only members
        note_qs = note_qs.filter(
            note__noteuser__user__memberships__club=activity.attendees_club,
            note__noteuser__user__memberships__date_start__lte=timezone.now(),
            note__noteuser__user__memberships__date_end__gte=timezone.now(),
        )

        # Filter with permission backend
        note_qs = note_qs.filter(PermissionBackend.filter_queryset(self.request.user, Alias, "view"))

        if "search" in self.request.GET and self.request.GET["search"]:
            pattern = self.request.GET["search"]
            note_qs = note_qs.filter(
                Q(note__noteuser__user__first_name__regex=pattern)
                | Q(note__noteuser__user__last_name__regex=pattern)
                | Q(name__regex=pattern)
                | Q(normalized_name__regex=Alias.normalize(pattern))
            )
        else:
            note_qs = note_qs.none()

        if settings.DATABASES[note_qs.db]["ENGINE"] == 'django.db.backends.postgresql':
            note_qs = note_qs.distinct('note__pk')[:20]
        else:
            # SQLite doesn't support distinct fields. For compatibility reason (in dev mode), the note list will only
            # have distinct aliases rather than distinct notes with a SQLite DB, but it can fill the result page.
            # In production mode, please use PostgreSQL.
            note_qs = note_qs.distinct()[:20]
        return note_qs

    def get_context_data(self, **kwargs):
        """
        Query the list of Guest and Note to the activity and add information to makes entry with JS.
        """
        context = super().get_context_data(**kwargs)

        activity = Activity.objects.filter(PermissionBackend.filter_queryset(self.request.user, Activity, "view"))\
            .distinct().get(pk=self.kwargs["pk"])
        context["activity"] = activity

        matched = []

        for guest in self.get_invited_guest(activity):
            guest.type = "Invité"
            matched.append(guest)

        for note in self.get_invited_note(activity):
            note.type = "Adhérent"
            note.activity = activity
            matched.append(note)

        table = EntryTable(data=matched)
        context["table"] = table

        context["entries"] = Entry.objects.filter(activity=activity)

        context["title"] = _('Entry for activity "{}"').format(activity.name)
        context["noteuser_ctype"] = ContentType.objects.get_for_model(NoteUser).pk
        context["notespecial_ctype"] = ContentType.objects.get_for_model(NoteSpecial).pk

        activities_open = Activity.objects.filter(open=True).filter(
            PermissionBackend.filter_queryset(self.request.user, Activity, "view")).distinct().all()
        context["activities_open"] = [a for a in activities_open
                                      if PermissionBackend.check_perm(self.request.user,
                                                                      "activity.add_entry",
                                                                      Entry(activity=a, note=self.request.user.note,))]

        return context
