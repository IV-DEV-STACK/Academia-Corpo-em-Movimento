from django.conf import settings
from django.shortcuts import render

from .models import ClassSession, Modality


def home(request):
    return render(
        request,
        "principal/home.html",
        {
            "modalities": Modality.objects.filter(is_active=True),
            "academy_address": settings.ACADEMY_ADDRESS,
            "academy_phone": settings.ACADEMY_PHONE,
        },
    )


def schedule(request):
    return render(
        request,
        "principal/schedule.html",
        {"classes": ClassSession.objects.select_related("modality")},
    )
