from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
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

    def test_homepage_shows_modalities_with_their_status_and_descriptions(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pilates Teste")
        self.assertContains(response, "Aulas de solo")
        self.assertContains(response, "Natação Teste")
        self.assertContains(response, "Ativa")
        self.assertContains(response, "Inativa")
        self.assertContains(response, "Piscina em reforma")
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

    def test_public_schedule_filters_by_modality(self):
        response = self.client.get("/turmas/", {"modality": self.pilates.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["classes"].values_list("modality_id", flat=True)),
            [self.pilates.pk],
        )

    def test_public_schedule_filters_by_weekday(self):
        response = self.client.get(
            "/turmas/",
            {"weekday": ClassSession.Weekday.TUESDAY},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            all(
                weekday == ClassSession.Weekday.TUESDAY
                for weekday in response.context["classes"].values_list(
                    "weekday", flat=True
                )
            )
        )
        self.assertGreater(response.context["classes"].count(), 0)

    def test_public_schedule_searches_partial_instructor_name(self):
        response = self.client.get("/turmas/", {"instructor": "rafa"})

        self.assertEqual(response.status_code, 200)
        instructors = list(
            response.context["classes"].values_list("instructor", flat=True)
        )
        self.assertGreater(len(instructors), 0)
        self.assertTrue(all("rafa" in instructor.lower() for instructor in instructors))

    def test_public_schedule_combines_modality_weekday_and_instructor_filters(self):
        response = self.client.get(
            "/turmas/",
            {
                "modality": self.pilates.pk,
                "weekday": ClassSession.Weekday.MONDAY,
                "instructor": "rafa",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["classes"].count(), 1)
        self.assertContains(response, "Rafael")

    def test_public_schedule_reports_when_filters_have_no_matches(self):
        response = self.client.get("/turmas/", {"instructor": "instrutor inexistente"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhuma turma encontrada")
        self.assertEqual(response.context["classes"].count(), 0)

    def test_invalid_public_filter_is_reported_without_server_error(self):
        response = self.client.get("/turmas/", {"weekday": "domingo"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Não foi possível aplicar os filtros")
        self.assertEqual(response.context["classes"].count(), ClassSession.objects.count())

    def test_both_public_pages_link_to_each_other(self):
        home_response = self.client.get("/")
        schedule_response = self.client.get("/turmas/")

        self.assertContains(home_response, 'href="/turmas/"')
        self.assertContains(schedule_response, 'href="/"')


class AcademyAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        self.modality_admin = ModalityAdmin(Modality, self.site)
        self.class_admin = ClassSessionAdmin(ClassSession, self.site)
        self.pilates = Modality.objects.create(name="Pilates Admin Teste")
        self.functional = Modality.objects.create(name="Funcional Admin Teste")
        self.inactive = Modality.objects.create(
            name="Natação Admin Teste",
            is_active=False,
        )
        ClassSession.objects.create(
            modality=self.pilates,
            instructor="Rafael Instrutor Teste",
            weekday=ClassSession.Weekday.MONDAY,
            time="07:30",
            seats=8,
        )
        ClassSession.objects.create(
            modality=self.functional,
            instructor="Carla Instrutora Teste",
            weekday=ClassSession.Weekday.TUESDAY,
            time="18:00",
            seats=15,
        )
        user = User.objects.create_superuser(
            username="admin-test",
            email="admin-test@example.com",
            password="test-password",
        )
        self.client.force_login(user)

    def test_modality_admin_filters_by_active_status_and_searches_name(self):
        self.assertIn("is_active", self.modality_admin.get_list_filter(self.factory.get("/")))
        self.assertIn("name", self.modality_admin.get_search_fields(self.factory.get("/")))

    def test_modality_admin_displays_name_and_active_status_and_filters_inactive(self):
        response = self.client.get(
            "/admin/principal/modality/",
            {"is_active__exact": "0"},
        )

        self.assertEqual(response.status_code, 200)
        result_ids = [modality.pk for modality in response.context["cl"].result_list]
        self.assertIn(self.inactive.pk, result_ids)
        self.assertNotIn(self.pilates.pk, result_ids)
        self.assertNotIn(self.functional.pk, result_ids)
        self.assertIn("name", response.context["cl"].list_display)
        self.assertIn("is_active", response.context["cl"].list_display)

    def test_class_admin_filters_modality_and_weekday_and_searches_instructor(self):
        request = self.factory.get("/")
        request.user = User(is_superuser=True, is_staff=True, is_active=True)

        self.assertEqual(
            self.class_admin.get_list_filter(request),
            ("modality", "weekday"),
        )
        self.assertIn("instructor", self.class_admin.get_search_fields(request))
        self.assertEqual(
            self.class_admin.get_list_display(request),
            ("modality", "weekday", "time", "instructor", "seats"),
        )
        self.assertEqual(
            self.class_admin.get_fields(request),
            ("modality", "weekday", "time", "instructor", "seats"),
        )
        self.assertTrue(self.class_admin.has_add_permission(request))
        self.assertTrue(self.class_admin.has_delete_permission(request))
        self.assertIn("delete_selected", self.class_admin.get_actions(request))

    def test_class_admin_applies_modality_and_weekday_filters(self):
        response = self.client.get(
            "/admin/principal/classsession/",
            {
                "modality__id__exact": str(self.pilates.pk),
                "weekday__exact": str(ClassSession.Weekday.MONDAY),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [class_session.instructor for class_session in response.context["cl"].result_list],
            ["Rafael Instrutor Teste"],
        )

    def test_class_admin_searches_by_instructor_name(self):
        response = self.client.get(
            "/admin/principal/classsession/",
            {"q": "Carla Instrutora Teste"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [class_session.instructor for class_session in response.context["cl"].result_list],
            ["Carla Instrutora Teste"],
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
