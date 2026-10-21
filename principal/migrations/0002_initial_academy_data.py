from django.db import migrations


def add_initial_data(apps, schema_editor):
    Modality = apps.get_model("principal", "Modality")
    ClassSession = apps.get_model("principal", "ClassSession")
    database = schema_editor.connection.alias

    modalities = {
        "Musculação": Modality.objects.using(database).update_or_create(
            name="Musculação",
            defaults={
                "description": "Treino com pesos, acompanhamento individual",
                "is_active": True,
            },
        )[0],
        "Pilates": Modality.objects.using(database).update_or_create(
            name="Pilates",
            defaults={
                "description": "Solo e aparelhos, turmas pequenas",
                "is_active": True,
            },
        )[0],
        "Funcional": Modality.objects.using(database).update_or_create(
            name="Funcional",
            defaults={
                "description": "Circuito de alta intensidade",
                "is_active": True,
            },
        )[0],
        "Natação": Modality.objects.using(database).update_or_create(
            name="Natação",
            defaults={
                "description": "Piscina aquecida (em reforma)",
                "is_active": False,
            },
        )[0],
    }

    initial_classes = [
        ("Pilates", 0, "07:30", "Rafael", 8),
        ("Musculação", 0, "19:00", "Carla", 15),
        ("Funcional", 1, "06:30", "Diego", 12),
        ("Musculação", 1, "18:00", "Carla", 15),
        ("Pilates", 2, "07:30", "Rafael", 8),
        ("Funcional", 5, "09:00", "Diego", 20),
    ]

    for modality_name, weekday, time, instructor, seats in initial_classes:
        ClassSession.objects.using(database).get_or_create(
            modality=modalities[modality_name],
            weekday=weekday,
            time=time,
            instructor=instructor,
            defaults={"seats": seats},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("principal", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_initial_data, migrations.RunPython.noop),
    ]
