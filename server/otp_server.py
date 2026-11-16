"""
SPR School of Excellence — Official Election Administration Portal
Local Python OTP & Authentication Server

Handles:
- Verifying admin email against authorized admin allowlist
- Verifying password format: Spr-Elections@<name>
- Generating 6-digit secure OTP with 5-minute expiry
- Dispatching branded HTML verification email via Gmail SMTP
- Verifying OTP and issuing session auth tokens
"""

import sys
import os
import json
import time
import random
import secrets
import smtplib
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "server" / "config.json"

def load_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error loading config.json: {e}")
    return {
        "smtp": {
            "host": "smtp.gmail.com",
            "port": 587,
            "user": "sprelections@gmail.com",
            "pass": "tmhspxlaahlxklhm",
            "sender_name": "SPR School Elections"
        },
        "authorized_admins": [
            {"name": "Admin", "email": "sprelections@gmail.com"}
        ],
        "allow_all_verified_emails": False,
        "otp_expiry_seconds": 300
    }

# In-memory stores
# active_otps: { email: { "otp": "123456", "name": "Abhinav", "expires": timestamp, "last_sent": timestamp } }
ACTIVE_OTPS = {}
# active_sessions: { token: { "email": "...", "name": "...", "created": timestamp } }
ACTIVE_SESSIONS = {}

def get_authorized_admin(email: str, config: dict) -> dict | None:
    """Finds the admin record for an authorized email."""
    clean_email = str(email or "").strip().lower()
    if not clean_email or "@" not in clean_email:
        return None
    for admin in config.get("authorized_admins", []):
        if admin.get("email", "").strip().lower() == clean_email:
            return admin
    if config.get("allow_all_verified_emails"):
        return {"name": clean_email.split("@")[0].capitalize(), "email": clean_email}
    return None

def verify_admin_password(entered_password: str, admin_record: dict) -> tuple[bool, str]:
    """
    Verifies admin password against config.
    Accepts:
    1. If admin_record defines 'password', matches configured password (case-insensitive)
       or matches with/without 'Spr-Elections@' (e.g. 'rc4616105' and 'Spr-Elections@rc4616105').
    2. Format 'Spr-Elections@<name>' if no specific password is set.
    Returns (is_valid, display_name).
    """
    p = str(entered_password or "").strip()
    if not p:
        return False, ""
    
    admin_name = admin_record.get("name", "Admin")
    cfg_pwd = str(admin_record.get("password", "")).strip()

    if cfg_pwd:
        clean_p = p.lower()
        clean_cfg = cfg_pwd.lower()
        if clean_p == clean_cfg:
            return True, admin_name
        if clean_p == clean_cfg.replace("spr-elections@", ""):
            return True, admin_name
        if f"spr-elections@{clean_p}" == clean_cfg:
            return True, admin_name
        return False, ""

    prefix = "spr-elections@"
    if p.lower().startswith(prefix):
        name_part = p[len(prefix):].strip()
        if len(name_part) >= 2:
            return True, name_part

    return False, ""

def send_otp_email(to_email: str, admin_name: str, otp: str, config: dict) -> tuple[bool, str]:
    smtp_cfg = config.get("smtp", {})
    host = smtp_cfg.get("host", "smtp.gmail.com")
    port = int(smtp_cfg.get("port", 587))
    user = smtp_cfg.get("user")
    pwd = smtp_cfg.get("pass")
    sender_name = smtp_cfg.get("sender_name", "SPR School Elections")

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{sender_name} <{user}>"
    msg["To"] = to_email
    msg["Subject"] = f"🔐 Your Admin Access Code: {otp} — SPR School Elections 2026"

    plain_text = f"""SPR School of Excellence — Official Election Administration

Hello {admin_name},

Your one-time verification code to access the Admin Panel is:

    {otp}

This code is confidential and will expire in 5 minutes.
If you did not request this code, please ignore this email.
"""

    html_text = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #faf6ee; margin: 0; padding: 24px; color: #141413; }}
    .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e5dccb; box-shadow: 0 12px 30px rgba(0,0,0,0.06); overflow: hidden; }}
    .header {{ background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; padding: 28px 24px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 20px; letter-spacing: 0.5px; font-weight: 700; }}
    .header p {{ margin: 6px 0 0; font-size: 13px; opacity: 0.9; }}
    .body {{ padding: 32px 28px; text-align: center; }}
    .greeting {{ font-size: 15px; color: #4a4741; margin-bottom: 20px; }}
    .otp-box {{ background: #f3fbf6; border: 2px dashed #059669; border-radius: 12px; padding: 18px 24px; display: inline-block; margin: 10px auto 20px; }}
    .otp-code {{ font-family: 'JetBrains Mono', Consolas, monospace; font-size: 36px; font-weight: 800; color: #047857; letter-spacing: 8px; }}
    .note {{ font-size: 13px; color: #767167; line-height: 1.6; margin-top: 14px; }}
    .expiry {{ display: inline-block; background: #fef3c7; color: #92400e; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px; margin-top: 8px; }}
    .footer {{ background: #faf6ee; border-top: 1px solid #e5dccb; padding: 16px 24px; text-align: center; font-size: 11px; color: #767167; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h1>SPR SCHOOL OF EXCELLENCE</h1>
      <p>Official School House Elections 2026 • Admin Portal Access</p>
    </div>
    <div class="body">
      <div class="greeting">Hello <strong>{admin_name}</strong>,</div>
      <p style="font-size:14px; color:#4a4741; margin:0 0 16px;">Use the following 6-digit verification code to unlock the election administration dashboard:</p>
      
      <div class="otp-box">
        <div class="otp-code">{otp}</div>
      </div>
      <div>
        <span class="expiry">⏱️ Valid for 5 minutes</span>
      </div>

      <div class="note">
        This code is strictly confidential. Never share this code with anyone.<br/>
        If you did not request this verification, please contact election security.
      </div>
    </div>
    <div class="footer">
      SPR School of Excellence • Secured Election Administration System
    </div>
  </div>
</body>
</html>"""

    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_text, "html"))

    try:
        server = smtplib.SMTP(host, port, timeout=12)
        server.starttls()
        server.login(user, pwd)
        server.sendmail(user, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully"
    except Exception as e:
        print(f"SMTP send error: {e}")
        return False, str(e)


class OTPRequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def _json_response(self, data, status_code=200):
        self.send_response(status_code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        if self.path == "/api/health" or self.path == "/":
            self._json_response({
                "status": "online",
                "service": "SPR Elections Local OTP & Admin Auth Server",
                "active_otps_count": len(ACTIVE_OTPS)
            })
            return
        self._json_response({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        config = load_config()

        # 0. DIRECT LOGIN ENDPOINT (Email + Password, No OTP)
        if self.path == "/api/admin/login":
            email = str(body.get("email", "")).strip().lower()
            password = str(body.get("password", "")).strip()

            if not email or "@" not in email:
                self._json_response({"ok": False, "code": "INVALID_EMAIL", "message": "Please enter your administrator email."}, 400)
                return

            admin_record = get_authorized_admin(email, config)
            if not admin_record:
                self._json_response({
                    "ok": False,
                    "code": "UNAUTHORIZED_EMAIL",
                    "message": "Access Denied: This email is not in the authorized administrator list."
                }, 403)
                return

            is_valid_pw, display_name = verify_admin_password(password, admin_record)
            if not is_valid_pw:
                self._json_response({
                    "ok": False,
                    "code": "INVALID_PASSWORD",
                    "message": "Incorrect administrative password. Access denied."
                }, 401)
                return

            # Login Successful!
            final_name = display_name or admin_record.get("name", "Admin")
            token = secrets.token_hex(24)
            now = time.time()
            ACTIVE_SESSIONS[token] = {
                "email": email,
                "name": final_name,
                "created": now,
                "expires": now + int(config.get("session_expiry_seconds", 86400))
            }

            print(f"[AUTH SERVER] Direct login SUCCESS for {email} ({final_name})! Token issued.")

            self._json_response({
                "ok": True,
                "token": token,
                "admin": {
                    "name": final_name,
                    "email": email
                },
                "message": "Authentication successful. Access granted."
            })
            return

        # 1. SEND OTP ENDPOINT
        if self.path == "/api/admin/send-otp":
            email = str(body.get("email", "")).strip().lower()
            password = str(body.get("password", "")).strip()

            if not email or "@" not in email:
                self._json_response({"ok": False, "code": "INVALID_EMAIL", "message": "Please enter a valid email address."}, 400)
                return

            # Check email authorization
            admin_record = get_authorized_admin(email, config)
            if not admin_record:
                self._json_response({
                    "ok": False,
                    "code": "UNAUTHORIZED_EMAIL",
                    "message": "Access Denied: This email address is not in the authorized election administrators list."
                }, 403)
                return

            # Validate password against config / format
            is_valid_pw, display_name = verify_admin_password(password, admin_record)
            if not is_valid_pw:
                self._json_response({
                    "ok": False,
                    "code": "INVALID_PASSWORD",
                    "message": "Incorrect administrative password. Access denied."
                }, 401)
                return

            # Rate limit check (30 seconds between requests for same email)
            now = time.time()
            existing = ACTIVE_OTPS.get(email)
            if existing and (now - existing.get("last_sent", 0)) < 30:
                wait_sec = int(30 - (now - existing["last_sent"]))
                self._json_response({
                    "ok": False,
                    "code": "RATE_LIMITED",
                    "message": f"Please wait {wait_sec} seconds before requesting a new code."
                }, 429)
                return

            # Generate 6-digit OTP
            otp = f"{random.randint(100000, 999999):06d}"
            expiry_sec = config.get("otp_expiry_seconds", 300)
            final_name = display_name or admin_record.get("name", "Admin")
            ACTIVE_OTPS[email] = {
                "otp": otp,
                "name": final_name,
                "expires": now + expiry_sec,
                "last_sent": now
            }

            print(f"[OTP SERVER] Generated OTP {otp} for {email} ({final_name})")

            # Dispatch email via SMTP
            sent_ok, err_msg = send_otp_email(email, final_name, otp, config)
            if not sent_ok:
                self._json_response({
                    "ok": False,
                    "code": "EMAIL_SEND_FAILED",
                    "message": f"Failed to send email: {err_msg}"
                }, 500)
                return

            self._json_response({
                "ok": True,
                "email": email,
                "expires_in": expiry_sec,
                "message": f"Verification code sent to {email}. Please check your inbox."
            })
            return

        # 2. VERIFY OTP ENDPOINT
        elif self.path == "/api/admin/verify-otp":
            email = str(body.get("email", "")).strip().lower()
            entered_otp = str(body.get("otp", "")).strip().replace(" ", "").replace("-", "")

            if not email or not entered_otp:
                self._json_response({"ok": False, "code": "MISSING_FIELDS", "message": "Email and 6-digit verification code are required."}, 400)
                return

            record = ACTIVE_OTPS.get(email)
            now = time.time()

            if not record:
                self._json_response({
                    "ok": False,
                    "code": "NO_ACTIVE_OTP",
                    "message": "No active verification code found for this email. Please request a new code."
                }, 400)
                return

            if now > record.get("expires", 0):
                ACTIVE_OTPS.pop(email, None)
                self._json_response({
                    "ok": False,
                    "code": "OTP_EXPIRED",
                    "message": "Verification code has expired. Please request a new code."
                }, 400)
                return

            if entered_otp != record.get("otp"):
                self._json_response({
                    "ok": False,
                    "code": "INVALID_OTP",
                    "message": "Incorrect verification code. Please check your email and try again."
                }, 401)
                return

            # Verification Successful!
            admin_name = record.get("name", "Admin")
            token = secrets.token_hex(24)
            ACTIVE_SESSIONS[token] = {
                "email": email,
                "name": admin_name,
                "created": now,
                "expires": now + 86400 # 24 hours
            }

            # Clear used OTP
            ACTIVE_OTPS.pop(email, None)
            print(f"[OTP SERVER] Verification SUCCESS for {email} ({admin_name})! Token issued.")

            self._json_response({
                "ok": True,
                "token": token,
                "admin": {
                    "name": admin_name,
                    "email": email
                },
                "message": "Authentication successful. Access granted."
            })
            return

        # 3. CHECK SESSION ENDPOINT
        elif self.path == "/api/admin/check-session":
            token = str(body.get("token", "")).strip()
            session = ACTIVE_SESSIONS.get(token)
            if not session or time.time() > session.get("expires", 0):
                self._json_response({"ok": False, "valid": False}, 401)
                return

            self._json_response({
                "ok": True,
                "valid": True,
                "admin": {
                    "name": session.get("name"),
                    "email": session.get("email")
                }
            })
            return

        self._json_response({"error": "Unknown endpoint"}, 404)


def run_server(port=5001):
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, OTPRequestHandler)
    print(f"=== SPR School Elections OTP Server listening on http://0.0.0.0:{port} ===")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down OTP server...")
        httpd.server_close()


if __name__ == "__main__":
    p = 5001
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        p = int(sys.argv[1])
    run_server(p)
