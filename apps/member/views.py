# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import io
from datetime import datetime, timedelta

from PIL import Image
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.views.generic.edit import FormMixin
from django_tables2.views import SingleTableView
from rest_framework.authtoken.models import Token
from note.forms import ImageForm
from note.models import Alias, NoteUser, NoteSpecial
from note.models.transactions import Transaction, SpecialTransaction
from note.tables import HistoryTable, AliasTable
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms import ProfileForm, ClubForm, MembershipForm, CustomAuthenticationForm
from .models import Club, Membership, Role
from .tables import ClubTable, UserTable, MembershipTable


class CustomLoginView(LoginView):
    """
    Login view, where the user can select its permission mask.
    """
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        self.request.session['permission_mask'] = form.cleaned_data['permission_mask'].rank
        return super().form_valid(form)


class UserUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update the user information.
    """
    model = User
    fields = ['first_name', 'last_name', 'username', 'email']
    template_name = 'member/profile_update.html'
    context_object_name = 'user_object'
    profile_form = ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context['form']
        form.fields['username'].widget.attrs.pop("autofocus", None)
        form.fields['first_name'].widget.attrs.update({"autofocus": "autofocus"})
        form.fields['first_name'].required = True
        form.fields['last_name'].required = True
        form.fields['email'].required = True
        form.fields['email'].help_text = _("This address must be valid.")

        context['profile_form'] = self.profile_form(instance=context['user_object'].profile)
        context['title'] = _("Update Profile")
        return context

    def form_valid(self, form):
        new_username = form.data['username']
        # Si l'utilisateur cherche à modifier son pseudo, le nouveau pseudo ne doit pas être proche d'un alias existant
        note = NoteUser.objects.filter(
            alias__normalized_name=Alias.normalize(new_username))
        if note.exists() and note.get().user != self.object:
            form.add_error('username',
                           _("An alias with a similar name already exists."))
            return super().form_invalid(form)

        profile_form = ProfileForm(
            data=self.request.POST,
            instance=self.object.profile,
        )
        if form.is_valid() and profile_form.is_valid():
            new_username = form.data['username']
            alias = Alias.objects.filter(name=new_username)
            # Si le nouveau pseudo n'est pas un de nos alias,
            # on supprime éventuellement un alias similaire pour le remplacer
            if not alias.exists():
                similar = Alias.objects.filter(
                    normalized_name=Alias.normalize(new_username))
                if similar.exists():
                    similar.delete()

            olduser = User.objects.get(pk=form.instance.pk)

            user = form.save(commit=False)
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            user.save()

            if olduser.email != user.email:
                # If the user changed her/his email, then it is unvalidated and a confirmation link is sent.
                user.profile.email_confirmed = False
                user.profile.send_email_validation_link()

        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        url = 'member:user_detail' if self.object.profile.registration_valid else 'registration:future_user_detail'
        return reverse_lazy(url, args=(self.object.id,))


class UserDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Affiche les informations sur un utilisateur, sa note, ses clubs...
    """
    model = User
    context_object_name = "user_object"
    template_name = "member/profile_detail.html"

    def get_queryset(self, **kwargs):
        """
        We can't display information of a not registered user.
        """
        return super().get_queryset().filter(profile__registration_valid=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context['user_object']
        history_list = \
            Transaction.objects.all().filter(Q(source=user.note) | Q(destination=user.note)).order_by("-id")\
            .filter(PermissionBackend.filter_queryset(self.request.user, Transaction, "view"))
        history_table = HistoryTable(history_list, prefix='transaction-')
        history_table.paginate(per_page=20, page=self.request.GET.get("transaction-page", 1))
        context['history_list'] = history_table

        club_list = Membership.objects.filter(user=user, date_end__gte=datetime.today())\
            .filter(PermissionBackend.filter_queryset(self.request.user, Membership, "view"))
        membership_table = MembershipTable(data=club_list, prefix='membership-')
        membership_table.paginate(per_page=10, page=self.request.GET.get("membership-page", 1))
        context['club_list'] = membership_table
        return context


class UserListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    Display user list, with a search bar
    """
    model = User
    table_class = UserTable
    template_name = 'member/user_list.html'

    def get_queryset(self, **kwargs):
        """
        Filter the user list with the given pattern.
        """
        qs = super().get_queryset().filter(profile__registration_valid=True)
        if "search" in self.request.GET:
            pattern = self.request.GET["search"]

            if not pattern:
                return qs.none()

            qs = qs.filter(
                Q(first_name__iregex=pattern)
                | Q(last_name__iregex=pattern)
                | Q(profile__section__iregex=pattern)
                | Q(profile__username__iregex="^" + pattern)
                | Q(note__alias__name__iregex="^" + pattern)
                | Q(note__alias__normalized_name__iregex=Alias.normalize("^" + pattern))
            )
        else:
            qs = qs.none()

        return qs[:20]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = _("Search user")

        return context


class ProfileAliasView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    View and manage user aliases.
    """
    model = User
    template_name = 'member/profile_alias.html'
    context_object_name = 'user_object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = context['object'].note
        context["aliases"] = AliasTable(note.alias_set.all())
        return context


class PictureUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, FormMixin, DetailView):
    """
    Update profile picture of the user note.
    """
    form_class = ImageForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.POST, self.request.FILES)
        return context

    def get_success_url(self):
        return reverse_lazy('member:user_detail', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        self.object = self.get_object()
        if form.is_valid():
            return self.form_valid(form)
        else:
            print('is_invalid')
            print(form)
            return self.form_invalid(form)

    def form_valid(self, form):
        image_field = form.cleaned_data['image']
        x = form.cleaned_data['x']
        y = form.cleaned_data['y']
        w = form.cleaned_data['width']
        h = form.cleaned_data['height']
        # image crop and resize
        image_file = io.BytesIO(image_field.read())
        # ext = image_field.name.split('.')[-1].lower()
        # TODO: support GIF format
        image = Image.open(image_file)
        image = image.crop((x, y, x + w, y + h))
        image_clean = image.resize((settings.PIC_WIDTH,
                                    settings.PIC_RATIO * settings.PIC_WIDTH),
                                   Image.ANTIALIAS)
        image_file = io.BytesIO()
        image_clean.save(image_file, "PNG")
        image_field.file = image_file
        # renaming
        filename = "{}_pic.png".format(self.object.note.pk)
        image_field.name = filename
        self.object.note.display_image = image_field
        self.object.note.save()
        return super().form_valid(form)


class ProfilePictureUpdateView(PictureUpdateView):
    model = User
    template_name = 'member/profile_picture_update.html'
    context_object_name = 'user_object'


class ManageAuthTokens(LoginRequiredMixin, TemplateView):
    """
    Affiche le jeton d'authentification, et permet de le regénérer
    """
    model = Token
    template_name = "member/manage_auth_tokens.html"

    def get(self, request, *args, **kwargs):
        if 'regenerate' in request.GET and Token.objects.filter(user=request.user).exists():
            Token.objects.get(user=self.request.user).delete()
            return redirect(reverse_lazy('member:auth_token') + "?show",
                            permanent=True)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = Token.objects.get_or_create(user=self.request.user)[0]
        return context


# ******************************* #
#              CLUB               #
# ******************************* #


class ClubCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create Club
    """
    model = Club
    form_class = ClubForm
    success_url = reverse_lazy('member:club_list')

    def form_valid(self, form):
        return super().form_valid(form)


class ClubListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List existing Clubs
    """
    model = Club
    table_class = ClubTable


class ClubDetailView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Display details of a club
    """
    model = Club
    context_object_name = "club"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        club = context["club"]
        if PermissionBackend.check_perm(self.request.user, "member.change_club_membership_start", club):
            club.update_membership_dates()

        club_transactions = Transaction.objects.all().filter(Q(source=club.note) | Q(destination=club.note))\
            .filter(PermissionBackend.filter_queryset(self.request.user, Transaction, "view")).order_by('-id')
        history_table = HistoryTable(club_transactions, prefix="history-")
        history_table.paginate(per_page=20, page=self.request.GET.get('history-page', 1))
        context['history_list'] = history_table
        club_member = Membership.objects.filter(
            club=club,
            date_end__gte=datetime.today(),
        ).filter(PermissionBackend.filter_queryset(self.request.user, Membership, "view"))

        membership_table = MembershipTable(data=club_member, prefix="membership-")
        membership_table.paginate(per_page=20, page=self.request.GET.get('membership-page', 1))
        context['member_list'] = membership_table

        # Check if the user has the right to create a membership, to display the button.
        empty_membership = Membership(
            club=club,
            user=User.objects.first(),
            date_start=datetime.now().date(),
            date_end=datetime.now().date(),
            fee=0,
        )
        context["can_add_members"] = PermissionBackend()\
            .has_perm(self.request.user, "member.add_membership", empty_membership)

        return context


class ClubAliasView(ProtectQuerysetMixin, LoginRequiredMixin, DetailView):
    """
    Manage aliases of a club.
    """
    model = Club
    template_name = 'member/club_alias.html'
    context_object_name = 'club'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = context['object'].note
        context["aliases"] = AliasTable(note.alias_set.all())
        return context


class ClubUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update the information of a club.
    """
    model = Club
    context_object_name = "club"
    form_class = ClubForm
    template_name = "member/club_form.html"

    def get_success_url(self):
        return reverse_lazy("member:club_detail", kwargs={"pk": self.object.pk})


class ClubPictureUpdateView(PictureUpdateView):
    """
    Update the profile picture of a club.
    """
    model = Club
    template_name = 'member/club_picture_update.html'
    context_object_name = 'club'

    def get_success_url(self):
        return reverse_lazy('member:club_detail', kwargs={'pk': self.object.id})


class ClubAddMemberView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Add a membership to a club.
    """
    model = Membership
    form_class = MembershipForm
    template_name = 'member/add_members.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']

        if "club_pk" in self.kwargs:
            # We create a new membership.
            club = Club.objects.filter(PermissionBackend.filter_queryset(self.request.user, Club, "view"))\
                .get(pk=self.kwargs["club_pk"])
            form.fields['credit_amount'].initial = club.membership_fee_paid
            form.fields['roles'].initial = Role.objects.filter(name="Membre de club").all()

            # If the concerned club is the BDE, then we add the option that Société générale pays the membership.
            if club.name != "BDE":
                del form.fields['soge']
            else:
                fee = 0
                bde = Club.objects.get(name="BDE")
                fee += bde.membership_fee_paid
                kfet = Club.objects.get(name="Kfet")
                fee += kfet.membership_fee_paid
                context["total_fee"] = "{:.02f}".format(fee / 100, )
        else:
            # This is a renewal. Fields can be pre-completed.
            old_membership = self.get_queryset().get(pk=self.kwargs["pk"])
            club = old_membership.club
            user = old_membership.user
            form.fields['user'].initial = user
            form.fields['user'].disabled = True
            form.fields['roles'].initial = old_membership.roles.all()
            form.fields['date_start'].initial = old_membership.date_end + timedelta(days=1)
            form.fields['credit_amount'].initial = club.membership_fee_paid if user.profile.paid \
                else club.membership_fee_unpaid
            form.fields['last_name'].initial = user.last_name
            form.fields['first_name'].initial = user.first_name

            # If this is a renewal of a BDE membership, Société générale can pays, if it is not yet done
            if club.name != "BDE" or user.profile.soge:
                del form.fields['soge']
            else:
                fee = 0
                bde = Club.objects.get(name="BDE")
                fee += bde.membership_fee_paid if user.profile.paid else bde.membership_fee_unpaid
                kfet = Club.objects.get(name="Kfet")
                fee += kfet.membership_fee_paid if user.profile.paid else kfet.membership_fee_unpaid
                context["total_fee"] = "{:.02f}".format(fee / 100, )

        context['club'] = club

        return context

    def form_valid(self, form):
        """
        Create membership, check that all is good, make transactions
        """
        # Get the club that is concerned by the membership
        if "club_pk" in self.kwargs:
            club = Club.objects.filter(PermissionBackend.filter_queryset(self.request.user, Club, "view")) \
                .get(pk=self.kwargs["club_pk"])
            user = form.instance.user
        else:
            old_membership = self.get_queryset().get(pk=self.kwargs["pk"])
            club = old_membership.club
            user = old_membership.user

        form.instance.club = club

        # Get form data
        credit_type = form.cleaned_data["credit_type"]
        credit_amount = form.cleaned_data["credit_amount"]
        last_name = form.cleaned_data["last_name"]
        first_name = form.cleaned_data["first_name"]
        bank = form.cleaned_data["bank"]
        soge = form.cleaned_data["soge"] and not user.profile.soge and club.name == "BDE"

        # If Société générale pays, then we auto-fill some data
        if soge:
            credit_type = NoteSpecial.objects.get(special_type="Virement bancaire")
            bde = club
            kfet = Club.objects.get(name="Kfet")
            if user.profile.paid:
                fee = bde.membership_fee_paid + kfet.membership_fee_paid
            else:
                fee = bde.membership_fee_unpaid + kfet.membership_fee_unpaid
            credit_amount = fee
            bank = "Société générale"

        if credit_type is None:
            credit_amount = 0

        if user.profile.paid:
            fee = club.membership_fee_paid
        else:
            fee = club.membership_fee_unpaid
        if user.note.balance + credit_amount < fee and not Membership.objects.filter(
                club__name="Kfet",
                user=user,
                date_start__lte=datetime.now().date(),
                date_end__gte=datetime.now().date(),
        ).exists():
            # Users without a valid Kfet membership can't have a negative balance.
            # Club 2 = Kfet (hard-code :'( )
            # TODO Send a notification to the user (with a mail?) to tell her/him to credit her/his note
            form.add_error('user',
                           _("This user don't have enough money to join this club, and can't have a negative balance."))
            return super().form_invalid(form)

        if club.parent_club is not None:
            if not Membership.objects.filter(user=form.instance.user, club=club.parent_club).exists():
                form.add_error('user', _('User is not a member of the parent club') + ' ' + club.parent_club.name)
                return super().form_invalid(form)

        if Membership.objects.filter(
                user=form.instance.user,
                club=club,
                date_start__lte=form.instance.date_start,
                date_end__gte=form.instance.date_start,
        ).exists():
            form.add_error('user', _('User is already a member of the club'))
            return super().form_invalid(form)

        if club.membership_start and form.instance.date_start < club.membership_start:
            form.add_error('user', _("The membership must start after {:%m-%d-%Y}.")
                           .format(form.instance.club.membership_start))
            return super().form_invalid(form)

        if club.membership_end and form.instance.date_start > club.membership_end:
            form.add_error('user', _("The membership must begin before {:%m-%d-%Y}.")
                           .format(form.instance.club.membership_start))
            return super().form_invalid(form)

        # Now, all is fine, the membership can be created.

        # Credit note before the membership is created.
        if credit_amount > 0:
            if not last_name or not first_name or (not bank and credit_type.special_type == "Chèque"):
                if not last_name:
                    form.add_error('last_name', _("This field is required."))
                if not first_name:
                    form.add_error('first_name', _("This field is required."))
                if not bank and credit_type.special_type == "Chèque":
                    form.add_error('bank', _("This field is required."))
                return self.form_invalid(form)

            SpecialTransaction.objects.create(
                source=credit_type,
                destination=user.note,
                quantity=1,
                amount=credit_amount,
                reason="Crédit " + credit_type.special_type + " (Adhésion " + club.name + ")",
                last_name=last_name,
                first_name=first_name,
                bank=bank,
                valid=True,
            )

        ret = super().form_valid(form)

        # If Société générale pays, then we store the information: the bank can't pay twice to a same person.
        if soge:
            user.profile.soge = True
            user.profile.save()

            kfet = Club.objects.get(name="Kfet")
            kfet_fee = kfet.membership_fee_paid if user.profile.paid else kfet.membership_fee_unpaid

            # Get current membership, to get the end date
            old_membership = Membership.objects.filter(
                club__name="Kfet",
                user=user,
                date_start__lte=datetime.today(),
                date_end__gte=datetime.today(),
            )

            membership = Membership.objects.create(
                club=kfet,
                user=user,
                fee=kfet_fee,
                date_start=old_membership.get().date_end + timedelta(days=1)
                if old_membership.exists() else form.instance.date_start,
            )
            if old_membership.exists():
                membership.roles.set(old_membership.get().roles.all())
            else:
                membership.roles.add(Role.objects.get(name="Adhérent Kfet"))
            membership.save()

        return ret

    def get_success_url(self):
        return reverse_lazy('member:club_detail', kwargs={'pk': self.object.club.id})


class ClubManageRolesView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Manage the roles of a user in a club
    """
    model = Membership
    form_class = MembershipForm
    template_name = 'member/add_members.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = self.object.club
        context['club'] = club
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # We don't create a full membership, we only update one field
        form.fields['user'].disabled = True
        del form.fields['date_start']
        del form.fields['credit_type']
        del form.fields['credit_amount']
        del form.fields['last_name']
        del form.fields['first_name']
        del form.fields['bank']
        return form

    def get_success_url(self):
        return reverse_lazy('member:club_detail', kwargs={'pk': self.object.club.id})
