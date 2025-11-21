"""
CÓDIGO EXEMPLO - Funcionalidades Prontas para Integrar

Copie e cole no app.py conforme necessário
"""

from datetime import datetime
from services import LeadScoringService

# ============================================
# 1. PERSONALIZAÇÃO POR HORÁRIO
# ============================================

def obter_saudacao_personalizada(nome):
    """Retorna saudação baseada no horário"""
    hora = datetime.now().hour

    if 5 <= hora < 12:
        return f"☀️ Bom dia, {nome}!"
    elif 12 <= hora < 18:
        return f"🌤️ Boa tarde, {nome}!"
    else:
        return f"🌙 Boa noite, {nome}!"


# ============================================
# 2. BARRA DE PROGRESSO VISUAL
# ============================================

def gerar_barra_progresso(etapa_atual, total_etapas=5):
    """
    Gera barra de progresso visual
    Exemplo: ━━━━●━━━━━ 3/5
    """
    barra = ""
    for i in range(1, total_etapas + 1):
        if i < etapa_atual:
            barra += "━"
        elif i == etapa_atual:
            barra += "●"
        else:
            barra += "━"

    return f"{barra} {etapa_atual}/{total_etapas}"


# Exemplo de uso nos menus
EXEMPLO_MENU_COM_PROGRESSO = f"""
🎯 Vamos descobrir seu cruzeiro ideal!

{gerar_barra_progresso(1, 5)}

📊 Me conta:
• Quantas pessoas vão viajar?
• Orçamento aproximado por pessoa?
• Quando pretende viajar?
"""


# ============================================
# 3. QUIZ DE PERFIL DE VIAJANTE
# ============================================

QUIZ_PERGUNTAS = {
    "quiz_pergunta_1": {
        "pergunta": "🎲 *QUIZ: Descubra seu perfil de viajante!*\n\nPergunta 1/3:\n\n🌟 Qual seu estilo de viagem?",
        "opcoes": [
            "🏖️ Praia e relaxamento total",
            "🏛️ Cultura e história",
            "🎉 Festa e entretenimento",
            "🍽️ Gastronomia e experiências"
        ],
        "proximo_estado": "quiz_pergunta_2"
    },
    "quiz_pergunta_2": {
        "pergunta": "Pergunta 2/3:\n\n💎 Qual seu orçamento ideal?",
        "opcoes": [
            "💰 Econômico (até R$ 4mil)",
            "💎 Intermediário (R$ 4-8mil)",
            "👑 Premium (R$ 8mil+)"
        ],
        "proximo_estado": "quiz_pergunta_3"
    },
    "quiz_pergunta_3": {
        "pergunta": "Pergunta 3/3:\n\n👥 Com quem você viaja?",
        "opcoes": [
            "👨‍👩‍👧 Família com crianças",
            "💑 Casal romântico",
            "👥 Grupo de amigos",
            "🧳 Solo traveler"
        ],
        "proximo_estado": "quiz_resultado"
    }
}

QUIZ_PERFIS = {
    ("praia", "economico", "familia"): {
        "nome": "🌴 FAMÍLIA AVENTUREIRA",
        "descricao": "Vocês adoram praia, diversão e bom custo-benefício!",
        "recomendacao": "Cruzeiro 5 dias no Caribe com atividades para todas as idades"
    },
    ("cultura", "premium", "casal"): {
        "nome": "🎭 CASAL SOFISTICADO",
        "descricao": "Vocês apreciam cultura, gastronomia e conforto!",
        "recomendacao": "Cruzeiro 10 dias no Mediterrâneo com experiências exclusivas"
    },
    # ... adicionar mais combinações
}

def calcular_perfil_quiz(respostas):
    """
    Calcula perfil baseado nas respostas do quiz

    Args:
        respostas: dict com respostas {"quiz_1": "1", "quiz_2": "3", ...}

    Returns:
        dict com perfil
    """
    # Simplificado - você pode fazer mais elaborado
    chave_perfil = (
        "praia" if respostas.get("quiz_1") == "1" else "cultura",
        "economico" if respostas.get("quiz_2") == "1" else "premium",
        "familia" if respostas.get("quiz_3") == "1" else "casal"
    )

    perfil = QUIZ_PERFIS.get(chave_perfil, QUIZ_PERFIS[("praia", "economico", "familia")])

    return f"""
🎊 *SEU PERFIL DE VIAJANTE*

{perfil['nome']}

{perfil['descricao']}

✨ *Recomendação especial:*
{perfil['recomendacao']}

━━━━━━━━━━━━━━━━━━━━

Quer ver opções personalizadas?
Digite 'SIM' para falar com um especialista!
"""


# ============================================
# 4. INTEGRAÇÃO COM LEAD SCORING
# ============================================

def processar_com_lead_scoring(sender, estado_atual, telegram_service):
    """
    Exemplo de como integrar lead scoring no fluxo

    Adicione isso após coletar dados do cliente
    """
    # Calcula score
    score = LeadScoringService.calcular_score(estado_atual)
    prioridade, emoji, descricao = LeadScoringService.get_prioridade(score)

    print(f"[LEAD SCORE] {estado_atual.get('nome')}: {score}/100 - {prioridade}")

    # Envia para Telegram com score
    telegram_service.enviar_conversa(
        sender,
        forcar=(score >= 70),  # Força envio imediato se lead quente
        lead_score=score
    )

    # Alerta especial para leads quentes
    if score >= 70:
        telegram_service.enviar_mensagem_urgente(
            f"🔥🔥🔥 *LEAD QUENTE DETECTADO!*\n\n"
            f"Score: *{score}/100*\n"
            f"Prioridade: *{prioridade}*\n\n"
            f"{descricao}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            nome_cliente=estado_atual.get("nome"),
            numero=sender
        )

    return score


# ============================================
# 5. NOVO FLUXO - EMAIL DEPOIS
# ============================================

NOVO_FLUXO_MENSAGENS = {
    "boas_vindas_v2": (
        "{saudacao}\n\n"  # Personalizado por horário
        "🌊✨ *Travessia dos Sonhos* ✨🌊\n\n"
        "Imagine acordar numa cidade DIFERENTE a cada dia,\n"
        "sem desfazer malas... 🧳\n\n"
        "É isso que fazemos REALIDADE! 🚢\n\n"
        "✍️ Pra começar, qual seu *nome*?"
    ),

    "apos_nome_v2": (
        "{saudacao_personalizada}\n\n"
        "🎯 *Quiz Rápido* - 3 perguntas pra encontrar\n"
        "seu cruzeiro PERFEITO!\n\n"
        "Bora começar? Digite *SIM*"
    ),

    # Email só é pedido DEPOIS do quiz/interesse demonstrado
    "pedir_email_v2": (
        "🎉 Perfeito, {nome}!\n\n"
        "Vou te enviar uma proposta INCRÍVEL por email.\n\n"
        "Qual seu *e-mail*?"
    )
}


# ============================================
# 6. QUICK REPLY BUTTONS (Twilio)
# ============================================

def criar_resposta_com_botoes(mensagem, opcoes):
    """
    NOTA: Quick replies só funcionam com WhatsApp Business API
    (não funciona no Sandbox gratuito do Twilio)

    Para usar, você precisa:
    1. Conta Twilio paga
    2. WhatsApp Business API aprovado
    3. Número próprio do WhatsApp

    Código de exemplo:
    """
    from twilio.twiml.messaging_response import MessagingResponse

    resp = MessagingResponse()
    msg = resp.message(mensagem)

    # Adiciona quick reply buttons
    # NOTA: Isso só funciona com WhatsApp Business API oficial
    for i, opcao in enumerate(opcoes, 1):
        msg.action = [{
            "id": str(i),
            "title": opcao[:20]  # Max 20 caracteres
        }]

    return str(resp)


# ALTERNATIVA: Usar emojis numéricos (funciona em qualquer Twilio)
def criar_menu_visual_melhorado(titulo, opcoes):
    """
    Cria menu bonito com emojis que funciona em qualquer Twilio
    """
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    mensagem = f"{titulo}\n\n"

    for i, opcao in enumerate(opcoes):
        mensagem += f"{emojis[i]} {opcao}\n\n"

    mensagem += "━━━━━━━━━━━━━━━━━━━━\n"
    mensagem += "💡 Digite o número da opção"

    return mensagem


# ============================================
# 7. MEMÓRIA DE CONVERSA ANTERIOR
# ============================================

def verificar_conversa_anterior(telefone, database):
    """
    Verifica se cliente já interagiu antes e personaliza mensagem

    Adicione isso no início do fluxo
    """
    from database import get_client_state

    estado_anterior = get_client_state(telefone)

    if estado_anterior and estado_anterior.get("nome"):
        # Cliente retornando
        nome = estado_anterior.get("nome")
        interesse_anterior = estado_anterior.get("interesse_principal")

        mensagem = f"""
{obter_saudacao_personalizada(nome)}

🎉 *Que bom te ver de novo!*

Lembro que você estava interessado em {interesse_anterior or "cruzeiros"}.

Quer:
1️⃣ Retomar de onde parou
2️⃣ Ver novas opções
3️⃣ Falar com especialista agora

━━━━━━━━━━━━━━━━━━━━
"""
        return True, mensagem
    else:
        # Cliente novo
        return False, None


# ============================================
# 8. EXEMPLO DE INTEGRAÇÃO COMPLETA
# ============================================

def exemplo_processar_mensagem_completo(sender, mensagem, estado_atual, telegram_service):
    """
    Exemplo completo integrando todas as features
    """

    # 1. Verifica se é cliente retornando
    is_retorno, msg_retorno = verificar_conversa_anterior(sender, None)
    if is_retorno:
        return msg_retorno, estado_atual, {}

    # 2. Usa saudação personalizada
    saudacao = obter_saudacao_personalizada(estado_atual.get("nome", ""))

    # 3. Processa normalmente...
    # (seu código atual)

    # 4. Calcula lead score ao final
    if estado_atual.get("estado") == "atendimento_solicitado":
        score = processar_com_lead_scoring(sender, estado_atual, telegram_service)

    # 5. Adiciona barra de progresso nas respostas
    etapa_atual = {
        "aguardando_nome": 1,
        "quiz_pergunta_1": 2,
        "quiz_pergunta_2": 3,
        "quiz_pergunta_3": 4,
        "perguntando_forma_contato": 5
    }.get(estado_atual.get("estado"), 1)

    progresso = gerar_barra_progresso(etapa_atual, 5)

    # ... continua processamento


# ============================================
# 9. TESTES RÁPIDOS
# ============================================

if __name__ == "__main__":
    # Teste saudações
    print(obter_saudacao_personalizada("Rafael"))

    # Teste barra de progresso
    for i in range(1, 6):
        print(gerar_barra_progresso(i, 5))

    # Teste lead scoring
    estado_teste = {
        "orcamento_pp": "R$ 10.000",
        "periodo_desejado": "janeiro 2026",
        "experiencia_previa": "Veterano",
        "num_pessoas": "4 pessoas"
    }
    score = LeadScoringService.calcular_score(estado_teste)
    print(f"\nLead Score: {score}/100")
    print(LeadScoringService.get_prioridade(score))
