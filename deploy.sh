#!/bin/bash

# === НАСТРОЙКИ ===
PROJECT_NAME="diplom"
PROJECT_DIR="/home/$USER/$PROJECT_NAME"
REPO_URL="https://your-repo-url.git"   # Поменяй на свой
DJANGO_USER="$USER"
DOMAIN="giraffecars.ru"             # Или оставь как IP

DB_NAME="diplom"
DB_USER="aivv"
DB_PASS="zamay228"

# === УСТАНОВКА ПАКЕТОВ ===
dnf update -y
dnf install python3 python3-pip python3-virtualenv git nginx postgresql-server postgresql-contrib -y

# === PostgreSQL ===
postgresql-setup --initdb
systemctl enable --now postgresql

# === Создание БД и пользователя ===
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# === Django-проект ===
cd /home/$USER
git clone $REPO_URL $PROJECT_NAME
cd $PROJECT_NAME
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# === Настройка .env или settings.py вручную здесь ===
echo "⚠️ ВНИМАНИЕ: Настрой БД в settings.py вручную перед продолжением."

read -p "Нажми [Enter], когда будешь готов продолжить..."

# === Миграции и статика ===
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# === Gunicorn systemd socket ===
cat <<EOF > /etc/systemd/system/gunicorn.socket
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

# === Gunicorn systemd service ===
cat <<EOF > /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=$DJANGO_USER
Group=nginx
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock $PROJECT_NAME.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reexec
systemctl daemon-reload
systemctl start gunicorn.socket
systemctl enable gunicorn.socket

# === NGINX конфиг ===
cat <<EOF > /etc/nginx/conf.d/$PROJECT_NAME.conf
server {
    listen 80;
    server_name $DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root $PROJECT_DIR;
    }

    location /media/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
EOF

nginx -t && systemctl restart nginx

# === Firewall ===
firewall-cmd --permanent --add-service=http
firewall-cmd --reload

echo "🎉 Готово! Перейди на http://$DOMAIN и проверь приложение!"
