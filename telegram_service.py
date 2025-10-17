import re
import requests
import datetime
from zoneinfo import ZoneInfo
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# Timezone de Brasília
BRASIL_TZ = ZoneInfo("America/Sao_Paulo")

def formatar_numero_whatsapp(numero):
    """Formata o número para o formato wa.me"""
    # Remove "whatsapp:" e caracteres não numéricos
    limpo = re.sub(r'[^\d]', '', numero.replace("whatsapp:", ""))
    
    # Garante que o número está completo (com código do país)
    if not limpo.startswith("55") and len(limpo) <= 11:
        limpo = "55" + limpo
        
    return f"wa.me/{limpo}"

class TelegramService:
    def __init__(self):
        self.conversas = {}  # Armazena conversas temporariamente por remetente
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
    
    def adicionar_mensagem(self, sender, nome_cliente, cliente_msg, bot_msg, tipo="mensagem"):
        """Adiciona mensagem à conversa para envio agrupado"""
        timestamp = datetime.datetime.now(BRASIL_TZ).strftime("%H:%M:%S")

        if sender not in self.conversas:
            self.conversas[sender] = {
                "nome": nome_cliente or "Cliente sem nome",
                "numero": sender,
                "mensagens": [],
                "ultima_atualizacao": datetime.datetime.now(BRASIL_TZ),
                "perfil": {}
            }

        # Atualiza nome se vier diferente de "Novo cliente" ou genérico
        if nome_cliente and nome_cliente != "Novo cliente" and nome_cliente != "Cliente sem nome":
            self.conversas[sender]["nome"] = nome_cliente

        # Adiciona a mensagem ao histórico
        self.conversas[sender]["mensagens"].append({
            "timestamp": timestamp,
            "cliente": cliente_msg,
            "bot": bot_msg,
            "tipo": tipo
        })

        # Atualiza o timestamp
        self.conversas[sender]["ultima_atualizacao"] = datetime.datetime.now(BRASIL_TZ)
    
    def atualizar_perfil(self, sender, chave, valor):
        """Atualiza informações de perfil do cliente"""
        if sender in self.conversas:
            self.conversas[sender]["perfil"][chave] = valor
    
    def enviar_conversa(self, sender, forcar=False):
        """Envia a conversa acumulada para o Telegram"""
        if sender not in self.conversas:
            return False
        
        # Verifica se tem mensagens para enviar
        if not self.conversas[sender]["mensagens"]:
            return False
            
        # Verifica se é hora de enviar (após última mensagem ou forçado)
        tempo_decorrido = (datetime.datetime.now(BRASIL_TZ) - self.conversas[sender]["ultima_atualizacao"]).total_seconds()
        if not forcar and tempo_decorrido < 60:  # Aguarda 60 segundos ou envio forçado
            return False
        
        # Formata a mensagem para o Telegram
        nome = self.conversas[sender]["nome"]
        numero = self.conversas[sender]["numero"]
        link_whatsapp = formatar_numero_whatsapp(numero)
        
        # Formata o cabeçalho
        cabecalho = (
            f"{'✅' if self.conversas[sender]['mensagens'][-1].get('tipo') == 'atendimento' else '🔔'} "
            f"*{nome.upper()}*\n"
            f"📱 [{link_whatsapp}](https://{link_whatsapp})\n"
            f"🕒 {datetime.datetime.now(BRASIL_TZ).strftime('%d/%m/%Y %H:%M')}\n"
        )

        # Filtra e limpa informações de perfil
        perfil_limpo = {}
        campos_invalidos = ["Não especificado", "X dias", "período", "mês/ano", "mês/período"]

        if self.conversas[sender]["perfil"]:
            for chave, valor in self.conversas[sender]["perfil"].items():
                # Remove campos com valores genéricos/inválidos
                if valor and valor not in campos_invalidos:
                    perfil_limpo[chave] = valor

        # Adiciona perfil se tiver dados válidos
        if perfil_limpo:
            cabecalho += "\n📋 *Perfil*:\n"
            for chave, valor in perfil_limpo.items():
                cabecalho += f"• {chave}: {valor}\n"

        cabecalho += "─────────────\n"

        # Formata apenas as RESPOSTAS DO CLIENTE (sem mensagens do bot)
        respostas_cliente = []
        for msg in self.conversas[sender]["mensagens"]:
            tempo = msg["timestamp"]
            cliente_msg = msg['cliente']

            # Adiciona marcador se for atendimento/urgente
            marcador = ""
            if msg["tipo"] == "atendimento":
                marcador = "✅ "
            elif msg["tipo"] == "urgente":
                marcador = "🔴 "

            respostas_cliente.append(f"{marcador}*{tempo}*: {cliente_msg}")

        # Junta tudo
        mensagem_completa = f"{cabecalho}\n💬 *Respostas*:\n" + "\n".join(respostas_cliente)
        
        # Envia para o Telegram
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            "chat_id": self.chat_id,
            "text": mensagem_completa,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        
        try:
            resposta = requests.get(url, params=params)
            resultado = resposta.json()
            
            # Limpa as mensagens após envio bem-sucedido
            if resultado.get("ok", False):
                self.conversas[sender]["mensagens"] = []
            
            return resultado.get("ok", False)
        except Exception as e:
            print(f"[ERRO TELEGRAM] {e}")
            return False
    
    def enviar_mensagem_urgente(self, mensagem, nome_cliente=None, numero=None, botoes=None):
        """Envia uma mensagem urgente diretamente para o Telegram com botões opcionais"""
        try:
            link_whatsapp = formatar_numero_whatsapp(numero) if numero else None

            texto = mensagem
            if nome_cliente or numero:
                info_adicional = []
                if nome_cliente:
                    info_adicional.append(f"👤 *Nome*: {nome_cliente}")
                if numero:
                    info_adicional.append(f"📱 *Contato*: [{link_whatsapp}](https://{link_whatsapp})")

                texto += "\n\n" + "\n".join(info_adicional)

            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            params = {
                "chat_id": self.chat_id,
                "text": texto,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }

            # Adiciona botões inline se fornecidos
            if botoes:
                params["reply_markup"] = {
                    "inline_keyboard": [botoes]
                }

            resposta = requests.post(url, json=params, timeout=5)
            return resposta.status_code == 200
        except Exception as e:
            print(f"[ERRO TELEGRAM URGENTE] {e}")
            return False

    def enviar_relatorio_diario(self, stats):
        """Envia relatório diário com estatísticas"""
        try:
            hoje = datetime.datetime.now(BRASIL_TZ).strftime('%d/%m/%Y')

            mensagem = f"""📊 *Relatório Diário - {hoje}*

👥 *Novos clientes*: {stats.get('clients_24h', 0)}
👨‍👩‍👧‍👦 *Total de clientes*: {stats.get('total_clients', 0)}
💬 *Mensagens*: {stats.get('messages_24h', 0)}
🎯 *Taxa de conversão*: {stats.get('conversion_rate', 0):.1f}%
⚠️ *Atendimentos pendentes*: {stats.get('atendimentos_pendentes', 0)}

🚢 *Travessia dos Sonhos*
"""

            botoes = [
                {"text": "📊 Ver Dashboard", "url": "https://bot-travessia.onrender.com/dashboard"}
            ]

            return self.enviar_mensagem_urgente(mensagem, botoes=botoes)
        except Exception as e:
            print(f"[ERRO RELATÓRIO DIÁRIO] {e}")
            return False

    def enviar_alerta_inatividade(self, horas_inativo):
        """Envia alerta quando não há mensagens há X horas"""
        try:
            mensagem = f"""⚠️ *Alerta de Inatividade*

🕐 Nenhuma mensagem recebida nas últimas *{horas_inativo} horas*

Possíveis causas:
• Webhook do Twilio não está funcionando
• Bot está offline
• Nenhum cliente entrou em contato

🔍 Verifique o sistema"""

            botoes = [
                {"text": "🔧 Testar Webhook", "url": "https://bot-travessia.onrender.com/health"},
                {"text": "📊 Ver Dashboard", "url": "https://bot-travessia.onrender.com/dashboard"}
            ]

            return self.enviar_mensagem_urgente(mensagem, botoes=botoes)
        except Exception as e:
            print(f"[ERRO ALERTA INATIVIDADE] {e}")
            return False

    def enviar_alerta_performance(self, operacao, tempo_ms):
        """Envia alerta quando operação está lenta"""
        try:
            mensagem = f"""⚠️ *Alerta de Performance*

🐌 Operação lenta detectada:
*{operacao}*

⏱️ Tempo médio: *{tempo_ms:.0f}ms*
⚡ Esperado: <2000ms

📊 Verifique o dashboard para mais detalhes"""

            botoes = [
                {"text": "📊 Ver Dashboard", "url": "https://bot-travessia.onrender.com/dashboard"}
            ]

            return self.enviar_mensagem_urgente(mensagem, botoes=botoes)
        except Exception as e:
            print(f"[ERRO ALERTA PERFORMANCE] {e}")
            return False

    def enviar_alerta_health(self, componentes_com_problema):
        """Envia alerta quando componentes estão com problema"""
        try:
            componentes_texto = "\n".join([f"❌ {c}" for c in componentes_com_problema])

            mensagem = f"""🔴 *Alerta de Health Check*

Componentes com problema:
{componentes_texto}

🔧 Ação necessária!"""

            botoes = [
                {"text": "🏥 Ver Health", "url": "https://bot-travessia.onrender.com/api/health/detailed"},
                {"text": "📊 Ver Dashboard", "url": "https://bot-travessia.onrender.com/dashboard"}
            ]

            return self.enviar_mensagem_urgente(mensagem, botoes=botoes)
        except Exception as e:
            print(f"[ERRO ALERTA HEALTH] {e}")
            return False