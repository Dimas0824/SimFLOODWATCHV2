from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("devices", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Telemetry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField()),
                ("jarak_cm", models.FloatField()),
                ("raw_jarak_cm", models.FloatField()),
                ("water_height_cm", models.FloatField(default=0.0)),
                ("water_switch", models.BooleanField(default=False)),
                ("status", models.CharField(choices=[("AMAN", "AMAN"), ("WASPADA", "WASPADA"), ("BAHAYA", "BAHAYA"), ("ERROR", "ERROR")], max_length=20)),
                ("servo_pos", models.PositiveSmallIntegerField()),
                ("servo_pos_control", models.PositiveSmallIntegerField()),
                ("sensor_valid", models.PositiveSmallIntegerField(default=0)),
                ("scenario", models.CharField(max_length=50)),
                ("control_mode", models.CharField(choices=[("AUTO", "AUTO"), ("MANUAL", "MANUAL")], max_length=10)),
                ("published_to_mqtt", models.BooleanField(default=False)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("node", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="telemetry_records", to="devices.iotnode")),
            ],
            options={"ordering": ["-timestamp", "-id"]},
        ),
        migrations.AddIndex(
            model_name="telemetry",
            index=models.Index(fields=["node", "-timestamp"], name="telemetry_t_node_id_00eef6_idx"),
        ),
        migrations.AddIndex(
            model_name="telemetry",
            index=models.Index(fields=["status", "-timestamp"], name="telemetry_t_status_4e68de_idx"),
        ),
    ]
