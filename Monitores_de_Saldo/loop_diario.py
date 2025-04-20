import time
import datetime
from Monitores_de_Saldo.openai_monitor import consultar_saldo
from Monitores_de_Saldo.twilio_monitor import monitorar_twilio

def esperar_ate_8_da_manha():
    agora = datetime.datetime.now()
    proxima_8h = agora.replace(hour=8, minute=0, second=0, microsecond=0)

    if agora >= proxima_8h:
        proxima_8h += datetime.timedelta(days=1)

    segundos_espera = (proxima_8h - agora).total_seconds()
    print(f"⏳ Esperando até as 08:00... ({int(segundos_espera)}s)")
    time.sleep(segundos_espera)

if __name__ == "__main__":
    while True:
        esperar_ate_8_da_manha()
        print("📡 Enviando alertas diários...")
        consultar_saldo()
        monitorar_twilio()
        time.sleep(60)  # só pra não travar se rodar em loop por engano

