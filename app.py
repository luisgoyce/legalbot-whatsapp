
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

openai.api_key = os.getenv("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")

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    mensaje = request.form.get("Body")
    respuesta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": mensaje}]
    )
    contenido = respuesta.choices[0].message.content

    twilio_response = MessagingResponse()
    twilio_response.message(contenido)
    return str(twilio_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
