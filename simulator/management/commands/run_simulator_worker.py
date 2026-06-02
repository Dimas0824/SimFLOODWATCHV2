from __future__ import annotations

import json
import time
import traceback

from django.core.management.base import BaseCommand
from django.utils import timezone

from devices.models import IoTNode
from simulator.control import apply_control_message
from simulator.mqtt_client import FloodWatchMQTTClient
from simulator.services import FloodWatchSimulator


class Command(BaseCommand):
    help = "Menjalankan loop simulator kontinu untuk semua node yang simulator_enabled."

    def add_arguments(self, parser):
        parser.add_argument(
            "--node-id",
            action="append",
            dest="node_ids",
            help="Batasi worker ke node tertentu. Bisa dipakai berulang.",
        )
        parser.add_argument(
            "--poll-ms",
            type=int,
            default=250,
            help="Interval polling worker dalam milidetik.",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Aktifkan log debug worker yang lebih detail.",
        )

    def handle(self, *args, **options):
        node_ids = options.get("node_ids") or []
        poll_ms = max(100, int(options["poll_ms"]))
        debug = bool(options["debug"])
        mqtt_clients: dict[str, FloodWatchMQTTClient] = {}
        last_empty_log_at = 0.0

        self.stdout.write(
            self.style.SUCCESS(
                f"Simulator worker start poll_ms={poll_ms} node_filter={','.join(node_ids) or 'ALL'}"
            )
        )
        self._debug(debug, "WORKER", "debug logging aktif")

        try:
            while True:
                queryset = IoTNode.objects.filter(is_active=True, simulator_enabled=True).order_by("node_id")
                if node_ids:
                    queryset = queryset.filter(node_id__in=node_ids)

                active_nodes = list(queryset)
                active_ids = {node.node_id for node in active_nodes}

                self._cleanup_inactive_clients(mqtt_clients, active_ids, debug)

                if not active_nodes:
                    now_ts = time.monotonic()
                    if now_ts - last_empty_log_at >= 5:
                        self.stdout.write("[WORKER] belum ada node aktif dengan simulator_enabled=true")
                        last_empty_log_at = now_ts

                now = timezone.now()
                for node in active_nodes:
                    due, remaining_seconds = self._due_status(node, now)
                    if not due:
                        self._debug(
                            debug,
                            "SKIP",
                            f"node={node.node_id} next_tick_in={remaining_seconds:.2f}s last_telemetry_at={node.last_telemetry_at}",
                        )
                        continue

                    try:
                        self._debug(debug, "NODE", self._describe_node(node))

                        if not node.mqtt_enabled and node.node_id in mqtt_clients:
                            mqtt_clients.pop(node.node_id).disconnect()
                            self._debug(debug, "MQTT", f"disconnect node={node.node_id} karena mqtt_enabled=false")

                        mqtt_client = self._ensure_mqtt_client(node, mqtt_clients, debug)
                        telemetry, payload = FloodWatchSimulator(node).tick()

                        if mqtt_client is not None:
                            try:
                                mqtt_client.publish_sensor_data(payload)
                                telemetry.published_to_mqtt = True
                                telemetry.save(update_fields=["published_to_mqtt"])
                            except Exception as exc:  # pragma: no cover - network dependent path.
                                self.stderr.write(f"[MQTT] publish gagal node={node.node_id}: {exc}")
                                mqtt_clients.pop(node.node_id, None)
                                try:
                                    mqtt_client.disconnect()
                                except Exception:
                                    pass

                        self.stdout.write(
                            f"[TICK] node={node.node_id} mode={node.simulation_mode} "
                            f"scenario={node.current_scenario} distance={payload['jarak_cm']} "
                            f"water={payload['water_switch']} status={payload['status']} "
                            f"mqtt={'yes' if telemetry.published_to_mqtt else 'no'}"
                        )
                        self._debug(
                            debug,
                            "PAYLOAD",
                            json.dumps(payload, ensure_ascii=True, separators=(",", ":")),
                        )
                        self._debug(debug, "RUNTIME", json.dumps(node.runtime_defaults(), ensure_ascii=True, separators=(",", ":")))
                    except Exception as exc:
                        self.stderr.write(f"[WORKER] node={node.node_id} gagal diproses: {exc}")
                        if debug:
                            self.stderr.write(traceback.format_exc())

                time.sleep(poll_ms / 1000.0)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Simulator worker dihentikan user."))
        finally:
            for client in mqtt_clients.values():
                try:
                    client.disconnect()
                except Exception:
                    pass

    def _cleanup_inactive_clients(
        self,
        mqtt_clients: dict[str, FloodWatchMQTTClient],
        active_ids: set[str],
        debug: bool,
    ) -> None:
        stale_node_ids = [node_id for node_id in mqtt_clients if node_id not in active_ids]
        for node_id in stale_node_ids:
            client = mqtt_clients.pop(node_id)
            try:
                client.disconnect()
            except Exception:
                pass
            self._debug(debug, "MQTT", f"cleanup client node={node_id} karena node tidak aktif lagi")

    def _ensure_mqtt_client(
        self,
        node: IoTNode,
        mqtt_clients: dict[str, FloodWatchMQTTClient],
        debug: bool,
    ) -> FloodWatchMQTTClient | None:
        if not node.mqtt_enabled:
            self._debug(debug, "MQTT", f"node={node.node_id} mqtt_enabled=false, publish ke broker dilewati")
            return None

        existing_client = mqtt_clients.get(node.node_id)
        if existing_client is not None:
            self._debug(debug, "MQTT", f"reuse existing client node={node.node_id}")
            return existing_client

        client = FloodWatchMQTTClient(
            node_id=node.node_id,
            on_control_message=lambda payload: apply_control_message(
                IoTNode.objects.get(pk=node.pk),
                payload,
                persist=True,
            ),
        )

        try:
            client.connect()
        except Exception as exc:  # pragma: no cover - network dependent path.
            self.stderr.write(f"[MQTT] connect gagal node={node.node_id}: {exc}")
            return None

        mqtt_clients[node.node_id] = client
        self.stdout.write(self.style.SUCCESS(f"[MQTT] connected node={node.node_id}"))
        self._debug(debug, "MQTT", f"client baru dibuat node={node.node_id}")
        return client

    @staticmethod
    def _due_status(node: IoTNode, now) -> tuple[bool, float]:
        interval_seconds = max(1, int(node.interval_seconds))
        if node.last_telemetry_at is None:
            return True, 0.0
        elapsed_seconds = (now - node.last_telemetry_at).total_seconds()
        if elapsed_seconds >= interval_seconds:
            return True, 0.0
        return False, interval_seconds - elapsed_seconds

    @staticmethod
    def _describe_node(node: IoTNode) -> str:
        return (
            f"node={node.node_id} interval={node.interval_seconds}s "
            f"mode={node.simulation_mode} scenario={node.current_scenario} "
            f"manual_distance={node.simulation_distance_cm} "
            f"manual_water={node.simulation_water_active} "
            f"drift_bias={node.simulation_drift_bias_cm} "
            f"mqtt_enabled={node.mqtt_enabled} control_mode={node.control_mode}"
        )

    def _debug(self, enabled: bool, category: str, message: str) -> None:
        if enabled:
            self.stdout.write(f"[DEBUG][{category}] {message}")
