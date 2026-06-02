# SimFLOODWATCHV2

Simulator Django untuk meniru perilaku inti `FloodWatchV2` tanpa bergantung pada Wokwi atau perangkat ESP32 fisik.

## Yang disediakan

- Registry node FloodWatch virtual.
- Penyimpanan telemetry ke database SQLite.
- Simulator sensor dengan scenario `normal`, `drift`, `spike`, `dropout`, `flood_rising`, `stuck`, dan `invalid_sensor`.
- Logika klasifikasi `AMAN`, `WASPADA`, `BAHAYA` yang meniru threshold, hysteresis, dan hold-time FloodWatchV2.
- Kontrol servo `AUTO` dan `MANUAL` yang kompatibel dengan command MQTT proyek firmware.
- API untuk node, telemetry, health, control command, dan manual tick simulator.
- Management command untuk loop simulator dan publish/subscribe MQTT.

## Setup

```bash
cd SimFLOODWATCHV2
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo_nodes
python manage.py runserver
```

## Login admin Django

Project ini tidak menyediakan username/password admin default.

Buat akun admin sendiri dengan:

```bash
python manage.py createsuperuser
```

Lalu login ke halaman admin di:

```text
http://127.0.0.1:8000/admin/
```

Jika Anda menjalankan server di port lain, sesuaikan URL-nya. Contoh:

```text
http://127.0.0.1:8001/admin/
```

## Menjalankan simulator

Satu tick manual via API:

```bash
POST /api/simulator/tick/FW-1234ABCD/
```

Loop simulator per node:

```bash
python manage.py simulate_node --node-id FW-1234ABCD --scenario normal --interval 5
python manage.py simulate_node --node-id FW-1234ABCD --scenario flood_rising --interval 3 --mqtt
```

## Endpoint utama

- `GET /api/health/`
- `GET /api/nodes/`
- `POST /api/nodes/`
- `GET /api/telemetry/?node_id=FW-1234ABCD`
- `POST /api/simulator/control/`
- `POST /api/simulator/tick/<node_id>/`

## Kompatibilitas command

Endpoint control dan subscriber MQTT mendukung dua gaya payload:

1. Payload guideline simulator, misalnya:

```json
{
  "node_id": "FW-1234ABCD",
  "command": "set_scenario",
  "scenario": "drift"
}
```

2. Payload kompatibel firmware FloodWatchV2, misalnya:

```json
{
  "nodeId": "FW-1234ABCD",
  "mode": "MANUAL",
  "servobuka": 10
}
```
