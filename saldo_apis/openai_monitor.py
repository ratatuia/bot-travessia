import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LIMITE_ALERTA = 2.00  # Limite mínimo para disparar alerta

def enviar_alerta(msg):
    print("📤 Enviando alerta para o Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    resposta = requests.post(url, data=data)
    print(f"📬 Status Telegram: {resposta.status_code} | Resposta: {resposta.text}")

def consultar_saldo():
    url = "https://api.openai.com/dashboard/billing/credit_grants"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    resposta = requests.get(url, headers=headers)

    if resposta.status_code != 200:
        enviar_alerta("❌ Erro ao consultar saldo da OpenAI.")
        return

    dados = resposta.json()
    saldo = dados.get("total_available", 0.0)
    total_grant = dados.get("total_granted", 0.0)
    total_usado = dados.get("total_used", 0.0)

    mensagem = (
        f"💳 *Status do Crédito OpenAI*\n"
        f"- Crédito total: *${total_grant:.2f}*\n"
        f"- Já usado: *${total_usado:.2f}*\n"
        f"- *Saldo atual:* ${saldo:.2f}"
    )
    enviar_alerta(mensagem)

    if saldo <= LIMITE_ALERTA:
        alerta = f"⚠️ *ALERTA:* Saldo abaixo de $2.00!\nSaldo atual: *${saldo:.2f}*"
        enviar_alerta(alerta)
    else:
        print("✅ Saldo acima de $2.00 — nenhum alerta crítico enviado.")

if __name__ == "__main__":
    consultar_saldo()
