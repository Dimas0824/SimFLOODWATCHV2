from __future__ import annotations

from typing import Any

from devices.models import IoTNode
from simulator.scenarios import SCENARIO_CHOICES


SENSOR_OFFSET_KEYS = (
    "sensoroffset",
    "sensoroffsetcm",
    "sensorOffsetCm",
    "sensor_offset_cm",
    "sensorHeightCm",
)


def clamp_int(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def servo_percent_to_degree(percent: int) -> int:
    return (clamp_int(percent, 0, 100) * 180 + 50) // 100


def servo_degree_to_percent(degree: int) -> int:
    return (clamp_int(degree, 0, 180) * 100 + 90) // 180


def normalize_target_node_id(payload: dict[str, Any]) -> str | None:
    raw_node_id = payload.get("node_id") or payload.get("nodeId")
    return str(raw_node_id).strip() if raw_node_id else None


def ensure_payload_targets_node(node: IoTNode, payload: dict[str, Any]) -> None:
    target_node_id = normalize_target_node_id(payload)
    if target_node_id and target_node_id != node.node_id:
        raise ValueError(f"Payload node id `{target_node_id}` tidak cocok dengan `{node.node_id}`.")


def apply_control_message(node: IoTNode, payload: dict[str, Any], persist: bool = True) -> dict[str, Any]:
    ensure_payload_targets_node(node, payload)

    updates: list[str] = []
    valid_scenarios = {key for key, _ in SCENARIO_CHOICES}
    command = payload.get("command")
    runtime_state = node.runtime_defaults()

    if command == "set_scenario":
        scenario = str(payload.get("scenario", node.current_scenario))
        if scenario not in valid_scenarios:
            raise ValueError(f"Scenario `{scenario}` tidak didukung.")
        node.current_scenario = scenario
        updates.append(f"scenario={scenario}")

    if command == "set_interval":
        interval_seconds = clamp_int(int(payload.get("interval_seconds", node.interval_seconds)), 1, 3600)
        node.interval_seconds = interval_seconds
        updates.append(f"interval_seconds={interval_seconds}")

    if command == "set_servo":
        node.control_mode = IoTNode.ControlMode.MANUAL
        node.manual_servo_target = clamp_int(int(payload.get("servo_pos_control", node.manual_servo_target)), 0, 180)
        runtime_state["mqtt_servo_percent"] = servo_degree_to_percent(node.manual_servo_target)
        updates.append(f"manual_servo_target={node.manual_servo_target}")

    mode = payload.get("mode")
    if isinstance(mode, str):
        mode = mode.upper().strip()
        if mode == IoTNode.ControlMode.AUTO:
            node.control_mode = IoTNode.ControlMode.AUTO
            node.manual_servo_target = node.resolve_auto_servo_target(node.current_status)
            runtime_state["mqtt_servo_percent"] = 0
            updates.append("control_mode=AUTO")
        elif mode == IoTNode.ControlMode.MANUAL:
            node.control_mode = IoTNode.ControlMode.MANUAL
            if not node.manual_servo_target:
                node.manual_servo_target = node.target_servo_pos
            runtime_state["mqtt_servo_percent"] = servo_degree_to_percent(node.manual_servo_target)
            updates.append("control_mode=MANUAL")
        else:
            raise ValueError(f"Mode `{mode}` tidak didukung.")

    if "servoauto" in payload:
        auto_value = int(payload["servoauto"])
        if auto_value > 0:
            node.control_mode = IoTNode.ControlMode.AUTO
            node.manual_servo_target = node.resolve_auto_servo_target(node.current_status)
            runtime_state["mqtt_servo_percent"] = 0
            updates.append("control_mode=AUTO")
        else:
            node.control_mode = IoTNode.ControlMode.MANUAL
            if not node.manual_servo_target:
                node.manual_servo_target = node.target_servo_pos
            runtime_state["mqtt_servo_percent"] = servo_degree_to_percent(node.manual_servo_target)
            updates.append("control_mode=MANUAL")

    if "servotarget" in payload:
        node.control_mode = IoTNode.ControlMode.MANUAL
        node.manual_servo_target = clamp_int(int(payload["servotarget"]), 0, 180)
        runtime_state["mqtt_servo_percent"] = servo_degree_to_percent(node.manual_servo_target)
        updates.append(f"manual_servo_target={node.manual_servo_target}")

    if "servobuka" in payload:
        node.control_mode = IoTNode.ControlMode.MANUAL
        current_percent = servo_degree_to_percent(node.manual_servo_target or node.target_servo_pos)
        next_percent = clamp_int(current_percent + int(payload["servobuka"]), 0, 100)
        node.manual_servo_target = servo_percent_to_degree(next_percent)
        runtime_state["mqtt_servo_percent"] = next_percent
        updates.append(f"manual_servo_target={node.manual_servo_target}")

    if "servotutup" in payload:
        node.control_mode = IoTNode.ControlMode.MANUAL
        current_percent = servo_degree_to_percent(node.manual_servo_target or node.target_servo_pos)
        next_percent = clamp_int(current_percent - int(payload["servotutup"]), 0, 100)
        node.manual_servo_target = servo_percent_to_degree(next_percent)
        runtime_state["mqtt_servo_percent"] = next_percent
        updates.append(f"manual_servo_target={node.manual_servo_target}")

    for key in SENSOR_OFFSET_KEYS:
        if key in payload:
            node.sensor_offset_cm = max(2.0, min(float(payload[key]), 400.0))
            node.baseline_distance_cm = min(node.baseline_distance_cm, node.sensor_offset_cm)
            updates.append(f"sensor_offset_cm={node.sensor_offset_cm}")
            break

    metadata_keys = {
        "nodeName": "node_name",
        "siteName": "site_name",
        "locationLabel": "location_label",
        "coordinateLabel": "coordinate_label",
        "latitude": "lat",
        "longitude": "lng",
    }
    for source_key, field_name in metadata_keys.items():
        if source_key in payload:
            setattr(node, field_name, payload[source_key])
            updates.append(f"{field_name}={payload[source_key]}")

    if updates:
        node.runtime_state = runtime_state

    if persist and updates:
        node.save()

    return {
        "node_id": node.node_id,
        "applied": bool(updates),
        "updates": updates,
        "control_mode": node.control_mode,
        "manual_servo_target": node.manual_servo_target,
        "current_scenario": node.current_scenario,
        "interval_seconds": node.interval_seconds,
    }
