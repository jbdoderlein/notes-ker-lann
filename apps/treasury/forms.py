# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from crispy_forms.helper import FormHelper
from django import forms

from .models import Billing, Product


class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = '__all__'


ProductFormSet = forms.inlineformset_factory(
    Billing,
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
