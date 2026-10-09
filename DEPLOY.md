# Deploy

One Ubuntu box, Docker Compose: Caddy (auto-HTTPS, static files) → gunicorn → SQLite on a volume.

## Server setup (once)

1. **Hetzner Cloud Firewall**: inbound TCP 22, 80, 443 and UDP 443 only. Enable Hetzner Backups.
   Don't rely on `ufw` for containers: Docker's published ports bypass it.
2. **SSH**: key-only. In `/etc/ssh/sshd_config.d/hardening.conf`:
   ```
   PasswordAuthentication no
   PermitRootLogin prohibit-password
   ```
   then `systemctl restart ssh`.
3. **Updates**: `apt install unattended-upgrades && dpkg-reconfigure -plow unattended-upgrades`.
4. **Docker**: install Docker Engine from the official apt repo (https://docs.docker.com/engine/install/ubuntu/).
5. **DNS**: A/AAAA records for the domain and `www` pointing at the box. Caddy can't get a certificate until they resolve.
6. **App**:
   ```
   git clone <repo> /opt/eshop && cd /opt/eshop
   cp .env.example .env && chmod 600 .env   # fill in
   docker compose up -d --build
   docker compose exec web python manage.py createsuperuser
   ```
7. **Stripe**: add a live webhook endpoint `https://<domain>/stripe/webhook/`, put its signing secret in `.env`, then `docker compose up -d`.
8. **Cron** (`crontab -e`):
   ```
   # drop abandoned pending orders
   0 4 * * * cd /opt/eshop && docker compose exec -T web python manage.py cleanup_orders
   # consistent SQLite snapshot (safe while the app is writing), keep 14 days
   30 4 * * * cd /opt/eshop && docker compose exec -T web sh -c 'mkdir -p /data/backup && python -c "import sqlite3,datetime; sqlite3.connect(\"/data/db.sqlite3\").backup(sqlite3.connect(f\"/data/backup/db-{datetime.date.today()}.sqlite3\"))" && find /data/backup -name "db-*.sqlite3" -mtime +14 -delete'
   ```
   Snapshots stay on the same disk; Hetzner Backups is what gets them off the box.

## Update

```
git pull && docker compose up -d --build
```
Migrations and `collectstatic` run on container start. Expect a few seconds of downtime.

## Useful

- Logs: `docker compose logs -f web`
- Shell: `docker compose exec web python manage.py shell`
- Data lives in the `data` volume (`/data/db.sqlite3`, `/data/media`); certificates in `caddy_data`. `docker compose down -v` deletes both.
- Local smoke test: set `DOMAIN=localhost` and `ALLOWED_HOSTS=localhost` in `.env`; Caddy issues a self-signed cert (`curl -k`).
