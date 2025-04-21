import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

def enviar_alerta(msg):
    print("📤 Enviando alerta para o Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    resposta = requests.post(url, data=data)
    print(f"✅ Status Telegram: {resposta.status_code} | Resposta: {resposta.text}")

def monitorar_twilio():
    print("🚀 Iniciando monitoramento do Twilio...")
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        balance = client.api.balance.fetch()  # <- Aqui está o fix real
        saldo = float(balance.balance)
        moeda = balance.currency

        print(f"💰 Saldo Twilio retornado pela API: {moeda} ${saldo:.2f}")

        resumo = f"💰 *Resumo Twilio*\n- Saldo atual: *{moeda} ${saldo:.2f}*"
        enviar_alerta(resumo)

        if saldo <= 2:
            enviar_alerta(f"⚠️ *Saldo Twilio abaixo de $2: {moeda} ${saldo:.2f}*")
        else:
            print("✅ Saldo acima de $2 — nenhum alerta crítico enviado.")

    except Exception as e:
        print(f"❌ Erro ao monitorar Twilio: {e}")
