from django.conf import settings
from django.shortcuts import render

from .forms import PublicScheduleFilterForm
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
    filters = PublicScheduleFilterForm(request.GET or None)
    classes = ClassSession.objects.select_related("modality")

    if filters.is_valid():
        modality = filters.cleaned_data["modality"]
        weekday = filters.cleaned_data["weekday"]
        instructor = filters.cleaned_data["instructor"].strip()
        if modality:
            classes = classes.filter(modality=modality)
        if weekday:
            classes = classes.filter(weekday=weekday)
        if instructor:
            classes = classes.filter(instructor__icontains=instructor)

    return render(
        request,
        "principal/schedule.html",
        {
            "classes": classes,
            "filters": filters,
            "has_filters": any(request.GET.values()),
        },
    )
