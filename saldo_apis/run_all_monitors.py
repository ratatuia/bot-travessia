from saldo_apis.openai_monitor import consultar_saldo
from saldo_apis.twilio_monitor import monitorar_twilio

if __name__ == "__main__":
    consultar_saldo()
    monitorar_twilio()
