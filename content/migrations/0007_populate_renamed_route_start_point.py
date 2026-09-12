from django.db import migrations


def populate_renamed_route(apps, schema_editor):
    route_model = apps.get_model("content", "Route")
    route_model.objects.filter(
        start_latitude__isnull=True,
        start_longitude__isnull=True,
        visual_style="forest",
    ).update(
        start_location="Хабаровск",
        start_latitude=48.480223,
        start_longitude=135.071917,
    )


def clear_renamed_route(apps, schema_editor):
    route_model = apps.get_model("content", "Route")
    route_model.objects.filter(
        start_location="Хабаровск",
        start_latitude=48.480223,
        start_longitude=135.071917,
    ).update(
        start_location="",
        start_latitude=None,
        start_longitude=None,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0006_populate_route_start_points"),
    ]

    operations = [
        migrations.RunPython(populate_renamed_route, clear_renamed_route),
    ]
