# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Invoice, Product, Remittance, SpecialTransactionProxy


class InvoiceForm(forms.ModelForm):
    date = forms.DateField(
        initial=datetime.date.today,
        widget=forms.TextInput(attrs={'type': 'date'})
    )

    def clean_date(self):
        self.instance.date = self.data.get("date")

    class Meta:
        model = Invoice
        exclude = ('bde', )


ProductFormSet = forms.inlineformset_factory(
    Invoice,
    Product,
    fields='__all__',
    extra=1,
)


class ProductFormSetHelper(FormHelper):
    def __init__(self, form=None):
        super().__init__(form)
        self.form_tag = False
        self.form_method = 'POST'
        self.form_class = 'form-inline'
        self.template = 'bootstrap4/table_inline_formset.html'


class RemittanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()

        if self.instance.pk:
            self.fields["type"].disabled = True
            self.fields["type"].required = False

        if not self.instance.closed:
            self.helper.add_input(Submit('submit', _("Submit"), attr={'class': 'btn btn-block btn-primary'}))
            if self.instance.transactions:
                self.helper.add_input(Submit("close", _("Close"), css_class='btn btn-success'))
        else:
            self.fields["comment"].disabled = True
            self.fields["comment"].required = False

    def clean(self):
        if self.instance.closed:
            self.add_error("comment", _("Remittance is already closed."))

        cleaned_data = super().clean()

        if "type" in self.changed_data:
            self.add_error("type", _("You can't change the type of the remittance."))

        if "close" in self.data:
            self.instance.closed = True
            self.cleaned_data["closed"] = True

        return cleaned_data

    class Meta:
        model = Remittance
        fields = ('type', 'comment', )


class LinkTransactionToRemittanceForm(forms.ModelForm):
    last_name = forms.CharField(label=_("Last name"))

    first_name = forms.Field(label=_("First name"))

    bank = forms.Field(label=_("Bank"))

    amount = forms.IntegerField(label=_("Amount"), min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _("Submit"), attr={'class': 'btn btn-block btn-primary'}))

    def clean_last_name(self):
        self.instance.transaction.last_name = self.data.get("last_name")
        self.instance.transaction.clean()

    def clean_first_name(self):
        self.instance.transaction.first_name = self.data.get("first_name")
        self.instance.transaction.clean()

    def clean_bank(self):
        self.instance.transaction.bank = self.data.get("bank")
        self.instance.transaction.clean()

    def clean_amount(self):
        self.instance.transaction.amount = self.data.get("amount")
        self.instance.transaction.clean()

    class Meta:
        model = SpecialTransactionProxy
        fields = ('remittance', )
