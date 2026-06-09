# Dokumentasi Kode SimFLOODWATCHV2

Dokumen ini adalah pintu masuk dokumentasi teknis untuk project `SimFLOODWATCHV2`. Fokusnya adalah menjelaskan fungsi tiap file, fungsi atau class penting di dalamnya, alur data, dan cara kerja sistem secara singkat dalam bahasa Indonesia.

## Cakupan

Dokumentasi ini mencakup:

- file root dan konfigurasi Django
- modul `devices`
- modul `telemetry`
- modul `simulator`
- file migration yang membentuk skema database

Dokumentasi ini tidak membahas file runtime atau file sensitif berikut:

- `.env`
- `db.sqlite3`
- folder `.venv`
- folder `__pycache__`
- folder `.git`

## Peta Dokumen

- [Alur Data](./alur-data.md)
- [Root dan Config](./root-config.md)
- [Modul Devices](./devices.md)
- [Modul Telemetry](./telemetry.md)
- [Modul Simulator](./simulator.md)
- [Migrations](./migrations.md)

## Ringkasan Arsitektur

Project ini adalah simulator FloodWatch berbasis Django dengan tiga domain utama:

- `devices`
  Menyimpan master node, konfigurasi simulasi, status runtime, dan konfigurasi servo.
- `simulator`
  Menjalankan logika simulasi sensor, menerima control command, dan mengirim payload ke MQTT bila aktif.
- `telemetry`
  Menyimpan histori hasil tick simulator dan menampilkan data tersebut lewat API/admin.

## Jalur Utama Sistem

1. Node dibuat atau diubah lewat Django Admin atau API `nodes`.
2. Worker simulator atau endpoint tick memanggil `FloodWatchSimulator.tick()`.
3. Hasil tick memperbarui record `IoTNode` dan menambah record `Telemetry`.
4. Jika MQTT aktif, payload telemetry dipublish ke broker.
5. API `health`, `nodes`, dan `telemetry` menyajikan data untuk UI atau integrasi lain.

## Cara Membaca Dokumentasi

- Mulai dari [Alur Data](./alur-data.md) jika ingin memahami sistem dari ujung ke ujung.
- Buka [Modul Simulator](./simulator.md) jika ingin fokus ke logika tick, kontrol, dan MQTT.
- Buka [Modul Devices](./devices.md) jika ingin fokus ke model node dan admin.
- Buka [Modul Telemetry](./telemetry.md) jika ingin fokus ke histori data dan query API.
