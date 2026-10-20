#!/usr/bin/env bash
# =============================================================================
# Deploy aplikasi Selmar ke shared hosting ksisolusi.com (Passenger)
# Pemakaian : ./deploy/deploy.sh [user@host]
# Server    : TIDAK punya rsync, jadi dipakai tar-over-SSH.
# =============================================================================
set -euo pipefail

REMOTE="${1:-ksisolusi.com}"
APP_DIR="/home/ksis7654/apps/selmar"
VENV="/home/ksis7654/virtualenv/apps/selmar/3.10"
DOCROOT="/home/ksis7654/public_html/selmar"

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> [1/7] Kirim source ke ${REMOTE}:${APP_DIR}"
tar czf - \
  --exclude='./venv' --exclude='./bin' --exclude='./lib' --exclude='./pyvenv.cfg' \
  --exclude='./.git' --exclude='*/__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
  --exclude='./._*' --exclude='*/._*' \
  --exclude='./.idea' --exclude='./.vscode' --exclude='./stderr.log' --exclude='./.env' \
  --exclude='./apps/media' --exclude='./apps/staticfiles' \
  -C "$SRC_DIR" . | ssh "$REMOTE" "set -e
    mkdir -p '$APP_DIR'
    cd '$APP_DIR'
    # bersihkan isi lama; simpan .git/tmp/public/passenger_wsgi/stderr.log
    find . -mindepth 1 -maxdepth 1 \
      ! -name .git ! -name tmp ! -name public \
      ! -name passenger_wsgi.py ! -name stderr.log \
      -exec rm -rf {} +
    tar xzf -
    find . -name '._*' -delete
    # media permanen ada di docroot -> jadikan symlink dari app
    if [ ! -L apps/media ]; then rm -rf apps/media; ln -s '$DOCROOT/apps/media' apps/media; fi
    [ -f passenger_wsgi.py ] || cp -f deploy/passenger_wsgi.py passenger_wsgi.py
    echo '    transfer OK'"

echo "==> [2/7] Sinkronkan dependensi"
ssh "$REMOTE" "$VENV/bin/pip install -q --upgrade pip >/dev/null 2>&1 || true"
ssh "$REMOTE" "set -e
  # File bawaan CloudLinux yang dibutuhkan /usr/local/lsws/fcgi-bin/lswsgi_wrapper.
  # Tanpa ini LiteSpeed membuang pesan 'set_env_vars.py: No such file' tiap spawn.
  [ -e '$VENV/bin/set_env_vars.py' ] || ln -s /usr/share/l.v.e-manager/utils/set_env_vars.py '$VENV/bin/set_env_vars.py'
  [ -e '$VENV/bin/python3.10_bin' ] || ln -s /opt/alt/python310/bin/python3.10 '$VENV/bin/python3.10_bin'
  '$VENV/bin/pip' install -q -r '$APP_DIR/requirements.txt' && echo '    pip OK'"

echo "==> [3/7] Pasang .htaccess produksi"
# Prioritas: berkas .local (berisi kredensial, ter-gitignore) > templat.
HTACCESS="$SRC_DIR/deploy/htaccess.production"
if [ -f "$HTACCESS.local" ]; then HTACCESS="$HTACCESS.local"; fi
if grep -q '<GANTI_\|<DB_\|<PASSWORD_' "$HTACCESS"; then
  echo "    ERROR: $HTACCESS masih berisi placeholder." >&2
  echo "    Isi dulu deploy/htaccess.production.local dari templatnya." >&2
  exit 1
fi
ssh "$REMOTE" "cat > '$DOCROOT/.htaccess'" < "$HTACCESS"
echo "    .htaccess OK ($(basename "$HTACCESS"))"

echo "==> [4/7] Siapkan symlink static di docroot"
# heredoc kutip ganda -> SEMUA variabel dieksekusi di server, bukan lokal
ssh "$REMOTE" <<EOF
set -e
APP_DIR="$APP_DIR"
DOCROOT="$DOCROOT"
TS="\$(date +%Y%m%d%H%M%S)"
mkdir -p "/home/ksis7654/trash"
# direktori statis lama dipindah (bukan dihapus) lalu diganti symlink
if [ ! -L "\$DOCROOT/apps/static" ] && [ -e "\$DOCROOT/apps/static" ]; then
  mv "\$DOCROOT/apps/static" "/home/ksis7654/trash/selmar-static-old-\$TS"
fi
[ -L "\$DOCROOT/apps/static" ] || ln -s "\$APP_DIR/apps/staticfiles" "\$DOCROOT/apps/static"
if [ ! -L "\$DOCROOT/static" ] && [ -e "\$DOCROOT/static" ]; then
  mv "\$DOCROOT/static" "/home/ksis7654/trash/selmar-root-static-old-\$TS"
fi
[ -L "\$DOCROOT/static" ] || ln -s "\$APP_DIR/apps/staticfiles" "\$DOCROOT/static"
echo "    symlink OK"
EOF

echo "==> [5/7] collectstatic (--clear: buang hasil lama agar tidak ada aset basi)"
ssh "$REMOTE" "$VENV/bin/python '$APP_DIR/manage.py' collectstatic --noinput --clear | tail -2"

echo "==> [6/7] Restart Passenger"
ssh "$REMOTE" "mkdir -p '$APP_DIR/tmp' && touch '$APP_DIR/tmp/restart.txt' && echo '    restart OK'"

echo "==> [7/7] Verifikasi"
curl -sS -o /dev/null -w "    https://selmar.ksisolusi.com/ -> %{http_code}\n" --max-time 60 \
  https://selmar.ksisolusi.com/ || true

echo "==> Deploy selesai."
