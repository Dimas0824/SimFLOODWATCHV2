from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="IoTNode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("node_id", models.CharField(max_length=50, unique=True)),
                ("node_name", models.CharField(default="FloodWatch Node", max_length=100)),
                ("site_name", models.CharField(default="Kampus", max_length=100)),
                ("location_label", models.CharField(default="Belum diset", max_length=100)),
                ("coordinate_label", models.CharField(default="Belum diset", max_length=100)),
                ("lat", models.FloatField(default=0.0)),
                ("lng", models.FloatField(default=0.0)),
                ("physical_id", models.CharField(blank=True, max_length=50)),
                ("is_active", models.BooleanField(default=True)),
                ("current_scenario", models.CharField(choices=[("normal", "normal"), ("drift", "drift"), ("spike", "spike"), ("dropout", "dropout"), ("flood_rising", "flood_rising"), ("stuck", "stuck"), ("invalid_sensor", "invalid_sensor")], default="normal", max_length=50)),
                ("interval_seconds", models.PositiveSmallIntegerField(default=5)),
                ("baseline_distance_cm", models.FloatField(default=42.0)),
                ("sensor_offset_cm", models.FloatField(default=100.0)),
                ("aman_min_percent", models.FloatField(default=70.0)),
                ("waspada_min_percent", models.FloatField(default=45.0)),
                ("status_hysteresis_percent", models.FloatField(default=3.0)),
                ("distance_change_cm", models.FloatField(default=0.5)),
                ("distance_filter_alpha", models.FloatField(default=0.35)),
                ("distance_decimals", models.PositiveSmallIntegerField(default=1)),
                ("status_hold_ms", models.PositiveIntegerField(default=2500)),
                ("water_debounce_ms", models.PositiveIntegerField(default=250)),
                ("servo_aman", models.PositiveSmallIntegerField(default=0)),
                ("servo_waspada", models.PositiveSmallIntegerField(default=120)),
                ("servo_bahaya", models.PositiveSmallIntegerField(default=170)),
                ("servo_step_degree", models.PositiveSmallIntegerField(default=3)),
                ("servo_step_interval_ms", models.PositiveSmallIntegerField(default=8)),
                ("control_mode", models.CharField(choices=[("AUTO", "AUTO"), ("MANUAL", "MANUAL")], default="AUTO", max_length=10)),
                ("manual_servo_target", models.PositiveSmallIntegerField(default=0)),
                ("current_status", models.CharField(choices=[("AMAN", "AMAN"), ("WASPADA", "WASPADA"), ("BAHAYA", "BAHAYA"), ("ERROR", "ERROR")], default="AMAN", max_length=20)),
                ("current_distance_cm", models.FloatField(blank=True, null=True)),
                ("last_raw_distance_cm", models.FloatField(blank=True, null=True)),
                ("last_water_height_cm", models.FloatField(default=0.0)),
                ("current_water_active", models.BooleanField(default=False)),
                ("current_servo_pos", models.PositiveSmallIntegerField(default=0)),
                ("target_servo_pos", models.PositiveSmallIntegerField(default=0)),
                ("last_sensor_valid", models.PositiveSmallIntegerField(default=0)),
                ("last_status_change_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("last_telemetry_at", models.DateTimeField(blank=True, null=True)),
                ("runtime_state", models.JSONField(blank=True, default=dict)),
                ("last_payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["node_id"]},
        ),
    ]
