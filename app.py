from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import random
import re
import datetime
import json
import traceback
import os
import psutil

# Variável global para rastrear quando o bot foi iniciado
app_start_time = datetime.datetime.now()

# Importações dos módulos do projeto
from config import LOGO_URL, HORARIO_ATENDIMENTO, RESPOSTAS_INVALIDAS, MENUS, MENSAGENS, BASE_CONHECIMENTO, DB_PATH
from database import init_db, get_client_state, update_client_state, save_message
from telegram_service import TelegramService
from openai_service import AIService
from log_service import registrar_log, capturar_erro


# Inicialização
app = Flask(__name__)
init_db()  # Inicializa o banco de dados
telegram_service = TelegramService()
ai_service = AIService()

# ADICIONE A ROTA RAIZ AQUI
@app.route("/", methods=["GET"])
def index():
    return "Bot da Travessia dos Sonhos - Online!", 200

# Funções auxiliares
def validar_email(email):
    """Verifica se o e-mail está em um formato válido"""
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def validar_opcao_menu(resposta, num_opcoes, incluir_numeros_texto=True):
    """Valida se a resposta é uma opção válida de menu"""
    resposta = resposta.strip().lower()
    
    # Verifica se é um número de 1 a num_opcoes
    if resposta.isdigit():
        num = int(resposta)
        if 1 <= num <= num_opcoes:
            return num, True
    
    # Verifica formas escritas dos números (se ativado)
    if incluir_numeros_texto:
        numeros_texto = ["um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"]
        if resposta in numeros_texto[:num_opcoes]:
            return numeros_texto.index(resposta) + 1, True
    
    # Resposta inválida
    return None, False

def obter_resposta_invalida():
    """Retorna uma mensagem aleatória para respostas inválidas"""
    return random.choice(RESPOSTAS_INVALIDAS)

def formatar_menu(tipo_menu, nome=None):
    """Gera um menu formatado com base no tipo"""
    if tipo_menu not in MENUS:
        return "Menu não encontrado"
    
    menu = MENUS[tipo_menu]
    resultado = ""
    
    # Adiciona título
    if "titulo" in menu:
        titulo = menu["titulo"]
        if nome and "{nome}" in titulo:
            titulo = titulo.format(nome=nome)
        resultado += f"{titulo}\n\n"
    
    # Adiciona subtítulo
    if "subtitulo" in menu:
        resultado += f"{menu['subtitulo']}\n\n"
    
    # Adiciona pergunta
    if "pergunta" in menu:
        resultado += f"{menu['pergunta']}\n\n"
    
    # Adiciona opções
    if "opcoes" in menu:
        emojis_numericos = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for i, opcao in enumerate(menu["opcoes"]):
            resultado += f"{emojis_numericos[i]} {opcao}\n\n"
    
    # Adiciona rodapé
    if "rodape" in menu:
        resultado += f"\n\n{menu['rodape']}"
    
    return resultado.strip()

def is_greeting(message):
    """Verifica se a mensagem é uma saudação ou comando de início"""
    message = message.lower().strip()
    
    # Lista de saudações comuns
    greetings = ["oi", "olá", "ola", "ei", "e ai", "eai", "hello", "hi", "hey", "hola"]
    
    # Frases de saudação
    greeting_phrases = ["bom dia", "boa tarde", "boa noite", "tudo bem"]
    
    # Comandos de início
    start_commands = ["menu", "ajuda", "iniciar", "começar", "start", "help"]
    
    # Verifica saudações exatas ou no início da mensagem
    for greeting in greetings:
        if message == greeting or message.startswith(greeting + " "):
            return True
    
    # Verifica frases de saudação
    for phrase in greeting_phrases:
        if message == phrase or message.startswith(phrase + " "):
            return True
    
    # Verifica comandos explícitos
    for command in start_commands:
        if message == command:
            return True
    
    return False

# Rota para reset do banco de dados
@app.route("/reset-db", methods=["GET"])
def reset_database():
    try:
        import os
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        return "Banco de dados reiniciado com sucesso!", 200
    except Exception as e:
        return f"Erro ao reiniciar banco de dados: {e}", 500

# Rota de diagnóstico
@app.route("/debug-state", methods=["GET"])
def debug_state():
    try:
        phone = request.args.get("phone")
        if not phone:
            return "Parâmetro 'phone' é obrigatório", 400
        
        state = get_client_state(phone)
        return f"Estado do cliente {phone}: {state}", 200
    except Exception as e:
        return f"Erro ao obter estado: {e}", 500

# NOVA ROTA DE HEALTH CHECK MELHORADA
@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Calcula quanto tempo o bot está rodando
        uptime = datetime.datetime.now() - app_start_time
        
        # Verifica conexão com banco de dados
        db_ok = True
        try:
            # Tenta fazer uma consulta simples
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            conn.execute("SELECT 1")
            conn.close()
        except Exception as e:
            db_ok = False
            registrar_log("error", f"Erro de conexão com banco de dados: {e}")
            
        # Contagem de clientes e mensagens
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Total de clientes
            cursor.execute("SELECT COUNT(*) FROM clientes")
            total_clientes = cursor.fetchone()[0]
            
            # Total de mensagens
            cursor.execute("SELECT COUNT(*) FROM mensagens")
            total_mensagens = cursor.fetchone()[0]
            
            # Clientes com atendimento solicitado
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE estado = 'atendimento_solicitado'")
            clientes_atendimento = cursor.fetchone()[0]
            
            # Mensagens nas últimas 24 horas
            cursor.execute("SELECT COUNT(*) FROM mensagens WHERE timestamp > datetime('now', '-1 day')")
            mensagens_24h = cursor.fetchone()[0]
            
            conn.close()
        except Exception as e:
            total_clientes = 0
            total_mensagens = 0
            clientes_atendimento = 0
            mensagens_24h = 0
            registrar_log("error", f"Erro ao consultar estatísticas do DB: {e}")
        
        # Informações de sistema
        process = psutil.Process(os.getpid())
        
        # Informações do sistema
        status = {
            "status": "online" if db_ok else "problema_detectado",
            "uptime": str(uptime),
            "uptime_horas": round(uptime.total_seconds() / 3600, 2),
            "database": "conectado" if db_ok else "erro",
            "estatisticas": {
                "total_clientes": total_clientes,
                "total_mensagens": total_mensagens,
                "clientes_atendimento": clientes_atendimento,
                "mensagens_24h": mensagens_24h
            },
            "sistema": {
                "memoria_uso_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                "cpu_percent": process.cpu_percent(),
                "threads": len(process.threads())
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Se houver problema no banco, retorna HTTP 500
        if not db_ok:
            return jsonify(status), 500
            
        return jsonify(status), 200
    except Exception as e:
        registrar_log("error", f"Erro ao executar health check: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# Rota principal do bot
@app.route("/zap", methods=["POST"])
def whatsapp_bot():
    # Adicione estes logs no início da função
    print("====== NOVA REQUISIÇÃO WEBHOOK ======")
    print(f"Headers: {dict(request.headers)}")
    print(f"Form Data: {dict(request.form)}")
    print(f"JSON Data: {request.get_json()}")
    print("======================================") 
        
    # Extrai informações da requisição
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")
    
    print(f"[CLIENTE] {sender} disse: {incoming_msg}")
    registrar_log("info", f"Mensagem recebida de {sender}: {incoming_msg}")
    
    try:
        # Inicialização para novas conversas ou saudações
        if is_greeting(incoming_msg):
            print(f"[DEBUG] Detectada saudação: {incoming_msg}")
            registrar_log("info", f"Nova conversa iniciada com {sender}")
            # Inicia nova conversa
            update_client_state(sender, {"estado": "aguardando_nome"})
            
            # Limpa conversa Telegram existente se houver
            telegram_service.enviar_conversa(sender, forcar=True)
            
            # Prepara resposta com logo
            resp = MessagingResponse()
            msg = resp.message()
            msg.media(LOGO_URL)
            msg.body(MENSAGENS["boas_vindas"])
            
            # Adiciona mensagem ao Telegram
            telegram_service.adicionar_mensagem(
                sender, 
                "Novo cliente", 
                incoming_msg, 
                MENSAGENS["boas_vindas"]
            )
            
            return str(resp)
        
        # Obtém o estado atual do cliente
        estado_atual = get_client_state(sender)
        print(f"[DEBUG] Estado atual: {estado_atual}")
        
        # Determina nome do cliente se disponível
        nome_cliente = estado_atual.get("nome") if estado_atual else None
        print(f"[DEBUG] Nome do cliente: {nome_cliente}")
        
        # Processa a mensagem com base no estado atual
        try:
            print(f"[DEBUG] Processando mensagem...")
            resposta, novo_estado, meta = processar_mensagem(sender, incoming_msg, estado_atual)
            print(f"[DEBUG] Processamento bem-sucedido. Novo estado: {novo_estado}")
            print(f"[DEBUG] Resposta: {resposta[:100]}...")  # Imprime apenas o início da resposta
        except Exception as e:
            print(f"[ERRO CRÍTICO] Erro no processamento da mensagem: {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            capturar_erro("processamento_mensagem", e)
            # Resposta genérica de erro
            resposta = f"{'Olá' if not nome_cliente else nome_cliente}, desculpe, tivemos um probleminha técnico. Pode tentar novamente em instantes?"
            novo_estado = estado_atual
            meta = {}
        
        # Atualiza estado no banco de dados
        if novo_estado:
            update_client_state(sender, novo_estado)
            print(f"[DEBUG] Estado atualizado no banco de dados")
        
        # Salva a mensagem
        precisa_atendimento = meta.get("tipo_msg") in ["urgente", "atendimento"] if meta else False
        save_message(sender, incoming_msg, resposta, precisa_atendimento)
        
        # Adiciona mensagem ao Telegram
        tipo_msg = meta.get("tipo_msg", "mensagem") if meta else "mensagem"
        telegram_service.adicionar_mensagem(sender, nome_cliente, incoming_msg, resposta, tipo_msg)
        
        # Envia notificação urgente se necessário
        if tipo_msg == "urgente":
            print(f"[DEBUG] Enviando notificação urgente para o Telegram")
            registrar_log("info", f"Atendimento solicitado por {nome_cliente} ({sender})")
            telegram_service.enviar_mensagem_urgente(
                "🔴 *URGENTE: Cliente precisa de atendimento especializado!*", 
                nome_cliente, 
                sender
            )
        elif tipo_msg == "atendimento":
            print(f"[DEBUG] Enviando notificação de atendimento para o Telegram")
            perfil = telegram_service.conversas.get(sender, {}).get("perfil", {})
            
            mensagem_telegram = "✅ *CLIENTE COMPLETOU PLANEJAMENTO DE VIAGEM*\n\n"
            for chave, valor in perfil.items():
                mensagem_telegram += f"*{chave}*: {valor}\n"
            
            telegram_service.enviar_mensagem_urgente(mensagem_telegram, nome_cliente, sender)
        
        # Envia conversa agrupada para o Telegram
        if tipo_msg in ["urgente", "atendimento"]:
            telegram_service.enviar_conversa(sender, forcar=True)
        else:
            telegram_service.enviar_conversa(sender)
        
        # Responde ao cliente
        resp = MessagingResponse()
        resp.message(resposta)
        return str(resp)
        
    except Exception as e:
        print(f"[ERRO GERAL] {e}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        capturar_erro("whatsapp_bot", e)
        
        # Resposta de erro
        erro_msg = "⚠️ {nome}, desculpe, tivemos um probleminha técnico. Pode tentar novamente em instantes?".format(
            nome='Olá' if not nome_cliente else nome_cliente
        )
        
        # Adiciona mensagem de erro ao Telegram
        telegram_service.adicionar_mensagem(sender, nome_cliente, incoming_msg, erro_msg)
        
        resp = MessagingResponse()
        resp.message(erro_msg)
        return str(resp)

def processar_mensagem(sender, mensagem, estado_atual):
    """
    Processa a mensagem do usuário com base no estado atual
    
    Returns:
        - resposta (str): Texto de resposta para o cliente
        - novo_estado (dict): Novo estado do cliente
        - meta (dict): Metadados da mensagem (tipo etc.)
    """
    print(f"[DEBUG] Processando mensagem: '{mensagem}'")
    print(f"[DEBUG] Estado atual: {estado_atual}")
    
    # Se não tem estado, retorna mensagem de boas-vindas
    if not estado_atual:
        print("[DEBUG] Sem estado atual, iniciando nova conversa")
        return MENSAGENS["boas_vindas"], {"estado": "aguardando_nome"}, {}
    
    # Determina o estado e nome
    estado = estado_atual.get("estado") if isinstance(estado_atual, dict) else estado_atual
    nome = estado_atual.get("nome") if isinstance(estado_atual, dict) else None
    
    print(f"[DEBUG] Estado: {estado}, Nome: {nome}")
    
    # Verifica se o cliente já solicitou atendimento
    if estado == "atendimento_solicitado":
        print("[DEBUG] Cliente em estado de atendimento solicitado")
        # Se o cliente já solicitou atendimento, reenviar a mensagem de confirmação
        # apenas se ele enviar um novo comando de atendimento
        if mensagem == "3" or mensagem.lower() in ["atendimento", "ajuda", "especialista", "falar"]:
            resposta = MENSAGENS["atendimento_solicitado"].format(
                nome=nome,
                horario=HORARIO_ATENDIMENTO
            )
            return resposta, estado_atual, {"tipo_msg": "urgente"}
        
        # Para qualquer outra mensagem após solicitar atendimento, enviar uma resposta genérica
        # que informa que um atendente humano entrará em contato
        resposta = (
            f"✨ {nome}, sua solicitação já foi registrada! Um especialista entrará em contato em breve conforme solicitado. "
            f"Horário de atendimento: {HORARIO_ATENDIMENTO}\n\n"
            f"Caso precise de atendimento imediato, você também pode nos contatar pelo telefone "
            f"ou WhatsApp: (11) 91529-0344"
        )
        return resposta, estado_atual, {}
    
    # Comando para menu a qualquer momento
    if mensagem.lower() == "menu" and nome:
        print("[DEBUG] Comando de menu detectado")
        novo_estado = {**estado_atual, "estado": "menu"}
        resposta = formatar_menu("principal", nome)
        return resposta, novo_estado, {}
    
    # Processamento baseado no estado
    if estado == "aguardando_nome":
        print("[DEBUG] Processando aguardando_nome")
        # Captura o nome
        novo_estado = {"nome": mensagem, "estado": "aguardando_email"}
        resposta = MENSAGENS["pedir_email"]
        return resposta, novo_estado, {}
        
    elif estado == "aguardando_email":
        print("[DEBUG] Processando aguardando_email")
        # Valida e captura o email
        if not validar_email(mensagem):
            print("[DEBUG] Email inválido")
            resposta = MENSAGENS["email_invalido"].format(nome=nome)
            return resposta, estado_atual, {}
        
        print("[DEBUG] Email válido")
        novo_estado = {
            "nome": nome,
            "email": mensagem,
            "estado": "menu"
        }
        
        resposta = formatar_menu("principal", nome)
        telegram_service.atualizar_perfil(sender, "Email", mensagem)
        
        return resposta, novo_estado, {}
        
    elif estado == "menu":
        print("[DEBUG] Processando menu")
        # Processa opções do menu principal
        if mensagem == "1":  # Conhecer tripulação
            print("[DEBUG] Opção 1 selecionada")
            novo_estado = {**estado_atual, "estado": "pos_conhecer_tripulacao"}
            resposta = MENSAGENS["apresentacao_empresa"].format(nome=nome)
            return resposta, novo_estado, {}
            
        elif mensagem == "2":  # Iniciar viagem
            print("[DEBUG] Opção 2 selecionada")
            novo_estado = {**estado_atual, "estado": "perguntando_periodo_viagem"}
            resposta = formatar_menu("periodo_viagem", nome)
            return resposta, novo_estado, {}
            
        elif mensagem == "3":  # Solicitar atendimento
            print("[DEBUG] Opção 3 selecionada")
            novo_estado = {**estado_atual, "estado": "atendimento_solicitado"}
            resposta = MENSAGENS["atendimento_solicitado"].format(
                nome=nome,
                horario=HORARIO_ATENDIMENTO
            )
            # Aqui metadados indicam que é uma mensagem urgente
            return resposta, novo_estado, {"tipo_msg": "urgente"}
            
        else:
            print("[DEBUG] Opção inválida no menu")
            # Resposta inválida para o menu
            resposta = f"{nome}, {obter_resposta_invalida()}\n\n{formatar_menu('principal', nome)}"
            return resposta, estado_atual, {}
    
    # Estado após conhecer tripulação
    elif estado == "pos_conhecer_tripulacao":
        print(f"[DEBUG] Processando pos_conhecer_tripulacao, mensagem: '{mensagem}'")
        # Simplificado para diagnóstico - sempre passa para o próximo passo
        try:
            # Valida opção
            opcao, valida = validar_opcao_menu(mensagem, 2)
            print(f"[DEBUG] Validação: opcao={opcao}, valida={valida}")
            
            if not valida:
                print("[DEBUG] Opção inválida")
                resposta = f"{nome}, {obter_resposta_invalida()}\n\nVocê já teve alguma experiência anterior com cruzeiros marítimos?\n\n1️⃣ Sim\n2️⃣ Não, será minha primeira vez"
                return resposta, estado_atual, {}
            
            # Registra a experiência prévia
            experiencia = "Sim" if opcao == 1 else "Não"
            print(f"[DEBUG] Experiência: {experiencia}")
            
            # Configurando próximo estado
            print("[DEBUG] Configurando próximo estado para perguntando_interesses")
            novo_estado = {
                **estado_atual, 
                "estado": "perguntando_interesses",
                "experiencia_previa": experiencia
            }
            
            # Atualiza Telegram
            telegram_service.atualizar_perfil(sender, "Experiência prévia", experiencia)
            
            # Resposta (menu de interesses)
            resposta = formatar_menu("interesses", nome)
            
            print("[DEBUG] Retornando resposta do menu de interesses")
            return resposta, novo_estado, {}
        except Exception as e:
            print(f"[ERRO] Erro ao processar pos_conhecer_tripulacao: {e}")
            print(traceback.format_exc())
            capturar_erro("pos_conhecer_tripulacao", e)
            
            # Solução de contorno - força ir para o próximo estado
            novo_estado = {
                **estado_atual, 
                "estado": "perguntando_interesses",
                "experiencia_previa": "Não especificada"
            }
            
            resposta = formatar_menu("interesses", nome)
            return resposta, novo_estado, {}
    
    # Estado de perguntando interesses
    elif estado == "perguntando_interesses":
        print("[DEBUG] Processando perguntando_interesses")
        # Valida opção
        opcao, valida = validar_opcao_menu(mensagem, 6)
        
        if not valida:
            print("[DEBUG] Opção inválida para interesses")
            resposta = f"{nome}, {obter_resposta_invalida()}\n\n{formatar_menu('interesses')}"
            return resposta, estado_atual, {}
        
        # Mapeamento dos interesses
        opcoes_interesses = {
            1: "Gastronomia",
            2: "Entretenimento",
            3: "Destinos exóticos",
            4: "Relaxamento",
            5: "Atividades para família",
            6: "Experiência completa"
        }
        
        # Registra o interesse principal
        interesse = opcoes_interesses.get(opcao)
        novo_estado = {
            **estado_atual,
            "estado": "apos_interesses",
            "interesse_principal": interesse
        }
        
        # Atualiza Telegram
        telegram_service.atualizar_perfil(sender, "Interesse principal", interesse)
        
        # Resposta - pergunta se quer planejar viagem
        resposta = (
            f"✨ Excelente escolha, {nome}! Entendi que você se interessa por {interesse}.\n\n"
            f"Gostaria de planejar sua viagem personalizada agora?\n\n"
            f"1️⃣ Sim, vamos começar!\n"
            f"2️⃣ Não, apenas pesquisando por enquanto"
        )
        
        return resposta, novo_estado, {}
    
    # Estado após coletar interesse
    elif estado == "apos_interesses":
        print("[DEBUG] Processando apos_interesses")
        # Valida opção
        opcao, valida = validar_opcao_menu(mensagem, 2)
        
        if not valida:
            print("[DEBUG] Opção inválida após interesses")
            resposta = (
                f"{nome}, {obter_resposta_invalida()}\n\n"
                f"Gostaria de planejar sua viagem personalizada agora?\n\n"
                f"1️⃣ Sim, vamos começar!\n"
                f"2️⃣ Não, apenas pesquisando por enquanto"
            )
            return resposta, estado_atual, {}
        
        if opcao == 1:  # Sim, quer planejar
            print("[DEBUG] Cliente quer planejar viagem")
            # Direciona para o fluxo de planejamento
            novo_estado = {**estado_atual, "estado": "perguntando_periodo_viagem"}
            resposta = formatar_menu("periodo_viagem", nome)
            return resposta, novo_estado, {}
        else:  # Não, apenas pesquisando
            print("[DEBUG] Cliente apenas pesquisando")
            # Retorna ao menu
            novo_estado = {**estado_atual, "estado": "menu"}
            resposta = MENSAGENS["resposta_pesquisa"].format(nome=nome)
            return resposta, novo_estado, {}
    
    # Estado de perguntando período de viagem
    elif estado == "perguntando_periodo_viagem":
        print("[DEBUG] Processando perguntando_periodo_viagem")
        # Valida opção
        opcao, valida = validar_opcao_menu(mensagem, 6)
        
        if not valida:
            print("[DEBUG] Opção inválida para período")
            resposta = f"{nome}, {obter_resposta_invalida()}\n\n{formatar_menu('periodo_viagem')}"
            return resposta, estado_atual, {}
        
        # Mapeamento dos períodos
        opcoes_periodo = {
            1: "Primeiros meses (Jan-Mar)",
            2: "Meio do ano (Abr-Jun)",
            3: "Férias de julho",
            4: "Segundo semestre (Ago-Out)",
            5: "Final do ano (Nov-Dez)",
            6: "Ainda não decidido"
        }
        
        # Registra o período desejado
        periodo = opcoes_periodo.get(opcao)
        novo_estado = {
            **estado_atual,
            "estado": "perguntando_duracao",
            "periodo_viagem": periodo
        }
        
        # Atualiza Telegram
        telegram_service.atualizar_perfil(sender, "Período desejado", periodo)
        
        # Resposta (menu de duração)
        resposta = f"📅 Excelente, {nome}! {formatar_menu('duracao')}"
        
        return resposta, novo_estado, {}
    
    # Estado de perguntando duração
    elif estado == "perguntando_duracao":
        print("[DEBUG] Processando perguntando_duracao")
        # Valida opção
        opcao, valida = validar_opcao_menu(mensagem, 5)
        
        if not valida:
            print("[DEBUG] Opção inválida para duração")
            resposta = f"{nome}, {obter_resposta_invalida()}\n\n{formatar_menu('duracao')}"
            return resposta, estado_atual, {}
        
        # Mapeamento das durações
        opcoes_duracao = {
            1: "Mini-cruzeiro (3-5 dias)",
            2: "Cruzeiro padrão (6-9 dias)",
            3: "Cruzeiro estendido (10-14 dias)",
            4: "Longa duração (15+ dias)",
            5: "Ainda não decidido"
        }
        
        # Registra a duração desejada
        duracao = opcoes_duracao.get(opcao)
        novo_estado = {
            **estado_atual,
            "estado": "perguntando_destino",
            "duracao": duracao
        }
        
        # Atualiza Telegram
        telegram_service.atualizar_perfil(sender, "Duração desejada", duracao)
        
        # Resposta (menu de destino)
        resposta = f"⏱️ Perfeito, {nome}! {formatar_menu('destino_regiao')}"
        
        return resposta, novo_estado, {}
    
    # Estado de perguntando destino
    elif estado == "perguntando_destino":
        print("[DEBUG] Processando perguntando_destino")
        # Valida opção
        opcao, valida = validar_opcao_menu(mensagem, 8)  # Agora são 8 opções
        
        if not valida:
            print("[DEBUG] Opção inválida para destino")
            resposta = f"{nome}, {obter_resposta_invalida()}\n\n{formatar_menu('destino_regiao')}"
            return resposta, estado_atual, {}
        
        # Mapeamento dos destinos
        opcoes_destino = {
            1: "Brasil",
            2: "Caribe e Bahamas",
            3: "Mediterrâneo",
            4: "Europa e Escandinávia",
            5: "América do Sul",
            6: "Alasca",
            7: "Ásia e Oceania",
            8: "Outro destino / Não decidido"
        }
        
        # Registra o destino desejado
        destino = opcoes_destino.get(opcao)
        novo_estado = {
            **estado_atual,
            "estado": "perguntando_forma_contato",
            "destino": destino
        }
        
        # Atualiza Telegram
        telegram_service.atualizar_perfil(sender, "Destino desejado", destino)
        
        # Resposta (forma de contato)
        resposta = f"🌎 Excelente escolha, {nome}! {formatar_menu('forma_contato')}"
        
        return resposta, novo_estado, {}
    
# Estado de perguntando forma de contato
    elif estado == "perguntando_forma_contato":
        print("[DEBUG] Processando perguntando_forma_contato")
        # Valida opção
        opcao, valida = validar_opcao_menu(mensagem, 3)  # Agora são 3 opções
        
        if not valida:
            print("[DEBUG] Opção inválida para forma de contato")
            resposta = f"{nome}, {obter_resposta_invalida()}\n\n{formatar_menu('forma_contato')}"
            return resposta, estado_atual, {}
        
        # Mapeamento das formas de contato
        opcoes_contato = {
            1: "WhatsApp",
            2: "Ligação telefônica",
            3: "Vídeo-chamada"
        }
        
        # Registra a forma de contato
        metodo_contato = opcoes_contato.get(opcao)
        novo_estado = {
            **estado_atual,
            "estado": "perguntando_horario",
            "metodo_contato": metodo_contato
        }
        
        # Atualiza Telegram
        telegram_service.atualizar_perfil(sender, "Método de contato", metodo_contato)
        
        # Resposta (horário de contato)
        resposta = f"📱 Anotado, {nome}! {formatar_menu('horario_contato')}"
        
        return resposta, novo_estado, {}
    
    # Estado de perguntando horário de contato
    elif estado == "perguntando_horario":
        print("[DEBUG] Processando perguntando_horario")
        # Valida opção
        opcao, valida = validar_opcao_menu(mensagem, 5)
        
        if not valida:
            print("[DEBUG] Opção inválida para horário")
            resposta = f"{nome}, {obter_resposta_invalida()}\n\n{formatar_menu('horario_contato')}"
            return resposta, estado_atual, {}
        
        # Mapeamento dos horários
        opcoes_horario = {
            1: "Manhã (9h-12h)",
            2: "Horário de almoço (12h-14h)",
            3: "Tarde (14h-18h)",
            4: "Noite (18h-20h)",
            5: "Qualquer horário dentro do horário de atendimento"
        }
        
        # Registra o horário desejado
        horario = opcoes_horario.get(opcao)
        metodo = estado_atual.get("metodo_contato", "Não especificado")
        
        novo_estado = {
            **estado_atual,
            "estado": "atendimento_solicitado",
            "horario_contato": horario
        }
        
        # Atualiza Telegram
        telegram_service.atualizar_perfil(sender, "Horário de contato", horario)
        
        # Resposta final
        resposta = (
            f"✅ Perfeito, {nome}! Seus dados foram registrados com sucesso.\n\n"
            f"Um de nossos especialistas entrará em contato em breve conforme sua preferência "
            f"({metodo} no horário {horario}).\n\n"
            f"Obrigado por escolher a Travessia dos Sonhos para sua próxima aventura marítima! 🚢✨"
        )
        
        return resposta, novo_estado, {"tipo_msg": "atendimento"}

    # Estado para outros fluxos ainda não implementados ou mensagens não mapeadas
    print("[DEBUG] Estado não reconhecido, tentando resposta com IA")
    try:
        resposta_ia = ai_service.gerar_resposta(nome, mensagem, BASE_CONHECIMENTO)
        return resposta_ia, estado_atual, {}
    except Exception as e:
        print(f"[ERRO IA] {e}")
        print(traceback.format_exc())
        capturar_erro("resposta_ia", e)
        # Mensagem genérica se tudo falhar
        if nome:
            resposta = f"{nome}, para continuar nossa conversa, você pode digitar 'menu' para ver as opções disponíveis."
        else:
            resposta = "Para começarmos nossa conversa, digite 'oi' ou 'olá'."
        return resposta, estado_atual, {}

# Rota de teste do Telegram
@app.route("/test-telegram", methods=["GET"])
def test_telegram():
    try:
        result = telegram_service.enviar_mensagem_urgente("Teste de mensagem do bot Travessia dos Sonhos", "Teste", "whatsapp:+5511999999999")
        return f"Telegram test: {result}", 200
    except Exception as e:
        capturar_erro("test_telegram", e)
        return f"Telegram test error: {e}", 500

# Rota para monitoramento diário
@app.route("/daily-stats", methods=["GET"])
def daily_stats():
    try:
        # Data de hoje
        hoje = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Conecta ao banco de dados
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Consulta clientes novos de hoje
        cursor.execute("""
            SELECT COUNT(*) FROM clientes 
            WHERE date(ultima_interacao) = ?
        """, (hoje,))
        novos_clientes = cursor.fetchone()[0]
        
        # Consulta mensagens de hoje
        cursor.execute("""
            SELECT COUNT(*) FROM mensagens 
            WHERE date(timestamp) = ?
        """, (hoje,))
        mensagens_hoje = cursor.fetchone()[0]
        
        # Consulta solicitações de atendimento
        cursor.execute("""
            SELECT COUNT(*) FROM mensagens 
            WHERE date(timestamp) = ? AND precisa_atendimento = 1
        """, (hoje,))
        atendimentos = cursor.fetchone()[0]
        
        conn.close()
        
        # Formata o relatório
        relatorio = {
            "data": hoje,
            "novos_clientes": novos_clientes,
            "mensagens_trocadas": mensagens_hoje,
            "solicitacoes_atendimento": atendimentos,
            "uptime": str(datetime.datetime.now() - app_start_time)
        }
        
        # Envia para o Telegram se solicitado
        if request.args.get("notify") == "true":
            mensagem = (
                f"📊 *Relatório Diário - {hoje}*\n\n"
                f"• Novos clientes: {novos_clientes}\n"
                f"• Mensagens trocadas: {mensagens_hoje}\n"
                f"• Solicitações de atendimento: {atendimentos}\n\n"
                f"🚢 *Travessia dos Sonhos* - Bot de Atendimento"
            )
            
            telegram_service.enviar_mensagem_urgente(mensagem, None, None)
        
        return jsonify(relatorio), 200
    except Exception as e:
        capturar_erro("daily_stats", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    registrar_log("info", "Iniciando Bot da Travessia dos Sonhos...")
    print("Iniciando Bot da Travessia dos Sonhos...")
    print(f"Data e hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Usar a porta definida pelo Render ou 5000 como fallback
    port = int(os.environ.get("PORT", 5000))
    print(f"Iniciando na porta: {port}")
    
    # Iniciando o app com a porta correta e debug=False para produção
    app.run(debug=False, host="0.0.0.0", port=port)