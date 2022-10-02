from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from main.models import HoneypotAttack, Honeypot
from django.shortcuts import get_object_or_404


class IndexView(TemplateView):
    template_name = "index.html"
    # def setup():
    #     pass

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["honeypots"] = Honeypot.objects.all()
        return context


class HoneypotView(TemplateView):
    template_name = "honeypot.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        honeypot = get_object_or_404(Honeypot, pk=kwargs["pk"])
        context["honeypots"] = Honeypot.objects.all()
        attacks = HoneypotAttack.objects.filter(honeypot=honeypot)

        keys = set()
        for attack in attacks:
            for key in attack.data:
                keys.add(key)

        context["attacks"] = attacks
        context["data_keys"] = keys
        return context
