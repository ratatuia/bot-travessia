import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# ============================================
# 1. Carrega variáveis do arquivo .env
# ============================================
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Ex: 8147537930:AA...
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")           # Ex: 1002535493280

# ============================================
# 2. Configura o arquivo de log local
# ============================================
logging.basicConfig(
    filename='bot.log',              # Nome do arquivo onde será salvo o log
    level=logging.INFO,              # Nível de log: INFO, WARNING, ERROR, etc
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================
# 3. Função para registrar uma mensagem no log
# ============================================
def registrar_log(tipo, mensagem):
    if tipo == 'info':
        logging.info(mensagem)
    elif tipo == 'warning':
        logging.warning(mensagem)
    elif tipo == 'error':
        logging.error(mensagem)
    else:
        logging.debug(mensagem)

# ============================================
# 4. Envia uma mensagem para o Telegram
# ============================================
def enviar_alerta_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"🚨 [BOT ALERTA] {mensagem}"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        logging.error(f"Erro ao enviar alerta para Telegram: {e}")

# ============================================
# 5. Combina log + alerta em caso de erro
# ============================================
def capturar_erro(contexto, erro):
    mensagem = f"Erro em {contexto}: {str(erro)}"
    registrar_log("error", mensagem)
    enviar_alerta_telegram(mensagem)

# ============================================
# 6. Exemplo de uso (pode remover depois)
# ============================================
if __name__ == "__main__":
    registrar_log("info", "Bot iniciado com sucesso.")
    try:
        raise ValueError("Teste de erro")
    except Exception as e:
        capturar_erro("teste_local", e)
