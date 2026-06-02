from __future__ import annotations

import random


SCENARIO_NORMAL = "normal"
SCENARIO_DRIFT = "drift"
SCENARIO_SPIKE = "spike"
SCENARIO_DROPOUT = "dropout"
SCENARIO_FLOOD_RISING = "flood_rising"
SCENARIO_STUCK = "stuck"
SCENARIO_INVALID_SENSOR = "invalid_sensor"

SCENARIO_CHOICES = [
    (SCENARIO_NORMAL, SCENARIO_NORMAL),
    (SCENARIO_DRIFT, SCENARIO_DRIFT),
    (SCENARIO_SPIKE, SCENARIO_SPIKE),
    (SCENARIO_DROPOUT, SCENARIO_DROPOUT),
    (SCENARIO_FLOOD_RISING, SCENARIO_FLOOD_RISING),
    (SCENARIO_STUCK, SCENARIO_STUCK),
    (SCENARIO_INVALID_SENSOR, SCENARIO_INVALID_SENSOR),
]


def generate_distance_for_scenario(
    scenario: str,
    base_distance_cm: float,
    sensor_offset_cm: float,
    runtime_state: dict,
) -> float | None:
    noise = random.uniform(-2.0, 2.0)

    if scenario == SCENARIO_NORMAL:
        raw_distance = base_distance_cm + noise
    elif scenario == SCENARIO_DRIFT:
        runtime_state["drift_bias"] = float(runtime_state.get("drift_bias", 0.0)) + 0.2
        raw_distance = base_distance_cm + noise + runtime_state["drift_bias"]
    elif scenario == SCENARIO_SPIKE:
        raw_distance = base_distance_cm + noise
        if random.random() < 0.15:
            raw_distance += random.choice([-25.0, 30.0, 45.0])
    elif scenario == SCENARIO_DROPOUT:
        if random.random() < 0.2:
            return None
        raw_distance = base_distance_cm + noise
    elif scenario == SCENARIO_FLOOD_RISING:
        drop_amount = random.uniform(0.0, sensor_offset_cm * 0.55)
        raw_distance = base_distance_cm - drop_amount + noise
    elif scenario == SCENARIO_STUCK:
        raw_distance = float(runtime_state.get("last_distance_cm", base_distance_cm))
    elif scenario == SCENARIO_INVALID_SENSOR:
        if random.random() < 0.5:
            return None
        raw_distance = base_distance_cm + random.uniform(-30.0, 30.0)
    else:
        raw_distance = base_distance_cm + noise

    return max(0.0, min(raw_distance, sensor_offset_cm))
