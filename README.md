# Prince Kumar — DevOps Portfolio

A full-stack portfolio website with Python Flask backend, Gmail SMTP contact, and a server marketplace.

---

## 📁 Project Structure

```
portfolio/
├── index.html        ← Frontend (single-page portfolio)
├── app.py            ← Python Flask backend
├── servers.json      ← Auto-created server listings database
├── requirements.txt  ← Python dependencies
└── README.md
```

---

## ⚙️ Setup & Run

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Gmail SMTP

You need a **Gmail App Password** (NOT your regular Gmail password):

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Go to **App Passwords** → Select "Mail" → Generate
4. Copy the 16-character password

Set environment variables:

```bash
# Linux / macOS
export GMAIL_USER="kmprince15932@gmail.com"
export GMAIL_PASSWORD="your_16_char_app_password"
export NOTIFY_EMAIL="kmprince15932@gmail.com"

# Windows (Command Prompt)
set GMAIL_USER=kmprince15932@gmail.com
set GMAIL_PASSWORD=your_16_char_app_password
```

Or edit `app.py` directly:
```python
GMAIL_USER     = "kmprince15932@gmail.com"
GMAIL_PASSWORD = "your_app_password_here"
NOTIFY_EMAIL   = "kmprince15932@gmail.com"
```

### 3. Run the server

```bash
# Development
python app.py

# Production (Gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Visit: **http://localhost:5000**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/contact` | Send contact form email |
| `GET` | `/api/servers` | List all servers |
| `GET` | `/api/servers?type=vps` | Filter by type |
| `POST` | `/api/servers` | Add new server listing |
| `GET` | `/api/servers/:id` | Get single server |
| `PUT` | `/api/servers/:id` | Update server |
| `DELETE` | `/api/servers/:id` | Delete server |
| `POST` | `/api/servers/:id/inquire` | Send server inquiry email |

---

## 📧 Contact API Example

```bash
curl -X POST http://localhost:5000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Client Name",
    "email": "client@company.com",
    "subject": "DevOps Consulting",
    "message": "I need help setting up Kubernetes on AWS EKS."
  }'
```

## 🖥️ Add Server API Example

```bash
curl -X POST http://localhost:5000/api/servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-prod-vps",
    "type": "vps",
    "cpu": "8 vCPU",
    "ram": "16 GB DDR4",
    "storage": "500 GB NVMe",
    "bandwidth": "1 Gbps",
    "location": "Mumbai, IN",
    "price": 59
  }'
```

---

## ☁️ Deploy to Production

### Option 1 — VPS (Ubuntu/Nginx)

```bash
# Install nginx
sudo apt install nginx

# Run with Gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app &

# Nginx config /etc/nginx/sites-available/portfolio
server {
    listen 80;
    server_name yourdomain.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 2 — Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t prince-portfolio .
docker run -p 5000:5000 \
  -e GMAIL_USER=kmprince15932@gmail.com \
  -e GMAIL_PASSWORD=your_app_password \
  prince-portfolio
```

### Option 3 — Render / Railway (Free hosting)
1. Push to GitHub
2. Connect to [render.com](https://render.com) or [railway.app](https://railway.app)
3. Set environment variables in dashboard
4. Deploy!

---

## 🔒 Security Notes

- Never commit `GMAIL_PASSWORD` to git — always use environment variables
- Add a `.gitignore` with `servers.json` if you don't want to commit listings
- For production, add rate limiting (`flask-limiter`) to the contact endpoint

---

*Built for Prince Kumar — DevOps & SRE Engineer*
# portfolio
