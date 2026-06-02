from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Callable

import paho.mqtt.client as mqtt

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency installed at runtime.
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


def env_bool(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


class FloodWatchMQTTClient:
    def __init__(self, node_id: str, on_control_message: Callable[[dict], None] | None = None):
        self.node_id = node_id
        self.endpoint = os.getenv("MQTT_ENDPOINT", "")
        self.port = int(os.getenv("MQTT_PORT", "8883"))
        self.use_tls = env_bool("MQTT_USE_TLS", True)
        self.root_ca = os.getenv("MQTT_ROOT_CA", "")
        self.cert = os.getenv("MQTT_CERT", "")
        self.private_key = os.getenv("MQTT_PRIVATE_KEY", "")
        self.publish_topic = os.getenv("MQTT_PUBLISH_TOPIC", "floodwatch/sensor/data")
        self.subscribe_topic = os.getenv("MQTT_SUBSCRIBE_TOPIC", "floodwatch/device/control")
        self.client_id = f"{os.getenv('MQTT_CLIENT_ID_PREFIX', 'floodwatch-aws')}-{node_id}"
        self.on_control_message = on_control_message
        self._tls_temp_dir: Path | None = None

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        if self.use_tls:
            # Support both filesystem paths and inline PEM values from .env.
            self.root_ca = self._prepare_tls_material("root_ca", self.root_ca, ".pem")
            self.cert = self._prepare_tls_material("device_cert", self.cert, ".pem")
            self.private_key = self._prepare_tls_material("private_key", self.private_key, ".key")
            self.client.tls_set(
                ca_certs=self.root_ca or None,
                certfile=self.cert or None,
                keyfile=self.private_key or None,
            )

    def is_configured(self) -> bool:
        if not self.endpoint:
            return False
        if not self.use_tls:
            return True
        return all([self.root_ca, self.cert, self.private_key])

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        client.subscribe(self.subscribe_topic, qos=1)

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            return
        if self.on_control_message:
            self.on_control_message(payload)

    def connect(self) -> None:
        if not self.is_configured():
            raise RuntimeError("Konfigurasi MQTT belum lengkap.")
        self.client.connect(self.endpoint, self.port, keepalive=60)
        self.client.loop_start()

    def publish_sensor_data(self, payload: dict) -> None:
        self.client.publish(self.publish_topic, json.dumps(payload), qos=1)

    def disconnect(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()
        if self._tls_temp_dir is not None:
            shutil.rmtree(self._tls_temp_dir, ignore_errors=True)
            self._tls_temp_dir = None

    def _prepare_tls_material(self, name: str, value: str, suffix: str) -> str:
        raw_value = value.strip()
        if not raw_value:
            return ""
        if os.path.exists(raw_value):
            return raw_value
        if "-----BEGIN" not in raw_value:
            return raw_value

        if self._tls_temp_dir is None:
            self._tls_temp_dir = Path(tempfile.mkdtemp(prefix="floodwatch-mqtt-"))

        target_path = self._tls_temp_dir / f"{name}{suffix}"
        normalized_value = self._normalize_pem(raw_value)
        target_path.write_text(normalized_value, encoding="utf-8")
        return str(target_path)

    @staticmethod
    def _normalize_pem(value: str) -> str:
        return value.replace("\\n", "\n").replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"
