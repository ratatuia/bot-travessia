from openai import OpenAI
from config import OPENAI_API_KEY

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def gerar_resposta(self, nome_cliente, mensagem, contexto):
        """
        Gera uma resposta personalizada usando GPT
        
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