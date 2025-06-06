
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
import os

# Inicializar cliente OpenAI con API Key desde variables de entorno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    mensaje = request.form.get("Body")
    print(f"📩 Mensaje recibido: {mensaje}")

    # Llamada a OpenAI con el nuevo formato
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Responde como asistente legal colombiano. Usa lenguaje claro, sin jerga."},
            {"role": "user", "content": mensaje}
        ]
    )
    contenido = response.choices[0].message.content

    twilio_response = MessagingResponse()
    twilio_response.message(contenido)
    return str(twilio_response)

@app.route("/", methods=["GET"])
def home():
    return "✅ LegalBot está activo y esperando mensajes de WhatsApp."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
