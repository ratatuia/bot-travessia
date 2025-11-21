"""
Resilience Layer - Retry e Circuit Breaker
Gerencia falhas de serviços externos (OpenAI, Twilio, etc)
"""

import time
import functools
from datetime import datetime, timedelta

# ===================================
# Retry com Exponential Backoff
# ===================================

def retry_with_backoff(max_retries=3, initial_delay=1, backoff_factor=2, exceptions=(Exception,)):
    """
    Decorator para retry automático com exponential backoff

    Args:
        max_retries: Número máximo de tentativas
        initial_delay: Delay inicial em segundos (1s, 2s, 4s...)
        backoff_factor: Multiplicador do delay a cada retry
        exceptions: Tupla de exceções que devem acionar retry

    Exemplo:
        @retry_with_backoff(max_retries=3, initial_delay=1)
        def chamar_api():
            return requests.get("https://api.example.com")
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries - 1:  # Não espera na última tentativa
                        print(f"[RETRY] {func.__name__} falhou (tentativa {attempt + 1}/{max_retries}). Retry em {delay}s...")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        print(f"[RETRY] {func.__name__} falhou após {max_retries} tentativas")

            # Se chegou aqui, todas as tentativas falharam
            raise last_exception

        return wrapper
    return decorator


# ===================================
# Circuit Breaker
# ===================================

class CircuitBreaker:
    """
    Circuit Breaker Pattern - previne cascata de falhas

    Estados:
    - CLOSED: Normal, permite chamadas
    - OPEN: Serviço está falhando, bloqueia chamadas (usa fallback)
    - HALF_OPEN: Testa se serviço voltou

    Uso:
        breaker = CircuitBreaker(failure_threshold=5, timeout=60)

        @breaker
        def chamar_openai():
            return client.chat.completions.create(...)
    """

    def __init__(self, failure_threshold=5, timeout=60, fallback=None):
        """
        Args:
            failure_threshold: Número de falhas para abrir o circuit
            timeout: Segundos para tentar novamente após abrir
            fallback: Função de fallback quando circuit está aberto
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.fallback = fallback

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Se circuit está aberto, verifica timeout
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                    print(f"[CIRCUIT] {func.__name__} - Estado: HALF_OPEN (testando)")
                else:
                    print(f"[CIRCUIT] {func.__name__} - Estado: OPEN (usando fallback)")
                    if self.fallback:
                        return self.fallback(*args, **kwargs)
                    raise Exception(f"Circuit breaker aberto para {func.__name__}")

            # Tenta executar
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()

                # Se circuit abriu agora e tem fallback, usa
                if self.state == "OPEN" and self.fallback:
                    print(f"[CIRCUIT] {func.__name__} - Usando fallback")
                    return self.fallback(*args, **kwargs)

                raise e

        return wrapper

    def _should_attempt_reset(self):
        """Verifica se já passou tempo suficiente para testar novamente"""
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time >= timedelta(seconds=self.timeout)
        )

    def _on_success(self):
        """Reseta contadores após sucesso"""
        if self.state == "HALF_OPEN":
            print(f"[CIRCUIT] Serviço recuperado - Estado: CLOSED")

        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Incrementa falhas e abre circuit se necessário"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print(f"[CIRCUIT] ABERTO após {self.failure_count} falhas - usando fallback por {self.timeout}s")


# ===================================
# Instâncias Globais
# ===================================

# Circuit breaker para OpenAI
openai_circuit = CircuitBreaker(
    failure_threshold=3,  # Abre após 3 falhas
    timeout=60,           # Tenta novamente após 60s
    fallback=None         # Será definido no openai_service.py
)

# Circuit breaker para Twilio (se necessário no futuro)
twilio_circuit = CircuitBreaker(
    failure_threshold=5,
    timeout=30
)
