"""
Prince Kumar — DevOps Portfolio Backend v2
==========================================
Features:
  - SQLite database (servers, contacts, profile, admin)
  - Session-based Admin authentication
  - Gmail SMTP contact form + auto-reply + inbox storage
  - Full server marketplace CRUD
  - Dynamic profile / resume API
  - Page view tracking
"""

import os, json, uuid, smtplib, sqlite3
from functools import wraps
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import (Flask, request, jsonify, session, send_from_directory, redirect)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = os.getenv("SECRET_KEY", "prince-sre-secret-2025-change-in-prod")
CORS(app, supports_credentials=True)

# ── CONFIG ────────────────────────────────────────────────────────────────────
GMAIL_USER     = os.getenv("GMAIL_USER",     "kmprince15932@gmail.com")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "your_gmail_app_password_here")
NOTIFY_EMAIL   = os.getenv("NOTIFY_EMAIL",   "kmprince15932@gmail.com")
DB_PATH        = os.getenv("DB_PATH",        "portfolio.db")

# ── DATABASE ──────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS servers (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, type TEXT NOT NULL,
            cpu TEXT, ram TEXT, storage TEXT, bandwidth TEXT, location TEXT,
            price REAL NOT NULL, status TEXT DEFAULT 'available',
            featured INTEGER DEFAULT 0, description TEXT, os_options TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT NOT NULL, subject TEXT, message TEXT NOT NULL,
            type TEXT DEFAULT 'contact', server_id TEXT, server_name TEXT,
            is_read INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS profile (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT, page TEXT, ip TEXT,
            user_agent TEXT, created_at TEXT DEFAULT (datetime('now'))
        );
        """)

        # Default admin
        if not db.execute("SELECT id FROM admin_users WHERE username='admin'").fetchone():
            db.execute("INSERT INTO admin_users (username,password_hash) VALUES (?,?)",
                       ("admin", generate_password_hash("admin123")))

        # Default profile
        defaults = {
            "name": "Prince Kumar", "title": "DevOps Engineer | SRE | Cloud Engineer",
            "tagline": "Building reliable, scalable cloud-native infrastructure",
            "email": "kmprince15932@gmail.com", "phone": "+91 8081366401",
            "location": "Noida, IN", "linkedin": "https://www.linkedin.com/in/kmprincekumar",
            "github": "", "experience": "2+", "availability": "open",
            "rate": "Negotiable",
            "summary": "DevOps & SRE with 2+ years engineering production-grade cloud-native platforms across AWS, Azure & OpenStack. Specialized in Kubernetes orchestration, IaC, CI/CD automation, and reliability engineering. Reduced provisioning time by 60% through Terraform automation.",
            "education": "B.Tech — Computer Science & Engineering\nBaba Banda Singh Engineering College, Punjab\nGPA: 7.4/10 | 2024",
            "resume_url": "",
            "skills": json.dumps({
                "Cloud Platforms": ["AWS","Microsoft Azure","OpenStack"],
                "DevOps & CI/CD": ["Jenkins","GitHub Actions","GitLab CI","ArgoCD","GitOps"],
                "Infrastructure as Code": ["Terraform","CloudFormation","Ansible"],
                "Containers & Orchestration": ["Docker","Kubernetes","Helm","Podman","OpenShift"],
                "Monitoring & Observability": ["Prometheus","Grafana","ELK Stack","Datadog","VictoriaMetrics","Zabbix"],
                "Identity & Security": ["AWS IAM","Azure AD","Okta","Keycloak","HashiCorp Vault","OPA"],
                "Scripting & Automation": ["Bash","Python","PowerShell"],
                "Networking": ["TCP/IP","DNS","VPN","Load Balancers","VPC","NSG"],
                "Databases": ["MySQL","PostgreSQL","MongoDB","Redis"],
                "Compliance": ["SOC2","GDPR","ISO27001","RBAC","MFA","SSO"]
            }),
            "experience_json": json.dumps([
                {"title":"Site Reliability Engineer","company":"Coredge (Client: Apeiro Digital)",
                 "location":"Noida, India / Nairobi, Kenya","period":"Jan 2026 – Present",
                 "bullets":["Ensured reliability & availability on private OpenStack cloud",
                            "Built CI/CD pipelines (Jenkins, GitLab CI, GitHub Actions)",
                            "Automated infrastructure provisioning with Terraform + OpenStack APIs",
                            "Designed Kubernetes clusters with Helm-based deployments",
                            "Implemented Prometheus & Grafana monitoring — reduced MTTR",
                            "Deployed ELK Stack + Fluentd for centralized logging & RCA",
                            "Designed HA architecture with auto-scaling & failover"]},
                {"title":"Cloud Engineer","company":"TOL","location":"Noida, India",
                 "period":"April 2025 – June 2025",
                 "bullets":["Led containerization with Docker & Docker Compose",
                            "Managed AKS Kubernetes clusters for production workloads",
                            "Developed reusable Terraform IaC modules",
                            "Configured Azure AD RBAC & authentication policies",
                            "Designed secure Azure networking (VNets, NSGs, VPN Gateway)",
                            "Managed AWS EC2, S3, RDS, VPC, IAM, Lambda; deployed EKS"]},
                {"title":"Junior DevOps Engineer","company":"ERP Consulting","location":"Pune, India",
                 "period":"Feb 2024 – Feb 2025",
                 "bullets":["Built Docker images & multi-container applications",
                            "Administered EKS & AKS clusters for high availability",
                            "Automated provisioning with Terraform & Ansible — 60% faster",
                            "Integrated SSO: Okta, Auth0, Keycloak; secrets via HashiCorp Vault",
                            "Enforced SOC2, GDPR, ISO27001 compliance",
                            "Architected AWS: EC2, VPC, RDS, Lambda, SQS, SNS"]}
            ]),
            "achievements_json": json.dumps([
                {"metric":"60%","label":"Reduced infrastructure provisioning time via Terraform & Ansible"},
                {"metric":"↓ MTTR","label":"Improved incident response with proactive monitoring & alerting"},
                {"metric":"99.9%","label":"Delivered highly available Kubernetes production platforms"},
                {"metric":"3+","label":"Cloud platforms managed: AWS, Azure, OpenStack in production"},
                {"metric":"CI/CD","label":"Reduced manual deployment effort via automated pipeline engineering"},
                {"metric":"IAM","label":"Strengthened security with IAM, RBAC, SSO & HashiCorp Vault"}
            ]),
            "freelance_services": json.dumps([
                "CI/CD Pipeline Setup & Optimization","Kubernetes Cluster Deployment & Management",
                "Cloud Infrastructure (AWS / Azure / GCP)","Terraform / Ansible IaC Automation",
                "Monitoring & Observability Stack","Security Hardening & Compliance",
                "Linux Server Administration","DevOps Consulting & Code Review"
            ])
        }
        for k, v in defaults.items():
            db.execute("INSERT OR IGNORE INTO profile (key,value) VALUES (?,?)", (k, v))

        # Sample servers
        sample_servers = [
            ("srv-001","cloud-burst-01","vps","4 vCPU","8 GB DDR4","200 GB NVMe","500 Mbps","Mumbai, IN",29,"available",0,"Entry-level VPS for dev/staging workloads","Ubuntu 22.04, CentOS 9, Debian 12"),
            ("srv-002","titan-k8s-node","dedicated","16 Core Intel Xeon","64 GB DDR4","2 TB NVMe SSD","1 Gbps Unmetered","Noida, IN",199,"available",1,"Production dedicated server ideal for Kubernetes","Ubuntu 22.04, RHEL 9, Rocky Linux"),
            ("srv-003","micro-vps-lite","vps","2 vCPU","4 GB","80 GB SSD","250 Mbps","Delhi, IN",12,"available",0,"Budget VPS for small apps & websites","Ubuntu 22.04, Debian 12"),
            ("srv-004","forge-bare-metal","dedicated","32 Core AMD EPYC","128 GB ECC","4 TB NVMe RAID","10 Gbps","Bangalore, IN",499,"available",1,"Hyper-scale bare metal for AI/ML workloads","Ubuntu 22.04, RHEL 9"),
            ("srv-005","dev-sandbox-02","vps","8 vCPU","16 GB DDR4","500 GB SSD","1 Gbps","Hyderabad, IN",59,"available",0,"Mid-range VPS for production web apps","Ubuntu 22.04, CentOS 9"),
        ]
        for s in sample_servers:
            db.execute("""INSERT OR IGNORE INTO servers
                (id,name,type,cpu,ram,storage,bandwidth,location,price,status,featured,description,os_options)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", s)
        db.commit()
    print("✓ DB initialized:", DB_PATH)

# ── AUTH HELPERS ──────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            if request.path.startswith("/api/admin"):
                return jsonify({"success":False,"error":"Unauthorized"}), 401
            return redirect("/admin")
        return f(*args, **kwargs)
    return decorated

# ── EMAIL ─────────────────────────────────────────────────────────────────────
def send_email(to_addr, subject, html_body, text_body=""):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject; msg["From"] = GMAIL_USER; msg["To"] = to_addr
        if text_body: msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as s:
            s.ehlo(); s.starttls(); s.login(GMAIL_USER, GMAIL_PASSWORD)
            s.sendmail(GMAIL_USER, to_addr, msg.as_string())
        return {"success": True}
    except smtplib.SMTPAuthenticationError:
        return {"success": False, "error": "Gmail auth failed — use App Password"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _notify_html(name, email, subject, message):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    return f"""<html><body style="font-family:monospace;background:#050a08;color:#c8e6c9;padding:40px">
<div style="border:1px solid #00c452;padding:32px;max-width:600px;margin:0 auto;background:#0d1810">
<h2 style="color:#00ff6a;border-bottom:1px solid #1a3a1e;padding-bottom:12px">⚡ New Message — {ts}</h2>
<p><b style="color:#5a7a5e">FROM:</b> {name} &lt;{email}&gt;</p>
<p><b style="color:#5a7a5e">SUBJECT:</b> {subject}</p>
<div style="background:#080f0b;border:1px solid #1a2e1c;padding:16px;margin-top:12px;line-height:1.7">{message.replace(chr(10),'<br>')}</div>
<p style="color:#2d4a30;font-size:0.75rem;margin-top:24px">prince-kumar.dev portfolio</p></div></body></html>"""

def _reply_html(name, message):
    return f"""<html><body style="font-family:monospace;background:#050a08;color:#c8e6c9;padding:40px">
<div style="border:1px solid #00c452;padding:32px;max-width:600px;margin:0 auto;background:#0d1810">
<h2 style="color:#00ff6a">Prince Kumar — DevOps & SRE Engineer</h2>
<span style="border:1px solid #00c452;padding:4px 12px;color:#00ff6a;font-size:0.75rem">🟢 FREELANCER · AVAILABLE</span>
<p style="margin-top:20px">Hi {name},</p>
<div style="line-height:1.8;background:#080f0b;padding:16px;border:1px solid #1a2e1c">{message.replace(chr(10),'<br>')}</div>
<p style="margin-top:20px;color:#5a7a5e">— Prince Kumar<br>
<a href="mailto:kmprince15932@gmail.com" style="color:#00ff6a">kmprince15932@gmail.com</a> · +91 8081366401<br>
<a href="https://www.linkedin.com/in/kmprincekumar" style="color:#00ff6a">linkedin.com/in/kmprincekumar</a></p>
</div></body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC ROUTES
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/")
def index():
    with get_db() as db:
        db.execute("INSERT INTO page_views (page,ip,user_agent) VALUES (?,?,?)",
                   ("/", request.remote_addr, request.user_agent.string[:200]))
        db.commit()
    return send_from_directory(".", "index.html")

@app.route("/admin")
@app.route("/admin/")
def admin_page(): return send_from_directory(".", "admin.html")

@app.route("/api/health")
def health():
    with get_db() as db:
        avail = db.execute("SELECT COUNT(*) FROM servers WHERE status='available'").fetchone()[0]
        unread = db.execute("SELECT COUNT(*) FROM contacts WHERE is_read=0").fetchone()[0]
    return jsonify({"status":"ok","available_servers":avail,"unread_messages":unread,"timestamp":datetime.now().isoformat()}), 200

@app.route("/api/profile")
def get_profile():
    with get_db() as db:
        rows = db.execute("SELECT key,value FROM profile").fetchall()
    p = {r["key"]:r["value"] for r in rows}
    for f in ("skills","experience_json","achievements_json","freelance_services"):
        if f in p:
            try: p[f] = json.loads(p[f])
            except: pass
    return jsonify({"success":True,"profile":p}), 200

@app.route("/api/servers")
def get_servers():
    t = request.args.get("type","").lower()
    with get_db() as db:
        q = "SELECT * FROM servers WHERE 1=1"
        params = []
        if t in ("vps","dedicated"): q += " AND type=?"; params.append(t)
        q += " ORDER BY featured DESC, created_at DESC"
        rows = db.execute(q, params).fetchall()
    return jsonify({"success":True,"servers":[dict(r) for r in rows],"total":len(rows)}), 200

@app.route("/api/servers/<sid>")
def get_server(sid):
    with get_db() as db:
        row = db.execute("SELECT * FROM servers WHERE id=?", (sid,)).fetchone()
    if not row: return jsonify({"success":False,"error":"Not found"}), 404
    return jsonify({"success":True,"server":dict(row)}), 200

@app.route("/api/contact", methods=["POST"])
def contact():
    d = request.get_json(silent=True) or {}
    name=d.get("name","").strip(); email=d.get("email","").strip()
    subject=d.get("subject","Contact").strip(); message=d.get("message","").strip()
    ctype=d.get("type","contact"); srv_id=d.get("server_id",""); srv_name=d.get("server_name","")
    if not name or not email or not message:
        return jsonify({"success":False,"error":"name, email and message required"}), 400
    if "@" not in email:
        return jsonify({"success":False,"error":"Invalid email"}), 400
    with get_db() as db:
        db.execute("INSERT INTO contacts (name,email,subject,message,type,server_id,server_name) VALUES (?,?,?,?,?,?,?)",
                   (name,email,subject,message,ctype,srv_id,srv_name))
        db.commit()
    result = send_email(NOTIFY_EMAIL, f"[Portfolio] {subject} — {name}",
                        _notify_html(name,email,subject,message), f"From: {name} <{email}>\n\n{message}")
    if not result["success"]: return jsonify({"success":False,"error":result["error"]}), 500
    send_email(email,"Thanks for reaching out — Prince Kumar",_reply_html(name,"Thanks for reaching out! I'll reply within 24 hours.\n\nLooking forward to connecting!"))
    return jsonify({"success":True}), 200

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN AUTH
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    d=request.get_json(silent=True) or {}
    username=d.get("username","").strip(); password=d.get("password","").strip()
    with get_db() as db:
        user=db.execute("SELECT * FROM admin_users WHERE username=?",(username,)).fetchone()
    if user and check_password_hash(user["password_hash"],password):
        session["admin_logged_in"]=True; session["admin_username"]=username
        return jsonify({"success":True,"username":username}), 200
    return jsonify({"success":False,"error":"Invalid credentials"}), 401

@app.route("/api/admin/logout",methods=["POST"])
def admin_logout(): session.clear(); return jsonify({"success":True}), 200

@app.route("/api/admin/me")
@login_required
def admin_me(): return jsonify({"success":True,"username":session.get("admin_username")}), 200

@app.route("/api/admin/change-password",methods=["POST"])
@login_required
def change_password():
    d=request.get_json(silent=True) or {}
    cur=d.get("current_password",""); new=d.get("new_password","")
    if not new or len(new)<6: return jsonify({"success":False,"error":"Min 6 chars"}), 400
    with get_db() as db:
        user=db.execute("SELECT * FROM admin_users WHERE username=?",(session.get("admin_username"),)).fetchone()
        if not user or not check_password_hash(user["password_hash"],cur):
            return jsonify({"success":False,"error":"Current password wrong"}), 401
        db.execute("UPDATE admin_users SET password_hash=? WHERE username=?",
                   (generate_password_hash(new),session.get("admin_username")))
        db.commit()
    return jsonify({"success":True}), 200

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/admin/stats")
@login_required
def admin_stats():
    with get_db() as db:
        total_srv=db.execute("SELECT COUNT(*) FROM servers").fetchone()[0]
        avail_srv=db.execute("SELECT COUNT(*) FROM servers WHERE status='available'").fetchone()[0]
        sold_srv=db.execute("SELECT COUNT(*) FROM servers WHERE status='sold'").fetchone()[0]
        total_msg=db.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
        unread_msg=db.execute("SELECT COUNT(*) FROM contacts WHERE is_read=0").fetchone()[0]
        total_views=db.execute("SELECT COUNT(*) FROM page_views").fetchone()[0]
        today_views=db.execute("SELECT COUNT(*) FROM page_views WHERE date(created_at)=date('now')").fetchone()[0]
        recent=db.execute("SELECT * FROM contacts ORDER BY created_at DESC LIMIT 5").fetchall()
        revenue=db.execute("SELECT SUM(price) FROM servers WHERE status='sold'").fetchone()[0] or 0
    return jsonify({"success":True,"stats":{
        "servers":{"total":total_srv,"available":avail_srv,"sold":sold_srv},
        "contacts":{"total":total_msg,"unread":unread_msg},
        "views":{"total":total_views,"today":today_views},
        "revenue":revenue
    },"recent_contacts":[dict(r) for r in recent]}), 200

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN SERVER CRUD
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/admin/servers")
@login_required
def admin_get_servers():
    with get_db() as db:
        rows=db.execute("SELECT * FROM servers ORDER BY created_at DESC").fetchall()
    return jsonify({"success":True,"servers":[dict(r) for r in rows]}), 200

@app.route("/api/admin/servers",methods=["POST"])
@login_required
def admin_add_server():
    d=request.get_json(silent=True) or {}
    for f in ["name","type","price"]:
        if not d.get(f): return jsonify({"success":False,"error":f"'{f}' required"}), 400
    if d["type"] not in ("vps","dedicated"):
        return jsonify({"success":False,"error":"type: vps or dedicated"}), 400
    srv={"id":f"srv-{str(uuid.uuid4())[:8]}","name":d["name"].strip(),"type":d["type"],
         "cpu":d.get("cpu",""),"ram":d.get("ram",""),"storage":d.get("storage",""),
         "bandwidth":d.get("bandwidth",""),"location":d.get("location",""),
         "price":float(d["price"]),"status":d.get("status","available"),
         "featured":1 if d.get("featured") else 0,
         "description":d.get("description",""),"os_options":d.get("os_options","")}
    with get_db() as db:
        db.execute("INSERT INTO servers (id,name,type,cpu,ram,storage,bandwidth,location,price,status,featured,description,os_options) VALUES (:id,:name,:type,:cpu,:ram,:storage,:bandwidth,:location,:price,:status,:featured,:description,:os_options)",srv)
        db.commit()
    return jsonify({"success":True,"server":srv}), 201

@app.route("/api/admin/servers/<sid>",methods=["PUT"])
@login_required
def admin_update_server(sid):
    d=request.get_json(silent=True) or {}
    fields=["name","type","cpu","ram","storage","bandwidth","location","price","status","featured","description","os_options"]
    updates,params=[],[]
    for f in fields:
        if f in d:
            updates.append(f"{f}=?")
            params.append(float(d[f]) if f=="price" else (1 if f=="featured" and d[f] else d[f]))
    if not updates: return jsonify({"success":False,"error":"Nothing to update"}), 400
    params.append(sid)
    with get_db() as db:
        db.execute(f"UPDATE servers SET {', '.join(updates)} WHERE id=?",params)
        db.commit()
        row=db.execute("SELECT * FROM servers WHERE id=?",(sid,)).fetchone()
    if not row: return jsonify({"success":False,"error":"Not found"}), 404
    return jsonify({"success":True,"server":dict(row)}), 200

@app.route("/api/admin/servers/<sid>",methods=["DELETE"])
@login_required
def admin_delete_server(sid):
    with get_db() as db:
        r=db.execute("DELETE FROM servers WHERE id=?",(sid,))
        db.commit()
    return jsonify({"success":True} if r.rowcount else {"success":False,"error":"Not found"}), 200 if r.rowcount else 404

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN CONTACTS
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/admin/contacts")
@login_required
def admin_get_contacts():
    with get_db() as db:
        rows=db.execute("SELECT * FROM contacts ORDER BY created_at DESC").fetchall()
    return jsonify({"success":True,"contacts":[dict(r) for r in rows]}), 200

@app.route("/api/admin/contacts/<int:cid>/read",methods=["PUT"])
@login_required
def mark_read(cid):
    with get_db() as db:
        db.execute("UPDATE contacts SET is_read=1 WHERE id=?",(cid,)); db.commit()
    return jsonify({"success":True}), 200

@app.route("/api/admin/contacts/<int:cid>",methods=["DELETE"])
@login_required
def delete_contact(cid):
    with get_db() as db:
        db.execute("DELETE FROM contacts WHERE id=?",(cid,)); db.commit()
    return jsonify({"success":True}), 200

@app.route("/api/admin/contacts/<int:cid>/reply",methods=["POST"])
@login_required
def reply_contact(cid):
    with get_db() as db:
        row=db.execute("SELECT * FROM contacts WHERE id=?",(cid,)).fetchone()
    if not row: return jsonify({"success":False,"error":"Not found"}), 404
    d=request.get_json(silent=True) or {}
    msg=d.get("message","").strip()
    if not msg: return jsonify({"success":False,"error":"message required"}), 400
    result=send_email(row["email"],f"Re: {row['subject'] or 'Your inquiry'}",_reply_html(row["name"],msg),msg)
    if result["success"]:
        with get_db() as db:
            db.execute("UPDATE contacts SET is_read=1 WHERE id=?",(cid,)); db.commit()
    return jsonify(result), 200 if result["success"] else 500

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN PROFILE
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/admin/profile")
@login_required
def admin_get_profile():
    with get_db() as db:
        rows=db.execute("SELECT key,value FROM profile").fetchall()
    return jsonify({"success":True,"profile":{r["key"]:r["value"] for r in rows}}), 200

@app.route("/api/admin/profile",methods=["PUT"])
@login_required
def admin_update_profile():
    data=request.get_json(silent=True) or {}
    with get_db() as db:
        for k,v in data.items():
            val=json.dumps(v) if isinstance(v,(dict,list)) else str(v)
            db.execute("INSERT OR REPLACE INTO profile (key,value) VALUES (?,?)",(k,val))
        db.commit()
    return jsonify({"success":True}), 200

@app.route("/api/admin/gmail-test",methods=["POST"])
@login_required
def test_gmail():
    r=send_email(NOTIFY_EMAIL,"✓ Gmail Test — Prince Kumar Portfolio","<h2 style='color:green'>Gmail SMTP is working!</h2>","Gmail test OK")
    return jsonify(r), 200 if r["success"] else 500

if __name__=="__main__":
    init_db()
    port=int(os.getenv("PORT",5000))
    print(f"\n  Portfolio : http://localhost:{port}\n  Admin     : http://localhost:{port}/admin\n  Login     : admin / admin123\n")
    app.run(host="0.0.0.0",port=port,debug=os.getenv("DEBUG","false").lower()=="true")
