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
from django.forms import Form
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, DetailView
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import BaseFormView, DeleteView
from django_tables2 import SingleTableView
from note.models import SpecialTransaction, NoteSpecial, Alias
from note_kfet.settings.base import BASE_DIR
from permission.backends import PermissionBackend
from permission.views import ProtectQuerysetMixin

from .forms import InvoiceForm, ProductFormSet, ProductFormSetHelper, RemittanceForm, LinkTransactionToRemittanceForm
from .models import Invoice, Product, Remittance, SpecialTransactionProxy, SogeCredit
from .tables import InvoiceTable, RemittanceTable, SpecialTransactionTable, SogeCreditTable


class InvoiceCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create Invoice
    """
    model = Invoice
    form_class = InvoiceForm
    extra_context = {"title": _("Create new invoice")}

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
    extra_context = {"title": _("Invoices list")}


class InvoiceUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Create Invoice
    """
    model = Invoice
    form_class = InvoiceForm
    extra_context = {"title": _("Update an invoice")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context['form']
        form.helper = FormHelper()
        # Remove form tag on the generation of the form in the template (already present on the template)
        form.helper.form_tag = False
        # The formset handles the set of the products
        form_set = ProductFormSet(instance=self.object)
        context['formset'] = form_set
        context['helper'] = ProductFormSetHelper()
        context['no_cache'] = True

        if self.object.locked:
            for field_name in form.fields:
                form.fields[field_name].disabled = True
            for f in form_set.forms:
                for field_name in f.fields:
                    f.fields[field_name].disabled = True


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


class InvoiceDeleteView(ProtectQuerysetMixin, LoginRequiredMixin, DeleteView):
    """
    Delete a non-validated WEI registration
    """
    model = Invoice
    extra_context = {"title": _("Delete invoice")}

    def get_success_url(self):
        return reverse_lazy('treasury:invoice_list')


class InvoiceRenderView(LoginRequiredMixin, View):
    """
    Render Invoice as a generated PDF with the given information and a LaTeX template
    """

    def get(self, request, **kwargs):
        pk = kwargs["pk"]
        invoice = Invoice.objects.filter(PermissionBackend.filter_queryset(request.user, Invoice, "view")).get(pk=pk)
        tex = invoice.tex

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
            for ignored in range(2):
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
            response['Content-Disposition'] = "inline;filename=Facture%20n°{:d}.pdf".format(pk)
        except IOError as e:
            raise e
        finally:
            # Delete all temporary files
            shutil.rmtree(tmp_dir)

        return response


class RemittanceCreateView(ProtectQuerysetMixin, LoginRequiredMixin, CreateView):
    """
    Create Remittance
    """
    model = Remittance
    form_class = RemittanceForm
    extra_context = {"title": _("Create a new remittance")}

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
    extra_context = {"title": _("Remittances list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        opened_remittances = RemittanceTable(
            data=Remittance.objects.filter(closed=False).filter(
                PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).all(),
            prefix="opened-remittances-",
        )
        opened_remittances.paginate(page=self.request.GET.get("opened-remittances-page", 1), per_page=10)
        context["opened_remittances"] = opened_remittances

        closed_remittances = RemittanceTable(
            data=Remittance.objects.filter(closed=True).filter(
                PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).all(),
            prefix="closed-remittances-",
        )
        closed_remittances.paginate(page=self.request.GET.get("closed-remittances-page", 1), per_page=10)
        context["closed_remittances"] = closed_remittances

        no_remittance_tr = SpecialTransactionTable(
            data=SpecialTransaction.objects.filter(source__in=NoteSpecial.objects.filter(~Q(remittancetype=None)),
                                                   specialtransactionproxy__remittance=None).filter(
                PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).all(),
            exclude=('remittance_remove', ),
            prefix="no-remittance-",
        )
        no_remittance_tr.paginate(page=self.request.GET.get("no-remittance-page", 1), per_page=10)
        context["special_transactions_no_remittance"] = no_remittance_tr

        with_remittance_tr = SpecialTransactionTable(
            data=SpecialTransaction.objects.filter(source__in=NoteSpecial.objects.filter(~Q(remittancetype=None)),
                                                   specialtransactionproxy__remittance__closed=False).filter(
                PermissionBackend.filter_queryset(self.request.user, Remittance, "view")).all(),
            exclude=('remittance_add', ),
            prefix="with-remittance-",
        )
        with_remittance_tr.paginate(page=self.request.GET.get("with-remittance-page", 1), per_page=10)
        context["special_transactions_with_remittance"] = with_remittance_tr

        return context


class RemittanceUpdateView(ProtectQuerysetMixin, LoginRequiredMixin, UpdateView):
    """
    Update Remittance
    """
    model = Remittance
    form_class = RemittanceForm
    extra_context = {"title": _("Update a remittance")}

    def get_success_url(self):
        return reverse_lazy('treasury:remittance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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
    extra_context = {"title": _("Attach a transaction to a remittance")}

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


class SogeCreditListView(LoginRequiredMixin, ProtectQuerysetMixin, SingleTableView):
    """
    List all Société Générale credits
    """
    model = SogeCredit
    table_class = SogeCreditTable
    extra_context = {"title": _("List of credits from the Société générale")}

    def get_queryset(self, **kwargs):
        """
        Filter the table with the given parameter.
        :param kwargs:
        :return:
        """
        qs = super().get_queryset()
        if "search" in self.request.GET:
            pattern = self.request.GET["search"]
            if pattern:
                qs = qs.filter(
                    Q(user__first_name__iregex=pattern)
                    | Q(user__last_name__iregex=pattern)
                    | Q(user__note__alias__name__iregex="^" + pattern)
                    | Q(user__note__alias__normalized_name__iregex="^" + Alias.normalize(pattern))
                )

        if "valid" in self.request.GET:
            q = Q(credit_transaction=None)
            if not self.request.GET["valid"]:
                q = ~q
            qs = qs.filter(q)

        return qs[:20]


class SogeCreditManageView(LoginRequiredMixin, ProtectQuerysetMixin, BaseFormView, DetailView):
    """
    Manage credits from the Société générale.
    """
    model = SogeCredit
    form_class = Form
    extra_context = {"title": _("Manage credits from the Société générale")}

    def form_valid(self, form):
        if "validate" in form.data:
            self.get_object().validate(True)
        elif "delete" in form.data:
            self.get_object().delete()
        return super().form_valid(form)

    def get_success_url(self):
        if "validate" in self.request.POST:
            return reverse_lazy('treasury:manage_soge_credit', args=(self.get_object().pk,))
        return reverse_lazy('treasury:soge_credits')
