# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
import subprocess
from tempfile import mkdtemp

from crispy_forms.helper import FormHelper
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic.base import View, TemplateView
from django_tables2 import SingleTableView
from note.models import SpecialTransaction, NoteSpecial
from note_kfet.settings.base import BASE_DIR
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms import InvoiceForm, ProductFormSet, ProductFormSetHelper, RemittanceForm, LinkTransactionToRemittanceForm
from .models import Invoice, Product, Remittance, SpecialTransactionProxy
from .tables import InvoiceTable, RemittanceTable, SpecialTransactionTable


class InvoiceCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create Invoice
    """
    model = Invoice
    form_class = InvoiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context['form']
        form.helper = FormHelper()
        # Remove form tag on the generation of the form in the template (already present on the template)
        form.helper.form_tag = False
        # The formset handles the set of the products
        form_set = ProductFormSet(instance=form.instance)
        context['formset'] = form_set
        context['helper'] = ProductFormSetHelper()
        context['no_cache'] = True

        return context

    def form_valid(self, form):
        ret = super().form_valid(form)

        # For each product, we save it
        formset = ProductFormSet(self.request.POST, instance=form.instance)
        if formset.is_valid():
            for f in formset:
                # We don't save the product if the designation is not entered, ie. if the line is empty
                if f.is_valid() and f.instance.designation:
                    f.save()
                    f.instance.save()
                else:
                    f.instance = None

        return ret

    def get_success_url(self):
        return reverse_lazy('treasury:invoice_list')


class InvoiceListView(ProtectQuerysetMixin, LoginRequiredMixin, SingleTableView):
    """
    List existing Invoices
    """
    model = Invoice
    table_class = InvoiceTable


class InvoiceUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Create Invoice
    """
    model = Invoice
    form_class = InvoiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context['form']
        form.helper = FormHelper()
        # Remove form tag on the generation of the form in the template (already present on the template)
        form.helper.form_tag = False
        # Fill the intial value for the date field, with the initial date of the model instance
        form.fields['date'].initial = form.instance.date
        # The formset handles the set of the products
        form_set = ProductFormSet(instance=form.instance)
        context['formset'] = form_set
        context['helper'] = ProductFormSetHelper()
        context['no_cache'] = True

        return context

    def form_valid(self, form):
        ret = super().form_valid(form)

        formset = ProductFormSet(self.request.POST, instance=form.instance)
        saved = []
        # For each product, we save it
        if formset.is_valid():
            for f in formset:
                # We don't save the product if the designation is not entered, ie. if the line is empty
                if f.is_valid() and f.instance.designation:
                    f.save()
                    f.instance.save()
                    saved.append(f.instance.pk)
                else:
                    f.instance = None
            # Remove old products that weren't given in the form
            Product.objects.filter(~Q(pk__in=saved), invoice=form.instance).delete()

        return ret

    def get_success_url(self):
        return reverse_lazy('treasury:invoice_list')


class InvoiceRenderView(LoginRequiredMixin, View):
    """
    Render Invoice as a generated PDF with the given information and a LaTeX template
    """

    def get(self, request, **kwargs):
        pk = kwargs["pk"]
        invoice = Invoice.objects.filter(PermissionBackend.filter_queryset(request.user, Invoice, "view")).get(pk=pk)
        products = Product.objects.filter(invoice=invoice).all()

        # Informations of the BDE. Should be updated when the school will move.
        invoice.place = "Cachan"
        invoice.my_name = "BDE ENS Cachan"
        invoice.my_address_street = "61 avenue du Président Wilson"
        invoice.my_city = "94230 Cachan"
        invoice.bank_code = 30003
        invoice.desk_code = 3894
        invoice.account_number = 37280662
        invoice.rib_key = 14
        invoice.bic = "SOGEFRPP"

        # Replace line breaks with the LaTeX equivalent
        invoice.description = invoice.description.replace("\r", "").replace("\n", "\\\\ ")
        invoice.address = invoice.address.replace("\r", "").replace("\n", "\\\\ ")
        # Fill the template with the information
        tex = render_to_string("treasury/invoice_sample.tex", dict(obj=invoice, products=products))

        try:
            os.mkdir(BASE_DIR + "/tmp")
        except FileExistsError:
            pass
        # We render the file in a temporary directory
        tmp_dir = mkdtemp(prefix=BASE_DIR + "/tmp/")

        try:
            with open("{}/invoice-{:d}.tex".format(tmp_dir, pk), "wb") as f:
                f.write(tex.encode("UTF-8"))
            del tex

            # The file has to be rendered twice
            for _ in range(2):
                error = subprocess.Popen(
                    ["pdflatex", "invoice-{}.tex".format(pk)],
                    cwd=tmp_dir,
                    stdin=open(os.devnull, "r"),
                    stderr=open(os.devnull, "wb"),
                    stdout=open(os.devnull, "wb"),
                ).wait()

                if error:
                    raise IOError("An error attempted while generating a invoice (code=" + str(error) + ")")

            # Display the generated pdf as a HTTP Response
            pdf = open("{}/invoice-{}.pdf".format(tmp_dir, pk), 'rb').read()
            response = HttpResponse(pdf, content_type="application/pdf")
            response['Content-Disposition'] = "inline;filename=invoice-{:d}.pdf".format(pk)
        except IOError as e:
            raise e
        finally:
            # Delete all temporary forms
            shutil.rmtree(tmp_dir)

        return response


class RemittanceCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create Remittance
    """
    model = Remittance
    form_class = RemittanceForm

    def get_success_url(self):
        return reverse_lazy('treasury:remittance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["table"] = RemittanceTable(
            data=Remittance.objects.filter(
                PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).all())
        context["special_transactions"] = SpecialTransactionTable(data=SpecialTransaction.objects.none())

        return context


class RemittanceListView(LoginRequiredMixin, TemplateView):
    """
    List existing Remittances
    """
    template_name = "treasury/remittance_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["opened_remittances"] = RemittanceTable(
            data=Remittance.objects.filter(closed=False).filter(
                PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).all())
        context["closed_remittances"] = RemittanceTable(
            data=Remittance.objects.filter(closed=True).filter(
                PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).reverse().all())

        context["special_transactions_no_remittance"] = SpecialTransactionTable(
            data=SpecialTransaction.objects.filter(source__in=NoteSpecial.objects.filter(~Q(remittancetype=None)),
                                                   specialtransactionproxy__remittance=None).filter(
                PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).all(),
            exclude=('remittance_remove', ))
        context["special_transactions_with_remittance"] = SpecialTransactionTable(
            data=SpecialTransaction.objects.filter(source__in=NoteSpecial.objects.filter(~Q(remittancetype=None)),
                                                   specialtransactionproxy__remittance__closed=False).filter(
                PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).all(),
            exclude=('remittance_add', ))

        return context


class RemittanceUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update Remittance
    """
    model = Remittance
    form_class = RemittanceForm

    def get_success_url(self):
        return reverse_lazy('treasury:remittance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["table"] = RemittanceTable(data=Remittance.objects.filter(
            PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).all())
        data = SpecialTransaction.objects.filter(specialtransactionproxy__remittance=self.object).filter(
            PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).all()
        context["special_transactions"] = SpecialTransactionTable(
            data=data,
            exclude=('remittance_add', 'remittance_remove', ) if self.object.closed else ('remittance_add', ))

        return context


class LinkTransactionToRemittanceView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Attach a special transaction to a remittance
    """

    model = SpecialTransactionProxy
    form_class = LinkTransactionToRemittanceForm

    def get_success_url(self):
        return reverse_lazy('treasury:remittance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context["form"]
        form.fields["last_name"].initial = self.object.transaction.last_name
        form.fields["first_name"].initial = self.object.transaction.first_name
        form.fields["bank"].initial = self.object.transaction.bank
        form.fields["amount"].initial = self.object.transaction.amount
        form.fields["remittance"].queryset = form.fields["remittance"] \
            .queryset.filter(remittance_type__note=self.object.transaction.source)

        return context


class UnlinkTransactionToRemittanceView(LoginRequiredMixin, View):
    """
    Unlink a special transaction and its remittance
    """

    def get(self, *args, **kwargs):
        pk = kwargs["pk"]
        transaction = SpecialTransactionProxy.objects.get(pk=pk)

        # The remittance must be open (or inexistant)
        if transaction.remittance and transaction.remittance.closed:
            raise ValidationError("Remittance is already closed.")

        transaction.remittance = None
        transaction.save()

        return redirect('treasury:remittance_list')
