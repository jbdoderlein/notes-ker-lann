# Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
import subprocess
from tempfile import mkdtemp

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import CreateView, UpdateView
from django.views.generic.base import View
from django_tables2 import SingleTableView
from note_kfet.settings.base import BASE_DIR

from .models import Billing
from .tables import BillingTable


class BillingCreateView(LoginRequiredMixin, CreateView):
    """
    Create Billing
    """
    model = Billing
    fields = '__all__'
    # form_class = ClubForm


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
    fields = '__all__'
    # form_class = BillingForm


class BillingRenderView(LoginRequiredMixin, View):
    """
    Render Billing as generated PDF
    """

    def get(self, request, **kwargs):
        pk = kwargs["pk"]
        billing = Billing.objects.get(pk=pk)

        billing.description = billing.description.replace("\n", "\\newline\n")
        billing.address = billing.address.replace("\n", "\\newline\n")
        tex = render_to_string("treasury/billing_sample.tex", dict(obj=billing))
        try:
            os.mkdir(BASE_DIR + "/tmp")
        except FileExistsError:
            pass
        tmp_dir = mkdtemp(prefix=BASE_DIR + "/tmp/")

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

        error = subprocess.Popen(
            ["pdflatex", "billing-{}.tex".format(pk)],
            cwd=tmp_dir,
            stdin=open(os.devnull, "r"),
            stderr=open(os.devnull, "wb"),
            stdout=open(os.devnull, "wb")
        ).wait()

        pdf = open("{}/billing-{}.pdf".format(tmp_dir, pk), 'rb').read()
        shutil.rmtree(tmp_dir)

        response = HttpResponse(pdf, content_type="application/pdf")
        response['Content-Disposition'] = "inline;filename=billing-{:d}.pdf".format(pk)

        return response
