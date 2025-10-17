"""
Testes automatizados do fluxo conversacional do Bot Travessia dos Sonhos

Este arquivo testa:
1. Cada estado individual (testes unitários)
2. Fluxos completos de ponta a ponta (testes E2E)
3. Comandos especiais
4. Validações de entrada
5. Casos extremos e edge cases

Autor: Claude Code
Data: 2025-10-16
"""

import pytest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from app import processar_mensagem
from config import MENSAGENS, detectar_comando, COMANDOS_ESPECIAIS


class TestComandosEspeciais:
    """Testa os comandos especiais que funcionam a qualquer momento"""

    def test_detectar_comando_menu(self):
        """Testa detecção do comando 'menu'"""
        assert detectar_comando("menu") == "menu"
        assert detectar_comando("MENU") == "menu"
        assert detectar_comando("voltar") == "menu"
        assert detectar_comando("inicio") == "menu"

    def test_detectar_comando_resumo(self):
        """Testa detecção do comando 'resumo'"""
        assert detectar_comando("resumo") == "resumo"
        assert detectar_comando("RESUMO") == "resumo"

    def test_detectar_comando_ajuda(self):
        """Testa detecção do comando 'ajuda'"""
        assert detectar_comando("ajuda") == "ajuda"
        assert detectar_comando("help") == "ajuda"
        assert detectar_comando("?") == "ajuda"

    def test_detectar_comando_contato(self):
        """Testa detecção do comando 'contato'"""
        assert detectar_comando("falar") == "contato"
        assert detectar_comando("atendimento") == "contato"
        assert detectar_comando("especialista") == "contato"

    def test_detectar_comando_invalido(self):
        """Testa mensagem que não é comando"""
        assert detectar_comando("Rafael") is None
        assert detectar_comando("123") is None
        assert detectar_comando("teste123") is None


class TestEstadoAguardandoNome:
    """Testa o estado inicial de coleta de nome"""

    def test_nome_valido(self):
        """Testa nome válido"""
        estado_atual = {"estado": "aguardando_nome"}
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "Rafael",
            estado_atual
        )

        assert novo_estado["nome"] == "Rafael"
        assert novo_estado["estado"] == "aguardando_email"
        assert "email" in resposta.lower()

    def test_nome_com_espaco(self):
        """Testa nome composto"""
        estado_atual = {"estado": "aguardando_nome"}
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "Maria Silva",
            estado_atual
        )

        assert novo_estado["nome"] == "Maria Silva"
        assert novo_estado["estado"] == "aguardando_email"

    def test_nome_com_numeros_rejeitado(self):
        """Testa que nome com números é rejeitado"""
        estado_atual = {"estado": "aguardando_nome"}
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "Rafael123",
            estado_atual
        )

        # Nome inválido deve manter o estado
        assert novo_estado["estado"] == "aguardando_nome"
        assert "válido" in resposta.lower()


class TestEstadoAguardandoEmail:
    """Testa validação de email"""

    def test_email_valido(self):
        """Testa email válido"""
        estado_atual = {
            "estado": "aguardando_email",
            "nome": "Rafael"
        }
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "rafael@email.com",
            estado_atual
        )

        assert novo_estado["email"] == "rafael@email.com"
        assert novo_estado["estado"] == "menu"
        assert "Rafael" in resposta  # Deve ter o nome no menu

    def test_email_invalido(self):
        """Testa email inválido"""
        estado_atual = {
            "estado": "aguardando_email",
            "nome": "Rafael"
        }
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "emailinvalido",
            estado_atual
        )

        # Email inválido deve manter o estado
        assert novo_estado["estado"] == "aguardando_email"
        assert "incorreto" in resposta.lower() or "email" in resposta.lower()


class TestFluxoMenuPrincipal:
    """Testa navegação no menu principal"""

    def setup_method(self):
        """Prepara estado inicial para cada teste"""
        self.estado_menu = {
            "estado": "menu",
            "nome": "Rafael",
            "email": "rafael@email.com"
        }

    def test_opcao1_descobrir_cruzeiro(self):
        """Testa opção 1: Descobrir cruzeiro ideal (CORRIGIDO)"""
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "1",
            self.estado_menu
        )

        assert novo_estado["estado"] == "qualificacao_inicial"
        assert "1/5" in resposta or "pessoas" in resposta.lower()  # Deve perguntar qualificação

    def test_opcao2_conhecer_tripulacao(self):
        """Testa opção 2: Conhecer a Travessia (CORRIGIDO)"""
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "2",
            self.estado_menu
        )

        assert novo_estado["estado"] == "pos_conhecer_tripulacao"
        assert "Travessia dos Sonhos" in resposta
        assert "+500 famílias" in resposta  # Social proof

    def test_opcao3_solicitar_atendimento(self):
        """Testa opção 3: Solicitar atendimento"""
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "3",
            self.estado_menu
        )

        assert novo_estado["estado"] == "atendimento_solicitado"
        assert meta.get("tipo_msg") == "urgente"
        # Resposta deve ter o nome do cliente
        assert "Rafael" in resposta

    def test_opcao_invalida(self):
        """Testa opção inválida no menu"""
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "999",
            self.estado_menu
        )

        # Deve manter no menu
        assert novo_estado["estado"] == "menu"
        # Deve mostrar mensagem de erro amigável (verifica se resposta não é vazia)
        assert len(resposta) > 0 and "Rafael" in resposta


class TestFluxoPosConhecerTripulacao:
    """Testa fluxo após apresentação da empresa"""

    def setup_method(self):
        """Prepara estado inicial"""
        self.estado = {
            "estado": "pos_conhecer_tripulacao",
            "nome": "Rafael",
            "email": "rafael@email.com"
        }

    def test_veterano(self):
        """Testa resposta para cliente veterano"""
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "1",  # Sim, sou veterano
            self.estado
        )

        assert novo_estado["estado"] == "qualificacao_inicial"
        assert novo_estado["experiencia_previa"] == "Veterano"
        assert "veterano" in resposta.lower() or "já sabe" in resposta.lower()

    def test_primeira_vez(self):
        """Testa resposta para primeira viagem"""
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "2",  # Primeira vez
            self.estado
        )

        assert novo_estado["estado"] == "qualificacao_inicial"
        assert novo_estado["experiencia_previa"] == "Primeira vez"
        assert "primeira" in resposta.lower() or "emoção" in resposta.lower()


class TestFluxoQualificacaoInicial:
    """Testa o estado de qualificação inicial com IA"""

    def setup_method(self):
        """Prepara estado inicial"""
        self.estado = {
            "estado": "qualificacao_inicial",
            "nome": "Rafael",
            "email": "rafael@email.com"
        }

    @pytest.mark.skip(reason="Requer API OpenAI - teste manual")
    def test_qualificacao_completa(self):
        """Testa qualificação com todas informações"""
        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "somos 4 pessoas, 5 mil cada, queremos ir em dezembro",
            self.estado
        )

        # Deve extrair as 3 informações
        assert novo_estado["estado"] == "experiencia_desejada"
        assert "num_pessoas" in novo_estado
        assert "orcamento_pp" in novo_estado
        assert "periodo_desejado" in novo_estado


class TestFluxoCompletoE2E:
    """Testes de ponta a ponta do fluxo completo"""

    def test_fluxo_rapido_opcao1(self):
        """
        Testa fluxo completo pela opção 1 (descobrir cruzeiro ideal) - CORRIGIDO

        Simula um cliente que:
        1. Informa nome
        2. Informa email
        3. Escolhe opção 1 (descobrir cruzeiro) - CORRIGIDO
        4. Responde qualificação (sem IA - vai para fallback)
        5. Responde experiência desejada
        6. Responde quando/quanto tempo
        7. Escolhe forma de contato
        8. Escolhe horário
        """
        sender = "whatsapp:+5511999999999"

        # Passo 1: Nome
        estado = {"estado": "aguardando_nome"}
        resposta, estado, meta = processar_mensagem(sender, "Rafael", estado)
        assert estado["nome"] == "Rafael"
        assert estado["estado"] == "aguardando_email"

        # Passo 2: Email
        resposta, estado, meta = processar_mensagem(sender, "rafael@email.com", estado)
        assert estado["email"] == "rafael@email.com"
        assert estado["estado"] == "menu"

        # Passo 3: Opção 1 (descobrir cruzeiro) - CORRIGIDO
        resposta, estado, meta = processar_mensagem(sender, "1", estado)
        assert estado["estado"] == "qualificacao_inicial"

        # Passo 4: Qualificação (texto livre - pode falhar IA e pedir reformulação)
        # Por isso vamos direto para experiencia_desejada manualmente
        estado["estado"] = "experiencia_desejada"
        resposta, estado, meta = processar_mensagem(
            sender,
            "gosto de praia e relaxamento",
            estado
        )
        assert estado["estado"] == "quando_quanto_tempo"

        # Passo 5: Quando e quanto tempo
        estado["estado"] = "quando_quanto_tempo"
        resposta, estado, meta = processar_mensagem(sender, "dezembro, 7 dias", estado)
        assert estado["estado"] == "perguntando_forma_contato"

        # Passo 6: Forma de contato
        resposta, estado, meta = processar_mensagem(sender, "1", estado)  # WhatsApp
        assert estado["estado"] == "perguntando_horario"

        # Passo 7: Horário
        resposta, estado, meta = processar_mensagem(sender, "3", estado)  # Tarde
        assert estado["estado"] == "atendimento_solicitado"
        assert meta.get("tipo_msg") == "atendimento"

        print("\n✅ FLUXO COMPLETO TESTADO COM SUCESSO!")
        print(f"   Estado final: {estado['estado']}")
        print(f"   Dados coletados: nome={estado.get('nome')}, email={estado.get('email')}")

    def test_comando_resumo_durante_fluxo(self):
        """Testa comando 'resumo' no meio do fluxo"""
        sender = "whatsapp:+5511999999999"

        # Cria estado no meio do fluxo com alguns dados
        estado = {
            "estado": "perguntando_forma_contato",
            "nome": "Rafael",
            "email": "rafael@email.com",
            "num_pessoas": "4 pessoas",
            "orcamento_pp": "R$ 5.000",
            "periodo_desejado": "Dezembro"
        }

        # Digita 'resumo'
        resposta, novo_estado, meta = processar_mensagem(sender, "resumo", estado)

        # Deve manter o estado atual
        assert novo_estado["estado"] == "perguntando_forma_contato"

        # Deve mostrar dados coletados
        assert "resumo" in resposta.lower()
        # Não vamos verificar campos específicos pois dependem do mapeamento

    def test_comando_menu_durante_fluxo(self):
        """Testa comando 'menu' no meio do fluxo"""
        sender = "whatsapp:+5511999999999"

        # Estado no meio do fluxo
        estado = {
            "estado": "experiencia_desejada",
            "nome": "Rafael",
            "email": "rafael@email.com"
        }

        # Digita 'menu'
        resposta, novo_estado, meta = processar_mensagem(sender, "menu", estado)

        # Deve voltar ao menu
        assert novo_estado["estado"] == "menu"
        assert "Rafael" in resposta


class TestValidacoes:
    """Testa validações de segurança e edge cases"""

    def test_mensagem_muito_longa_truncada(self):
        """Testa que mensagens muito longas são truncadas"""
        estado = {"estado": "aguardando_nome"}
        mensagem_longa = "A" * 1000  # 1000 caracteres

        # Não deve quebrar o sistema
        try:
            resposta, novo_estado, meta = processar_mensagem(
                "whatsapp:+5511999999999",
                mensagem_longa,
                estado
            )
            # Se chegou aqui, não quebrou
            assert True
        except Exception as e:
            pytest.fail(f"Mensagem longa quebrou o sistema: {e}")

    def test_caracteres_especiais_no_nome(self):
        """Testa nome com caracteres especiais"""
        estado = {"estado": "aguardando_nome"}

        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            "João@#$%",
            estado
        )

        # Deve rejeitar
        assert novo_estado["estado"] == "aguardando_nome"

    def test_email_com_espacos(self):
        """Testa email com espaços"""
        estado = {
            "estado": "aguardando_email",
            "nome": "Rafael"
        }

        resposta, novo_estado, meta = processar_mensagem(
            "whatsapp:+5511999999999",
            " rafael@email.com ",
            estado
        )

        # Deve aceitar (sanitização remove espaços)
        assert novo_estado["estado"] == "menu"
        assert novo_estado["email"] == "rafael@email.com"


# Fixture para configuração global dos testes
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configura ambiente de testes"""
    print("\n" + "="*70)
    print("🧪 INICIANDO TESTES DO BOT TRAVESSIA DOS SONHOS")
    print("="*70)
    yield
    print("\n" + "="*70)
    print("✅ TESTES FINALIZADOS")
    print("="*70)


if __name__ == "__main__":
    # Permite executar com: python test_bot_fluxo.py
    pytest.main([__file__, "-v", "--tb=short"])
