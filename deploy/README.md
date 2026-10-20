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
| Konfigurasi (Passenger + env) | `~/public_html/selmar/.htaccess` ← salinan `deploy/htaccess.production.local` (bila ada, else templat `deploy/htaccess.production`) |
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

## Kredensial & kebersihan repo

**Repo ini pernah publik dan pernah memuat kredensial** — karena itu:

- `deploy/htaccess.production` (ikut commit) hanya berisi **placeholder**.
  Nilai asli ada di `deploy/htaccess.production.local` yang masuk
  `.gitignore` — **tidak boleh** di-commit, dan hanya file itulah yang
  dikirim ke server.
- `deploy.sh` otomatis memakai `.local` bila ada, dan **gagal keras** bila
  yang terpilih masih berisi placeholder (mencegah `.htaccess` server
  tertimpa nilai `<GANTI_...>` yang membuat situs mati).
- `core/settings.py` tidak lagi menyimpan password: `SECRET_KEY`,
  `DB_*`, dan `EMAIL_HOST_PASSWORD` semuanya dari env.
- Ambil nilai produksi yang asli kapan saja dari server:
  `grep '^SetEnv' ~/public_html/selmar/.htaccess`
- Setelah mengubah `.local`, jalankan ulang `./deploy/deploy.sh`.

**Rotasi (wajib setelah repo pernah publik):**

1. Repo → Settings → *Danger Zone* → **Make repository private**.
2. cPanel → MySQL® Databases → ubah password user `ksis7654_bono`
   (password lama pernah terekspos dan user ini menguasai 3 database:
   `selmar`, `sekolah`, `wp106`). Lalu perbarui `DB_PASSWORD` di
   `deploy/htaccess.production.local` dan jalankan ulang deploy.
3. cPanel → Email Accounts → ubah password `abc_is@ksisolusi.com`, lalu
   perbarui `EMAIL_HOST_PASSWORD` di `.local` dan deploy ulang.
4. `SECRET_KEY` sudah diganti saat sanitasi ini (`z5y7vl…`), sehingga
   sesi lama kedaluwarsa — pengguna cukup login ulang.

## Konfigurasi environment

Dibaca `core/settings.py` melalui `os.environ` (diisi `SetEnv` di `.htaccess`):

- `ALLOWED_HOSTS`, `DEBUG`, `SECRET_KEY`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `DATABASE_URL` (opsional, menimpa `DB_*` bila diisi)

> **PENTING:** setiap kali `SetEnv` di `.htaccess` diubah, jalankan
> `touch ~/apps/selmar/tmp/restart.txt` — Passenger membaca env saat proses
> di-spawn, jadi perubahan tidak aktif sampai restart.
>
> **PENTING (stale worker):** LiteSpeed kadang menyajikan beberapa request
> pertama memakai worker yang lahir *sebelum* `.htaccess` baru dibaca,
> jadi header/env baru bisa telat terlihat. Verifikasi ulang setelah
> beberapa request, jangan hanya yang pertama.

## Hardening (`manage.py check --deploy` → 0 issues)

Semua saklar ada di env (`.htaccess`), tanpa perubahan kode:

| Env | Nilai | Efek |
|---|---|---|
| `SECURE_SSL_REDIRECT` | `True` | `http://` → 301 `https://` |
| `SESSION_COOKIE_SECURE` | `True` | `sessionid` hanya dikirim via HTTPS |
| `CSRF_COOKIE_SECURE` | `True` | `csrftoken` hanya dikirim via HTTPS |
| `SECURE_HSTS_SECONDS` | `31536000` | HSTS 1 tahun |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` | berlaku juga untuk `www.selmar.…` |
| `SECURE_HSTS_PRELOAD` | `True` | menandai situs *layak* preload |

`SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` menangkap skema
asli dari balik LiteSpeed, dengan fallback ke `wsgi.url_scheme` bila header
tidak ada — inilah yang mencegah redirect-loop.

> ⚠️ Mengaktifkan `SECURE_HSTS_PRELOAD` **belum** mendaftarkan apa pun ke
> browser. Pengiriman ke daftar preload dilakukan manual di
> <https://hstspreload.org>, butuh waktu berhari-hari untuk dicabut, dan
> `http://` pada subdomain ini tidak akan bisa dipakai lagi. Kalau tidak
> jadi, set `SECURE_HSTS_PRELOAD "False"` (atau `SECURE_HSTS_SECONDS "0"`
> untuk melepas HSTS sepenuhnya) lalu restart Passenger.

Matikan/menyalakan sementara tanpa menyentuh kode:

```bash
ssh ksisolusi.com
sed -i 's/SetEnv SECURE_SSL_REDIRECT "True"/SetEnv SECURE_SSL_REDIRECT "False"/' \
  ~/public_html/selmar/.htaccess
touch ~/apps/selmar/tmp/restart.txt
```

## Perintah operasional (via SSH)

```bash
ssh ksisolusi.com
cd ~/apps/selmar
# ambil SEMUA env produksi langsung dari .htaccess (jangan ketik manual).
# NB: pakai file, jangan <( proses ) — CageFS tidak menyediakan /dev/fd.
grep '^SetEnv' ~/public_html/selmar/.htaccess \
  | sed -E 's/^SetEnv "?([^" ]+)"? "?([^"]*)"?.*/\1="\2"/' > /tmp/selmar.envrc
set -a; . /tmp/selmar.envrc; set +a; rm -f /tmp/selmar.envrc
V=~/virtualenv/apps/selmar/3.10/bin/python

$V manage.py migrate                 # terapkan migrasi baru
$V manage.py loaddata setup_data     # fixture awal (saat ini: model sudah tidak ada)
$V manage.py collectstatic --noinput
$V manage.py check --deploy          # harus "no issues"
$V manage.py shell                   # diagnosa interaktif
touch tmp/restart.txt                # restart aplikasi
```

## Membuat superuser

Model `apps.User` adalah `AUTH_USER_MODEL` dan `save()` memanggil
`get_current_user()` yang `None` di luar konteks request, sehingga
`manage.py createsuperuser` bisa gagal. Gunakan shell:

```bash
cd ~/apps/selmar
grep '^SetEnv' ~/public_html/selmar/.htaccess \
  | sed -E 's/^SetEnv "?([^" ]+)"? "?([^"]*)"?.*/\1="\2"/' > /tmp/selmar.envrc
set -a; . /tmp/selmar.envrc; set +a; rm -f /tmp/selmar.envrc
~/virtualenv/apps/selmar/3.10/bin/python manage.py shell
```

```python
# `user_id` adalah USERNAME_FIELD (primary key), bukan `username`.
# save() memanggil get_current_user().user_id -> None di luar request,
# jadi patch dulu sebelum menyimpan.
import apps.models as m


class _System:
    user_id = 'system'


m.get_current_user = lambda: _System()

from apps.models import User

u, created = User.objects.get_or_create(
    user_id='bono2666',
    defaults={'username': 'bono2666', 'email': 'bono2666@ksisolusi.com'},
)
u.username = 'bono2666'
u.is_superuser = u.is_staff = u.is_active = True
u.set_password('GANTI_PASSWORD_DI_SINI')
u.save()
print(created, u.user_id, u.is_superuser, u.check_password('GANTI_PASSWORD_DI_SINI'))
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
