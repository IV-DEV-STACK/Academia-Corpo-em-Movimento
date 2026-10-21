from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class Modality(models.Model):
    name = models.CharField("nome", max_length=100)
    description = models.TextField("descrição", blank=True)
    is_active = models.BooleanField("ativa", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "modalidade"
        verbose_name_plural = "modalidades"
        constraints = [
            models.UniqueConstraint(Lower("name"), name="unique_modality_name_ci"),
        ]

    def __str__(self):
        return self.name


class ClassSession(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Segunda-feira"
        TUESDAY = 1, "Terça-feira"
        WEDNESDAY = 2, "Quarta-feira"
        THURSDAY = 3, "Quinta-feira"
        FRIDAY = 4, "Sexta-feira"
        SATURDAY = 5, "Sábado"

    modality = models.ForeignKey(
        Modality,
        on_delete=models.PROTECT,
        related_name="classes",
        verbose_name="modalidade",
    )
    instructor = models.CharField("instrutor", max_length=150)
    weekday = models.PositiveSmallIntegerField("dia da semana", choices=Weekday.choices)
    time = models.TimeField("horário")
    seats = models.PositiveIntegerField("vagas", default=10)

    class Meta:
        ordering = ["weekday", "time", "modality__name"]
        verbose_name = "turma"
        verbose_name_plural = "turmas"
        constraints = [
            models.CheckConstraint(
                condition=Q(seats__gte=0),
                name="class_seats_nonnegative",
            ),
        ]

    def clean(self):
        super().clean()
        if self.weekday is not None and self.weekday not in dict(self.Weekday.choices):
            raise ValidationError(
                {"weekday": "Selecione um dia entre segunda-feira e sábado."}
            )

    def __str__(self):
        return f"{self.modality} - {self.get_weekday_display()} {self.time:%H:%M}"
