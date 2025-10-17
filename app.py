from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from twilio.twiml.messaging_response import MessagingResponse
import random
import datetime
import json
import traceback
import os
import psutil
import sqlite3
import shutil

# Variável global para rastrear quando o bot foi iniciado
app_start_time = datetime.datetime.now()

# Importações dos módulos do projeto
from config import LOGO_URL, HORARIO_ATENDIMENTO, RESPOSTAS_INVALIDAS, MENUS, MENSAGENS, BASE_CONHECIMENTO, DB_PATH
from database import init_db, get_client_state, update_client_state, save_message
from telegram_service import TelegramService
from openai_service import AIService
from log_service import registrar_log, capturar_erro

# Importações de segurança
from security import (
    require_api_key,
    require_twilio_signature,
    sanitize_text,
    validate_email as security_validate_email,
    validate_name,
    validate_phone_number,
    validate_menu_option as security_validate_menu,
    add_security_headers,
    mask_sensitive_data
)

# Inicialização
app = Flask(__name__)
init_db()  # Inicializa o banco de dados
telegram_service = TelegramService()
ai_service = AIService()

# Registrar Blueprint do Dashboard
from dashboard_routes import dashboard_bp
app.register_blueprint(dashboard_bp)

# Configuração de Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Adiciona headers de segurança a todas as respostas
@app.after_request
def after_request_func(response):
    return add_security_headers(response)

# ADICIONE A ROTA RAIZ AQUI
@app.route("/", methods=["GET"])
def index():
    return "Bot da Travessia dos Sonhos - Online!", 200

# Funções auxiliares
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

# Rota para reset do banco de dados (PROTEGIDA)
@app.route("/reset-db", methods=["POST"])
@require_api_key
@limiter.limit("5 per day")
def reset_database():
    """
    ENDPOINT PROTEGIDO: Requer API Key no header Authorization
    Uso: curl -X POST -H "Authorization: Bearer YOUR_API_KEY" https://seu-app.onrender.com/reset-db
    """
    try:
        registrar_log("warning", "Solicitação de reset do banco de dados recebida")

        if os.path.exists(DB_PATH):
            # Backup antes de deletar
            backup_path = f"{DB_PATH}.backup.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(DB_PATH, backup_path)
            registrar_log("info", f"Backup criado em: {backup_path}")

            os.remove(DB_PATH)

        init_db()
        registrar_log("info", "Banco de dados reiniciado com sucesso")

        return jsonify({
            "success": True,
            "message": "Banco de dados reiniciado com sucesso",
            "backup": backup_path if os.path.exists(DB_PATH) else None
        }), 200
    except Exception as e:
        capturar_erro("reset_database", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Rota de diagnóstico (PROTEGIDA)
@app.route("/debug-state", methods=["GET"])
@require_api_key
@limiter.limit("30 per hour")
def debug_state():
    """
    ENDPOINT PROTEGIDO: Requer API Key no header Authorization
    Uso: curl -H "Authorization: Bearer YOUR_API_KEY" "https://seu-app.onrender.com/debug-state?phone=whatsapp:+5511999999999"
    """
    try:
        phone = request.args.get("phone")
        if not phone:
            return jsonify({
                "error": "Parâmetro 'phone' é obrigatório"
            }), 400

        # Valida formato do telefone
        if not validate_phone_number(phone):
            return jsonify({
                "error": "Formato de telefone inválido. Use: whatsapp:+5511999999999"
            }), 400

        state = get_client_state(phone)

        # Mascara dados sensíveis antes de retornar
        if state and isinstance(state, dict):
            if 'email' in state:
                state['email'] = mask_sensitive_data(state['email'])

        return jsonify({
            "phone": phone,
            "state": state
        }), 200
    except Exception as e:
        capturar_erro("debug_state", e)
        return jsonify({
            "error": str(e)
        }), 500

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

# Rota principal do bot (PROTEGIDA COM VALIDAÇÃO TWILIO)
@app.route("/zap", methods=["POST"])
@limiter.limit("100 per hour")  # Rate limit por IP
# @require_twilio_signature  # TEMPORARIAMENTE DESABILITADO para debug
def whatsapp_bot():
    # Logs de debug (mascarando dados sensíveis)
    print("====== NOVA REQUISIÇÃO WEBHOOK ======")
    registrar_log("info", f"Nova requisição webhook de {request.headers.get('X-Forwarded-For', request.remote_addr)}")

    # Extrai informações da requisição
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    # Sanitiza entrada do usuário
    incoming_msg = sanitize_text(incoming_msg, max_length=500)

    # Valida formato do telefone
    if not validate_phone_number(sender):
        registrar_log("warning", f"Número de telefone inválido: {mask_sensitive_data(sender)}")
        resp = MessagingResponse()
        resp.message("Desculpe, ocorreu um erro com seu número de telefone.")
        return str(resp)
    
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

    # NOVO: Detecta comandos especiais a qualquer momento
    from config import COMANDOS_ESPECIAIS, detectar_comando
    comando_detectado = detectar_comando(mensagem)

    if comando_detectado == "menu" and nome:
        print("[DEBUG] Comando 'menu' detectado")
        novo_estado = {**estado_atual, "estado": "menu"}
        resposta = formatar_menu("principal", nome)
        return resposta, novo_estado, {}

    elif comando_detectado == "resumo" and nome:
        print("[DEBUG] Comando 'resumo' detectado")
        # Gera resumo do que foi coletado até agora
        resumo_texto = "📋 *Resumo da sua viagem até agora:*\n\n"

        mapeamento = {
            "experiencia_previa": "Experiência prévia",
            "interesse_principal": "Interesse",
            "periodo_viagem": "Período",
            "duracao": "Duração",
            "destino": "Destino",
            "metodo_contato": "Contato preferido",
            "horario_contato": "Horário preferido"
        }

        tem_dados = False
        for campo, label in mapeamento.items():
            if campo in estado_atual and estado_atual[campo]:
                resumo_texto += f"✅ {label}: {estado_atual[campo]}\n"
                tem_dados = True

        if not tem_dados:
            resumo_texto += "Ainda não coletamos informações sobre sua viagem.\n"

        resumo_texto += "\n💬 Digite *menu* para ver as opções ou continue de onde parou!"

        return resumo_texto, estado_atual, {}

    elif comando_detectado == "ajuda":
        print("[DEBUG] Comando 'ajuda' detectado")
        resposta = MENSAGENS.get("ajuda_comandos",
            "💡 *Comandos disponíveis:*\n\n"
            "• *menu* - Ver menu principal\n"
            "• *resumo* - Ver dados coletados\n"
            "• *ajuda* - Ver esta mensagem\n"
            "• *contato* - Falar com especialista"
        )
        return resposta, estado_atual, {}

    elif comando_detectado == "contato":
        print("[DEBUG] Comando 'contato' detectado - redireciona para atendimento")
        novo_estado = {**estado_atual, "estado": "atendimento_solicitado"}
        email = estado_atual.get("email", "seu email cadastrado")
        resposta = MENSAGENS["atendimento_solicitado"].format(
            nome=nome if nome else "Olá",
            email=email,
            horario=HORARIO_ATENDIMENTO
        )
        return resposta, novo_estado, {"tipo_msg": "urgente"}

    # Verifica se o cliente já solicitou atendimento
    if estado == "atendimento_solicitado":
        print("[DEBUG] Cliente em estado de atendimento solicitado")
        # Se o cliente já solicitou atendimento, reenviar a mensagem de confirmação
        # apenas se ele enviar um novo comando de atendimento
        if mensagem == "3" or mensagem.lower() in ["atendimento", "ajuda", "especialista", "falar"]:
            email = estado_atual.get("email", "seu email cadastrado")
            resposta = MENSAGENS["atendimento_solicitado"].format(
                nome=nome,
                email=email,
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
    
    # Processamento baseado no estado
    if estado == "aguardando_nome":
        print("[DEBUG] Processando aguardando_nome")

        # Sanitiza e valida o nome
        nome_sanitizado = sanitize_text(mensagem, max_length=100)

        if not validate_name(nome_sanitizado):
            print("[DEBUG] Nome inválido")
            resposta = (
                "Por favor, informe um nome válido contendo apenas letras e espaços. "
                "Evite números ou caracteres especiais."
            )
            return resposta, estado_atual, {}

        # Captura o nome válido
        novo_estado = {"nome": nome_sanitizado, "estado": "aguardando_email"}
        resposta = MENSAGENS["pedir_email"].format(nome=nome_sanitizado)
        return resposta, novo_estado, {}
        
    elif estado == "aguardando_email":
        print("[DEBUG] Processando aguardando_email")

        # Sanitiza email
        email_sanitizado = sanitize_text(mensagem, max_length=254).lower()

        # Valida email com função de segurança aprimorada
        if not security_validate_email(email_sanitizado):
            print("[DEBUG] Email inválido")
            resposta = MENSAGENS["email_invalido"].format(nome=nome)
            return resposta, estado_atual, {}

        print("[DEBUG] Email válido")
        novo_estado = {
            "nome": nome,
            "email": email_sanitizado,
            "estado": "menu"
        }

        resposta = formatar_menu("principal", nome)
        telegram_service.atualizar_perfil(sender, "Email", email_sanitizado)

        return resposta, novo_estado, {}
        
    elif estado == "menu":
        print("[DEBUG] Processando menu")
        # Processa opções do menu principal
        if mensagem == "1":  # Descobrir cruzeiro ideal (CORRIGIDO)
            print("[DEBUG] Opção 1 selecionada - Descobrir cruzeiro ideal")
            novo_estado = {**estado_atual, "estado": "qualificacao_inicial"}
            # Formata a nova pergunta combinada usando MENUS (não MENSAGENS)
            resposta = formatar_menu("qualificacao_inicial", nome)
            return resposta, novo_estado, {}

        elif mensagem == "2":  # Conhecer a Travessia (CORRIGIDO)
            print("[DEBUG] Opção 2 selecionada - Conhecer a Travessia")
            novo_estado = {**estado_atual, "estado": "pos_conhecer_tripulacao"}
            resposta = MENSAGENS["apresentacao_empresa"].format(nome=nome)
            return resposta, novo_estado, {}

        elif mensagem == "3":  # Solicitar atendimento
            print("[DEBUG] Opção 3 selecionada")
            novo_estado = {**estado_atual, "estado": "atendimento_solicitado"}
            email = estado_atual.get("email", "seu email cadastrado")
            resposta = MENSAGENS["atendimento_solicitado"].format(
                nome=nome,
                email=email,
                horario=HORARIO_ATENDIMENTO
            )
            # Aqui metadados indicam que é uma mensagem urgente
            return resposta, novo_estado, {"tipo_msg": "urgente"}

        else:
            print("[DEBUG] Opção inválida no menu")
            # Resposta inválida para o menu
            resposta = f"{nome}, {obter_resposta_invalida()}\n\n{formatar_menu('principal', nome)}"
            return resposta, estado_atual, {}
    
    # Estado após conhecer tripulação - NOVO FLUXO
    elif estado == "pos_conhecer_tripulacao":
        print(f"[DEBUG] Processando pos_conhecer_tripulacao, mensagem: '{mensagem}'")
        # Valida opção (1 ou 2: veterano ou primeira vez)
        opcao, valida = validar_opcao_menu(mensagem, 2)

        if not valida:
            print("[DEBUG] Opção inválida")
            resposta = f"{nome}, {obter_resposta_invalida()}\n\nVocê já fez algum cruzeiro antes?\n\n1️⃣ Sim, sou veterano! 🎖️\n2️⃣ Não, será minha primeira vez 🎉"
            return resposta, estado_atual, {}

        # Registra a experiência prévia
        experiencia = "Veterano" if opcao == 1 else "Primeira vez"
        print(f"[DEBUG] Experiência: {experiencia}")

        # Atualiza Telegram
        telegram_service.atualizar_perfil(sender, "Experiência prévia", experiencia)

        # Vai direto para qualificação inicial
        novo_estado = {
            **estado_atual,
            "estado": "qualificacao_inicial",
            "experiencia_previa": experiencia
        }

        # Resposta depende se é veterano ou primeira vez
        if opcao == 1:
            resposta_inicial = MENSAGENS.get("resposta_veterano", "Ótimo! Então você já sabe o que é bom!").format(nome=nome)
        else:
            resposta_inicial = MENSAGENS.get("resposta_primeira_vez", "Que emoção! Sua primeira vez será inesquecível!").format(nome=nome)

        # Adiciona a pergunta de qualificação (usa formatar_menu pois está em MENUS)
        menu_qualif = formatar_menu("qualificacao_inicial", nome)
        resposta = f"{resposta_inicial}\n\n{menu_qualif}"

        print("[DEBUG] Indo para qualificacao_inicial")
        return resposta, novo_estado, {}
    
    # NOVO: Estado de qualificação inicial (combina pessoas + orçamento + quando)
    elif estado == "qualificacao_inicial":
        print("[DEBUG] Processando qualificacao_inicial com IA")
        try:
            # Usa IA para extrair informações da resposta livre
            prompt_extracao = f"""
Analise esta mensagem do cliente e extraia 3 informações:
1. Número de pessoas que vão viajar
2. Orçamento aproximado POR PESSOA (em reais)
3. Quando pretende viajar (mês/período)

IMPORTANTE sobre o orçamento:
- Se o cliente diz "10 mil" ou "10000", assuma que é o orçamento POR PESSOA
- NÃO divida o valor pelo número de pessoas
- Se o cliente diz "10 mil para 2 pessoas", então divida (10.000 / 2 = 5.000 por pessoa)
- Se não especificar "total" ou "para X pessoas", considere o valor como sendo por pessoa

Mensagem do cliente: "{mensagem}"

Responda APENAS no formato JSON:
{{"pessoas": "X pessoas", "orcamento": "R$ X.000", "quando": "mês/ano"}}

Exemplos:
- "2 pessoas, 10 mil, janeiro 2026" → {{"pessoas": "2 pessoas", "orcamento": "R$ 10.000", "quando": "janeiro 2026"}}
- "somos 4, orçamento 5000 cada, dezembro" → {{"pessoas": "4 pessoas", "orcamento": "R$ 5.000", "quando": "dezembro"}}

Se alguma informação não estiver clara, use "Não especificado".
"""
            resposta_ia = ai_service.gerar_resposta_simples(prompt_extracao)
            print(f"[DEBUG] Resposta IA: {resposta_ia}")

            # Tenta parsear JSON
            try:
                dados = json.loads(resposta_ia)
                pessoas = dados.get("pessoas", "Não especificado")
                orcamento = dados.get("orcamento", "Não especificado")
                quando = dados.get("quando", "Não especificado")
            except:
                # Fallback se JSON não parseou
                pessoas = "Não especificado"
                orcamento = "Não especificado"
                quando = "Não especificado"

            # Salva no estado
            novo_estado = {
                **estado_atual,
                "estado": "experiencia_desejada",
                "num_pessoas": pessoas,
                "orcamento_pp": orcamento,
                "periodo_desejado": quando
            }

            # Atualiza Telegram
            telegram_service.atualizar_perfil(sender, "Pessoas", pessoas)
            telegram_service.atualizar_perfil(sender, "Orçamento p/pessoa", orcamento)
            telegram_service.atualizar_perfil(sender, "Quando viajar", quando)

            # Próxima pergunta: experiência desejada (combina interesses + destino)
            resposta = (
                f"✅ Ótimo, {nome}!\n\n"
                f"📊 Entendi:\n"
                f"• {pessoas}\n"
                f"• Orçamento: {orcamento}\n"
                f"• Período: {quando}\n\n"
                f"─────────────\n\n"
                f"{formatar_menu('experiencia_desejada', nome)}"
            )

            return resposta, novo_estado, {}

        except Exception as e:
            print(f"[ERRO] Erro ao processar qualificacao_inicial: {e}")
            # Fallback: pede para reformular
            resposta = (
                f"{nome}, não consegui entender todas as informações. "
                f"Pode me dizer de forma mais clara:\n\n"
                f"• Quantas pessoas?\n"
                f"• Orçamento por pessoa?\n"
                f"• Quando pretende viajar?"
            )
            return resposta, estado_atual, {}

    # NOVO: Estado de experiência desejada (combina interesses + destino)
    elif estado == "experiencia_desejada":
        print("[DEBUG] Processando experiencia_desejada")
        # Aqui podemos usar IA para entender resposta livre ou aceitar múltiplas escolhas
        # Por simplicidade, vou aceitar resposta livre e passar para próximo passo

        novo_estado = {
            **estado_atual,
            "estado": "quando_quanto_tempo",
            "interesse_descricao": mensagem
        }

        # Atualiza Telegram
        telegram_service.atualizar_perfil(sender, "Interesses", mensagem[:100])

        # Próxima pergunta: quando e quanto tempo
        resposta = formatar_menu("quando_quanto_tempo", nome)

        return resposta, novo_estado, {}

    # NOVO: Estado de quando e quanto tempo (combina período + duração)
    elif estado == "quando_quanto_tempo":
        print("[DEBUG] Processando quando_quanto_tempo")
        # Extrai informações com IA
        try:
            prompt_extracao = f"""
Analise esta mensagem e extraia:
1. Quando a pessoa quer viajar (mês/período)
2. Quantos dias de viagem

Mensagem: "{mensagem}"

Responda APENAS JSON:
{{"quando": "período", "duracao": "X dias"}}
"""
            resposta_ia = ai_service.gerar_resposta_simples(prompt_extracao)

            try:
                dados = json.loads(resposta_ia)
                quando = dados.get("quando", mensagem)
                duracao = dados.get("duracao", "Não especificado")
            except:
                quando = mensagem
                duracao = "Não especificado"

            # Salva e vai para solicitação de contato
            novo_estado = {
                **estado_atual,
                "estado": "perguntando_forma_contato",
                "periodo_final": quando,
                "duracao_final": duracao
            }

            telegram_service.atualizar_perfil(sender, "Período final", quando)
            telegram_service.atualizar_perfil(sender, "Duração", duracao)

            # Pergunta forma de contato
            resposta = f"🎯 Perfeito, {nome}! {formatar_menu('forma_contato')}"

            return resposta, novo_estado, {}

        except Exception as e:
            print(f"[ERRO] Erro ao processar quando_quanto_tempo: {e}")
            # Vai para próximo mesmo assim
            novo_estado = {
                **estado_atual,
                "estado": "perguntando_forma_contato",
                "periodo_final": mensagem,
                "duracao_final": "Não especificado"
            }
            resposta = f"✅ Anotado! {formatar_menu('forma_contato')}"
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

        # Total de clientes
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = cursor.fetchone()[0]

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

        # Clientes em atendimento pendente
        cursor.execute("""
            SELECT COUNT(*) FROM clientes
            WHERE estado = 'atendimento_solicitado'
        """)
        atendimentos_pendentes = cursor.fetchone()[0]

        # Taxa de conversão
        conversion_rate = (atendimentos_pendentes / total_clientes * 100) if total_clientes > 0 else 0

        conn.close()

        # Formata o relatório
        relatorio = {
            "data": hoje,
            "novos_clientes": novos_clientes,
            "total_clientes": total_clientes,
            "mensagens_trocadas": mensagens_hoje,
            "solicitacoes_atendimento": atendimentos,
            "atendimentos_pendentes": atendimentos_pendentes,
            "conversion_rate": conversion_rate,
            "uptime": str(datetime.datetime.now() - app_start_time)
        }

        # Envia para o Telegram se solicitado
        if request.args.get("notify") == "true":
            stats = {
                "clients_24h": novos_clientes,
                "total_clients": total_clientes,
                "messages_24h": mensagens_hoje,
                "conversion_rate": conversion_rate,
                "atendimentos_pendentes": atendimentos_pendentes
            }
            telegram_service.enviar_relatorio_diario(stats)

        return jsonify(relatorio), 200
    except Exception as e:
        capturar_erro("daily_stats", e)
        return jsonify({"error": str(e)}), 500

# Rota para verificar inatividade
@app.route("/check-inactivity", methods=["GET"])
def check_inactivity():
    """Verifica se não há mensagens há X horas e envia alerta"""
    try:
        horas = int(request.args.get("hours", 12))

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verifica última mensagem
        cursor.execute("""
            SELECT MAX(timestamp) FROM mensagens
        """)
        ultima_mensagem = cursor.fetchone()[0]
        conn.close()

        if not ultima_mensagem:
            # Nunca recebeu mensagens
            telegram_service.enviar_alerta_inatividade(horas)
            return jsonify({
                "inativo": True,
                "mensagem": "Nenhuma mensagem registrada",
                "alerta_enviado": True
            }), 200

        # Calcula tempo desde última mensagem
        ultima = datetime.datetime.fromisoformat(ultima_mensagem)
        agora = datetime.datetime.now()
        tempo_inativo = (agora - ultima).total_seconds() / 3600

        if tempo_inativo >= horas:
            # Envia alerta
            telegram_service.enviar_alerta_inatividade(int(tempo_inativo))
            return jsonify({
                "inativo": True,
                "horas_inativo": round(tempo_inativo, 1),
                "ultima_mensagem": ultima_mensagem,
                "alerta_enviado": True
            }), 200
        else:
            return jsonify({
                "inativo": False,
                "horas_inativo": round(tempo_inativo, 1),
                "ultima_mensagem": ultima_mensagem,
                "alerta_enviado": False
            }), 200

    except Exception as e:
        capturar_erro("check_inactivity", e)
        return jsonify({"error": str(e)}), 500

# Rota para verificar performance
@app.route("/check-performance", methods=["GET"])
def check_performance():
    """Verifica métricas de performance e envia alertas se necessário"""
    try:
        from observability import metrics

        # Obter resumo das métricas
        metrics_summary = metrics.get_summary()
        timings = metrics_summary.get('timings', {})
        alertas_enviados = []

        for operacao, data in timings.items():
            avg_ms = data.get('avg_ms', 0)
            if avg_ms > 2000:  # >2 segundos
                telegram_service.enviar_alerta_performance(operacao, avg_ms)
                alertas_enviados.append({
                    "operacao": operacao,
                    "tempo_ms": avg_ms
                })

        return jsonify({
            "alertas_enviados": len(alertas_enviados),
            "detalhes": alertas_enviados
        }), 200

    except Exception as e:
        capturar_erro("check_performance", e)
        return jsonify({"error": str(e)}), 500

# Rota para verificar health
@app.route("/check-health-components", methods=["GET"])
def check_health_components():
    """Verifica saúde dos componentes e envia alertas se necessário"""
    try:
        health = {
            'database': os.path.exists(DB_PATH),
            'logs': os.path.exists('logs/bot.log'),
            'metrics': os.path.exists('logs/metrics.json')
        }

        componentes_com_problema = [k for k, v in health.items() if not v]

        if componentes_com_problema:
            telegram_service.enviar_alerta_health(componentes_com_problema)
            return jsonify({
                "status": "degraded",
                "componentes_com_problema": componentes_com_problema,
                "alerta_enviado": True
            }), 200
        else:
            return jsonify({
                "status": "healthy",
                "componentes_com_problema": [],
                "alerta_enviado": False
            }), 200

    except Exception as e:
        capturar_erro("check_health_components", e)
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