"""
Prince Kumar — DevOps Portfolio Backend
Flask app with:
  - Gmail SMTP contact form email
  - Server marketplace REST API
  - CORS enabled for frontend
"""

import os
import json
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ─────────────────────────────────────────────────────────
# CONFIGURATION  —  Edit these or use environment variables
# ─────────────────────────────────────────────────────────
GMAIL_USER     = "kmprince15932@gmail.com"
GMAIL_PASSWORD = "dcce mklw yjil xbhk"
NOTIFY_EMAIL   = "kmprince15932@gmail.com"
SERVERS_FILE   = "servers.json"


# ─────────────────────────────────────────────────────────
# SERVER DATA HELPERS
# ─────────────────────────────────────────────────────────
DEFAULT_SERVERS = [
    {
        "id": "srv-001", "name": "cloud-burst-01", "type": "vps",
        "cpu": "4 vCPU", "ram": "8 GB DDR4", "storage": "200 GB NVMe",
        "bandwidth": "500 Mbps", "location": "Mumbai, IN",
        "price": 29, "status": "available", "featured": False,
        "created_at": "2025-01-01"
    },
    {
        "id": "srv-002", "name": "titan-k8s-node", "type": "dedicated",
        "cpu": "16 Core Intel Xeon", "ram": "64 GB DDR4", "storage": "2 TB NVMe SSD",
        "bandwidth": "1 Gbps Unmetered", "location": "Noida, IN",
        "price": 199, "status": "available", "featured": True,
        "created_at": "2025-01-01"
    },
    {
        "id": "srv-003", "name": "micro-vps-lite", "type": "vps",
        "cpu": "2 vCPU", "ram": "4 GB", "storage": "80 GB SSD",
        "bandwidth": "250 Mbps", "location": "Delhi, IN",
        "price": 12, "status": "available", "featured": False,
        "created_at": "2025-01-01"
    },
    {
        "id": "srv-004", "name": "forge-bare-metal", "type": "dedicated",
        "cpu": "32 Core AMD EPYC", "ram": "128 GB ECC", "storage": "4 TB NVMe RAID",
        "bandwidth": "10 Gbps", "location": "Bangalore, IN",
        "price": 499, "status": "available", "featured": True,
        "created_at": "2025-01-01"
    },
]


def load_servers():
    """Load servers from JSON file, create with defaults if missing."""
    if not os.path.exists(SERVERS_FILE):
        save_servers(DEFAULT_SERVERS)
        return DEFAULT_SERVERS
    try:
        with open(SERVERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SERVERS


def save_servers(servers):
    """Persist servers list to JSON file."""
    with open(SERVERS_FILE, "w") as f:
        json.dump(servers, f, indent=2)


# ─────────────────────────────────────────────────────────
# EMAIL HELPER
# ─────────────────────────────────────────────────────────
def send_email(to_addr: str, subject: str, html_body: str, text_body: str = "") -> dict:
    """
    Send email via Gmail SMTP (TLS on port 587).
    Returns {"success": True} or {"success": False, "error": "..."}

    Gmail setup:
    1. Enable 2-Step Verification on your Google account
    2. Go to: myaccount.google.com → Security → App Passwords
    3. Generate an App Password for 'Mail'
    4. Use that 16-char password as GMAIL_PASSWORD
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = GMAIL_USER
        msg["To"]      = to_addr
        msg["Reply-To"] = to_addr

        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, to_addr, msg.as_string())

        return {"success": True}
    except smtplib.SMTPAuthenticationError:
        return {"success": False, "error": "Gmail auth failed. Check GMAIL_PASSWORD (use App Password, not account password)."}
    except smtplib.SMTPException as e:
        return {"success": False, "error": f"SMTP error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def contact_notification_html(name: str, email: str, subject: str, message: str) -> str:
    """HTML email template for contact form notification."""
    return f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family: 'Courier New', monospace; background: #050a08; color: #c8e6c9; margin: 0; padding: 40px; }}
    .card {{ border: 1px solid #00c452; padding: 32px; max-width: 600px; margin: 0 auto; background: #0d1810; }}
    .header {{ color: #00ff6a; font-size: 1.2rem; font-weight: bold; border-bottom: 1px solid #00c452; padding-bottom: 16px; margin-bottom: 24px; }}
    .field {{ margin-bottom: 16px; }}
    .label {{ color: #5a7a5e; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px; }}
    .value {{ color: #c8e6c9; font-size: 0.9rem; }}
    .message-box {{ background: #080f0b; border: 1px solid #1a2e1c; padding: 16px; margin-top: 8px; line-height: 1.7; }}
    .footer {{ color: #2d4a30; font-size: 0.7rem; border-top: 1px solid #0d1810; padding-top: 16px; margin-top: 24px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">⚡ New Portfolio Contact — {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
    <div class="field">
      <div class="label">From</div>
      <div class="value">{name} &lt;{email}&gt;</div>
    </div>
    <div class="field">
      <div class="label">Subject</div>
      <div class="value">{subject}</div>
    </div>
    <div class="field">
      <div class="label">Message</div>
      <div class="message-box">{message.replace(chr(10), '<br>')}</div>
    </div>
    <div class="footer">Sent via Prince Kumar's Portfolio — prince-kumar.dev</div>
  </div>
</body>
</html>
"""


def contact_auto_reply_html(name: str) -> str:
    """HTML auto-reply template sent to the person who contacted."""
    return f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family: 'Courier New', monospace; background: #050a08; color: #c8e6c9; margin: 0; padding: 40px; }}
    .card {{ border: 1px solid #00c452; padding: 32px; max-width: 600px; margin: 0 auto; background: #0d1810; }}
    .header {{ color: #00ff6a; font-size: 1.2rem; font-weight: bold; margin-bottom: 24px; }}
    p {{ line-height: 1.8; color: #c8e6c9; margin-bottom: 12px; }}
    .badge {{ display: inline-block; border: 1px solid #00c452; padding: 4px 12px; color: #00ff6a; font-size: 0.75rem; letter-spacing: 0.1em; margin-bottom: 24px; }}
    .sig {{ color: #5a7a5e; font-size: 0.8rem; border-top: 1px solid #0d1810; padding-top: 16px; margin-top: 24px; }}
    a {{ color: #00ff6a; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">Prince Kumar — DevOps & SRE Engineer</div>
    <div class="badge">🟢 FREELANCER · AVAILABLE NOW</div>
    <p>Hi {name},</p>
    <p>Thanks for reaching out! I've received your message and will get back to you within <strong style="color:#00ff6a">24 hours</strong>.</p>
    <p>While you wait, feel free to explore my work on LinkedIn or check out the server listings on my portfolio.</p>
    <p>Looking forward to connecting!</p>
    <div class="sig">
      <strong style="color:#00ff6a">Prince Kumar</strong><br>
      DevOps Engineer | SRE | Cloud Engineer<br>
      📧 kmprince15932@gmail.com<br>
      📞 +91 8081366401<br>
      🔗 <a href="https://www.linkedin.com/in/kmprincekumar">linkedin.com/in/kmprincekumar</a>
    </div>
  </div>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main portfolio HTML."""
    return send_from_directory(".", "index.html")


# ── CONTACT ──────────────────────────────────────────────

@app.route("/api/contact", methods=["POST"])
def contact():
    """
    POST /api/contact
    Body: { name, email, subject, message }
    - Sends notification email to Prince
    - Sends auto-reply to the sender
    """
    data = request.get_json(silent=True) or {}
    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip()
    subject = data.get("subject", "Portfolio Contact").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"success": False, "error": "name, email, and message are required"}), 400

    if "@" not in email:
        return jsonify({"success": False, "error": "Invalid email address"}), 400

    # 1. Notify Prince
    notify_result = send_email(
        to_addr   = NOTIFY_EMAIL,
        subject   = f"[Portfolio] {subject} — from {name}",
        html_body = contact_notification_html(name, email, subject, message),
        text_body = f"From: {name} <{email}>\nSubject: {subject}\n\n{message}"
    )

    if not notify_result["success"]:
        return jsonify({"success": False, "error": notify_result["error"]}), 500

    # 2. Auto-reply to sender
    send_email(
        to_addr   = email,
        subject   = "Thanks for reaching out — Prince Kumar",
        html_body = contact_auto_reply_html(name),
        text_body = f"Hi {name},\n\nThanks for reaching out! I'll reply within 24 hours.\n\n— Prince Kumar\nDevOps & SRE Engineer"
    )

    return jsonify({"success": True, "message": "Email sent successfully"}), 200


# ── SERVER MARKETPLACE ────────────────────────────────────

@app.route("/api/servers", methods=["GET"])
def get_servers():
    """
    GET /api/servers?type=vps|dedicated
    Returns all server listings, optionally filtered by type.
    """
    servers = load_servers()
    server_type = request.args.get("type", "").lower()
    if server_type in ("vps", "dedicated"):
        servers = [s for s in servers if s.get("type") == server_type]
    return jsonify({"success": True, "servers": servers, "total": len(servers)}), 200


@app.route("/api/servers", methods=["POST"])
def add_server():
    """
    POST /api/servers
    Body: { name, type, cpu, ram, storage, bandwidth, location, price }
    Adds a new server listing.
    """
    data = request.get_json(silent=True) or {}
    required = ["name", "type", "cpu", "ram", "price"]
    for field in required:
        if not data.get(field):
            return jsonify({"success": False, "error": f"'{field}' is required"}), 400

    if data["type"] not in ("vps", "dedicated"):
        return jsonify({"success": False, "error": "type must be 'vps' or 'dedicated'"}), 400

    server = {
        "id":        f"srv-{str(uuid.uuid4())[:8]}",
        "name":      data["name"].strip(),
        "type":      data["type"],
        "cpu":       data.get("cpu", "").strip(),
        "ram":       data.get("ram", "").strip(),
        "storage":   data.get("storage", "").strip(),
        "bandwidth": data.get("bandwidth", "").strip(),
        "location":  data.get("location", "").strip(),
        "price":     float(data["price"]),
        "status":    "available",
        "featured":  bool(data.get("featured", False)),
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }

    servers = load_servers()
    servers.append(server)
    save_servers(servers)

    return jsonify({"success": True, "server": server}), 201


@app.route("/api/servers/<server_id>", methods=["GET"])
def get_server(server_id):
    """GET /api/servers/<id> — Get a single server."""
    servers = load_servers()
    server = next((s for s in servers if s["id"] == server_id), None)
    if not server:
        return jsonify({"success": False, "error": "Server not found"}), 404
    return jsonify({"success": True, "server": server}), 200


@app.route("/api/servers/<server_id>", methods=["PUT"])
def update_server(server_id):
    """
    PUT /api/servers/<id>
    Update server fields (price, status, featured, etc.)
    """
    servers = load_servers()
    idx = next((i for i, s in enumerate(servers) if s["id"] == server_id), None)
    if idx is None:
        return jsonify({"success": False, "error": "Server not found"}), 404

    data = request.get_json(silent=True) or {}
    allowed = ["name", "price", "status", "featured", "bandwidth", "location"]
    for field in allowed:
        if field in data:
            servers[idx][field] = data[field]
    servers[idx]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    save_servers(servers)
    return jsonify({"success": True, "server": servers[idx]}), 200


@app.route("/api/servers/<server_id>", methods=["DELETE"])
def delete_server(server_id):
    """DELETE /api/servers/<id> — Remove a server listing."""
    servers = load_servers()
    original_len = len(servers)
    servers = [s for s in servers if s["id"] != server_id]
    if len(servers) == original_len:
        return jsonify({"success": False, "error": "Server not found"}), 404
    save_servers(servers)
    return jsonify({"success": True, "message": f"Server {server_id} deleted"}), 200


@app.route("/api/servers/<server_id>/inquire", methods=["POST"])
def inquire_server(server_id):
    """
    POST /api/servers/<id>/inquire
    Body: { name, email, message }
    Send a server purchase inquiry email.
    """
    servers = load_servers()
    server = next((s for s in servers if s["id"] == server_id), None)
    if not server:
        return jsonify({"success": False, "error": "Server not found"}), 404

    data = request.get_json(silent=True) or {}
    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email:
        return jsonify({"success": False, "error": "name and email are required"}), 400

    inquiry_subject = f"[Server Inquiry] {server['name']} — ${server['price']}/mo — from {name}"
    inquiry_body = contact_notification_html(
        name, email, inquiry_subject,
        f"Server: {server['name']} ({server['type'].upper()})\n"
        f"Specs: {server['cpu']} | {server['ram']} | {server['storage']}\n"
        f"Price: ${server['price']}/mo\nLocation: {server['location']}\n\n{message}"
    )

    result = send_email(NOTIFY_EMAIL, inquiry_subject, inquiry_body)
    if result["success"]:
        send_email(email, f"Server Inquiry Received — {server['name']}", contact_auto_reply_html(name))

    return jsonify(result), 200 if result["success"] else 500


# ── HEALTH ────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "Prince Kumar Portfolio API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "gmail_configured": GMAIL_PASSWORD != "dcce mklw yjil xbhk"
    }), 200


# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"""
╔══════════════════════════════════════════════════════╗
║   Prince Kumar — Portfolio API                       ║
║   Running on: http://localhost:{port}                    ║
║   Health:     http://localhost:{port}/api/health         ║
╚══════════════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=port, debug=debug)
