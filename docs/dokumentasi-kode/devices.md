# Dokumentasi Modul Devices

## `devices/__init__.py`

### Fungsi file

Marker package Python untuk app `devices`.

### Cara kerja

Tidak ada logika khusus.

## `devices/apps.py`

### Fungsi file

Mendaftarkan app `devices` ke Django.

### Class penting

- `DevicesConfig`
  Menentukan nama app dan tipe primary key default.

### Cara kerja

Django membaca class ini saat memuat `INSTALLED_APPS`.

## `devices/urls.py`

### Fungsi file

Placeholder route lokal untuk app `devices`.

### Cara kerja

Saat ini file belum dipakai karena route `devices` langsung didaftarkan di `config/urls.py` melalui DRF router.

## `devices/forms.py`

### Fungsi file

Mengatur form admin untuk model `IoTNode`.

### Class penting

- `IoTNodeAdminForm`
  Menambahkan widget slider untuk field simulasi manual.

### Detail fungsi

- `Meta.widgets`
  Mengubah `simulation_distance_cm` dan `simulation_drift_bias_cm` menjadi `input[type=range]`.
- `Media`
  Menyisipkan file JavaScript admin kustom.

### Alur data

Admin membuka form node -> Django memakai form ini -> slider tampil -> JS menampilkan nilai realtime.

### Cara kerja

File ini tidak menyentuh logika simulasi. Tugasnya hanya memperbaiki pengalaman input di admin.

## `devices/models.py`

### Fungsi file

Menyimpan model utama node FloodWatch dan state runtime terkini.

### Fungsi dan class penting

- `_default_last_payload()`
  Nilai default aman untuk field JSON payload terakhir.
- `_default_runtime_state()`
  Nilai default aman untuk state runtime internal simulator.
- `IoTNode`
  Model utama seluruh simulator.
- `IoTNode.clean()`
  Menormalkan semua nilai input agar tetap berada dalam rentang aman.
- `IoTNode.save()`
  Memastikan `clean()` selalu dijalankan sebelum simpan.
- `IoTNode.resolve_auto_servo_target(status=None)`
  Menentukan target servo otomatis berdasarkan status banjir.
- `IoTNode.runtime_defaults()`
  Menggabungkan default runtime dengan data runtime yang tersimpan.
- `IoTNode.health_snapshot()`
  Membentuk ringkasan status node untuk API health dan serializer.

### Data penting dalam model

- identitas node: `node_id`, `node_name`, `physical_id`
- lokasi: `site_name`, `location_label`, `lat`, `lng`
- kontrol loop: `simulator_enabled`, `mqtt_enabled`, `interval_seconds`
- sumber simulasi: `current_scenario`, `simulation_mode`, `simulation_distance_cm`
- threshold status: `aman_min_percent`, `waspada_min_percent`, `status_hysteresis_percent`
- servo: `control_mode`, `manual_servo_target`, `servo_aman`, `servo_waspada`, `servo_bahaya`
- runtime: `current_status`, `current_distance_cm`, `current_servo_pos`, `runtime_state`, `last_payload`

### Alur data

1. Node dibuat dari admin, API, atau seed command.
2. `clean()` memastikan field valid sebelum tersimpan.
3. Simulator membaca field konfigurasi node untuk menghasilkan tick.
4. Setelah tick, simulator menulis balik status dan payload terakhir ke model ini.
5. API health dan API nodes membaca model ini sebagai state saat ini.

### Cara kerja

`IoTNode` berperan ganda:

- sebagai konfigurasi node
- sebagai cache state runtime terbaru

Karena itu model ini menjadi pusat hampir semua alur data sistem.

## `devices/serializers.py`

### Fungsi file

Serializer DRF untuk model `IoTNode`.

### Class penting

- `IoTNodeSerializer`
  Mengekspos hampir seluruh field node dan menambahkan field `health`.

### Fungsi penting

- `get_health(obj)`
  Mengambil hasil `obj.health_snapshot()`.

### Alur data

Model `IoTNode` -> serializer -> response API `nodes`.

### Cara kerja

Field runtime dijadikan read-only agar state hasil simulator tidak mudah ditimpa oleh request API biasa.

## `devices/views.py`

### Fungsi file

Menyediakan endpoint API untuk data node dan ringkasan health.

### Class penting

- `IoTNodeViewSet`
  Endpoint CRUD node berbasis DRF `ModelViewSet`.
- `FleetHealthView`
  Endpoint ringkas status seluruh node aktif.

### Alur data

- `IoTNodeViewSet`
  request API -> ORM `IoTNode` -> serializer -> response
- `FleetHealthView`
  request API -> filter node aktif -> `health_snapshot()` tiap node -> response

### Cara kerja

`lookup_field = "node_id"` membuat API node memakai `node_id` sebagai identitas URL, bukan primary key integer.

## `devices/admin.py`

### Fungsi file

Mengatur tampilan dan perilaku Django admin untuk model `IoTNode`.

### Class dan method penting

- `IoTNodeAdmin`
  Konfigurasi lengkap admin node.
- `simulation_console_help(self, obj)`
  Menampilkan panduan cara menjalankan worker dari halaman admin.

### Bagian penting admin

- `list_display`
  Kolom ringkas daftar node.
- `list_filter`
  Filter cepat berdasarkan status, mode, dan flag runtime.
- `readonly_fields`
  Melindungi field runtime agar tidak diedit manual.
- `fieldsets`
  Memecah form ke blok identitas, simulator, sensor, servo, dan runtime.

### Alur data

Admin membuka atau menyimpan node -> Django memakai `IoTNodeAdminForm` -> model `IoTNode` disimpan -> worker membaca node tersebut saat tick berikutnya.

### Cara kerja

File ini penting untuk operasional karena hampir semua pengaturan simulator manual tersedia dari admin.

## `devices/static/devices/admin/iotnode_simulation.js`

### Fungsi file

JavaScript kecil untuk menampilkan nilai slider realtime di admin.

### Fungsi penting

- `attachRangeOutput(input)`
  Membuat atau memperbarui elemen output untuk slider tertentu.
- listener `DOMContentLoaded`
  Mencari seluruh slider yang punya atribut `data-range-output`.

### Alur data

Perubahan slider di browser -> event `input` -> teks nilai di bawah slider ikut diperbarui.

### Cara kerja

File ini hanya mempengaruhi tampilan admin. Tidak mengubah logika backend.
