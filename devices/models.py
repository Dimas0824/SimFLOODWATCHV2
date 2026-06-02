from __future__ import annotations

from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from simulator.scenarios import SCENARIO_CHOICES, SCENARIO_NORMAL


def _default_last_payload() -> dict[str, Any]:
    return {}


def _default_runtime_state() -> dict[str, Any]:
    return {
        "drift_bias": 0.0,
        "last_distance_cm": 42.0,
        "ultrasonic_consecutive_failures": 0,
        "ultrasonic_using_held_value": False,
        "mqtt_servo_percent": 0,
    }


class IoTNode(models.Model):
    class Status(models.TextChoices):
        AMAN = "AMAN", "AMAN"
        WASPADA = "WASPADA", "WASPADA"
        BAHAYA = "BAHAYA", "BAHAYA"
        ERROR = "ERROR", "ERROR"

    class ControlMode(models.TextChoices):
        AUTO = "AUTO", "AUTO"
        MANUAL = "MANUAL", "MANUAL"

    class SimulationMode(models.TextChoices):
        SCENARIO = "SCENARIO", "SCENARIO"
        MANUAL = "MANUAL", "MANUAL"

    node_id = models.CharField(max_length=50, unique=True)
    node_name = models.CharField(max_length=100, default="FloodWatch Node")
    site_name = models.CharField(max_length=100, default="Kampus")
    location_label = models.CharField(max_length=100, default="Belum diset")
    coordinate_label = models.CharField(max_length=100, default="Belum diset")
    lat = models.FloatField(default=0.0, validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    lng = models.FloatField(default=0.0, validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    physical_id = models.CharField(max_length=50, blank=True)

    is_active = models.BooleanField(default=True)
    simulator_enabled = models.BooleanField(default=False)
    mqtt_enabled = models.BooleanField(default=False)
    current_scenario = models.CharField(
        max_length=50,
        choices=SCENARIO_CHOICES,
        default=SCENARIO_NORMAL,
    )
    simulation_mode = models.CharField(
        max_length=10,
        choices=SimulationMode.choices,
        default=SimulationMode.SCENARIO,
    )
    simulation_distance_cm = models.FloatField(default=42.0)
    simulation_water_active = models.BooleanField(default=False)
    simulation_drift_bias_cm = models.FloatField(default=0.0)
    interval_seconds = models.PositiveSmallIntegerField(default=5)
    baseline_distance_cm = models.FloatField(default=42.0)
    sensor_offset_cm = models.FloatField(default=100.0)
    aman_min_percent = models.FloatField(default=70.0)
    waspada_min_percent = models.FloatField(default=45.0)
    status_hysteresis_percent = models.FloatField(default=3.0)
    distance_change_cm = models.FloatField(default=0.5)
    distance_filter_alpha = models.FloatField(default=0.35)
    distance_decimals = models.PositiveSmallIntegerField(default=1)
    status_hold_ms = models.PositiveIntegerField(default=2500)
    water_debounce_ms = models.PositiveIntegerField(default=250)

    servo_aman = models.PositiveSmallIntegerField(default=0)
    servo_waspada = models.PositiveSmallIntegerField(default=120)
    servo_bahaya = models.PositiveSmallIntegerField(default=170)
    servo_step_degree = models.PositiveSmallIntegerField(default=3)
    servo_step_interval_ms = models.PositiveSmallIntegerField(default=8)

    control_mode = models.CharField(
        max_length=10,
        choices=ControlMode.choices,
        default=ControlMode.AUTO,
    )
    manual_servo_target = models.PositiveSmallIntegerField(default=0)

    current_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AMAN,
    )
    current_distance_cm = models.FloatField(null=True, blank=True)
    last_raw_distance_cm = models.FloatField(null=True, blank=True)
    last_water_height_cm = models.FloatField(default=0.0)
    current_water_active = models.BooleanField(default=False)
    current_servo_pos = models.PositiveSmallIntegerField(default=0)
    target_servo_pos = models.PositiveSmallIntegerField(default=0)
    last_sensor_valid = models.PositiveSmallIntegerField(default=0)
    last_status_change_at = models.DateTimeField(default=timezone.now)
    last_telemetry_at = models.DateTimeField(null=True, blank=True)

    runtime_state = models.JSONField(default=_default_runtime_state, blank=True)
    last_payload = models.JSONField(default=_default_last_payload, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["node_id"]

    def __str__(self) -> str:
        return f"{self.node_id} - {self.node_name}"

    def clean(self) -> None:
        valid_scenarios = {key for key, _ in SCENARIO_CHOICES}
        if self.current_scenario not in valid_scenarios:
            self.current_scenario = SCENARIO_NORMAL
        if self.simulation_mode not in {self.SimulationMode.SCENARIO, self.SimulationMode.MANUAL}:
            self.simulation_mode = self.SimulationMode.SCENARIO
        self.interval_seconds = max(1, min(int(self.interval_seconds or 1), 3600))
        self.sensor_offset_cm = max(2.0, min(float(self.sensor_offset_cm or 100.0), 400.0))
        self.baseline_distance_cm = max(0.0, min(float(self.baseline_distance_cm or 42.0), self.sensor_offset_cm))
        self.simulation_distance_cm = max(0.0, min(float(self.simulation_distance_cm or 0.0), self.sensor_offset_cm))
        self.simulation_drift_bias_cm = max(-200.0, min(float(self.simulation_drift_bias_cm or 0.0), 200.0))
        self.aman_min_percent = max(50.0, min(float(self.aman_min_percent or 70.0), 95.0))
        self.waspada_min_percent = max(5.0, min(float(self.waspada_min_percent or 45.0), 90.0))
        if self.waspada_min_percent >= self.aman_min_percent:
            self.waspada_min_percent = max(5.0, self.aman_min_percent - 5.0)
        self.status_hysteresis_percent = max(0.0, min(float(self.status_hysteresis_percent or 3.0), 20.0))
        self.distance_change_cm = max(0.1, min(float(self.distance_change_cm or 0.5), 50.0))
        self.distance_filter_alpha = max(0.1, min(float(self.distance_filter_alpha or 0.35), 1.0))
        self.distance_decimals = max(0, min(int(self.distance_decimals or 1), 3))
        self.status_hold_ms = max(0, min(int(self.status_hold_ms or 2500), 60000))
        self.water_debounce_ms = max(0, min(int(self.water_debounce_ms or 250), 10000))
        self.servo_aman = max(0, min(int(self.servo_aman or 0), 180))
        self.servo_waspada = max(0, min(int(self.servo_waspada or 120), 180))
        self.servo_bahaya = max(0, min(int(self.servo_bahaya or 170), 180))
        self.servo_step_degree = max(1, min(int(self.servo_step_degree or 3), 30))
        self.servo_step_interval_ms = max(1, min(int(self.servo_step_interval_ms or 8), 1000))
        self.manual_servo_target = max(0, min(int(self.manual_servo_target or 0), 180))
        self.current_servo_pos = max(0, min(int(self.current_servo_pos or 0), 180))
        self.target_servo_pos = max(0, min(int(self.target_servo_pos or 0), 180))
        if not self.physical_id:
            self.physical_id = self.node_id.replace("FW-", "")[-12:] or self.node_id[-12:]

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def resolve_auto_servo_target(self, status: str | None = None) -> int:
        resolved_status = status or self.current_status
        if resolved_status == self.Status.BAHAYA:
            return self.servo_bahaya
        if resolved_status == self.Status.WASPADA:
            return self.servo_waspada
        return self.servo_aman

    def runtime_defaults(self) -> dict[str, Any]:
        defaults = _default_runtime_state()
        defaults.update(self.runtime_state or {})
        return defaults

    def health_snapshot(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "site_name": self.site_name,
            "location_label": self.location_label,
            "coordinate_label": self.coordinate_label,
            "status": self.current_status,
            "control_mode": self.control_mode,
            "simulation_mode": self.simulation_mode,
            "simulator_enabled": self.simulator_enabled,
            "mqtt_enabled": self.mqtt_enabled,
            "simulation_distance_cm": self.simulation_distance_cm,
            "simulation_water_active": self.simulation_water_active,
            "simulation_drift_bias_cm": self.simulation_drift_bias_cm,
            "water_switch": self.current_water_active,
            "sensor_offset_cm": self.sensor_offset_cm,
            "sensor_height_cm": self.sensor_offset_cm,
            "water_height_cm": round(self.last_water_height_cm or 0.0, self.distance_decimals),
            "jarak_cm": self.current_distance_cm,
            "servo_target": self.target_servo_pos,
            "servo_current": self.current_servo_pos,
            "sensor_valid": self.last_sensor_valid,
            "scenario": self.current_scenario,
            "last_telemetry_at": self.last_telemetry_at,
        }
