"""
Configuração global do pytest para testes do Bot Travessia

Este arquivo:
- Configura mocks para dependências externas (Twilio, OpenAI)
- Define fixtures globais
- Prepara ambiente de testes
"""

import pytest
import sys
from unittest.mock import MagicMock, Mock

# Mock do Twilio antes de importar qualquer módulo
sys.modules['twilio'] = MagicMock()
sys.modules['twilio.twiml'] = MagicMock()
sys.modules['twilio.twiml.messaging_response'] = MagicMock()

# Mock do psycopg2 (PostgreSQL)
sys.modules['psycopg2'] = MagicMock()

# Configura variáveis de ambiente para testes
import os
os.environ['OPENAI_API_KEY'] = 'sk-test-fake-key-for-testing'
os.environ['TWILIO_ACCOUNT_SID'] = 'test_sid'
os.environ['TWILIO_AUTH_TOKEN'] = 'test_token'
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'


@pytest.fixture
def mock_ai_service(monkeypatch):
    """
    Mock do AIService para não gastar créditos da API durante testes
    """
    def mock_gerar_resposta_simples(self, prompt):
        """Mock que retorna JSON fake"""
        if "pessoas" in prompt.lower():
            return '{"pessoas": "4 pessoas", "orcamento": "R$ 5.000", "quando": "Dezembro"}'
        elif "quando" in prompt.lower():
            return '{"quando": "Dezembro", "duracao": "7 dias"}'
        return '{}'

    # Aplica o mock
    from openai_service import AIService
    monkeypatch.setattr(AIService, "gerar_resposta_simples", mock_gerar_resposta_simples)


@pytest.fixture
def mock_telegram_service(monkeypatch):
    """Mock do TelegramService para não enviar mensagens reais"""
    def mock_adicionar_mensagem(*args, **kwargs):
        pass

    def mock_atualizar_perfil(*args, **kwargs):
        pass

    def mock_enviar_conversa(*args, **kwargs):
        pass

    from telegram_service import TelegramService
    monkeypatch.setattr(TelegramService, "adicionar_mensagem", mock_adicionar_mensagem)
    monkeypatch.setattr(TelegramService, "atualizar_perfil", mock_atualizar_perfil)
    monkeypatch.setattr(TelegramService, "enviar_conversa", mock_enviar_conversa)


@pytest.fixture(autouse=True)
def setup_test_mocks(mock_ai_service, mock_telegram_service):
    """Aplica todos os mocks automaticamente em todos os testes"""
    yield
