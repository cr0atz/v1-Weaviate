# INSTALL – Ubuntu + Apache Deployment

This guide covers deploying the FastAPI backend (Uvicorn + systemd) behind Apache as a reverse proxy, with the optional Streamlit UI.

## Prerequisites
- Ubuntu 22.04+ (root or sudo access)
- OpenAI API key
- Weaviate instance reachable from the server
- Domain or server IP

## 1) System packages
```
sudo apt update && sudo apt install -y \
  python3 python3-venv python3-pip \
  apache2 libapache2-mod-proxy-uwsgi \
  build-essential

# Enable Apache modules for reverse proxy
sudo a2enmod proxy proxy_http headers rewrite ssl
sudo systemctl restart apache2
```

## 2) Clone code and create virtualenv
```
cd /opt
sudo mkdir -p /opt/flast-ai && sudo chown "$USER":"$USER" /opt/flast-ai
cd /opt/flast-ai

# Place your repo here (git clone or copy)
# Example:
# git clone https://github.com/cr0atz/v1-Weaviate.git .

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
# Install base requirements; tolerate missing pins and add runtime deps
pip install -r requirements.txt || true
pip install fastapi uvicorn weaviate-client python-dotenv openai transformers beautifulsoup4 streamlit requests
```

## 3) Environment configuration
Create `/opt/flast-ai/.env`:
```
OPENAI_API_KEY=sk-...
WEAVIATE_API=http://localhost:8080
API_ENDPOINT=http://127.0.0.1:8000/generate_answers/
```
Permissions:
```
chmod 600 /opt/flast-ai/.env
```

## 4) Systemd service for FastAPI
Create `/etc/systemd/system/flast-ai.service`:
```
[Unit]
Description=FLAST-AI FastAPI Service
After=network.target

[Service]
User=%i
WorkingDirectory=/opt/flast-ai
Environment="PYTHONUNBUFFERED=1"
ExecStart=/opt/flast-ai/venv/bin/uvicorn Main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
If running as a specific user (e.g., `ubuntu`), replace `%i` with that username or convert to a simple service without `%i`.

Reload and start:
```
sudo systemctl daemon-reload
sudo systemctl enable flast-ai
sudo systemctl start flast-ai
sudo systemctl status flast-ai --no-pager
```

## 5) Apache reverse proxy
Create `/etc/apache2/sites-available/flast-ai.conf`:
```
<VirtualHost *:80>
    ServerName your.domain.tld

    # Redirect HTTP to HTTPS if using TLS (optional)
    # RewriteEngine On
    # RewriteCond %{HTTPS} off
    # RewriteRule ^/?(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]

    ProxyPreserveHost On
    ProxyPass        / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-Port  "80"

    ErrorLog ${APACHE_LOG_DIR}/flast-ai_error.log
    CustomLog ${APACHE_LOG_DIR}/flast-ai_access.log combined
</VirtualHost>
```
Enable site and reload:
```
sudo a2dissite 000-default.conf || true
sudo a2ensite flast-ai.conf
sudo systemctl reload apache2
```

For HTTPS, obtain a cert (e.g., with `certbot`) and update the vhost to `*:443` with TLS config.

## 6) Optional: Streamlit service
Streamlit is typically used by developers. If you want to expose Streamlit:
- Run locally via `streamlit run pages/Question_Answer.py`.
- Or create a separate systemd unit on a different port (e.g., 8501) and add another Apache proxy block.

## 7) Health checks
- FastAPI docs: `http://your.domain.tld/docs`
- Service status: `systemctl status flast-ai`
- Logs: `journalctl -u flast-ai -f`

## 8) Updates & deploys
```
cd /opt/flast-ai
sudo systemctl stop flast-ai
# git pull or replace code
source venv/bin/activate
pip install -r requirements.txt || true
pip install fastapi uvicorn weaviate-client python-dotenv openai transformers beautifulsoup4 streamlit requests || true
sudo systemctl start flast-ai
```

## Security notes
- Do not expose `.env` or logs with secrets.
- Replace hardcoded auth token in `Main.py` with a proper mechanism before production.
- Consider a firewall to limit access to Weaviate and Uvicorn loopback only.
