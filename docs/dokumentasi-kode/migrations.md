# Dokumentasi Migrations

Dokumen ini menjelaskan file migration yang membentuk skema database. File migration tidak menjalankan logika bisnis harian, tetapi penting untuk memahami evolusi tabel.

## `devices/migrations/__init__.py`

### Fungsi file

Marker package Python untuk migration app `devices`.

### Cara kerja

Tidak ada logika khusus.

## `devices/migrations/0001_initial.py`

### Fungsi file

Migration awal untuk membuat tabel `IoTNode`.

### Isi penting

- membuat hampir seluruh field dasar node
- menyiapkan field runtime dan servo
- menetapkan ordering berdasarkan `node_id`

### Cara kerja

Saat `python manage.py migrate` dijalankan, file ini membentuk fondasi tabel master node.

## `devices/migrations/0002_iotnode_interactive_simulation.py`

### Fungsi file

Menambahkan field yang dibutuhkan mode simulasi interaktif.

### Perubahan penting

- `mqtt_enabled`
- `simulation_distance_cm`
- `simulation_drift_bias_cm`
- `simulation_mode`
- `simulation_water_active`
- `simulator_enabled`

### Cara kerja

Migration ini memperluas `IoTNode` agar bisa dipakai sebagai simulator manual dari admin.

## `devices/migrations/0003_alter_iotnode_last_payload_alter_iotnode_lat_and_more.py`

### Fungsi file

Menyempurnakan definisi field pada `IoTNode`.

### Perubahan penting

- default `last_payload` memakai helper function
- default `runtime_state` memakai helper function
- `lat` dan `lng` diberi validator rentang

### Cara kerja

Perubahan ini membuat default JSON lebih aman dan input koordinat lebih tervalidasi.

## `telemetry/migrations/__init__.py`

### Fungsi file

Marker package Python untuk migration app `telemetry`.

### Cara kerja

Tidak ada logika khusus.

## `telemetry/migrations/0001_initial.py`

### Fungsi file

Migration awal untuk membuat tabel `Telemetry`.

### Isi penting

- membuat relasi ke `IoTNode`
- menyimpan data sensor, status, servo, dan payload
- menambahkan index untuk node+timestamp dan status+timestamp

### Cara kerja

File ini membuat struktur histori telemetry agar query terbaru dan query filter status lebih efisien.

## `telemetry/migrations/0002_rename_telemetry_t_node_id_00eef6_idx_telemetry_t_node_id_d39d1f_idx_and_more.py`

### Fungsi file

Mengganti nama index telemetry.

### Perubahan penting

- rename index node-timestamp
- rename index status-timestamp

### Cara kerja

Tidak mengubah model bisnis. File ini hanya menyelaraskan nama index yang dihasilkan migration.
