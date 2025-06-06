from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    mensaje = request.form.get("Body")
    print(f"📩 Recibido: {mensaje}")

    # Mensaje fijo para prueba
    respuesta = MessagingResponse()
    respuesta.message("✅ ¡Hola! LegalBot recibió tu mensaje correctamente.")
    return str(respuesta)

@app.route("/", methods=["GET"])
def home():
    return "LegalBot está activo y esperando mensajes."
