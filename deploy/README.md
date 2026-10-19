# Deployment - Selmar

Target: **https://selmar.ksisolusi.com** (shared hosting `ksisolusi.com`,
cPanel + CloudLinux + LiteSpeed, tanpa Docker/root).

> Server tujuan **tidak mendukung Docker** (tidak ada daemon, tidak ada
> `sudo`/root, terisolasi CageFS). Karena itu deployment memakai mekanisme
> bawaan hosting: **virtualenv Python 3.10 + CloudLinux Passenger** — sama
> persis dengan deployment `sekolah.ksisolusi.com`.

## Peta deployment di server

| Komponen | Lokasi |
|---|---|
| Source aplikasi | `~/apps/selmar` (PassengerAppRoot) |
| Virtualenv Python 3.10 | `~/virtualenv/apps/selmar/3.10` |
| Docroot subdomain | `~/public_html/selmar` |
| Konfigurasi (Passenger + env) | `~/public_html/selmar/.htaccess` ← salinan `deploy/htaccess.production` |
| Media (permanen, di luar source) | `~/public_html/selmar/apps/media` ← symlink dari `~/apps/selmar/apps/media` |
| Static hasil `collectstatic` | `~/apps/selmar/apps/staticfiles` → disajikan via symlink `public_html/selmar/apps/static` dan `public_html/selmar/static` |
| Database | MariaDB `ksis7654_selmar`, user `ksis7654_bono` (di `.htaccess` sebagai `SetEnv DB_*`) |

## Cara deploy ulang

```bash
chmod +x deploy/deploy.sh     # sekali saja
./deploy/deploy.sh            # default host: ksisolusi.com (lihat ~/.ssh/config)
./deploy/deploy.sh user@host  # host lain
```

Alur skrip: kirim source (tar-over-SSH, server tidak punya `rsync`) →
`pip install -r requirements.txt` → tulis `.htaccess` → pasang symlink static
→ `collectstatic` → `touch tmp/restart.txt` (restart Passenger) → cek HTTP.

Perubahan kode **hanya** cukup jalankan ulang `./deploy/deploy.sh`.

## Konfigurasi environment

Dibaca `core/settings.py` melalui `os.environ` (diisi `SetEnv` di `.htaccess`):

- `ALLOWED_HOSTS`, `DEBUG`, `SECRET_KEY`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `DATABASE_URL` (opsional, menimpa `DB_*` bila diisi)

> **PENTING:** setiap kali `SetEnv` di `.htaccess` diubah, jalankan
> `touch ~/apps/selmar/tmp/restart.txt` — Passenger membaca env saat proses
> di-spawn, jadi perubahan tidak aktif sampai restart.

## Perintah operasional (via SSH)

```bash
ssh ksisolusi.com
cd ~/apps/selmar
export DB_NAME=ksis7654_selmar DB_USER=ksis7654_bono DB_PASSWORD='Tr1-B0n0' \
       DB_HOST=localhost DB_PORT=3306
V=~/virtualenv/apps/selmar/3.10/bin/python

$V manage.py migrate                 # terapkan migrasi baru
$V manage.py loaddata setup_data     # fixture awal
$V manage.py collectstatic --noinput
$V manage.py check --deploy          # cek setting produksi
touch tmp/restart.txt                # restart aplikasi
```

## Membuat superuser

Model `apps.User` adalah `AUTH_USER_MODEL` dan `save()` memanggil
`get_current_user()` yang `None` di luar konteks request, sehingga
`manage.py createsuperuser` bisa gagal. Gunakan shell:

```bash
cd ~/apps/selmar
DB_NAME=ksis7654_selmar DB_USER=ksis7654_bono DB_PASSWORD='Tr1-B0n0' \
  ~/virtualenv/apps/selmar/3.10/bin/python manage.py shell
```

```python
from apps.models import User
u = User(username='bono2666', email='bono2666@ksisolusi.com',
         is_superuser=True, is_staff=True, is_active=True)
u.set_password('PASSWORD')
u.save()
```

## Catatan penting

- **INSIDEN & AKAR MASALAH (wajib paham):** deploy pertama gagal total
  (LiteSpeed 500, sesi SSH ikut mati ±10 menit). Penyebabnya: request
  pertama memuat `apps/views.py` → `import pandas` → numpy/OpenBLAS mencoba
  membuat **48 thread** (jumlah core host) → `pthread_create failed:
  Resource temporarily unavailable` → worker crash, lalu LiteSpeed
  men-spawn ulang berulang kali dan membanjiri host dengan thread sampai
  proses lain (termasuk `sshd`) ikut gagal fork. **Fix: paksa 1 thread**
  di dua lapis — `SetEnv OMP_NUM_THREADS/OPENBLAS_NUM_THREADS/...` di
  `.htaccess` *dan* `os.environ.setdefault(...)` di `core/settings.py`.
  Jangan hapus keduanya.
- **Venv harus memuat file bawaan CloudLinux**: `bin/set_env_vars.py`
  (symlink ke `/usr/share/l.v.e-manager/utils/set_env_vars.py`) dan
  `bin/python3.10_bin`. Tanpanya `/usr/local/lsws/fcgi-bin/lswsgi_wrapper`
  gagal di baris 9 tiap spawn. `deploy/deploy.sh` sudah memastikannya.
- **Fixture `apps/fixtures/setup_data.json` kedaluwarsa**: model
  `apps.Setup` sudah tidak ada di `apps/models.py`, jadi `loaddata
  setup_data` gagal (`Invalid model identifier`). Aman dilewati —
  database cukup diisi lewat aplikasi/admin.
- **Log aplikasi**: `~/apps/selmar/stderr.log` (traceback Passenger/Django).
  Galat fork host: `~/error_log` (warning PHP `proc_open(): Fork failed`).
- **`STATIC_URL`** diperbaiki dari `'apps/static/'` (relatif, rusak di rute
  bersarang) menjadi `'/apps/static/'` — mengikuti deployment `sekolah`.
- **Media lama** di `public_html/selmar/apps/media` (±21 MB, dari hosting
  lama `ksis8742`) **dipertahankan** dan tetap menjadi dokumen yang dilayani.
- **Static lama** di `public_html/selmar/apps/static` dipindah ke
  `~/trash/selmar-static-old-<waktu>` (bukan dihapus) lalu diganti symlink ke
  hasil `collectstatic`.
- **Docker**: `docker compose` tidak tersedia di server tujuan; berkas
  Dockerfile dsb. hanya untuk mesin lokal.
- Menyalakan `DEBUG` sementara: ubah `SetEnv DEBUG "True"` di `.htaccess`
  lalu `touch ~/apps/selmar/tmp/restart.txt`. **Kembalikan ke `"False"`
  setelah selesai.**
