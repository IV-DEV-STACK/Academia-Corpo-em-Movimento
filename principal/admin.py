from django.contrib import admin

from .models import ClassSession, Modality


@admin.register(Modality)
class ModalityAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ("modality", "weekday", "time", "instructor", "seats")
    list_filter = ("modality", "weekday")
    search_fields = ("instructor", "modality__name")
    ordering = ("weekday", "time")
