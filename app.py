from flask import Flask, render_template, request, jsonify, Response, url_for
from flask_cors import CORS
from dotenv import load_dotenv
import os, re

# IMPORTANT: db now comes from models to avoid circular imports
from models import db, Lead
from notify import send_email_alert, send_whatsapp_alert

load_dotenv()  # load .env if present

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL")
            or f"sqlite:///{os.path.join(app.instance_path, 'app.sqlite')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    os.makedirs(app.instance_path, exist_ok=True)

    # Init extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # -------- PAGES --------
    @app.get("/")
    def home():
        return render_template("home.html")

    @app.get("/about")
    def about():
        return render_template("about.html")

    @app.get("/services")
    def services():
        return render_template("services.html")

    @app.get("/projects")
    def projects():
        return render_template("projects.html")

    @app.get("/contact")
    def contact():
        return render_template("contact.html")

    @app.get("/privacy")
    def privacy():
        return render_template("privacy.html")

    @app.get("/terms")
    def terms():
        return render_template("terms.html")

    @app.get("/calculator")
    def calculator():
        return render_template("calculator.html")

    # -------- SEO / OPS --------
    @app.get("/robots.txt")
    def robots():
        lines = [
            "User-agent: *",
            "Disallow:",
            f"Sitemap: {url_for('sitemap', _external=True)}",
        ]
        return Response("\n".join(lines), mimetype="text/plain")

    @app.get("/sitemap.xml")
    def sitemap():
        pages = [
            ("home", {}),
            ("about", {}),
            ("services", {}),
            ("projects", {}),
            ("contact", {}),
            ("privacy", {}),
            ("terms", {}),
        ]
        urls = [url_for(endpoint, _external=True, **params) for endpoint, params in pages]
        xml = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        xml += [f"<url><loc>{u}</loc></url>" for u in urls]
        xml.append("</urlset>")
        return Response("\n".join(xml), mimetype="application/xml")

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    # -------- APIs --------
    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    PHONE_RE = re.compile(r"^[0-9+().\-\s]{8,20}$")

    @app.post("/api/leads")
    def api_leads():
        data = request.get_json(silent=True) or request.form.to_dict() or {}

        # honeypot (add a hidden <input name="website"> in your form)
        honeypot = (data.get("website") or "").strip()
        if honeypot:
            return jsonify({"ok": False, "error": "Spam detected"}), 400

        name = (data.get("name") or "").strip()
        phone = (data.get("phone") or "").strip()
        email = (data.get("email") or "").strip()
        city = (data.get("city") or "").strip() or None
        message = (data.get("message") or "").strip() or None
        source = (data.get("source") or "website")[:32]
        consent = bool(data.get("consent"))

        # basic validations (email optional but validated if present)
        if len(name) < 2:
            return jsonify({"ok": False, "error": "Invalid name"}), 400
        if not PHONE_RE.match(phone):
            return jsonify({"ok": False, "error": "Invalid phone"}), 400
        if email and not EMAIL_RE.match(email):
            return jsonify({"ok": False, "error": "Invalid email"}), 400
        if not consent:
            return jsonify({"ok": False, "error": "Consent is required"}), 400

        lead = Lead(
            name=name,
            phone=phone,
            email=email or None,
            city=city,
            message=message,
            source=source,
            # If you later add these columns, uncomment:
            # ip=request.headers.get("X-Forwarded-For", request.remote_addr),
            # user_agent=(request.headers.get("User-Agent") or "")[:510],
            # consent=True,
        )
        db.session.add(lead)
        db.session.commit()

        # Alerts (best-effort; failures won't break the API)
        try:
            send_email_alert(lead)
        except Exception as e:
            app.logger.warning(f"Email alert failed: {e}")
        try:
            send_whatsapp_alert(lead)
        except Exception as e:
            app.logger.warning(f"WhatsApp alert failed: {e}")

        return jsonify({"ok": True, "leadId": lead.id})

    @app.post("/api/calc")
    def api_calc():
        d = request.get_json(silent=True) or {}
        try:
            bill = float(d.get("bill", 0))
            tariff = float(d.get("tariff", 8))
            sun_hours = float(d.get("sun_hours", 4.5))
            price_per_kw = float(d.get("price_per_kw", 70000))
            subsidy = float(d.get("subsidy", 0))  # fraction 0..1

            monthly_units = bill / max(tariff, 0.1)
            needed_kw = monthly_units / (30 * max(sun_hours, 0.1))
            kw = max(1, round(needed_kw, 1))
            cost_gross = kw * price_per_kw
            cost_net = cost_gross * (1 - subsidy)
            yearly_savings = monthly_units * tariff * 12 * 0.85
            payback_years = round(cost_net / max(yearly_savings, 1), 2)
            return jsonify({
                "ok": True,
                "kw": kw,
                "cost_gross": round(cost_gross),
                "cost_net": round(cost_net),
                "yearly_savings": round(yearly_savings),
                "payback_years": payback_years
            })
        except Exception:
            return jsonify({"ok": False, "error": "Bad input"}), 400

    return app

# local dev entrypoint (Gunicorn will use the factory)
if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
