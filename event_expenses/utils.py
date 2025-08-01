from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from event_expenses.models import Event
from flask_mail import Message
from event_expenses import mail
import string
import random
import hashlib


def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='event-validation')

def participant_color(value):
    """
    Retorna un color hexadecimal generat a partir del valor,
    però limitant la lluminositat per evitar colors massa clars.
    """
    h = hashlib.md5(value.encode()).hexdigest()

    # Agafem 3 bytes del hash i els limitem
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)

    # Limitem els valors per evitar colors clars (max 200) i foscos (min 50)
    def clamp(val):
        return max(50, min(val, 200))

    r, g, b = clamp(r), clamp(g), clamp(b)

    return f"#{r:02x}{g:02x}{b:02x}"


def generate_event_token(length=16):
    while True:
        token = generate_simple_token(length)
        if not Event.query.filter_by(token=token).first():
            return token
        
def generate_simple_token(length=16):
    chars = string.ascii_letters + string.digits  # A-Z a-z 0-9
    return ''.join(random.choices(chars, k=length))

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='event-validation', max_age=expiration)
    except Exception:
        return False
    return email

def send_styled_email(subject, recipients, body_html, body_text=None):
    """
    Envia un correu amb un estil uniforme.
    - subject: Assumpte
    - recipients: Llista de destinataris
    - body_html: Contingut HTML principal
    - body_text: Opcional, versió text pla
    """
    # Plantilla d'estil
    html_template = f"""
    <html>
  <head>
    <meta charset="UTF-8">
    <style>
      body {{
        font-family: 'Segoe UI', Arial, sans-serif;
        background-color: #f5f7fa;
        margin: 0;
        padding: 20px;
      }}
      .email-container {{
        max-width: 600px;
        margin: 0 auto;
        background-color: #ffffff;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      }}
      .header {{
        background-color: #131720;
        text-align: center;
        padding: 25px;
      }}
      .header img {{
        max-height: 45px;
      }}
      .content {{
        padding: 30px 25px;
        color: #333333;
        line-height: 1.6;
        text-align: center;
      }}
      .content h2 {{
        margin-top: 0;
        color: #131720;
      }}
      .button {{
        display: inline-block;
        background-color: #007bff;
        color: white !important;
        padding: 12px 28px;
        margin-top: 20px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 600;
        transition: background-color 0.2s;
      }}
      .button:hover {{
        background-color: #0056b3;
      }}
      .footer {{
        background-color: #f2f2f2;
        text-align: center;
        font-size: 12px;
        color: #888888;
        padding: 15px;
      }}
      .footer a {{
        color: #888888;
        text-decoration: none;
      }}
    </style>
  </head>
  <body>
    <div class="email-container">
      <div class="header">
        <img src="http://splitly.netpy.eu/static/logo_small.png" alt="Splitly">
      </div>
      <div class="content">
      {body_html}
      </div>
      <div class="footer">
        Splitly &copy; 2025 · Gestiona les teves despeses compartides fàcilment
      </div>
    </div>
  </body>
</html>
    """

    # Si no tenim versió text, en fem una bàsica
    if not body_text:
        import re
        body_text = re.sub('<[^<]+?>', '', body_html)

    msg = Message(subject, recipients=recipients, body=body_text, html=html_template)
    mail.send(msg)
