import time

from django.core.management.base import BaseCommand, CommandError

from devices.models import IoTNode
from simulator.control import apply_control_message
from simulator.mqtt_client import FloodWatchMQTTClient
from simulator.services import FloodWatchSimulator


class Command(BaseCommand):
    help = "Run FloodWatch simulator loop untuk satu node."

    def add_arguments(self, parser):
        parser.add_argument("--node-id", type=str, required=True)
        parser.add_argument("--scenario", type=str, default=None)
        parser.add_argument("--interval", type=int, default=None)
        parser.add_argument("--iterations", type=int, default=None)
        parser.add_argument("--mqtt", action="store_true")

    def handle(self, *args, **options):
        node_id = options["node_id"]
        scenario = options["scenario"]
        interval = options["interval"]
        iterations = options["iterations"]
        use_mqtt = options["mqtt"]

        try:
            node = IoTNode.objects.get(node_id=node_id)
        except IoTNode.DoesNotExist as exc:
            raise CommandError(f"Node `{node_id}` tidak ditemukan.") from exc

        if scenario:
            node.current_scenario = scenario
        if interval:
            node.interval_seconds = max(1, interval)
        node.save()

        mqtt_client = None
        if use_mqtt:
            mqtt_client = FloodWatchMQTTClient(
                node_id=node.node_id,
                on_control_message=lambda payload: apply_control_message(
                    IoTNode.objects.get(pk=node.pk),
                    payload,
                    persist=True,
                ),
            )
            mqtt_client.connect()

        self.stdout.write(
            self.style.SUCCESS(
                f"Simulator start node={node.node_id} scenario={node.current_scenario} interval={node.interval_seconds}s mqtt={use_mqtt}"
            )
        )

        executed = 0
        try:
            while True:
                node.refresh_from_db()
                telemetry, payload = FloodWatchSimulator(node).tick()
                if mqtt_client:
                    mqtt_client.publish_sensor_data(payload)
                    telemetry.published_to_mqtt = True
                    telemetry.save(update_fields=["published_to_mqtt"])

                self.stdout.write(str(payload))
                executed += 1
                if iterations is not None and executed >= iterations:
                    break
                time.sleep(node.interval_seconds)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Simulator dihentikan user."))
        finally:
            if mqtt_client:
                mqtt_client.disconnect()
