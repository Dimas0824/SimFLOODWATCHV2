from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("devices", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="iotnode",
            name="mqtt_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="iotnode",
            name="simulation_distance_cm",
            field=models.FloatField(default=42.0),
        ),
        migrations.AddField(
            model_name="iotnode",
            name="simulation_drift_bias_cm",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="iotnode",
            name="simulation_mode",
            field=models.CharField(
                choices=[("SCENARIO", "SCENARIO"), ("MANUAL", "MANUAL")],
                default="SCENARIO",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="iotnode",
            name="simulation_water_active",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="iotnode",
            name="simulator_enabled",
            field=models.BooleanField(default=False),
        ),
    ]
