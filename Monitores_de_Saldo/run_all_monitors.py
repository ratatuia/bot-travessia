from Monitores_de_Saldo.openai_monitor import monitorar_openai
from Monitores_de_Saldo.twilio_monitor import monitorar_twilio

if __name__ == "__main__":
    monitorar_openai()
    monitorar_twilio()