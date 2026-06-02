from django.contrib import admin

from .models import Telemetry


@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "node",
        "status",
        "jarak_cm",
        "water_height_cm",
        "water_switch",
        "servo_pos",
        "servo_pos_control",
        "sensor_valid",
        "published_to_mqtt",
    )
    list_filter = ("status", "water_switch", "published_to_mqtt", "scenario", "control_mode")
    search_fields = ("node__node_id", "node__node_name", "node__site_name")
    readonly_fields = ("payload", "created_at")
