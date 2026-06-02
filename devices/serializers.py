from rest_framework import serializers

from .models import IoTNode


class IoTNodeSerializer(serializers.ModelSerializer):
    health = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = IoTNode
        fields = [
            "id",
            "node_id",
            "node_name",
            "site_name",
            "location_label",
            "coordinate_label",
            "lat",
            "lng",
            "physical_id",
            "is_active",
            "simulator_enabled",
            "mqtt_enabled",
            "current_scenario",
            "simulation_mode",
            "simulation_distance_cm",
            "simulation_water_active",
            "simulation_drift_bias_cm",
            "interval_seconds",
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
            "servo_aman",
            "servo_waspada",
            "servo_bahaya",
            "servo_step_degree",
            "servo_step_interval_ms",
            "control_mode",
            "manual_servo_target",
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
            "health",
        ]
        read_only_fields = [
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
            "health",
        ]

    def get_health(self, obj: IoTNode) -> dict:
        return obj.health_snapshot()
