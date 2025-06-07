from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from openai import OpenAI          # ✅ SDK ≥ 1.0

# --- Init ---
app = Flask(__name__)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")  # Render → Environment → Add Secret
)

LUCIA_PROMPT = (
    "Eres lucIA, abogada experta en derecho colombiano. "
    "Responde en lenguaje claro, máximo 160 palabras y cita la ley/artículo si aplica."
)

# --- Webhooks ---
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    user_msg = request.form.get("Body", "").strip()

    # 1) Llamada a OpenAI
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": LUCIA_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            max_tokens=350,  # ≈160 palabras
        )
        answer = completion.choices[0].message.content.strip()
    except Exception as e:
        # Fallback para que Twilio no se quede esperando
        answer = (
            "⚠️ Lo siento, lucIA tuvo un problema técnico. "
            "Intenta de nuevo en unos minutos."
        )
        app.logger.error(f"OpenAI error: {e}")

    # 2) Respuesta a WhatsApp
    twiml = MessagingResponse()
    twiml.message(answer)
    return str(twiml)

@app.route("/", methods=["GET"])
def home():
    return "LegalBot activo"

# --- Local run / Render ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
