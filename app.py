from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    mensaje = request.form.get("Body")
    respuesta = MessagingResponse()
    respuesta.message("✅ LegalBot te saluda, ¡mensaje recibido correctamente!")
    return str(respuesta)

@app.route("/", methods=["GET"])
def home():
    return "LegalBot activo"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
