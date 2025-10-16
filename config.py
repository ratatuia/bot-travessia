import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do bot
BOT_NAME = "Travessia dos Sonhos"
LOGO_URL = "https://res.cloudinary.com/dejuykey4/image/upload/v1744305156/Imagem_do_WhatsApp_de_2025-03-30_%C3%A0_s_12.03.57_889f472b_xziked.jpg"
TWILIO_WHATSAPP = "whatsapp:+14155238886"
HORARIO_ATENDIMENTO = "Segunda a sexta: 9h às 20h\nSábados: 9h às 18h"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = "-1002535493280"

# Mensagens divertidas para respostas fora do padrão
RESPOSTAS_INVALIDAS = [
    "🤔 Hmm, não encontrei essa opção no cardápio de bordo! Por favor, escolha uma das opções disponíveis.",
    "😅 Parece que estamos em mares diferentes! Pode escolher uma das opções numeradas?",
    "🧭 Precisamos seguir a rota planejada! Por favor, selecione uma das opções acima.",
    "🚢 Nossa bússola está apontando para as opções numeradas! Pode escolher uma delas?",
    "✨ Que criatividade! Mas para seguirmos viagem, precisamos de uma das opções listadas.",
    "🌊 Ops! Essa resposta caiu no mar. Vamos tentar novamente com uma das opções numeradas?"
]

# Configuração do banco de dados
DB_PATH = "travessia_bot.db"

# Menus interativos - VERSÃO OTIMIZADA
MENUS = {
    "principal": {
        "titulo": "✨ Bem-vindo à Travessia dos Sonhos, {nome}! ✨",
        "subtitulo": "Transformando sonhos em viagens inesquecíveis! 🚢",
        "pergunta": "O que você gostaria de fazer hoje?",
        "opcoes": [
            "🎯 Descobrir meu cruzeiro ideal - Vamos encontrar a viagem perfeita pra você!",
            "🌊 Conhecer a Travessia - Saiba por que +500 famílias confiaram em nós",
            "💬 Falar com especialista - Atendimento personalizado agora"
        ],
        "rodape": "\n💡 Dica: Digite 'menu' a qualquer momento para voltar aqui!"
    },

    # NOVO: Qualificação inicial em 1 etapa só
    "qualificacao_inicial": {
        "titulo": "🎯 Vamos descobrir seu cruzeiro ideal!\n\n━━━━━━━━━━ 1/5",
        "subtitulo": "Pra te mostrar as MELHORES opções, preciso saber:",
        "pergunta": (
            "📊 Me conta:\n\n"
            "• Quantas pessoas vão viajar?\n"
            "• Orçamento aproximado por pessoa? (ex: 5 mil)\n"
            "• Quando pretende viajar? (ex: julho 2025)\n\n"
            "💬 Pode escrever tudo numa mensagem mesmo!"
        )
    },

    # COMBINADO: Interesses + Destino
    "experiencia_desejada": {
        "titulo": "✨ Que tipo de experiência você busca?\n\n━━━━━━━━━━ 2/5",
        "subtitulo": "🔥 73% dos nossos clientes escolhem Caribe + Gastronomia!",
        "opcoes": [
            "🍽️ Gastronomia + Destinos exóticos (Caribe, Bahamas)",
            "🎭 Entretenimento + Diversão (Shows, festas, cassino)",
            "🧖‍♂️ Relaxamento total (Spa, piscinas, muito descanso)",
            "👨‍👩‍👧‍👦 Família (Atividades para todas as idades)",
            "🌍 Cultura e história (Europa, Mediterrâneo)",
            "✨ Quero TUDO! Experiência completa!"
        ]
    },

    # COMBINADO: Período + Duração
    "quando_quanto_tempo": {
        "titulo": "🗓️ Quando e por quanto tempo?\n\n━━━━━━━━━━ 3/5",
        "subtitulo": "⚡ ATENÇÃO: Promoções para 2025 acabando rápido!",
        "opcoes": [
            "🏃‍♂️ Em breve + Mini (3-5 dias) - Escapada rápida!",
            "☀️ Meio do ano + Padrão (6-9 dias) - Equilíbrio perfeito",
            "🎆 Final do ano + Estendido (10-14 dias) - Fim de ano épico!",
            "❄️ Próximo ano + Padrão (6-9 dias) - Planejamento tranquilo",
            "🤔 Ainda não decidi - Me ajuda a escolher!"
        ]
    },

    "forma_contato": {
        "titulo": "📱 Como prefere que nossa equipe entre em contato?\n\n━━━━━━━━━━ 4/5",
        "opcoes": [
            "💬 WhatsApp (mais rápido)",
            "📞 Ligação telefônica",
            "📹 Vídeo-chamada (ideal para ver detalhes do navio)"
        ]
    },

    "horario_contato": {
        "titulo": "🕒 Qual o MELHOR horário pra te ligar?\n\n━━━━━━━━━━ 5/5 - Última pergunta!",
        "subtitulo": "💡 Assim evitamos te pegar num momento ruim! 😅",
        "opcoes": [
            "🌅 Manhã (9h-12h)",
            "☕ Horário de almoço (12h-14h)",
            "☀️ Tarde (14h-18h)",
            "🌙 Noite (18h-20h)",
            "✨ Qualquer horário - estou ansioso(a)!"
        ],
        "rodape": f"\n📍 Atendimento: {HORARIO_ATENDIMENTO}"
    }
}

# Templates de mensagens - VERSÃO WORLD-CLASS
MENSAGENS = {
    "boas_vindas": (
        "🌊✨ *Travessia dos Sonhos* ✨🌊\n\n"
        "Imagine acordar numa cidade DIFERENTE a cada dia,\n"
        "sem desfazer malas... 🧳\n\n"
        "É isso que fazemos REALIDADE! 🚢\n\n"
        "✍️ Pra começar, qual seu *nome*?"
    ),

    "pedir_email": (
        "📧 Perfeito, {nome}!\n\n"
        "Vou te enviar uma proposta personalizada por email.\n\n"
        "Qual seu *e-mail*?"
    ),

    "email_invalido": (
        "🤔 {nome}, esse e-mail parece estar incorreto.\n\n"
        "Confere pra mim? (exemplo: seu@email.com)"
    ),

    "atendimento_solicitado": (
        "🎉 *TUDO CERTO, {nome}!*\n\n"
        "✅ Sua solicitação foi registrada\n"
        "✅ Proposta será enviada para {email}\n"
        "✅ Especialista entrará em contato em breve\n\n"
        "📞 Atendimento: {horario}\n\n"
        "💡 *Enquanto isso:*\n"
        "• Visite nosso Instagram @travessiadossonhos\n"
        "• Veja depoimentos de clientes felizes\n"
        "• Confira promoções no site\n\n"
        "Nos vemos em breve! 🚢✨"
    ),

    "apresentacao_empresa": (
        "🌊 Olá {nome}!\n\n"
        "*Sabe aquele sonho de viajar sem estresse?*\n\n"
        "É isso que a Travessia dos Sonhos faz!\n\n"
        "🏆 *Por que somos diferentes:*\n\n"
        "✅ *+500 famílias* já realizaram sonho conosco\n"
        "⭐ *4.9/5 estrelas* no Google (veja depoimentos!)\n"
        "🎯 *100% especialistas* em cruzeiros\n"
        "💎 *Suporte 24/7* durante SUA viagem\n"
        "💰 *Melhores condições* de pagamento\n\n"
        "📍 Atibaia/SP • CNPJ: 48.814.173/0001-70\n"
        "🛟 Certificado CADASTUR\n"
        "🌐 travessiadossonhos.com.br\n"
        "📸 @travessiadossonhos\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Você já fez algum cruzeiro antes?*\n\n"
        "1️⃣ Sim, sou veterano! 🎖️\n"
        "2️⃣ Não, será minha primeira vez 🎉"
    ),

    "resposta_veterano": (
        "👑 *VETERANO A BORDO!*\n\n"
        "{nome}, então você já sabe o que é bom!\n\n"
        "Me conta: o que NÃO pode faltar no seu próximo cruzeiro?\n"
        "(Pode escrever livremente ou escolher do menu)"
    ),

    "resposta_primeira_vez": (
        "🎉 *QUE EMOÇÃO!*\n\n"
        "{nome}, sua primeira vez! Vai ser INESQUECÍVEL!\n\n"
        "💡 *Sabia que:*\n"
        "• Um cruzeiro é tipo um *resort FLUTUANTE*\n"
        "• Você visita *vários destinos* sem desfargar malas\n"
        "• *Tudo incluído*: comida, shows, atividades\n\n"
        "Bora descobrir o cruzeiro perfeito pra você! 🚢"
    ),

    "resumo_preferencias": (
        "📊 *RESUMO DAS SUAS PREFERÊNCIAS:*\n\n"
        "👥 Pessoas: {pessoas}\n"
        "💰 Orçamento: {orcamento}\n"
        "📅 Período: {periodo}\n"
        "🎯 Experiência: {experiencia}\n"
        "⏱️ Duração: {duracao}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎁 Com base nisso, temos *3 opções INCRÍVEIS* pra você!\n\n"
        "Um especialista vai te mostrar:\n"
        "• Fotos e vídeos dos navios\n"
        "• Roteiros detalhados\n"
        "• Condições exclusivas de pagamento\n\n"
        "Está tudo certinho? ✅"
    ),

    "resposta_pesquisa": (
        "Sem problemas, {nome}! 😊\n\n"
        "Quando quiser retomar, é só digitar *'menu'*\n\n"
        "Estaremos aqui pra transformar seu sonho em realidade! 🚢✨"
    ),

    "necessita_nome": (
        "Para {acao}, precisamos primeiro de suas informações.\n\n"
        "Por favor, escreva *'oi'* para começarmos! 🚢"
    ),

    "erro_tecnico": (
        "⚠️ Ops {nome}, um mar de dados nos confundiu!\n\n"
        "Pode tentar novamente? 😅"
    ),

    "consultor_especialista": (
        "🎯 Ótima pergunta, {nome}!\n\n"
        "Nosso especialista vai te explicar isso melhor.\n\n"
        "📞 Atendimento: {horario}\n\n"
        "💬 Já registrei sua dúvida aqui!"
    ),

    # NOVOS: Comandos de navegação
    "comando_menu": (
        "🏠 *MENU PRINCIPAL*\n\n"
        "Escolha uma opção:\n\n"
        "1️⃣ Retomar de onde parei\n"
        "2️⃣ Recomeçar do início\n"
        "3️⃣ Falar com especialista agora"
    ),

    "comando_resumo": (
        "📊 *SEU PROGRESSO*\n\n"
        "{resumo}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Quer continuar de onde parou? 🚢"
    )
}

# Base de conhecimento - MELHORADA
BASE_CONHECIMENTO = {
    "Informações sobre cruzeiros": (
        "💡 Um cruzeiro é tipo um RESORT FLUTUANTE! Você tem:\n\n"
        "✅ Hospedagem de hotel 5 estrelas\n"
        "✅ Todas as refeições incluídas\n"
        "✅ Shows e entretenimento\n"
        "✅ Visita a vários destinos\n"
        "✅ SEM desfazer malas!\n\n"
        "🎯 É a forma mais PRÁTICA e ECONÔMICA de conhecer vários lugares!"
    ),

    "Cabines": (
        "🏨 TIPOS DE CABINES:\n\n"
        "• *Interna* (R$ 3.500+) - Sem janela, ideal pra quem passa o dia fora\n"
        "• *Externa* (R$ 4.500+) - Com janela, luz natural\n"
        "• *Varanda* (R$ 6.500+) - Área privativa, café da manhã com vista!\n"
        "• *Suíte* (R$ 10k+) - Luxo total, mordomias VIP\n\n"
        "💡 73% dos clientes escolhem Varanda - melhor custo-benefício!"
    ),

    "Valores": (
        "💰 VALORES APROXIMADOS (por pessoa):\n\n"
        "🌴 *Caribe/Bahamas (7 dias)*\n"
        "  R$ 4.500 a R$ 15.000\n\n"
        "🏛️ *Mediterrâneo (10 dias)*\n"
        "  R$ 7.000 a R$ 25.000\n\n"
        "🇧🇷 *Costa Brasileira (5 dias)*\n"
        "  R$ 3.000 a R$ 8.000\n\n"
        "⚡ PROMOÇÃO: Parcelamento em até 10x sem juros!\n\n"
        "💡 Quanto antes reservar, MELHORES os preços!"
    ),

    "Destinos populares": (
        "🌎 TOP 5 DESTINOS (clientes Travessia):\n\n"
        "1️⃣ *Caribe* (40%) - Praias paradisíacas\n"
        "2️⃣ *Mediterrâneo* (30%) - História e cultura\n"
        "3️⃣ *Brasil* (15%) - Litoral brasileiro\n"
        "4️⃣ *Europa* (10%) - Cidades icônicas\n"
        "5️⃣ *América do Sul* (5%) - Patagônia, Antártica\n\n"
        "🔥 Caribe é SEMPRE sucesso!"
    ),

    "Temporadas": (
        "🗓️ MELHORES ÉPOCAS:\n\n"
        "🌴 *Caribe*: Ano todo! (alta: Dez-Mar)\n"
        "☀️ *Mediterrâneo*: Abr-Out (verão europeu)\n"
        "🇧🇷 *Brasil*: Nov-Mar (verão)\n"
        "❄️ *Alasca*: Mai-Set (só nessa época!)\n\n"
        "💡 Fora de temporada = preços MELHORES!"
    ),

    "Documentação": (
        "📄 DOCUMENTOS NECESSÁRIOS:\n\n"
        "✅ *Passaporte* válido (6+ meses)\n"
        "✅ *Visto* (alguns destinos exigem)\n"
        "✅ *Vacinas* (ex: febre amarela pra alguns países)\n\n"
        "💡 Nós te ajudamos com TUDO isso!"
    ),

    "Alimentação": (
        "🍽️ GASTRONOMIA A BORDO:\n\n"
        "✅ *Buffet principal* - 24h, ILIMITADO!\n"
        "✅ *Restaurantes temáticos* - Italiano, Japonês, Steakhouse\n"
        "✅ *Room service* - Jantar na cabine\n"
        "✅ *Cafés e lanchonetes* - Lanches o dia todo\n\n"
        "💎 Alguns restaurantes premium cobram taxa extra\n\n"
        "🔥 Clientes falam: 'Voltei 5kg mais gordo!' 😂"
    ),

    "Melhor época": (
        "⏰ *QUANDO RESERVAR:*\n\n"
        "🎯 6-12 meses de antecedência:\n"
        "  • Melhores cabines disponíveis\n"
        "  • Promoções early bird\n"
        "  • Mais tempo pra pagar\n\n"
        "⚡ Último minuto (30-60 dias):\n"
        "  • Preços MUITO bons\n"
        "  • Mas escolha limitada\n\n"
        "💡 Ideal: Reservar com 6+ meses!"
    )
}

# NOVO: Palavras-chave para comandos especiais
COMANDOS_ESPECIAIS = {
    "menu": ["menu", "voltar", "inicio", "começar"],
    "resumo": ["resumo", "progresso", "onde estou"],
    "ajuda": ["ajuda", "help", "socorro", "?"],
    "contato": ["falar", "atendimento", "humano", "especialista"]
}

# NOVO: Emojis de progresso
def get_progresso(passo_atual, total_passos=5):
    """Retorna barra de progresso visual"""
    completo = "━" * passo_atual
    vazio = "━" * (total_passos - passo_atual)
    return f"{completo}{vazio} {passo_atual}/{total_passos}"

# NOVO: Detecta comandos especiais na mensagem do usuário
def detectar_comando(mensagem):
    """
    Verifica se a mensagem contém um comando especial

    Args:
        mensagem: Texto da mensagem do usuário

    Returns:
        str ou None: Nome do comando detectado ou None
    """
    mensagem_lower = mensagem.lower().strip()

    for comando, palavras_chave in COMANDOS_ESPECIAIS.items():
        if mensagem_lower in palavras_chave:
            return comando

    return None
