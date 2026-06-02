from django.contrib import admin

from .models import IoTNode


@admin.register(IoTNode)
class IoTNodeAdmin(admin.ModelAdmin):
    list_display = (
        "node_id",
        "node_name",
        "site_name",
        "current_status",
        "control_mode",
        "current_scenario",
        "interval_seconds",
        "is_active",
        "last_telemetry_at",
    )
    list_filter = ("is_active", "current_status", "control_mode", "current_scenario")
    search_fields = ("node_id", "node_name", "site_name", "location_label", "physical_id")
    readonly_fields = (
        "current_status",
        "current_distance_cm",
        "last_raw_distance_cm",
        "last_water_height_cm",
        "current_water_active",
        "current_servo_pos",
        "target_servo_pos",
        "last_sensor_valid",
        "last_status_change_at",
        "last_telemetry_at",
        "runtime_state",
        "last_payload",
        "created_at",
        "updated_at",
    )
