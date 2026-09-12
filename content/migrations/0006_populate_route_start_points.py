from django.db import migrations


START_POINTS = {
    "Шантарские острова": ("Комсомольск-на-Амуре", 50.549923, 137.007948),
    "Дуссе-Алинь": ("Посёлок Бриакан", 50.711744, 134.066509),
    "По следам тигра": ("Хабаровск", 48.480223, 135.071917),
    "Амурские протоки": ("Хабаровск, набережная Амура", 48.472607, 135.052664),
}


def populate_start_points(apps, schema_editor):
    route_model = apps.get_model("content", "Route")
    for title, (location, latitude, longitude) in START_POINTS.items():
        route_model.objects.filter(title=title).update(
            start_location=location,
            start_latitude=latitude,
            start_longitude=longitude,
        )


def clear_start_points(apps, schema_editor):
    route_model = apps.get_model("content", "Route")
    route_model.objects.filter(title__in=START_POINTS).update(
        start_location="",
        start_latitude=None,
        start_longitude=None,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0005_route_start_latitude_route_start_location_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_start_points, clear_start_points),
    ]
