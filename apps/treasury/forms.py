# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from note_kfet.inputs import AmountInput, Autocomplete

from .models import Invoice, Product, Remittance, SpecialTransactionProxy


class InvoiceForm(forms.ModelForm):
    """
    Create and generate invoices.
    """

    def clean(self):
        # If the invoice is locked, it can't be updated.
        if self.instance and self.instance.locked:
            for field_name in self.fields:
                self.cleaned_data[field_name] = getattr(self.instance, field_name)
            self.errors.clear()
            self.add_error(None, _('This invoice is locked and can no longer be edited.'))
            return self.cleaned_data
        return super().clean()

    class Meta:
        model = Invoice
        exclude = ('bde', 'date', 'tex', )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            "amount": AmountInput(
                attrs={
                    "negative": True,
                }
            )
        }


# Add a subform per product in the invoice form, and manage correctly the link between the invoice and
# its products. The FormSet will search automatically the ForeignKey in the Product model.
ProductFormSet = forms.inlineformset_factory(
    Invoice,
    Product,
    form=ProductForm,
    extra=1,
)


class ProductFormSetHelper(FormHelper):
    """
    Specify some template information for the product form.
    """

    def __init__(self, form=None):
        super().__init__(form)
        self.form_tag = False
        self.form_method = 'POST'
        self.form_class = 'form-inline'
        self.template = 'bootstrap4/table_inline_formset.html'


class RemittanceForm(forms.ModelForm):
    """
    Create remittances.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()

        # We can't update the type of the remittance once created.
        if self.instance.pk:
            self.fields["remittance_type"].disabled = True
            self.fields["remittance_type"].required = False

        # We display the submit button iff the remittance is open,
        # the close button iff it is open and has a linked transaction
        if not self.instance.closed:
            self.helper.add_input(Submit('submit', _("Submit"), attr={'class': 'btn btn-block btn-primary'}))
            if self.instance.transactions:
                self.helper.add_input(Submit("close", _("Close"), css_class='btn btn-success'))
        else:
            # If the remittance is closed, we can't change anything
            self.fields["comment"].disabled = True
            self.fields["comment"].required = False

    def clean(self):
        # We can't update anything if the remittance is already closed.
        if self.instance.closed:
            self.add_error("comment", _("Remittance is already closed."))

        cleaned_data = super().clean()

        if self.instance.pk and cleaned_data.get("remittance_type") != self.instance.remittance_type:
            self.add_error("remittance_type", _("You can't change the type of the remittance."))

        # The close button is manually handled
        if "close" in self.data:
            self.instance.closed = True
            self.cleaned_data["closed"] = True

        return cleaned_data

    class Meta:
        model = Remittance
        fields = ('remittance_type', 'comment',)


class LinkTransactionToRemittanceForm(forms.ModelForm):
    """
    Attach a special transaction to a remittance.
    """
    remittance = forms.ModelChoiceField(
        queryset=Remittance.objects.none(),
        label=_("Remittance"),
        empty_label=_("No attached remittance"),
        required=False,
    )

    # Since we use a proxy model for special transactions, we add manually the fields related to the transaction
    last_name = forms.CharField(label=_("Last name"))

    first_name = forms.Field(label=_("First name"))

    amount = forms.IntegerField(label=_("Amount"), min_value=0, widget=AmountInput(), disabled=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # Add submit button
        self.helper.add_input(Submit('submit', _("Submit"), attr={'class': 'btn btn-block btn-primary'}))

        self.fields["remittance"].queryset = Remittance.objects.filter(closed=False)

    def clean(self):
        cleaned_data = super().clean()
        self.instance.transaction.last_name = cleaned_data["last_name"]
        self.instance.transaction.first_name = cleaned_data["first_name"]
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        """
        Save the transaction and the remittance.
        """
        self.instance.transaction.save()
        return super().save(commit)

    class Meta:
        model = SpecialTransactionProxy
        fields = ('remittance', )

