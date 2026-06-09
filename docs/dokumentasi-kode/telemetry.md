# Dokumentasi Modul Telemetry

## `telemetry/__init__.py`

### Fungsi file

Marker package Python untuk app `telemetry`.

### Cara kerja

Tidak ada logika khusus.

## `telemetry/apps.py`

### Fungsi file

Mendaftarkan app `telemetry` ke Django.

### Class penting

- `TelemetryConfig`
  Menentukan nama app dan tipe primary key default.

## `telemetry/urls.py`

### Fungsi file

Placeholder route lokal untuk app `telemetry`.

### Cara kerja

Saat ini route telemetry dipasang langsung dari `config/urls.py` lewat DRF router.

## `telemetry/models.py`

### Fungsi file

Menyimpan histori hasil simulasi per tick.

### Class dan method penting

- `Telemetry`
  Model histori telemetry.
- `Telemetry.as_payload()`
  Mengembalikan payload tersimpan atau membangun payload baru dari relasi node.

### Data penting dalam model

- relasi node: `node`
- waktu dan sensor: `timestamp`, `jarak_cm`, `raw_jarak_cm`, `water_height_cm`
- status: `water_switch`, `status`, `sensor_valid`
- aktuator: `servo_pos`, `servo_pos_control`
- konteks: `scenario`, `control_mode`
- integrasi: `published_to_mqtt`, `payload`

### Alur data

1. `FloodWatchSimulator.tick()` membuat satu record `Telemetry`.
2. API dan admin membaca tabel ini untuk histori.
3. Field `published_to_mqtt` diperbarui jika publish broker berhasil.

### Cara kerja

Model ini menyimpan snapshot final tiap tick, sehingga histori tidak tergantung lagi pada state terbaru di `IoTNode`.

## `telemetry/serializers.py`

### Fungsi file

Serializer read-only untuk data telemetry.

### Class penting

- `TelemetrySerializer`
  Mengembalikan data telemetry plus `node_id` dan `node_name`.

### Alur data

Model `Telemetry` -> serializer -> response API telemetry.

### Cara kerja

Semua field dibuat read-only karena telemetry adalah histori, bukan data yang seharusnya diedit dari API.

## `telemetry/views.py`

### Fungsi file

Endpoint baca telemetry dan endpoint data terbaru.

### Class dan method penting

- `TelemetryViewSet`
  Endpoint read-only berbasis DRF.
- `get_queryset()`
  Menambahkan filter `node_id` dan `status`.
- `latest()`
  Mengembalikan telemetry terbaru per node atau untuk satu node tertentu.

### Alur data

1. Request masuk ke viewset.
2. Queryset memuat relasi `node` dengan `select_related`.
3. Filter query param diterapkan bila ada.
4. Serializer mengubah hasil query menjadi JSON response.

### Cara kerja

Method `latest()` tidak memakai agregasi SQL khusus. Ia mengambil data sesuai urutan model lalu memilih item pertama per node di sisi Python.

## `telemetry/admin.py`

### Fungsi file

Mengatur tampilan admin untuk histori telemetry.

### Class penting

- `TelemetryAdmin`
  Menentukan kolom, filter, pencarian, dan field read-only.

### Cara kerja

Admin diposisikan sebagai alat inspeksi histori, bukan alat edit. Karena itu payload dan waktu pembuatan dijadikan read-only.
