# notify.py
import os
import smtplib
import ssl

SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASS = os.getenv("SMTP_PASS", "").strip()
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "").strip()
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", SMTP_USER or "noreply@example.com")

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "").strip()
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "").strip()
WHATSAPP_TO = os.getenv("WHATSAPP_TO", "").strip()

def _print_preview(prefix: str, lead_dict: dict):
    print(f"[notify:{prefix}] {lead_dict}")

def send_email_alert(lead) -> None:
    """Sends an email alert if SMTP is fully configured; otherwise prints a preview."""
    # Accept both Lead model or dict
    lead_dict = lead if isinstance(lead, dict) else {
        "id": getattr(lead, "id", None),
        "name": getattr(lead, "name", ""),
        "phone": getattr(lead, "phone", ""),
        "email": getattr(lead, "email", "") or "-",
        "city": getattr(lead, "city", "") or "-",
        "message": (getattr(lead, "message", "") or "")[:500],
        "source": getattr(lead, "source", "website"),
    }

    required = [SMTP_HOST, SMTP_USER, SMTP_PASS, ALERT_EMAIL_TO]
    if not all(required):
        _print_preview("email (dry-run)", lead_dict)
        return  # dev-safe: no network call

    subject = f"New Lead #{lead_dict.get('id')}"
    body = "\n".join([
        f"Name: {lead_dict['name']}",
        f"Phone: {lead_dict['phone']}",
        f"Email: {lead_dict['email']}",
        f"City: {lead_dict['city']}",
        f"Message: {lead_dict['message']}",
        f"Source: {lead_dict['source']}",
    ])
    msg = f"From: {ALERT_EMAIL_FROM}\r\nTo: {ALERT_EMAIL_TO}\r\nSubject: {subject}\r\n\r\n{body}"

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(ALERT_EMAIL_FROM, [ALERT_EMAIL_TO], msg.encode("utf-8"))

def send_whatsapp_alert(lead) -> None:
    """Stub: only prints unless WhatsApp Cloud API creds are present."""
    lead_dict = lead if isinstance(lead, dict) else {
        "id": getattr(lead, "id", None),
        "name": getattr(lead, "name", ""),
        "phone": getattr(lead, "phone", ""),
        "email": getattr(lead, "email", "") or "-",
        "city": getattr(lead, "city", "") or "-",
        "message": (getattr(lead, "message", "") or "")[:500],
        "source": getattr(lead, "source", "website"),
    }

    if not (WHATSAPP_TOKEN and WHATSAPP_PHONE_ID and WHATSAPP_TO):
        _print_preview("whatsapp (dry-run)", lead_dict)
        return  # dev-safe

    # If you want real sending later, add the POST request to Graph API here.
    _print_preview("whatsapp (configured)", lead_dict)
