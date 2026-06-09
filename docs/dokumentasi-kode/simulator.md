# Dokumentasi Modul Simulator

## `simulator/__init__.py`

### Fungsi file

Marker package Python untuk app `simulator`.

### Cara kerja

Tidak ada logika khusus.

## `simulator/apps.py`

### Fungsi file

Mendaftarkan app `simulator` ke Django.

### Class penting

- `SimulatorConfig`
  Menentukan nama app dan tipe primary key default.

## `simulator/scenarios.py`

### Fungsi file

Menentukan daftar scenario simulasi dan generator jarak mentah.

### Konstanta penting

- `SCENARIO_NORMAL`
- `SCENARIO_DRIFT`
- `SCENARIO_SPIKE`
- `SCENARIO_DROPOUT`
- `SCENARIO_FLOOD_RISING`
- `SCENARIO_STUCK`
- `SCENARIO_INVALID_SENSOR`
- `SCENARIO_CHOICES`

### Fungsi penting

- `generate_distance_for_scenario(scenario, base_distance_cm, sensor_offset_cm, runtime_state)`
  Membuat nilai jarak mentah sesuai scenario aktif.

### Alur data

`FloodWatchSimulator._generate_raw_distance()` memanggil fungsi ini saat node berada pada mode `SCENARIO`.

### Cara kerja

Setiap scenario memiliki karakter berbeda:

- `normal`: noise kecil di sekitar baseline
- `drift`: bias perlahan bertambah
- `spike`: sesekali lonjakan besar
- `dropout`: sesekali tidak ada data
- `flood_rising`: jarak turun untuk meniru air naik
- `stuck`: nilai macet di pembacaan terakhir
- `invalid_sensor`: hasil sangat acak atau kosong

## `simulator/services.py`

### Fungsi file

Tempat inti logika simulasi FloodWatch.

### Fungsi dan class penting

- `STATUS_RANK`
  Urutan level status untuk logika eskalasi atau recovery.
- `clamp_float(value, min_value, max_value)`
  Membatasi angka float ke rentang aman.
- `round_distance(value, decimals)`
  Membulatkan hasil jarak.
- `calculate_water_height_cm(distance_cm, node)`
  Mengubah jarak sensor menjadi tinggi air.
- `water_height_percent(distance_cm, node)`
  Mengubah tinggi air menjadi persentase terhadap tinggi sensor.
- `SimulatorRuntime`
  Dataclass state runtime ringan yang disimpan ke `IoTNode.runtime_state`.
- `SimulatorRuntime.from_node(node)`
  Membaca runtime state dari node.
- `SimulatorRuntime.dump()`
  Mengubah runtime state kembali menjadi dict.
- `FloodWatchSimulator`
  Service utama untuk satu siklus tick.
- `FloodWatchSimulator.classify_status(...)`
  Menentukan status `AMAN`, `WASPADA`, `BAHAYA`, atau mempertahankan status lama.
- `FloodWatchSimulator._generate_raw_distance()`
  Menentukan nilai sensor mentah dari mode manual atau scenario.
- `FloodWatchSimulator._smooth_distance(raw_distance)`
  Menghaluskan data dengan exponential moving average.
- `FloodWatchSimulator._resolve_water_switch(distance_cm)`
  Menentukan status water switch.
- `FloodWatchSimulator._resolve_target_servo(status)`
  Menentukan target servo dari mode kontrol.
- `FloodWatchSimulator._step_servo(target_servo_pos)`
  Menggeser servo bertahap ke target.
- `FloodWatchSimulator.build_payload(...)`
  Membuat payload final untuk API, database, dan MQTT.
- `FloodWatchSimulator.tick()`
  Menjalankan satu siklus simulasi penuh dan menyimpan hasilnya.

### Alur data

1. `tick()` memuat waktu sekarang dan runtime state.
2. `_generate_raw_distance()` mengambil data sensor mentah.
3. `_smooth_distance()` membuat nilai sensor yang lebih stabil.
4. `classify_status()` menentukan status banjir.
5. `_resolve_target_servo()` dan `_step_servo()` menghitung posisi servo.
6. `build_payload()` membentuk payload final.
7. `IoTNode` diperbarui.
8. `Telemetry` dibuat.

### Cara kerja

File ini adalah jantung project. Hampir semua perilaku FloodWatch virtual diputuskan di sini.

## `simulator/control.py`

### Fungsi file

Memproses payload kontrol dari API atau MQTT dan menerapkannya ke `IoTNode`.

### Konstanta dan fungsi penting

- `SENSOR_OFFSET_KEYS`
  Daftar nama key alternatif yang dianggap setara untuk offset sensor.
- `clamp_int(value, min_value, max_value)`
  Membatasi integer ke rentang aman.
- `parse_boolish(value)`
  Mengubah nilai umum menjadi boolean.
- `servo_percent_to_degree(percent)`
  Mengubah persen servo ke derajat.
- `servo_degree_to_percent(degree)`
  Mengubah derajat servo ke persen.
- `normalize_target_node_id(payload)`
  Mengambil `node_id` dari dua format payload.
- `ensure_payload_targets_node(node, payload)`
  Menolak payload yang diarahkan ke node lain.
- `apply_control_message(node, payload, persist=True)`
  Fungsi utama untuk menerapkan command dan field kontrol.

### Alur data

1. Payload datang dari API control atau callback MQTT.
2. `apply_control_message()` memvalidasi target node.
3. Field yang relevan diperbarui pada objek `IoTNode`.
4. Runtime state servo ikut disesuaikan bila perlu.
5. Jika `persist=True`, node disimpan ke database.

### Cara kerja

File ini sengaja mendukung dua gaya payload:

- gaya internal simulator
- gaya yang kompatibel dengan firmware FloodWatch

Dengan begitu worker MQTT bisa menerima command yang lebih dekat ke sistem asli.

## `simulator/mqtt_client.py`

### Fungsi file

Wrapper kecil untuk koneksi MQTT publish dan subscribe.

### Fungsi dan class penting

- `env_bool(name, default=False)`
  Membaca environment variable boolean.
- `FloodWatchMQTTClient`
  Client MQTT per node.
- `is_configured()`
  Memeriksa apakah konfigurasi broker sudah lengkap.
- `connect()`
  Membuka koneksi dan memulai loop client.
- `publish_sensor_data(payload)`
  Publish payload sensor.
- `disconnect()`
  Menutup koneksi dan membersihkan file TLS sementara.
- `_prepare_tls_material(name, value, suffix)`
  Mendukung input sertifikat berupa path file atau isi PEM langsung.
- `_normalize_pem(value)`
  Menormalkan line break isi PEM.

### Alur data

1. Client dibuat oleh command simulator.
2. `connect()` membaca env broker dan membuka koneksi.
3. Saat terhubung, client subscribe ke topic kontrol.
4. Saat pesan kontrol masuk, callback meneruskan payload ke `apply_control_message()`.
5. Payload telemetry dipublish lewat `publish_sensor_data()`.

### Cara kerja

File ini membuat integrasi MQTT lebih fleksibel karena sertifikat TLS dapat diberikan sebagai path atau string inline di `.env`.

## `simulator/views.py`

### Fungsi file

Endpoint API untuk kontrol node dan tick manual.

### Class penting

- `SimulatorControlView`
  Menerima payload JSON control lalu menerapkan perubahan ke node.
- `SimulatorTickView`
  Menjalankan satu tick simulator untuk node tertentu.

### Alur data

- `SimulatorControlView`
  request JSON -> cari node -> `apply_control_message()` -> response hasil perubahan
- `SimulatorTickView`
  request -> cari node -> `FloodWatchSimulator.tick()` -> serializer telemetry -> response

### Cara kerja

View ini memisahkan perubahan konfigurasi/control dari eksekusi tick, sehingga pengujian manual jadi lebih mudah.

## `simulator/management/__init__.py`

### Fungsi file

Marker package Python untuk folder management app `simulator`.

### Cara kerja

Tidak ada logika khusus.

## `simulator/management/commands/__init__.py`

### Fungsi file

Marker package Python untuk kumpulan management command custom.

### Cara kerja

Tidak ada logika khusus.

## `simulator/management/commands/simulate_node.py`

### Fungsi file

Menjalankan loop simulator untuk satu node dari terminal.

### Class dan method penting

- `Command`
  Command Django custom.
- `add_arguments(parser)`
  Menambahkan argumen `--node-id`, `--scenario`, `--interval`, `--iterations`, dan `--mqtt`.
- `handle(*args, **options)`
  Menjalankan loop tick, publish MQTT opsional, dan menampilkan payload ke terminal.

### Alur data

1. Command membaca node dari database.
2. Jika perlu, scenario dan interval diperbarui.
3. Loop memanggil `FloodWatchSimulator(node).tick()`.
4. Jika MQTT aktif, payload dipublish dan flag telemetry diupdate.
5. Proses tidur sesuai interval node.

### Cara kerja

Command ini cocok untuk uji fokus pada satu node tanpa harus menjalankan worker semua node.

## `simulator/management/commands/seed_demo_nodes.py`

### Fungsi file

Membuat atau memperbarui node demo awal.

### Class dan method penting

- `Command`
  Command Django custom.
- `handle(*args, **options)`
  Menjalankan `update_or_create()` untuk dua node demo bawaan.

### Alur data

Data default di dalam file -> `IoTNode.update_or_create()` -> database.

### Cara kerja

Command ini aman dijalankan berulang karena memakai `update_or_create`, bukan create mentah.

## `simulator/management/commands/run_simulator_worker.py`

### Fungsi file

Worker kontinu untuk semua node aktif yang `simulator_enabled=true`.

### Class dan method penting

- `Command`
  Command Django custom untuk loop worker.
- `add_arguments(parser)`
  Menambahkan filter node, interval polling, dan mode debug.
- `handle(*args, **options)`
  Loop utama worker.
- `_cleanup_inactive_clients(...)`
  Menutup client MQTT yang tidak relevan lagi.
- `_ensure_mqtt_client(node, mqtt_clients, debug)`
  Membuat atau mengambil ulang client MQTT per node.
- `_due_status(node, now)`
  Menentukan apakah node sudah waktunya tick.
- `_describe_node(node)`
  Membentuk string debug singkat.
- `_debug(enabled, category, message)`
  Menulis log debug jika aktif.

### Alur data

1. Worker membaca semua node aktif yang simulatornya menyala.
2. Tiap node dicek apakah sudah due berdasarkan `interval_seconds`.
3. Jika due, worker menjalankan `FloodWatchSimulator.tick()`.
4. Jika `mqtt_enabled`, worker memastikan client MQTT tersedia lalu publish payload.
5. Histori telemetry dan flag publish diperbarui.
6. Worker mengulang polling terus-menerus sampai dihentikan user.

### Cara kerja

Ini adalah jalur paling realistis untuk meniru perangkat. File ini juga mengelola reuse client MQTT agar koneksi tidak dibuat ulang setiap tick.
