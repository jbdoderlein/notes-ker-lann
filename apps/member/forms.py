# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import io

from PIL import Image, ImageSequence
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.forms import CheckboxSelectMultiple
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from note.models import NoteSpecial, Alias
from note_kfet.inputs import Autocomplete, AmountInput, DatePickerInput
from permission.models import PermissionMask, Role

from .models import Profile, Club, Membership


class CustomAuthenticationForm(AuthenticationForm):
    permission_mask = forms.ModelChoiceField(
        label=_("Permission mask"),
        queryset=PermissionMask.objects.order_by("rank"),
        empty_label=None,
    )


class UserForm(forms.ModelForm):
    def _get_validation_exclusions(self):
        # Django usernames can only contain letters, numbers, @, ., +, - and _.
        # We want to allow users to have uncommon and unpractical usernames:
        # That is their problem, and we have normalized aliases for us.
        return super()._get_validation_exclusions() + ["username"]

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)


class ProfileForm(forms.ModelForm):
    """
    A form for the extras field provided by the :model:`member.Profile` model.
    """
    report_frequency = forms.IntegerField(required=False, initial=0, label=_("Report frequency"))

    last_report = forms.DateTimeField(required=False, disabled=True, label=_("Last report date"))

    def clean_promotion(self):
        promotion = self.cleaned_data["promotion"]
        if promotion > timezone.now().year:
            self.add_error("promotion", _("You can't register to the note if you come from the future."))
        return promotion

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].widget.attrs.update({"placeholder": "4 avenue des Sciences, 91190 GIF-SUR-YVETTE"})
        self.fields['promotion'].widget.attrs.update({"max": timezone.now().year})

    @transaction.atomic
    def save(self, commit=True):
        if not self.instance.section or (("department" in self.changed_data
                                         or "promotion" in self.changed_data) and "section" not in self.changed_data):
            self.instance.section = self.instance.section_generated
        return super().save(commit)

    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ('user', 'email_confirmed', 'registration_valid', )


class ImageForm(forms.Form):
    """
    Form used for the js interface for profile picture
    """
    image = forms.ImageField(required=False,
                             label=_('select an image'),
                             help_text=_('Maximal size: 2MB'))
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    def clean(self):
        """
        Load image and crop

        In the future, when Pillow will support APNG we will be able to
        simplify this code to save only PNG/APNG.
        """
        cleaned_data = super().clean()

        # Image size is limited by Django DATA_UPLOAD_MAX_MEMORY_SIZE
        image = cleaned_data.get('image')
        if image:
            # Let Pillow detect and load image
            # If it is an animation, then there will be multiple frames
            try:
                im = Image.open(image)
            except OSError:
                # Rare case in which Django consider the upload file as an image
                # but Pil is unable to load it
                raise forms.ValidationError(_('This image cannot be loaded.'))

            # Crop each frame
            x = cleaned_data.get('x', 0)
            y = cleaned_data.get('y', 0)
            w = cleaned_data.get('width', 200)
            h = cleaned_data.get('height', 200)
            frames = []
            for frame in ImageSequence.Iterator(im):
                frame = frame.crop((x, y, x + w, y + h))
                frame = frame.resize(
                    (settings.PIC_WIDTH, settings.PIC_RATIO * settings.PIC_WIDTH),
                    Image.ANTIALIAS,
                )
                frames.append(frame)

            # Save
            om = frames.pop(0)  # Get first frame
            om.info = im.info  # Copy metadata
            image.file = io.BytesIO()
            if len(frames) > 1:
                # Save as GIF
                om.save(image.file, "GIF", save_all=True, append_images=list(frames), loop=0)
            else:
                # Save as PNG
                om.save(image.file, "PNG")

        return cleaned_data


class ClubForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        if not self.instance.pk:    # Creating a club
            if Alias.objects.filter(normalized_name=Alias.normalize(self.cleaned_data["name"])).exists():
                self.add_error('name', _("An alias with a similar name already exists."))

        return cleaned_data

    class Meta:
        model = Club
        fields = '__all__'
        widgets = {
            "membership_fee_paid": AmountInput(),
            "membership_fee_unpaid": AmountInput(),
            "parent_club": Autocomplete(
                Club,
                resetable=True,
                attrs={
                    'api_url': '/api/members/club/',
                }
            ),
            "membership_start": DatePickerInput(),
            "membership_end": DatePickerInput(),
        }


class MembershipForm(forms.ModelForm):
    credit_type = forms.ModelChoiceField(
        queryset=NoteSpecial.objects,
        label=_("Credit type"),
        empty_label=_("No credit"),
        required=False,
        help_text=_("You can credit the note of the user."),
    )

    credit_amount = forms.IntegerField(
        label=_("Credit amount"),
        required=False,
        initial=0,
        widget=AmountInput(),
    )

    last_name = forms.CharField(
        label=_("Last name"),
        required=False,
    )

    first_name = forms.CharField(
        label=_("First name"),
        required=False,
    )

    class Meta:
        model = Membership
        fields = ('user', 'date_start')
        # Le champ d'utilisateur est remplacé par un champ d'auto-complétion.
        # Quand des lettres sont tapées, une requête est envoyée sur l'API d'auto-complétion
        # et récupère les noms d'utilisateur valides
        widgets = {
            'user':
                Autocomplete(
                    User,
                    attrs={
                        'api_url': '/api/user/',
                        'name_field': 'username',
                        'placeholder': 'Nom ...',
                    },
                ),
            'date_start': DatePickerInput(),
        }


class MembershipRolesForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects,
        label=_("User"),
        disabled=True,
        widget=Autocomplete(
            User,
            attrs={
                'api_url': '/api/user/',
                'name_field': 'username',
                'placeholder': 'Nom ...',
            },
        ),
    )

    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        label=_("Roles"),
        widget=CheckboxSelectMultiple(),
    )

    class Meta:
        model = Membership
        fields = ('user', 'roles')
