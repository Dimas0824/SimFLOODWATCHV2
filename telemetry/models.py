from __future__ import annotations

from typing import Any

from django.db import models

from devices.models import IoTNode


class Telemetry(models.Model):
    node = models.ForeignKey(IoTNode, on_delete=models.CASCADE, related_name="telemetry_records")
    timestamp = models.DateTimeField()
    jarak_cm = models.FloatField()
    raw_jarak_cm = models.FloatField()
    water_height_cm = models.FloatField(default=0.0)
    water_switch = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=IoTNode.Status.choices)
    servo_pos = models.PositiveSmallIntegerField()
    servo_pos_control = models.PositiveSmallIntegerField()
    sensor_valid = models.PositiveSmallIntegerField(default=0)
    scenario = models.CharField(max_length=50)
    control_mode = models.CharField(max_length=10, choices=IoTNode.ControlMode.choices)
    published_to_mqtt = models.BooleanField(default=False)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp", "-id"]
        indexes = [
            models.Index(fields=["node", "-timestamp"]),
            models.Index(fields=["status", "-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.node.node_id} - {self.timestamp:%Y-%m-%d %H:%M:%S} - {self.status}"

    def as_payload(self) -> dict[str, Any]:
        if self.payload:
            return self.payload

        return {
            "node_id": self.node.node_id,
            "node_name": self.node.node_name,
            "site_name": self.node.site_name,
            "location_label": self.node.location_label,
            "lat": self.node.lat,
            "lng": self.node.lng,
            "physical_id": self.node.physical_id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "jarak_cm": self.jarak_cm,
            "raw_jarak_cm": self.raw_jarak_cm,
            "water_switch": self.water_switch,
            "status": self.status,
            "servo_pos": self.servo_pos,
            "servo_pos_control": self.servo_pos_control,
            "sensor_valid": self.sensor_valid,
        }
