from openai import OpenAI
from config import OPENAI_API_KEY
from resilience import retry_with_backoff, openai_circuit
import random

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        # Define fallback para o circuit breaker
        openai_circuit.fallback = self._fallback_resposta

    def _fallback_resposta(self, nome_cliente, mensagem, contexto):
        """
        Fallback quando OpenAI está indisponível
        Usa respostas pré-definidas baseadas em palavras-chave
        """
        mensagem_lower = mensagem.lower()

        # Respostas baseadas em palavras-chave
        if any(word in mensagem_lower for word in ["preço", "valor", "custo", "quanto"]):
            return (
                f"{nome_cliente}, os valores variam bastante! 💰\n\n"
                "Depende do destino, duração e tipo de cabine.\n"
                "Um especialista pode te mostrar opções dentro do seu orçamento.\n\n"
                "Quer falar com nossa equipe agora?"
            )
        elif any(word in mensagem_lower for word in ["destino", "lugar", "onde"]):
            return (
                f"{nome_cliente}, temos cruzeiros incríveis! 🌎\n\n"
                "Caribe, Mediterrâneo, Brasil e muito mais.\n"
                "Vamos descobrir o destino perfeito pra você?\n\n"
                "Digite 'menu' para começar!"
            )
        else:
            return (
                f"{nome_cliente}, sua pergunta é ótima! 🤔\n\n"
                "Um especialista pode responder isso com muito mais detalhes.\n\n"
                "Quer que eu registre seu contato para atendimento?"
            )

    @retry_with_backoff(max_retries=3, initial_delay=1, exceptions=(Exception,))
    @openai_circuit
    def gerar_resposta(self, nome_cliente, mensagem, contexto):
        """
        Gera uma resposta personalizada usando GPT
        Com retry automático e circuit breaker

        Args:
            nome_cliente: Nome do cliente
            mensagem: Pergunta do cliente
            contexto: Contexto da base de conhecimento

        Returns:
            str: Resposta gerada
        """
        try:
            # Prepara contexto da base de conhecimento
            context_formatted = "\n\n".join([f"### {k}\n{v}" for k, v in contexto.items()])

            nome_prefix = f"Olá {nome_cliente}, " if nome_cliente else ""

            # Cria o prompt para a OpenAI
            prompt = f"""
            Você é um assistente da agência Travessia dos Sonhos, especializada em cruzeiros marítimos.
            Nome do cliente: {nome_cliente if nome_cliente else 'Desconhecido'}
            Pergunta: "{mensagem}"
            Base de conhecimento:
            {context_formatted}

            Regras importantes:
            1. Responda de forma concisa e amigável (máximo 3 frases)
            2. NÃO mencione nenhuma companhia de cruzeiros específica (como MSC, Royal Caribbean, etc)
            3. Sempre fale de forma genérica sobre "cruzeiros marítimos" ou "viagens marítimas"
            4. Se a pergunta não estiver clara, peça gentilmente ao cliente para reformular
            5. Mantenha o tom cordial mas OBJETIVO e BREVE
            6. Use emojis para tornar a resposta mais amigável e visual
            """

            # Obtém resposta da IA
            resposta = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=100
            ).choices[0].message.content.strip()

            return resposta

        except Exception as e:
            print(f"[ERRO GPT] {e}")
            return f"⚠️ {'Olá' if not nome_cliente else nome_cliente}, desculpe, tivemos um probleminha técnico. Pode tentar novamente em instantes?"

    @retry_with_backoff(max_retries=2, initial_delay=0.5, exceptions=(Exception,))
    def gerar_resposta_simples(self, prompt):
        """
        Gera uma resposta simples sem contexto adicional
        Útil para extração de informações
        Com retry automático (sem circuit breaker - menos crítico)

        Args:
            prompt: Prompt direto para a IA

        Returns:
            str: Resposta gerada
        """
        try:
            resposta = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Modelo mais rápido e barato para extração
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Baixa temperatura para respostas mais consistentes
                max_tokens=150
            ).choices[0].message.content.strip()

            return resposta

        except Exception as e:
            print(f"[ERRO GPT SIMPLES] {e}")
            return "{}"  # Retorna JSON vazio em caso de erro
