# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
import subprocess
from tempfile import mkdtemp

from crispy_forms.helper import FormHelper
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic.base import View
from django_tables2 import SingleTableView
from note_kfet.settings.base import BASE_DIR

from .forms import BillingForm, ProductFormSet, ProductFormSetHelper
from .models import Billing, Product
from .tables import BillingTable


class BillingCreateView(LoginRequiredMixin, CreateView):
    """
    Create Billing
    """
    model = Billing
    form_class = BillingForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        form.helper = FormHelper()
        form.helper.form_tag = False
        form_set = ProductFormSet(instance=form.instance)
        context['formset'] = form_set
        context['helper'] = ProductFormSetHelper()
        context['no_cache'] = True

        return context

    def form_valid(self, form):
        ret = super().form_valid(form)

        formset = ProductFormSet(self.request.POST, instance=form.instance)
        if formset.is_valid():
            for f in formset:
                if f.is_valid() and f.instance.designation:
                    f.save()
                    f.instance.save()
                else:
                    f.instance = None

        return ret

    def get_success_url(self):
        return reverse_lazy('treasury:billing')


class BillingListView(LoginRequiredMixin, SingleTableView):
    """
    List existing Billings
    """
    model = Billing
    table_class = BillingTable


class BillingUpdateView(LoginRequiredMixin, UpdateView):
    """
    Create Billing
    """
    model = Billing
    form_class = BillingForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        form.helper = FormHelper()
        form.helper.form_tag = False
        form_set = ProductFormSet(instance=form.instance)
        context['formset'] = form_set
        context['helper'] = ProductFormSetHelper()
        context['no_cache'] = True

        return context

    def form_valid(self, form):
        ret = super().form_valid(form)

        formset = ProductFormSet(self.request.POST, instance=form.instance)
        saved = []
        if formset.is_valid():
            for f in formset:
                if f.is_valid() and f.instance.designation:
                    if type(f.instance.pk) == 'number' and f.instance.pk <= 0:
                        f.instance.pk = None
                    f.save()
                    f.instance.save()
                    saved.append(f.instance.pk)
                else:
                    f.instance = None

        Product.objects.filter(~Q(pk__in=saved), billing=form.instance).delete()

        return ret

    def get_success_url(self):
        return reverse_lazy('treasury:billing')


class BillingRenderView(LoginRequiredMixin, View):
    """
    Render Billing as generated PDF
    """

    def get(self, request, **kwargs):
        pk = kwargs["pk"]
        billing = Billing.objects.get(pk=pk)
        products = Product.objects.filter(billing=billing).all()

        billing.description = billing.description.replace("\n", "\\newline\n")
        billing.address = billing.address.replace("\n", "\\newline\n")
        tex = render_to_string("treasury/billing_sample.tex", dict(obj=billing, products=products))
        try:
            os.mkdir(BASE_DIR + "/tmp")
        except FileExistsError:
            pass
        tmp_dir = mkdtemp(prefix=BASE_DIR + "/tmp/")

        try:
            with open("{}/billing-{:d}.tex".format(tmp_dir, pk), "wb") as f:
                f.write(tex.encode("UTF-8"))
            del tex

            error = subprocess.Popen(
                ["pdflatex", "billing-{}.tex".format(pk)],
                cwd=tmp_dir,
                stdin=open(os.devnull, "r"),
                stderr=open(os.devnull, "wb"),
                stdout=open(os.devnull, "wb")
            ).wait()

            if error:
                raise IOError("An error attempted while generating a billing:", error)

            error = subprocess.Popen(
                ["pdflatex", "billing-{}.tex".format(pk)],
                cwd=tmp_dir,
                stdin=open(os.devnull, "r"),
                stderr=open(os.devnull, "wb"),
                stdout=open(os.devnull, "wb")
            ).wait()

            if error:
                raise IOError("An error attempted while generating a billing:", error)

            pdf = open("{}/billing-{}.pdf".format(tmp_dir, pk), 'rb').read()
            response = HttpResponse(pdf, content_type="application/pdf")
            response['Content-Disposition'] = "inline;filename=billing-{:d}.pdf".format(pk)
        except IOError as e:
            raise e
        finally:
            shutil.rmtree(tmp_dir)

        return response
