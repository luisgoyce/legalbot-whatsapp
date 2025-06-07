import os, tempfile, requests, logging, re
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI          # SDK ≥1.0

# ---------- Config ----------
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
PORT = int(os.environ.get("PORT", 5000))

WELCOME = (
    "👋 ¡Hola! Soy *lucIA*, tu asistente legal en Colombia.\n\n"
    "Puedo orientarte en temas como:\n"
    "• Despido sin justa causa\n"
    "• Pensión alimentaria o de sobrevivientes\n"
    "• Divorcio, custodia y bienes\n"
    "• Arrendamientos y contratos\n"
    "• Herencias y sucesiones\n"
    "• Acción de tutela o derecho de petición\n"
    "• Cobro de deudas / insolvencia\n"
    "• Accidentes laborales y ARL\n\n"
    "✏️ Escríbeme tu caso con el mayor detalle posible (o envía una nota de voz)."
)

LUCIA_PROMPT = (
    "Eres lucIA, abogada experta en derecho colombiano. "
    "Responde en lenguaje claro, máximo 160 palabras. "
    "Si aplica, cita solo una norma así: 👩🏽‍⚖️ [Art. 64 CST] "
    "y no inventes artículos inexistentes."
)
REJECTION = (
    "👋 Hola. lucIA solo atiende dudas legales o financieras "
    "relacionadas con Colombia. Intenta reformular tu pregunta 🙂"
)

# ---------- Helpers ----------
def download_media(url: str) -> str:
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
    tmp.write(resp.content)
    tmp.close()
    return tmp.name

def transcribe(path: str) -> str:
    with open(path, "rb") as f:
        tr = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text",
        )
    return tr.strip()

def is_legal_or_financial(q: str) -> bool:
    out = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "Responde 'yes' si la pregunta es un problema legal "
                        "o financiero en Colombia; de lo contrario 'no'."},
            {"role": "user", "content": q[:500]},
        ],
        temperature=0,
        max_tokens=1,
    )
    return out.choices[0].message.content.strip().lower().startswith("y")

def ask_lucia(question: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": LUCIA_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0.3,
        max_tokens=350,
    )
    return completion.choices[0].message.content.strip()

# Saludos que disparan el mensaje de bienvenida
GREETING_PATTERN = re.compile(r"^(hola|buenas|hi|hey|👋|que tal|buen día)\b", re.I)

# ---------- Flask ----------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    form = request.form
    user_msg = form.get("Body", "").strip()

    # ¿Audio?
    media_type = form.get("MediaContentType0")
    media_url  = form.get("MediaUrl0")
    if media_type and media_type.startswith("audio"):
        try:
            local = download_media(media_url)
            user_msg = transcribe(local)
            logging.info(f"Transcripción: {user_msg}")
        except Exception as e:
            logging.error(f"Whisper error: {e}")
            user_msg = ""

    # 1) Sin texto válido
    if not user_msg:
        answer = ("⚠️ No pude leer tu mensaje. "
                  "Inténtalo de nuevo o escribe tu consulta.")
    # 2) Saludo → menú de bienvenida
    elif GREETING_PATTERN.match(user_msg):
        answer = WELCOME
    # 3) Filtro de dominio legal / financiero
    elif not is_legal_or_financial(user_msg):
        answer = REJECTION
    # 4) Consulta válida → GPT-4o
    else:
        try:
            answer = ask_lucia(user_msg)
        except Exception as e:
            logging.error(f"OpenAI error: {e}")
            answer = ("⚠️ lucIA tuvo un problema técnico. "
                      "Intenta de nuevo en unos minutos.")

    twiml = MessagingResponse()
    twiml.message(answer)
    return str(twiml)

@app.route("/", methods=["GET"])
def home():
    return "lucIA WhatsApp API activa"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
