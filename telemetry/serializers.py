from rest_framework import serializers

from .models import Telemetry


class TelemetrySerializer(serializers.ModelSerializer):
    node_id = serializers.CharField(source="node.node_id", read_only=True)
    node_name = serializers.CharField(source="node.node_name", read_only=True)

    class Meta:
        model = Telemetry
        fields = [
            "id",
            "node",
            "node_id",
            "node_name",
            "timestamp",
            "jarak_cm",
            "raw_jarak_cm",
            "water_height_cm",
            "water_switch",
            "status",
            "servo_pos",
            "servo_pos_control",
            "sensor_valid",
            "scenario",
            "control_mode",
            "published_to_mqtt",
            "payload",
            "created_at",
        ]
        read_only_fields = fields
