
# Solar Site — Flask (Enhanced) + Alerts

## Requirements
- Python 3.10+
- pip

## Setup
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# or: cp .env.example .env  # macOS/Linux
# then open .env and fill your SMTP and WhatsApp credentials

flask --app manage db_init
flask --app app run --debug
# open http://127.0.0.1:5000
```
