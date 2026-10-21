from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import RequestFactory, TestCase

from .admin import ClassSessionAdmin, ModalityAdmin
from .models import ClassSession, Modality


class PublicPagesTests(TestCase):
    def setUp(self):
        self.pilates = Modality.objects.create(name="Pilates Teste", description="Aulas de solo")
        self.inactive_modality = Modality.objects.create(
            name="Natação Teste",
            description="Piscina em reforma",
            is_active=False,
        )
        ClassSession.objects.create(
            modality=self.pilates,
            instructor="Rafael",
            weekday=ClassSession.Weekday.MONDAY,
            time="07:30",
            seats=8,
        )
        ClassSession.objects.create(
            modality=self.inactive_modality,
            instructor="Carla",
            weekday=ClassSession.Weekday.TUESDAY,
            time="18:00",
            seats=15,
        )

    def test_homepage_shows_active_modalities_and_descriptions(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pilates Teste")
        self.assertContains(response, "Aulas de solo")
        self.assertNotContains(response, "Natação Teste")
        self.assertContains(response, "Rua Exemplo, 100 - Centro, Caruaru - PE")
        self.assertContains(response, "(81) 90000-0000")
        self.assertContains(response, 'href="/turmas/"')

    def test_schedule_shows_all_classes_ordered_by_weekday_and_time(self):
        response = self.client.get("/turmas/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rafael")
        self.assertContains(response, "Carla")
        self.assertContains(response, "07:30")
        self.assertContains(response, "15")
        classes = list(response.context["classes"])
        ordering = [
            (item.weekday, item.time, item.modality.name)
            for item in classes
        ]
        self.assertEqual(ordering, sorted(ordering))
        test_classes = [
            item for item in classes if item.modality == self.pilates
        ]
        self.assertEqual(
            [item.weekday for item in test_classes],
            [ClassSession.Weekday.MONDAY],
        )
        self.assertContains(response, 'href="/"')

    def test_schedule_displays_all_required_columns(self):
        response = self.client.get("/turmas/")

        headings = ("Modalidade", "Dia da semana", "Horário", "Instrutor", "Vagas")
        for heading in headings:
            with self.subTest(heading=heading):
                self.assertContains(response, heading)


class AcademyAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        self.modality_admin = ModalityAdmin(Modality, self.site)
        self.class_admin = ClassSessionAdmin(ClassSession, self.site)

    def test_modality_admin_filters_by_active_status_and_searches_name(self):
        self.assertIn("is_active", self.modality_admin.get_list_filter(self.factory.get("/")))
        self.assertIn("name", self.modality_admin.get_search_fields(self.factory.get("/")))

    def test_class_admin_filters_modality_and_weekday_and_searches_instructor(self):
        request = self.factory.get("/")

        self.assertEqual(
            self.class_admin.get_list_filter(request),
            ("modality", "weekday"),
        )
        self.assertIn("instructor", self.class_admin.get_search_fields(request))
        self.assertEqual(
            self.class_admin.get_list_display(request),
            ("modality", "weekday", "time", "instructor", "seats"),
        )


class ModelRulesTests(TestCase):
    def test_modality_name_is_unique_ignoring_case(self):
        Modality.objects.create(name="Funcional Teste")
        duplicate = Modality(name="funcional teste")

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_modality_with_classes_cannot_be_deleted(self):
        modality = Modality.objects.create(name="Musculação Teste")
        ClassSession.objects.create(
            modality=modality,
            instructor="Carla",
            weekday=ClassSession.Weekday.MONDAY,
            time="19:00",
            seats=15,
        )

        with self.assertRaises(ProtectedError):
            modality.delete()

    def test_weekday_is_limited_to_monday_through_saturday(self):
        modality = Modality.objects.create(name="Funcional Regra")
        class_session = ClassSession(
            modality=modality,
            instructor="Diego",
            weekday=6,
            time="09:00",
            seats=20,
        )

        with self.assertRaises(ValidationError):
            class_session.full_clean()

    def test_seats_cannot_be_negative(self):
        modality = Modality.objects.create(name="Pilates Regra")
        class_session = ClassSession(
            modality=modality,
            instructor="Rafael",
            weekday=ClassSession.Weekday.MONDAY,
            time="07:30",
            seats=-1,
        )

        with self.assertRaises(ValidationError):
            class_session.full_clean()


class InitialDatasetTests(TestCase):
    def test_initial_modalities_and_classes_are_loaded(self):
        self.assertEqual(Modality.objects.count(), 4)
        self.assertEqual(ClassSession.objects.count(), 6)
        self.assertTrue(Modality.objects.get(name="Pilates").is_active)
        self.assertFalse(Modality.objects.get(name="Natação").is_active)
