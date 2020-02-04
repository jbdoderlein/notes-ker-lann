#!/usr/bin/env python

from django import forms
from .models import TransactionTemplate, Transaction

class TransactionTemplateForm(forms.ModelForm):
    class Meta:
        model = TransactionTemplate
        fields ='__all__'

class ConsoForm(forms.ModelForm):
    def save(self, commit=True):
        button: TransactionTemplate = TransactionTemplate.objects.filter(name=self.data['button']).get()
        self.instance.destination = button.destination
        self.instance.amount = button.amount
        self.instance.transaction_type = 'bouton'
        self.instance.reason = button.name
        super().save(commit)

    class Meta:
        model = Transaction
        fields = ('source',)
