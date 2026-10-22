from django import forms

from .models import ClassSession, Modality


class PublicScheduleFilterForm(forms.Form):
    modality = forms.ModelChoiceField(
        label="Modalidade",
        queryset=Modality.objects.order_by("name"),
        required=False,
        empty_label="Todas as modalidades",
    )
    weekday = forms.ChoiceField(
        label="Dia da semana",
        choices=[("", "Todos os dias"), *ClassSession.Weekday.choices],
        required=False,
    )
    instructor = forms.CharField(
        label="Instrutor",
        required=False,
        max_length=150,
    )
