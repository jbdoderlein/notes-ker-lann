# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Invoice, Product, Remittance


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
        self.helper.add_input(Submit('submit', _("Submit"), attr={'class': 'btn btn-block btn-primary'}))

    class Meta:
        model = Remittance
        fields = ('type', 'comment', )
