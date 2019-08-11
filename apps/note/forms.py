#!/usr/bin/env python

from django import forms
from .models import TransactionTemplate

class TransactionTemplateForm(forms.ModelForm):
    class Meta:
        model = TransactionTemplate
        fields ='__all__'
