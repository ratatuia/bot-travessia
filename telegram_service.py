import re
import requests
import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

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
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if sender not in self.conversas:
            self.conversas[sender] = {
                "nome": nome_cliente or "Cliente sem nome",
                "numero": sender,
                "mensagens": [],
                "ultima_atualizacao": datetime.datetime.now(),
                "perfil": {}
            }
        
        # Adiciona a mensagem ao histórico
        self.conversas[sender]["mensagens"].append({
            "timestamp": timestamp,
            "cliente": cliente_msg,
            "bot": bot_msg,
            "tipo": tipo
        })
        
        # Atualiza o timestamp
        self.conversas[sender]["ultima_atualizacao"] = datetime.datetime.now()
    
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
        tempo_decorrido = (datetime.datetime.now() - self.conversas[sender]["ultima_atualizacao"]).total_seconds()
        if not forcar and tempo_decorrido < 60:  # Aguarda 60 segundos ou envio forçado
            return False
        
        # Formata a mensagem para o Telegram
        nome = self.conversas[sender]["nome"]
        numero = self.conversas[sender]["numero"]
        link_whatsapp = formatar_numero_whatsapp(numero)
        
        # Formata o cabeçalho
        cabecalho = (
            f"💬 *Conversa com Cliente*\n"
            f"👤 *Nome*: {nome}\n"
            f"📱 *Contato*: [{link_whatsapp}](https://{link_whatsapp})\n"
            f"🕒 *Data*: {datetime.datetime.now().strftime('%d/%m/%Y')}\n"
        )
        
        # Adiciona informações de perfil se disponíveis
        if self.conversas[sender]["perfil"]:
            cabecalho += "\n📋 *Perfil do Cliente*:\n"
            for chave, valor in self.conversas[sender]["perfil"].items():
                cabecalho += f"- *{chave}*: {valor}\n"
        
        cabecalho += "➖➖➖➖➖➖➖➖➖➖➖➖"
        
        # Formata as mensagens
        conteudo_mensagens = []
        for msg in self.conversas[sender]["mensagens"]:
            tempo = msg["timestamp"]
            tipo = ""
            if msg["tipo"] == "atendimento":
                tipo = "⚠️ *ATENDIMENTO SOLICITADO*"
            elif msg["tipo"] == "urgente":
                tipo = "🔴 *URGENTE*"
            
            conteudo_mensagens.append(
                f"{tipo}\n"
                f"*{tempo}* Cliente: {msg['cliente']}\n"
                f"*{tempo}* Bot: {msg['bot']}"
            )
        
        # Junta tudo
        mensagem_completa = f"{cabecalho}\n\n" + "\n\n".join(conteudo_mensagens)
        
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
    
    def enviar_mensagem_urgente(self, mensagem, nome_cliente=None, numero=None):
        """Envia uma mensagem urgente diretamente para o Telegram"""
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
            
            resposta = requests.get(url, params=params, timeout=5)
            return resposta.status_code == 200
        except Exception as e:
            print(f"[ERRO TELEGRAM URGENTE] {e}")
            return False