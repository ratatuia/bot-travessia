"""
Lead Scoring Service
Calcula pontuação de leads baseado em comportamento e dados coletados
"""

import re
from datetime import datetime

class LeadScoringService:
    """
    Sistema de pontuação de leads (0-100)

    Critérios:
    - Orçamento alto = mais pontos
    - Urgência (próximos meses) = mais pontos
    - Veterano em cruzeiros = mais pontos
    - Família grande = mais pontos
    - Interesse em destinos premium = mais pontos
    """

    @staticmethod
    def calcular_score(estado_cliente):
        """
        Calcula score do lead baseado no estado atual

        Args:
            estado_cliente: Dict com dados do cliente

        Returns:
            int: Score de 0-100
        """
        score = 0

        # 1. Orçamento (max 30 pontos)
        score += LeadScoringService._score_orcamento(estado_cliente.get("orcamento_pp", ""))

        # 2. Urgência/Período (max 40 pontos)
        score += LeadScoringService._score_periodo(estado_cliente.get("periodo_desejado", ""))

        # 3. Experiência prévia (max 20 pontos)
        if estado_cliente.get("experiencia_previa") == "Veterano":
            score += 20

        # 4. Tamanho do grupo (max 10 pontos)
        score += LeadScoringService._score_grupo(estado_cliente.get("num_pessoas", ""))

        return min(score, 100)  # Cap em 100

    @staticmethod
    def _score_orcamento(orcamento_str):
        """
        Extrai valor do orçamento e pontua
        R$ 8.000+ = 30 pontos
        R$ 5.000-7.999 = 20 pontos
        R$ 3.000-4.999 = 10 pontos
        < R$ 3.000 = 5 pontos
        """
        try:
            # Extrai números do string
            numeros = re.findall(r'\d+', orcamento_str.replace('.', '').replace(',', ''))
            if not numeros:
                return 0

            valor = int(numeros[0])

            if valor >= 8000:
                return 30
            elif valor >= 5000:
                return 20
            elif valor >= 3000:
                return 10
            else:
                return 5
        except:
            return 0

    @staticmethod
    def _score_periodo(periodo_str):
        """
        Pontua baseado na urgência
        Próximos 3 meses = 40 pontos
        3-6 meses = 30 pontos
        6-12 meses = 20 pontos
        > 12 meses = 10 pontos
        """
        periodo_lower = periodo_str.lower()

        # Palavras-chave de urgência
        urgente = ["breve", "próximo", "janeiro", "fevereiro", "março", "logo", "rápido"]
        medio_prazo = ["abril", "maio", "junho", "julho", "meio do ano"]
        longo_prazo = ["dezembro", "final do ano", "ano que vem", "próximo ano"]

        if any(word in periodo_lower for word in urgente):
            return 40
        elif any(word in periodo_lower for word in medio_prazo):
            return 30
        elif any(word in periodo_lower for word in longo_prazo):
            return 20
        else:
            return 10

    @staticmethod
    def _score_grupo(num_pessoas_str):
        """
        Pontua baseado no tamanho do grupo
        4+ pessoas = 10 pontos
        2-3 pessoas = 7 pontos
        1 pessoa = 3 pontos
        """
        try:
            # Extrai primeiro número
            numeros = re.findall(r'\d+', num_pessoas_str)
            if not numeros:
                return 0

            num = int(numeros[0])

            if num >= 4:
                return 10
            elif num >= 2:
                return 7
            else:
                return 3
        except:
            return 0

    @staticmethod
    def get_prioridade(score):
        """
        Retorna nível de prioridade baseado no score

        Returns:
            tuple: (nivel, emoji, descricao)
        """
        if score >= 70:
            return ("ALTA", "🔥", "Lead quente - atender AGORA!")
        elif score >= 50:
            return ("MÉDIA", "⭐", "Bom lead - atender em até 2h")
        else:
            return ("BAIXA", "📋", "Lead frio - atender em até 24h")
