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
- Mode simulasi interaktif per node: slider jarak, toggle water switch, dan drift bias yang bisa diubah dari Django admin.

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

## Menjalankan loop simulator kontinu

`runserver` hanya menjalankan web admin dan API. Untuk meniru hardware yang sampling terus-menerus dan publish berkala ke AWS IoT Core, jalankan worker simulator terpisah:

```bash
.venv\Scripts\python.exe manage.py run_simulator_worker
```

Jika hanya ingin satu node:

```bash
.venv\Scripts\python.exe manage.py run_simulator_worker --node-id FW-1234ABCD
```

Node yang akan dijalankan worker adalah node dengan:

- `simulator_enabled = true`
- `is_active = true`

Jika `mqtt_enabled = true`, worker juga akan publish payload ke AWS IoT Core menggunakan konfigurasi MQTT dari `.env`.

Untuk log debug worker yang lebih detail:

```bash
.venv\Scripts\python.exe manage.py run_simulator_worker --debug
```

Mode debug akan menampilkan snapshot konfigurasi node, alasan node di-skip karena belum due, status MQTT, payload yang dipublish, dan error per-node tanpa menghentikan seluruh worker.

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

## Simulasi interaktif ala Wokwi

Di halaman admin node, sekarang ada blok `Kontrol Simulasi Interaktif`:

- `simulation_mode = MANUAL`
  Gunakan slider `simulation_distance_cm` untuk mengatur jarak sensor.
- `simulation_water_active`
  Toggle ini meniru water level switch aktif/nonaktif.
- `simulation_drift_bias_cm`
  Menambahkan bias drift ke pembacaan sensor, berguna untuk uji deviasi pembacaan.
- `simulation_mode = SCENARIO`
  Tetap memakai generator scenario lama seperti `normal`, `drift`, `spike`, `dropout`, dan `flood_rising`.

Field yang memang masuk akal untuk disimulasikan dijadikan kontrol langsung. Perilaku lain yang lebih cocok tetap dibiarkan mengikuti logic simulator yang sudah ada, seperti smoothing, klasifikasi status, hysteresis, dan step servo.

## Dokumentasi field admin tambah node

Berikut arti field yang muncul saat membuat atau mengedit node di Django admin.

### Identitas Node

- `node_id`
  ID unik node. Dipakai sebagai identitas utama di database, API, dan MQTT control payload.
- `node_name`
  Nama tampilan node untuk dashboard, payload telemetry, dan admin.
- `site_name`
  Nama lokasi besar atau site tempat node berada.
- `location_label`
  Label lokasi yang lebih spesifik, misalnya `Jembatan Utama`.
- `coordinate_label`
  Deskripsi koordinat atau titik pemasangan node.
- `lat`
  Latitude node.
- `lng`
  Longitude node.
- `physical_id`
  ID fisik perangkat. Jika dikosongkan, sistem akan mencoba membentuknya dari `node_id`.
- `is_active`
  Menandakan node aktif secara operasional. Worker hanya memproses node aktif.

### Loop Simulator

- `simulator_enabled`
  Jika aktif, node akan ikut dijalankan oleh `run_simulator_worker`.
- `mqtt_enabled`
  Jika aktif, hasil tick node akan dipublish ke AWS IoT Core oleh worker.
- `interval_seconds`
  Interval sampling simulator per node dalam detik.

### Kontrol Simulasi Interaktif

- `simulation_mode`
  Mode sumber data sensor. `MANUAL` untuk kontrol ala Wokwi, `SCENARIO` untuk generator otomatis.
- `simulation_distance_cm`
  Jarak sensor manual dalam cm. Dipakai saat `simulation_mode=MANUAL`.
- `simulation_water_active`
  Status water level switch manual. Dipakai saat `simulation_mode=MANUAL`.
- `simulation_drift_bias_cm`
  Bias drift tambahan dalam cm. Berguna untuk mensimulasikan pembacaan yang melenceng.
- `current_scenario`
  Scenario generator otomatis seperti `normal`, `drift`, `spike`, `dropout`, `flood_rising`, `stuck`, dan `invalid_sensor`.

### Kalibrasi Sensor dan Status

- `baseline_distance_cm`
  Jarak dasar sensor saat kondisi normal pada mode scenario.
- `sensor_offset_cm`
  Tinggi sensor dari dasar referensi. Dipakai untuk menghitung tinggi air.
- `aman_min_percent`
  Persentase jarak aman minimum dari tinggi sensor untuk klasifikasi `AMAN`.
- `waspada_min_percent`
  Persentase jarak minimum untuk klasifikasi `WASPADA`.
- `status_hysteresis_percent`
  Hysteresis agar status tidak mudah bolak-balik saat nilai dekat ambang.
- `distance_change_cm`
  Ambang perubahan jarak yang dianggap signifikan.
- `distance_filter_alpha`
  Faktor smoothing EMA untuk pembacaan jarak.
- `distance_decimals`
  Jumlah angka desimal yang disimpan/ditampilkan pada pembacaan jarak.
- `status_hold_ms`
  Waktu tahan sebelum status boleh turun level.
- `water_debounce_ms`
  Debounce untuk perubahan water switch.

### Servo

- `control_mode`
  Mode aktuator servo. `AUTO` mengikuti status banjir, `MANUAL` mengikuti target manual.
- `manual_servo_target`
  Target servo manual dalam derajat saat `control_mode=MANUAL`.
- `servo_aman`
  Posisi servo saat status `AMAN`.
- `servo_waspada`
  Posisi servo saat status `WASPADA`.
- `servo_bahaya`
  Posisi servo saat status `BAHAYA`.
- `servo_step_degree`
  Besar langkah servo per update.
- `servo_step_interval_ms`
  Interval antar langkah servo untuk pergerakan bertahap.

### Runtime Saat Ini

Field di bawah ini bersifat read-only dan terutama berguna setelah node tersimpan dan worker mulai berjalan:

- `current_status`
  Status node saat ini.
- `current_distance_cm`
  Jarak hasil smoothing yang sedang dipakai sistem.
- `last_raw_distance_cm`
  Jarak mentah terakhir sebelum smoothing.
- `last_water_height_cm`
  Tinggi air terakhir yang dihitung dari jarak dan offset sensor.
- `current_water_active`
  Status water switch terakhir yang dipakai logic.
- `current_servo_pos`
  Posisi servo aktual terakhir.
- `target_servo_pos`
  Target servo yang sedang dikejar.
- `last_sensor_valid`
  Nilai indikator sample sensor valid terakhir.
- `last_status_change_at`
  Waktu terakhir status berubah.
- `last_telemetry_at`
  Waktu tick/telemetry terakhir dibuat.
- `runtime_state`
  JSON state internal simulator, termasuk drift, held value, dan status runtime lain.
- `last_payload`
  Payload telemetry terakhir yang dibentuk simulator.
- `created_at`
  Waktu pembuatan record node.
- `updated_at`
  Waktu update terakhir record node.

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
