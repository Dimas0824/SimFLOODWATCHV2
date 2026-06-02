from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from django.db import transaction
from django.utils import timezone

from devices.models import IoTNode
from telemetry.models import Telemetry

from .scenarios import generate_distance_for_scenario


STATUS_RANK = {
    IoTNode.Status.AMAN: 0,
    IoTNode.Status.WASPADA: 1,
    IoTNode.Status.BAHAYA: 2,
    IoTNode.Status.ERROR: 3,
}


def clamp_float(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def round_distance(value: float, decimals: int) -> float:
    return round(float(value), int(decimals))


def calculate_water_height_cm(distance_cm: float, node: IoTNode) -> float:
    if distance_cm < 0:
        return -1.0
    return clamp_float(node.sensor_offset_cm - distance_cm, 0.0, node.sensor_offset_cm)


def water_height_percent(distance_cm: float, node: IoTNode) -> float:
    if node.sensor_offset_cm <= 0:
        return 0.0
    return (calculate_water_height_cm(distance_cm, node) / node.sensor_offset_cm) * 100.0


@dataclass
class SimulatorRuntime:
    drift_bias: float = 0.0
    last_distance_cm: float = 42.0
    ultrasonic_consecutive_failures: int = 0
    ultrasonic_using_held_value: bool = False
    mqtt_servo_percent: int = 0

    @classmethod
    def from_node(cls, node: IoTNode) -> "SimulatorRuntime":
        data = node.runtime_defaults()
        return cls(
            drift_bias=float(data.get("drift_bias", 0.0)),
            last_distance_cm=float(data.get("last_distance_cm", node.baseline_distance_cm)),
            ultrasonic_consecutive_failures=int(data.get("ultrasonic_consecutive_failures", 0)),
            ultrasonic_using_held_value=bool(data.get("ultrasonic_using_held_value", False)),
            mqtt_servo_percent=int(data.get("mqtt_servo_percent", 0)),
        )

    def dump(self) -> dict[str, Any]:
        return {
            "drift_bias": self.drift_bias,
            "last_distance_cm": self.last_distance_cm,
            "ultrasonic_consecutive_failures": self.ultrasonic_consecutive_failures,
            "ultrasonic_using_held_value": self.ultrasonic_using_held_value,
            "mqtt_servo_percent": self.mqtt_servo_percent,
        }


class FloodWatchSimulator:
    max_held_failure_samples = 3

    def __init__(self, node: IoTNode):
        self.node = node
        self.runtime = SimulatorRuntime.from_node(node)

    def classify_status(
        self,
        distance_cm: float,
        water_switch: bool,
        now,
    ) -> str:
        if water_switch:
            candidate = IoTNode.Status.BAHAYA
        elif distance_cm < 0:
            candidate = self.node.current_status
        else:
            percent = water_height_percent(distance_cm, self.node)
            aman_max = 100.0 - self.node.aman_min_percent
            waspada_max = 100.0 - self.node.waspada_min_percent
            if percent <= aman_max:
                candidate = IoTNode.Status.AMAN
            elif percent <= waspada_max:
                candidate = IoTNode.Status.WASPADA
            else:
                candidate = IoTNode.Status.BAHAYA

        current = self.node.current_status
        if current == IoTNode.Status.ERROR:
            return candidate
        if candidate == current:
            return current
        if STATUS_RANK.get(candidate, 0) > STATUS_RANK.get(current, 0):
            return candidate

        percent = water_height_percent(distance_cm, self.node)
        hysteresis = clamp_float(self.node.status_hysteresis_percent, 0.0, 20.0)
        aman_recovery = (100.0 - self.node.aman_min_percent) - hysteresis
        waspada_recovery = (100.0 - self.node.waspada_min_percent) - hysteresis
        status_age_ms = int((now - self.node.last_status_change_at).total_seconds() * 1000)

        if percent < aman_recovery:
            return candidate
        if status_age_ms < self.node.status_hold_ms:
            return current
        if current == IoTNode.Status.BAHAYA:
            return candidate if percent < waspada_recovery else current
        if current == IoTNode.Status.WASPADA:
            return candidate if percent < aman_recovery else current
        return candidate

    def _generate_raw_distance(self) -> tuple[float | None, int]:
        base_distance_cm = clamp_float(self.node.baseline_distance_cm, 0.0, self.node.sensor_offset_cm)
        runtime_data = self.runtime.dump()
        raw_distance = generate_distance_for_scenario(
            self.node.current_scenario,
            base_distance_cm,
            self.node.sensor_offset_cm,
            runtime_data,
        )
        self.runtime = SimulatorRuntime(
            drift_bias=float(runtime_data.get("drift_bias", self.runtime.drift_bias)),
            last_distance_cm=float(runtime_data.get("last_distance_cm", self.runtime.last_distance_cm)),
            ultrasonic_consecutive_failures=self.runtime.ultrasonic_consecutive_failures,
            ultrasonic_using_held_value=self.runtime.ultrasonic_using_held_value,
            mqtt_servo_percent=int(runtime_data.get("mqtt_servo_percent", self.runtime.mqtt_servo_percent)),
        )

        if raw_distance is None:
            self.runtime.ultrasonic_consecutive_failures += 1
            self.runtime.ultrasonic_using_held_value = (
                self.node.current_distance_cm is not None
                and self.runtime.ultrasonic_consecutive_failures <= self.max_held_failure_samples
            )
            if self.runtime.ultrasonic_using_held_value:
                held_value = self.node.current_distance_cm
                self.runtime.last_distance_cm = held_value
                return held_value, 0
            return None, 0

        self.runtime.ultrasonic_consecutive_failures = 0
        self.runtime.ultrasonic_using_held_value = False
        raw_distance = clamp_float(raw_distance, 0.0, self.node.sensor_offset_cm)
        self.runtime.last_distance_cm = raw_distance
        return raw_distance, 5

    def _smooth_distance(self, raw_distance: float | None) -> float | None:
        if raw_distance is None:
            return None

        if self.node.current_distance_cm is None:
            return round_distance(raw_distance, self.node.distance_decimals)

        alpha = clamp_float(self.node.distance_filter_alpha, 0.1, 1.0)
        smoothed = (alpha * raw_distance) + ((1.0 - alpha) * self.node.current_distance_cm)
        return round_distance(clamp_float(smoothed, 0.0, self.node.sensor_offset_cm), self.node.distance_decimals)

    def _resolve_water_switch(self, distance_cm: float | None) -> bool:
        if distance_cm is None:
            return False
        threshold = min(25.0, self.node.sensor_offset_cm * 0.25)
        return distance_cm <= threshold

    def _resolve_target_servo(self, status: str) -> int:
        if self.node.control_mode == IoTNode.ControlMode.MANUAL:
            return self.node.manual_servo_target
        return self.node.resolve_auto_servo_target(status)

    def _step_servo(self, target_servo_pos: int) -> int:
        current_servo_pos = int(self.node.current_servo_pos or 0)
        if current_servo_pos == target_servo_pos:
            return current_servo_pos

        step_interval_ms = max(1, int(self.node.servo_step_interval_ms))
        elapsed_ms = int((self.node.interval_seconds or 1) * 1000)
        elapsed_steps = max(1, elapsed_ms // step_interval_ms)
        max_move = elapsed_steps * max(1, int(self.node.servo_step_degree))
        delta = target_servo_pos - current_servo_pos
        move = min(abs(delta), max_move)
        direction = 1 if delta > 0 else -1
        return max(0, min(180, current_servo_pos + (direction * move)))

    def build_payload(self, now, distance_cm: float, raw_distance_cm: float, water_switch: bool, status: str, sensor_valid: int) -> dict[str, Any]:
        timestamp = timezone.localtime(now).strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "node_id": self.node.node_id,
            "node_name": self.node.node_name,
            "site_name": self.node.site_name,
            "location_label": self.node.location_label,
            "lat": self.node.lat,
            "lng": self.node.lng,
            "physical_id": self.node.physical_id,
            "timestamp": timestamp,
            "jarak_cm": round_distance(distance_cm, self.node.distance_decimals),
            "raw_jarak_cm": round_distance(raw_distance_cm, self.node.distance_decimals),
            "water_switch": water_switch,
            "status": status,
            "servo_pos": self.node.target_servo_pos,
            "servo_pos_control": self.node.current_servo_pos,
            "sensor_valid": sensor_valid,
        }
        return payload

    @transaction.atomic
    def tick(self) -> tuple[Telemetry, dict[str, Any]]:
        now = timezone.now()
        raw_distance_cm, sensor_valid = self._generate_raw_distance()
        distance_cm = self._smooth_distance(raw_distance_cm)
        water_switch = self._resolve_water_switch(distance_cm)

        if distance_cm is None:
            distance_cm = 0.0
            raw_distance_for_payload = 0.0
            water_height_cm = 0.0
            status = IoTNode.Status.ERROR
        else:
            raw_distance_for_payload = raw_distance_cm if raw_distance_cm is not None else distance_cm
            water_height_cm = calculate_water_height_cm(distance_cm, self.node)
            status = self.classify_status(distance_cm, water_switch, now)

        target_servo_pos = self._resolve_target_servo(status)
        current_servo_pos = self._step_servo(target_servo_pos)

        self.node.current_distance_cm = distance_cm
        self.node.last_raw_distance_cm = raw_distance_for_payload
        self.node.last_water_height_cm = water_height_cm
        self.node.current_water_active = water_switch
        self.node.target_servo_pos = target_servo_pos
        self.node.current_servo_pos = current_servo_pos
        self.node.last_sensor_valid = sensor_valid
        self.node.last_telemetry_at = now
        if status != self.node.current_status:
            self.node.last_status_change_at = now
        self.node.current_status = status

        payload = self.build_payload(
            now=now,
            distance_cm=distance_cm,
            raw_distance_cm=raw_distance_for_payload,
            water_switch=water_switch,
            status=status,
            sensor_valid=sensor_valid,
        )
        self.node.last_payload = payload
        self.node.runtime_state = self.runtime.dump()
        self.node.save()

        telemetry = Telemetry.objects.create(
            node=self.node,
            timestamp=now,
            jarak_cm=payload["jarak_cm"],
            raw_jarak_cm=payload["raw_jarak_cm"],
            water_height_cm=round_distance(water_height_cm, self.node.distance_decimals),
            water_switch=water_switch,
            status=status,
            servo_pos=self.node.target_servo_pos,
            servo_pos_control=self.node.current_servo_pos,
            sensor_valid=sensor_valid,
            scenario=self.node.current_scenario,
            control_mode=self.node.control_mode,
            payload=payload,
        )
        return telemetry, payload
