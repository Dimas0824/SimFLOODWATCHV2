# Dokumentasi Root dan Config

## `manage.py`

### Fungsi file

Entry point utama semua perintah Django.

### Fungsi penting

- `main()`
  Menetapkan `config.settings`, mengimpor `execute_from_command_line`, lalu menjalankan perintah Django sesuai argumen terminal.

### Alur data

Input terminal `python manage.py ...` masuk ke `sys.argv`, lalu diteruskan ke executor Django.

### Cara kerja

Jika Django belum terpasang, file ini melempar pesan error yang lebih ramah daripada traceback default.

## `requirements.txt`

### Fungsi file

Daftar dependency Python project.

### Isi penting

- `Django`
- `djangorestframework`
- `paho-mqtt`
- `python-dotenv`

### Cara kerja

File ini dipakai saat instalasi environment dengan `pip install -r requirements.txt`.

## `README.md`

### Fungsi file

Dokumentasi tingkat proyek untuk setup, endpoint utama, dan cara menjalankan simulator.

### Isi penting

- quick start
- penjelasan admin
- command worker
- mode simulasi interaktif
- penjelasan field admin
- daftar endpoint

### Cara kerja

README adalah panduan onboarding. Detail implementasi file-file kode dijelaskan lebih rinci pada folder dokumentasi ini.

## `.env.example`

### Fungsi file

Template environment variable yang dibutuhkan project.

### Key penting

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_TIME_ZONE`
- seluruh konfigurasi `MQTT_*`

### Alur data

Nilai pada file ini biasanya disalin ke `.env`, lalu dibaca `config/settings.py` dan `simulator/mqtt_client.py`.

### Cara kerja

File ini tidak dipakai langsung saat runtime. Nilainya menjadi acuan saat pengguna membuat `.env`.

## `.gitignore`

### Fungsi file

Mencegah file lokal dan sensitif ikut masuk git.

### Isi penting

- `.venv`
- `__pycache__`
- `.env`
- `db.sqlite3`

### Cara kerja

Git akan mengabaikan file/folder tersebut saat status dan commit.

## `config/__init__.py`

### Fungsi file

Marker package Python untuk folder `config`.

### Fungsi penting

Tidak ada isi logika.

### Cara kerja

Membuat `config` bisa diimpor sebagai module Python.

## `config/asgi.py`

### Fungsi file

Entry point ASGI untuk deployment async.

### Fungsi penting

- `application`
  Objek ASGI hasil `get_asgi_application()`.

### Alur data

Server ASGI akan memanggil objek `application` ini untuk setiap request atau koneksi yang masuk.

### Cara kerja

File ini minimal karena seluruh konfigurasi aplikasi tetap berasal dari `config.settings`.

## `config/wsgi.py`

### Fungsi file

Entry point WSGI untuk deployment sinkron klasik.

### Fungsi penting

- `application`
  Objek WSGI hasil `get_wsgi_application()`.

### Cara kerja

Dipakai oleh server yang berbasis WSGI seperti Gunicorn mode WSGI atau server hosting tradisional.

## `config/settings.py`

### Fungsi file

Konfigurasi inti Django dan REST API project.

### Fungsi penting

- `env_bool(name, default=False)`
  Mengubah environment variable menjadi boolean.
- `env_list(name, default)`
  Mengubah environment variable berbentuk comma separated string menjadi list.

### Konfigurasi penting

- `BASE_DIR`
- `INSTALLED_APPS`
- `MIDDLEWARE`
- `DATABASES`
- `LANGUAGE_CODE`
- `TIME_ZONE`
- `STATIC_URL`
- `REST_FRAMEWORK`

### Alur data

1. File mencoba memuat `.env`.
2. Nilai environment dipakai untuk `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, dan `TIME_ZONE`.
3. Django memakai file ini sebagai sumber semua konfigurasi runtime.

### Cara kerja

Project disetel cukup sederhana:

- database memakai SQLite
- validasi password default dimatikan
- REST API mendukung JSON, form, dan multipart
- bahasa default `id-id`

## `config/urls.py`

### Fungsi file

Pusat routing URL project.

### Komponen penting

- `router`
  `DefaultRouter` DRF untuk endpoint berbasis viewset.
- `urlpatterns`
  Daftar route final project.

### Route utama

- `admin/`
- `api/nodes/`
- `api/telemetry/`
- `api/health/`
- `api/simulator/control/`
- `api/simulator/tick/<node_id>/`

### Alur data

Request masuk ke file ini dulu, lalu diarahkan ke view module `devices`, `telemetry`, atau `simulator`.

### Cara kerja

File ini menggabungkan pendekatan router DRF dan route manual biasa.
