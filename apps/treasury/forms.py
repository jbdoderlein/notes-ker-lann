# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime

from crispy_forms.helper import FormHelper
from django import forms

from .models import Invoice, Product


class InvoiceForm(forms.ModelForm):
    date = forms.DateField(
        initial=datetime.date.today,
        widget=forms.TextInput(attrs={'type': 'date'})
    )

    def clean_date(self):
        self.instance.date = self.data.get("date")

    class Meta:
        model = Invoice
        fields = '__all__'


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
