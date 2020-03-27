# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Invoice, Product, Remittance, SpecialTransactionProxy


class InvoiceForm(forms.ModelForm):
    """
    Create and generate invoices.
    """

    # Django forms don't support date fields. We have to add it manually
    date = forms.DateField(
        initial=datetime.date.today,
        widget=forms.TextInput(attrs={'type': 'date'})
    )

    def clean_date(self):
        self.instance.date = self.data.get("date")

    class Meta:
        model = Invoice
        exclude = ('bde', )


# Add a subform per product in the invoice form, and manage correctly the link between the invoice and
# its products. The FormSet will search automatically the ForeignKey in the Product model.
ProductFormSet = forms.inlineformset_factory(
    Invoice,
    Product,
    fields='__all__',
    extra=1,
)


class ProductFormSetHelper(FormHelper):
    """
    Specify some template informations for the product form.
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

    # Since we use a proxy model for special transactions, we add manually the fields related to the transaction
    last_name = forms.CharField(label=_("Last name"))

    first_name = forms.Field(label=_("First name"))

    bank = forms.Field(label=_("Bank"))

    amount = forms.IntegerField(label=_("Amount"), min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # Add submit button
        self.helper.add_input(Submit('submit', _("Submit"), attr={'class': 'btn btn-block btn-primary'}))

        self.fields["remittance"].queryset = Remittance.objects.filter(closed=False)

    def clean_last_name(self):
        """
        Replace the first name in the information of the transaction.
        """
        self.instance.transaction.last_name = self.data.get("last_name")
        self.instance.transaction.clean()

    def clean_first_name(self):
        """
        Replace the last name in the information of the transaction.
        """
        self.instance.transaction.first_name = self.data.get("first_name")
        self.instance.transaction.clean()

    def clean_bank(self):
        """
        Replace the bank in the information of the transaction.
        """
        self.instance.transaction.bank = self.data.get("bank")
        self.instance.transaction.clean()

    def clean_amount(self):
        """
        Replace the amount of the transaction.
        """
        self.instance.transaction.amount = self.data.get("amount")
        self.instance.transaction.clean()

    class Meta:
        model = SpecialTransactionProxy
        fields = ('remittance', )
