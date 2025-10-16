"""
Módulo de Segurança do Bot Travessia
Implementa validações, sanitização e autenticação
"""

import os
import re
import hashlib
import hmac
import bleach
from functools import wraps
from flask import request, jsonify
from urllib.parse import urlencode
from typing import Optional, Dict, Any


# ===================================
# Configurações de Segurança
# ===================================

# Admin API Key para endpoints protegidos (deve estar no .env)
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

# Twilio credentials para validação de webhook
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")


# ===================================
# Validação de Input
# ===================================

def sanitize_text(text: str, max_length: int = 500) -> str:
    """
    Sanitiza texto do usuário removendo HTML/JS e limitando tamanho

    Args:
        text: Texto a ser sanitizado
        max_length: Tamanho máximo permitido

    Returns:
        Texto sanitizado e seguro
    """
    if not text:
        return ""

    # Remove HTML/JS tags
    clean_text = bleach.clean(text, tags=[], strip=True)

    # Remove caracteres de controle perigosos
    clean_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', clean_text)

    # Limita tamanho
    clean_text = clean_text[:max_length]

    # Remove espaços extras
    clean_text = ' '.join(clean_text.split())

    return clean_text.strip()


def validate_email(email: str) -> bool:
    """
    Valida formato de email de forma segura

    Args:
        email: Email a validar

    Returns:
        True se válido, False caso contrário
    """
    if not email or len(email) > 254:  # RFC 5321
        return False

    # Regex mais restritivo para evitar bypass
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9][a-zA-Z0-9.-]{0,253}\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False

    # Valida parts separadamente
    local, domain = email.rsplit('@', 1)

    # Local part checks
    if local.startswith('.') or local.endswith('.'):
        return False
    if '..' in local:
        return False

    # Domain checks
    if domain.startswith('-') or domain.endswith('-'):
        return False
    if '..' in domain:
        return False

    return True


def validate_phone_number(phone: str) -> bool:
    """
    Valida número de telefone no formato WhatsApp (whatsapp:+XXXXXXXXXXX)

    Args:
        phone: Número a validar

    Returns:
        True se válido, False caso contrário
    """
    if not phone:
        return False

    # Formato WhatsApp: whatsapp:+5511999999999
    pattern = r'^whatsapp:\+\d{10,15}$'
    return bool(re.match(pattern, phone))


def validate_name(name: str) -> bool:
    """
    Valida nome de usuário

    Args:
        name: Nome a validar

    Returns:
        True se válido, False caso contrário
    """
    if not name or len(name) < 2 or len(name) > 100:
        return False

    # Permite letras (incluindo acentuadas), espaços, hífens e apóstrofes
    pattern = r"^[a-zA-ZàáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ\s'-]+$"

    return bool(re.match(pattern, name))


def validate_menu_option(option: str, valid_options: list) -> bool:
    """
    Valida se opção do menu é válida

    Args:
        option: Opção selecionada
        valid_options: Lista de opções válidas

    Returns:
        True se válido, False caso contrário
    """
    if not option:
        return False

    # Remove espaços e converte para minúscula para comparação
    option_clean = option.strip().lower()
    valid_options_clean = [str(opt).strip().lower() for opt in valid_options]

    return option_clean in valid_options_clean


# ===================================
# Autenticação de Endpoints
# ===================================

def require_api_key(f):
    """
    Decorator para proteger endpoints com API Key

    Uso:
        @app.route('/admin')
        @require_api_key
        def admin_endpoint():
            return "Protected"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Checa header Authorization
        auth_header = request.headers.get('Authorization', '')

        # Formato esperado: "Bearer YOUR_API_KEY"
        if not auth_header.startswith('Bearer '):
            return jsonify({
                "error": "Unauthorized",
                "message": "Missing or invalid Authorization header"
            }), 401

        provided_key = auth_header.replace('Bearer ', '', 1).strip()

        # Verifica se ADMIN_API_KEY está configurado
        if not ADMIN_API_KEY:
            return jsonify({
                "error": "Server Configuration Error",
                "message": "Admin API key not configured"
            }), 500

        # Comparação segura contra timing attacks
        if not hmac.compare_digest(provided_key, ADMIN_API_KEY):
            return jsonify({
                "error": "Forbidden",
                "message": "Invalid API key"
            }), 403

        return f(*args, **kwargs)

    return decorated_function


# ===================================
# Validação de Webhook Twilio
# ===================================

def validate_twilio_signature(url: str, params: Dict[str, Any], signature: str) -> bool:
    """
    Valida assinatura do webhook Twilio para prevenir spoofing

    Args:
        url: URL completa do webhook
        params: Parâmetros do POST (request.form)
        signature: Header X-Twilio-Signature

    Returns:
        True se assinatura válida, False caso contrário

    Referência:
        https://www.twilio.com/docs/usage/security#validating-requests
    """
    if not TWILIO_AUTH_TOKEN:
        # Se não tiver token configurado, não pode validar
        return False

    # Ordena params alfabeticamente e concatena
    sorted_params = sorted(params.items())
    data = url + ''.join(f'{k}{v}' for k, v in sorted_params)

    # Calcula HMAC-SHA256
    mac = hmac.new(
        TWILIO_AUTH_TOKEN.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    )

    # Calcula base64
    import base64
    expected_signature = base64.b64encode(mac.digest()).decode('utf-8')

    # Comparação segura
    return hmac.compare_digest(signature, expected_signature)


def require_twilio_signature(f):
    """
    Decorator para validar webhooks do Twilio

    Uso:
        @app.route('/bot', methods=['POST'])
        @require_twilio_signature
        def whatsapp_bot():
            return "Valid Twilio request"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Pega assinatura do header
        signature = request.headers.get('X-Twilio-Signature', '')

        if not signature:
            return jsonify({
                "error": "Unauthorized",
                "message": "Missing Twilio signature"
            }), 401

        # Reconstroi URL completa
        url = request.url

        # Valida assinatura
        if not validate_twilio_signature(url, dict(request.form), signature):
            return jsonify({
                "error": "Forbidden",
                "message": "Invalid Twilio signature"
            }), 403

        return f(*args, **kwargs)

    return decorated_function


# ===================================
# Utilidades de Segurança
# ===================================

def generate_api_key(length: int = 32) -> str:
    """
    Gera uma API key segura

    Args:
        length: Tamanho da chave

    Returns:
        API key aleatória

    Uso:
        python -c "from security import generate_api_key; print(generate_api_key())"
    """
    import secrets
    return secrets.token_urlsafe(length)


def mask_sensitive_data(text: str, patterns: Optional[list] = None) -> str:
    """
    Mascara dados sensíveis em logs

    Args:
        text: Texto a mascarar
        patterns: Lista de padrões regex a mascarar (opcional)

    Returns:
        Texto com dados mascarados
    """
    if not text:
        return text

    # Padrões default
    if patterns is None:
        patterns = [
            (r'sk-proj-[a-zA-Z0-9_-]{20,}', 'sk-proj-***'),  # OpenAI keys
            (r'AC[a-z0-9]{32}', 'AC***'),  # Twilio SID
            (r'\d{10}:\w{35}', '***:***'),  # Telegram tokens
            (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '***-***-****'),  # Phone numbers
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.com'),  # Emails
        ]

    masked = text
    for pattern, replacement in patterns:
        masked = re.sub(pattern, replacement, masked)

    return masked


# ===================================
# Headers de Segurança
# ===================================

def add_security_headers(response):
    """
    Adiciona headers de segurança HTTP

    Uso no Flask:
        @app.after_request
        def after_request(response):
            return add_security_headers(response)
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"

    return response


# ===================================
# Rate Limiting Helpers
# ===================================

def get_rate_limit_key() -> str:
    """
    Gera chave para rate limiting baseada no IP + User-Agent

    Returns:
        Chave única para o cliente
    """
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'unknown')

    # Hash para não armazenar IPs diretamente
    key = f"{ip}:{user_agent}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]
