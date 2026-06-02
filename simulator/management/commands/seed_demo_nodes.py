from django.core.management.base import BaseCommand

from devices.models import IoTNode


class Command(BaseCommand):
    help = "Buat node demo FloodWatch simulator."

    def handle(self, *args, **options):
        defaults = [
            {
                "node_id": "FW-1234ABCD",
                "node_name": "FloodWatch Node",
                "site_name": "Kampus",
                "location_label": "Belum diset",
                "coordinate_label": "-6.200000, 106.816666",
                "lat": -6.2,
                "lng": 106.816666,
                "physical_id": "1234ABCD",
                "baseline_distance_cm": 42.0,
                "sensor_offset_cm": 100.0,
            },
            {
                "node_id": "FW-5678EFGH",
                "node_name": "FloodWatch Jembatan",
                "site_name": "Blue Bridge",
                "location_label": "Jembatan Utama",
                "coordinate_label": "-7.943583, 112.612801",
                "lat": -7.943583,
                "lng": 112.612801,
                "physical_id": "5678EFGH",
                "baseline_distance_cm": 38.0,
                "sensor_offset_cm": 100.0,
            },
        ]

        created = 0
        updated = 0
        for data in defaults:
            node, was_created = IoTNode.objects.update_or_create(
                node_id=data["node_id"],
                defaults=data,
            )
            created += int(was_created)
            updated += int(not was_created)
            self.stdout.write(f"{'CREATED' if was_created else 'UPDATED'} {node.node_id}")

        self.stdout.write(self.style.SUCCESS(f"Selesai. created={created} updated={updated}"))
