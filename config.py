import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do bot
BOT_NAME = "Travessia dos Sonhos"
LOGO_URL = "https://res.cloudinary.com/dejuykey4/image/upload/v1744305156/Imagem_do_WhatsApp_de_2025-03-30_%C3%A0_s_12.03.57_889f472b_xziked.jpg"
TWILIO_WHATSAPP = "whatsapp:+14155238886"  # Número do sandbox do Twilio
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

# Menus interativos
MENUS = {
    "principal": {
        "titulo": "✨ Bem-vindo à Travessia dos Sonhos, {nome}! ✨",
        "subtitulo": "É um prazer tê-lo(a) a bordo! Estamos prontos para transformar seus sonhos de viagem em realidade.",
        "pergunta": "Como podemos auxiliá-lo(a) hoje?",
        "opcoes": [
            "Conheça nossa tripulação - Descubra quem somos e nossa paixão por cruzeiros",
            "Hora de navegar - Planeje sua próxima aventura marítima",
            "Fale com um de nossos especialistas - Atendimento personalizado para suas dúvidas"
        ]
    },
    "interesses": {
        "titulo": "Quais aspectos de um cruzeiro mais chamam sua atenção?",
        "opcoes": [
            "🍽️ Gastronomia (buffets, restaurantes temáticos)",
            "🎭 Entretenimento (shows, cassino, festas)",
            "🌴 Destinos exóticos (praias, cidades históricas)",
            "🧖‍♂️ Relaxamento (spa, piscinas, áreas adultos)",
            "👨‍👩‍👧‍👦 Atividades para família",
            "✨ Tudo isso! Quero a experiência completa!"
        ]
    },
    "periodo_viagem": {
        "titulo": "🗓️ Qual seria o melhor período para sua viagem?",
        "opcoes": [
            "Primeiros meses do ano (Jan-Mar)",
            "Meio do ano (Abr-Jun)",
            "Férias de julho",
            "Segundo semestre (Ago-Out)",
            "Final do ano (Nov-Dez)",
            "Ainda não decidi, quero sugestões!"
        ]
    },
    "duracao": {
        "titulo": "⏱️ Qual seria a duração ideal para seu cruzeiro?",
        "opcoes": [
            "Mini-cruzeiro (3-5 dias)",
            "Cruzeiro padrão (6-9 dias)",
            "Cruzeiro estendido (10-14 dias)",
            "Longa duração (15+ dias)",
            "Ainda não decidi, podem me recomendar?"
        ]
    },
    "destino_regiao": {
        "titulo": "🌎 Qual região mais te interessa para seu próximo cruzeiro?",
        "opcoes": [
            "Brasil",
            "Caribe e Bahamas",
            "Mediterrâneo",
            "Europa e Escandinávia",
            "América do Sul",
            "Alasca",
            "Ásia e Oceania",
            "Outro destino ou não sei decidir ainda"
        ]
    },
    "forma_contato": {
        "titulo": "📱 Qual seria a melhor forma para entrarmos em contato com você?",
        "opcoes": [
            "WhatsApp",
            "Ligação telefônica",
            "Vídeo-chamada"
        ]
    },
    "horario_contato": {
        "titulo": "🕒 Qual seria o melhor horário para este contato?",
        "opcoes": [
            "Manhã (9h-12h)",
            "Horário de almoço (12h-14h)",
            "Tarde (14h-18h)",
            "Noite (18h-20h)",
            "Qualquer horário dentro do nosso funcionamento"
        ],
        "rodape": f"Nosso horário de atendimento: {HORARIO_ATENDIMENTO}"
    }
}

# Templates de mensagens
MENSAGENS = {
    "boas_vindas": "🌊✨ *Travessia dos Sonhos* ✨🌊\nSeja bem-vindo(a) à bordo!\n\n✍️ Pra começarmos, me diga seu *nome*, por favor.",
    "pedir_email": "📧 Agora me diga seu *e-mail*, por favor.",
    "email_invalido": "❌ {nome}, o e-mail informado não parece válido. Por favor, informe um e-mail no formato correto (exemplo@dominio.com).",
    "atendimento_solicitado": "✨ {nome}, sua solicitação foi registrada! Um especialista entrará em contato em breve.\n\nHorário de atendimento: {horario}",
    "apresentacao_empresa": (
        "🌊 Olá {nome}! Somos a Travessia dos Sonhos, agência especializada em cruzeiros marítimos.\n\n"
        "📌 CNPJ: 48.814.173/0001-70\n"
        "🛟 CADASTUR: Agência certificada\n"
        "📍 Localização: Atibaia/SP\n\n"
        "🌐 Site: travessiadossonhos.com.br\n"
        "📸 Instagram: @travessiadossonhos\n\n"
        "Você já teve alguma experiência anterior com cruzeiros marítimos?\n\n"
        "1️⃣ Sim\n"
        "2️⃣ Não, será minha primeira vez"
    ),
    "resposta_pesquisa": "Sem problemas, {nome}! Quando desejar planejar sua viagem, é só nos avisar.\n\nDigite 'menu' para ver as opções novamente quando estiver pronto.",
    "necessita_nome": "Para {acao}, precisamos primeiro de suas informações. Por favor, escreva 'oi' para começarmos.",
    "erro_tecnico": "⚠️ {nome}, desculpe, tivemos um probleminha técnico. Pode tentar novamente em instantes?",
    "consultor_especialista": "🤖 {nome}, essa dúvida será melhor respondida por um especialista. Um consultor entrará em contato em breve ({horario})."
}

# Base de conhecimento
BASE_CONHECIMENTO = {
    "Informações sobre cruzeiros": (
        "Os cruzeiros marítimos são uma forma única de viajar que combina hospedagem, "
        "alimentação, entretenimento e transporte em um único pacote. Durante a viagem, "
        "você pode visitar múltiplos destinos sem precisar desfazer malas."
    ),
    "Cabines": (
        "Os navios oferecem diferentes tipos de cabines: internas (sem janela), "
        "externas (com janela), cabines com varanda e suítes. O preço varia conforme "
        "a categoria, localização e tamanho."
    ),
    "Destinos populares": (
        "Os destinos mais procurados incluem Brasil (costa brasileira), Caribe, Bahamas, Mediterrâneo, Europa, "
        "Alasca, América do Sul e Ásia. Cada região tem sua temporada ideal para navegação."
    ),
    "Temporadas": (
        "Brasil: ano todo (melhor de novembro a março). Mediterrâneo: abril a outubro. "
        "Caribe: ano todo (alta temporada de dezembro a março). "
        "Alasca: maio a setembro. América do Sul: novembro a março."
    ),
    "Duração": (
        "Mini-cruzeiros: 3-5 dias. Cruzeiros padrão: 6-9 dias. Cruzeiros estendidos: 10-14 dias. "
        "Grand Voyages: 15+ dias."
    ),
    "Documentação": (
        "Para cruzeiros internacionais, é necessário passaporte válido (mínimo 6 meses). "
        "Alguns destinos podem exigir visto. Recomendamos verificar requisitos específicos "
        "para cada itinerário."
    ),
    "Alimentação": (
        "Os navios oferecem uma variedade de opções gastronômicas, desde buffets inclusos "
        "até restaurantes de especialidades (alguns com taxa extra). Todas as refeições "
        "principais são incluídas no valor da cabine."
    ),
    "Entretenimento": (
        "A bordo você encontra shows, teatro, música ao vivo, cassino, festas temáticas, "
        "atividades esportivas e muito mais. A programação diária oferece opções para todos os gostos."
    ),
    "Atividades para crianças": (
        "Os navios possuem clubes infantis divididos por faixa etária, com atividades "
        "supervisionadas, piscinas dedicadas, e em alguns casos, parques aquáticos e "
        "simuladores de aventura."
    ),
    "Melhor época": (
        "A escolha da melhor época depende do destino. Para economia, recomendamos "
        "temporadas intermediárias quando o clima ainda é bom mas os preços são mais acessíveis."
    ),
    "Pagamentos e reservas": (
        "Trabalhamos com diversas formas de pagamento incluindo cartão de crédito, "
        "boleto, pix e parcelamento. Garantimos o melhor preço e condições especiais "
        "para nossos clientes."
    )
}