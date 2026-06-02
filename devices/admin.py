from django.contrib import admin
from django.utils.html import format_html

from .forms import IoTNodeAdminForm
from .models import IoTNode


@admin.register(IoTNode)
class IoTNodeAdmin(admin.ModelAdmin):
    form = IoTNodeAdminForm
    list_display = (
        "node_id",
        "node_name",
        "site_name",
        "current_status",
        "control_mode",
        "simulation_mode",
        "current_scenario",
        "interval_seconds",
        "simulator_enabled",
        "mqtt_enabled",
        "is_active",
        "last_telemetry_at",
    )
    list_filter = (
        "is_active",
        "simulator_enabled",
        "mqtt_enabled",
        "current_status",
        "control_mode",
        "simulation_mode",
        "current_scenario",
    )
    search_fields = ("node_id", "node_name", "site_name", "location_label", "physical_id")
    readonly_fields = (
        "simulation_console_help",
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
    fieldsets = (
        (
            "Identitas Node",
            {
                "fields": (
                    "node_id",
                    "node_name",
                    "site_name",
                    "location_label",
                    "coordinate_label",
                    "lat",
                    "lng",
                    "physical_id",
                    "is_active",
                )
            },
        ),
        (
            "Loop Simulator",
            {
                "fields": (
                    "simulator_enabled",
                    "mqtt_enabled",
                    "interval_seconds",
                    "simulation_console_help",
                )
            },
        ),
        (
            "Kontrol Simulasi Interaktif",
            {
                "fields": (
                    "simulation_mode",
                    "simulation_distance_cm",
                    "simulation_water_active",
                    "simulation_drift_bias_cm",
                    "current_scenario",
                ),
                "description": "Mode MANUAL dipakai untuk simulasi ala Wokwi: jarak dari slider, water switch dari toggle, drift bias dari slider. Mode SCENARIO mempertahankan generator lama.",
            },
        ),
        (
            "Kalibrasi Sensor dan Status",
            {
                "fields": (
                    "baseline_distance_cm",
                    "sensor_offset_cm",
                    "aman_min_percent",
                    "waspada_min_percent",
                    "status_hysteresis_percent",
                    "distance_change_cm",
                    "distance_filter_alpha",
                    "distance_decimals",
                    "status_hold_ms",
                    "water_debounce_ms",
                )
            },
        ),
        (
            "Servo",
            {
                "fields": (
                    "control_mode",
                    "manual_servo_target",
                    "servo_aman",
                    "servo_waspada",
                    "servo_bahaya",
                    "servo_step_degree",
                    "servo_step_interval_ms",
                )
            },
        ),
        (
            "Runtime Saat Ini",
            {
                "fields": (
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
            },
        ),
    )

    @admin.display(description="Panduan Worker")
    def simulation_console_help(self, obj: IoTNode | None) -> str:
        node_hint = obj.node_id if obj else "FW-1234ABCD"
        return format_html(
            "<div>"
            "<p><strong>Loop kontinu tidak dijalankan oleh halaman admin.</strong></p>"
            "<p>Jalankan worker terpisah agar node publish periodik ke AWS IoT Core:</p>"
            "<pre style='white-space:pre-wrap;'>.venv\\Scripts\\python.exe manage.py run_simulator_worker --node-id {}</pre>"
            "<p>Jika ingin semua node yang <code>simulator_enabled=true</code> berjalan sekaligus:</p>"
            "<pre style='white-space:pre-wrap;'>.venv\\Scripts\\python.exe manage.py run_simulator_worker</pre>"
            "</div>",
            node_hint,
        )
