"""
Sistema de Observabilidade - Bot Travessia dos Sonhos
Logs estruturados, métricas, tracing e alertas
"""

import json
import logging
import logging.handlers
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from functools import wraps
from collections import defaultdict, deque
import threading

# Configurações
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "bot.log")
METRICS_FILE = os.path.join(LOG_DIR, "metrics.json")
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5


# ===================================
# Sistema de Logs Estruturados
# ===================================

class StructuredLogger:
    """Logger que gera logs em formato JSON estruturado"""

    def __init__(self, name: str = "travessia_bot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Criar diretório de logs se não existir
        os.makedirs(LOG_DIR, exist_ok=True)

        # Handler para arquivo com rotation
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Handler para console (para desenvolvimento e Render)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formato JSON para arquivo
        file_formatter = JsonFormatter()
        file_handler.setFormatter(file_formatter)

        # Formato legível para console
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)

        # Adicionar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log(self, level: str, message: str, **kwargs):
        """
        Log estruturado com contexto adicional

        Args:
            level: Nível do log (debug, info, warning, error, critical)
            message: Mensagem principal
            **kwargs: Contexto adicional (user_id, action, duration, etc)
        """
        extra = {
            'context': kwargs,
            'timestamp': datetime.now().isoformat()
        }

        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message, extra=extra)

    def debug(self, message: str, **kwargs):
        self.log('debug', message, **kwargs)

    def info(self, message: str, **kwargs):
        self.log('info', message, **kwargs)

    def warning(self, message: str, **kwargs):
        self.log('warning', message, **kwargs)

    def error(self, message: str, **kwargs):
        self.log('error', message, **kwargs)

    def critical(self, message: str, **kwargs):
        self.log('critical', message, **kwargs)


class JsonFormatter(logging.Formatter):
    """Formatter que converte logs para JSON"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Adicionar contexto extra se existir
        if hasattr(record, 'context'):
            log_data['context'] = record.context

        # Adicionar exception info se existir
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


# Instância global do logger
logger = StructuredLogger()


# ===================================
# Sistema de Métricas
# ===================================

class MetricsCollector:
    """Coleta e agrega métricas da aplicação"""

    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'count': 0,
            'total': 0,
            'min': float('inf'),
            'max': 0,
            'errors': 0,
            'last_24h': deque(maxlen=1440)  # 1 por minuto
        })
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.start_time = time.time()
        self.lock = threading.Lock()

    def increment(self, metric: str, value: int = 1, tags: Optional[Dict] = None):
        """Incrementa um contador"""
        with self.lock:
            key = self._make_key(metric, tags)
            self.counters[key] += value
            logger.debug(f"Metric incremented: {key} = {self.counters[key]}")

    def timing(self, metric: str, duration: float, tags: Optional[Dict] = None):
        """Registra uma métrica de tempo (ms)"""
        with self.lock:
            key = self._make_key(metric, tags)
            m = self.metrics[key]

            m['count'] += 1
            m['total'] += duration
            m['min'] = min(m['min'], duration)
            m['max'] = max(m['max'], duration)
            m['last_24h'].append({
                'timestamp': time.time(),
                'value': duration
            })

            logger.debug(f"Timing recorded: {key} = {duration}ms")

    def gauge(self, metric: str, value: float, tags: Optional[Dict] = None):
        """Define o valor de um gauge (valor atual)"""
        with self.lock:
            key = self._make_key(metric, tags)
            self.gauges[key] = value
            logger.debug(f"Gauge set: {key} = {value}")

    def error(self, metric: str, tags: Optional[Dict] = None):
        """Registra um erro"""
        with self.lock:
            key = self._make_key(metric, tags)
            self.metrics[key]['errors'] += 1
            logger.error(f"Error metric: {key}")

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo de todas as métricas"""
        with self.lock:
            return {
                'uptime_seconds': int(time.time() - self.start_time),
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'timings': {
                    k: {
                        'count': v['count'],
                        'avg_ms': v['total'] / v['count'] if v['count'] > 0 else 0,
                        'min_ms': v['min'] if v['min'] != float('inf') else 0,
                        'max_ms': v['max'],
                        'errors': v['errors']
                    }
                    for k, v in self.metrics.items()
                }
            }

    def save_to_file(self):
        """Salva métricas em arquivo JSON"""
        try:
            summary = self.get_summary()
            summary['saved_at'] = datetime.now().isoformat()

            with open(METRICS_FILE, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            logger.info("Metrics saved to file", file=METRICS_FILE)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def _make_key(self, metric: str, tags: Optional[Dict] = None) -> str:
        """Cria chave única para métrica com tags"""
        if not tags:
            return metric

        tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric}[{tag_str}]"


# Instância global do coletor de métricas
metrics = MetricsCollector()


# ===================================
# Correlation ID (Request Tracing)
# ===================================

class CorrelationContext:
    """Contexto de correlação para rastrear requests"""

    _local = threading.local()

    @classmethod
    def get_id(cls) -> str:
        """Retorna o correlation ID atual ou cria um novo"""
        if not hasattr(cls._local, 'correlation_id'):
            cls._local.correlation_id = str(uuid.uuid4())
        return cls._local.correlation_id

    @classmethod
    def set_id(cls, correlation_id: str):
        """Define o correlation ID"""
        cls._local.correlation_id = correlation_id

    @classmethod
    def clear(cls):
        """Limpa o correlation ID"""
        if hasattr(cls._local, 'correlation_id'):
            delattr(cls._local, 'correlation_id')


def with_correlation_id(f):
    """Decorator que adiciona correlation ID ao contexto"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        correlation_id = CorrelationContext.get_id()
        logger.info(
            f"Starting {f.__name__}",
            correlation_id=correlation_id,
            function=f.__name__
        )

        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            duration = (time.time() - start_time) * 1000  # ms

            metrics.timing(f"function.{f.__name__}", duration)
            logger.info(
                f"Completed {f.__name__}",
                correlation_id=correlation_id,
                duration_ms=round(duration, 2)
            )

            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            metrics.error(f"function.{f.__name__}")

            logger.error(
                f"Failed {f.__name__}: {str(e)}",
                correlation_id=correlation_id,
                duration_ms=round(duration, 2),
                exception=str(e)
            )
            raise
        finally:
            CorrelationContext.clear()

    return wrapper


# ===================================
# Monitoring de Performance
# ===================================

class PerformanceMonitor:
    """Monitor de performance para operações"""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.correlation_id = None

    def __enter__(self):
        self.start_time = time.time()
        self.correlation_id = CorrelationContext.get_id()

        logger.debug(
            f"Performance monitoring started: {self.operation_name}",
            correlation_id=self.correlation_id
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000  # ms

        if exc_type is None:
            # Sucesso
            metrics.timing(f"operation.{self.operation_name}", duration)
            logger.info(
                f"Performance: {self.operation_name}",
                correlation_id=self.correlation_id,
                duration_ms=round(duration, 2),
                status="success"
            )
        else:
            # Erro
            metrics.error(f"operation.{self.operation_name}")
            logger.error(
                f"Performance: {self.operation_name} failed",
                correlation_id=self.correlation_id,
                duration_ms=round(duration, 2),
                status="error",
                exception=str(exc_val)
            )


# ===================================
# Analytics e Insights
# ===================================

class ConversationAnalytics:
    """Analytics de conversações do bot"""

    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()

    def start_session(self, user_id: str):
        """Inicia uma nova sessão de conversa"""
        with self.lock:
            self.sessions[user_id] = {
                'start_time': time.time(),
                'messages': 0,
                'state_transitions': [],
                'errors': 0,
                'completed': False
            }

            metrics.increment('conversation.started')
            logger.info("Conversation started", user_id=user_id)

    def track_message(self, user_id: str, message_type: str):
        """Registra uma mensagem na conversa"""
        with self.lock:
            if user_id in self.sessions:
                self.sessions[user_id]['messages'] += 1
                metrics.increment(f'message.{message_type}')

    def track_state_transition(self, user_id: str, from_state: str, to_state: str):
        """Registra transição de estado"""
        with self.lock:
            if user_id in self.sessions:
                transition = {
                    'from': from_state,
                    'to': to_state,
                    'timestamp': time.time()
                }
                self.sessions[user_id]['state_transitions'].append(transition)

                logger.info(
                    "State transition",
                    user_id=user_id,
                    from_state=from_state,
                    to_state=to_state
                )

                metrics.increment(f'state.{to_state}')

    def track_error(self, user_id: str, error_type: str):
        """Registra erro na conversa"""
        with self.lock:
            if user_id in self.sessions:
                self.sessions[user_id]['errors'] += 1

            metrics.increment(f'error.{error_type}')
            logger.error("Conversation error", user_id=user_id, error_type=error_type)

    def complete_session(self, user_id: str, success: bool = True):
        """Marca sessão como completa"""
        with self.lock:
            if user_id in self.sessions:
                session = self.sessions[user_id]
                session['completed'] = True
                session['success'] = success
                session['duration'] = time.time() - session['start_time']

                metrics.timing('conversation.duration', session['duration'] * 1000)
                metrics.increment('conversation.completed' if success else 'conversation.abandoned')

                logger.info(
                    "Conversation completed",
                    user_id=user_id,
                    duration_seconds=round(session['duration'], 2),
                    messages=session['messages'],
                    success=success
                )

    def get_session_summary(self, user_id: str) -> Optional[Dict]:
        """Retorna resumo da sessão"""
        with self.lock:
            return self.sessions.get(user_id)


# Instância global de analytics
analytics = ConversationAnalytics()


# ===================================
# Health Check Avançado
# ===================================

class HealthChecker:
    """Sistema de health check com múltiplas verificações"""

    def __init__(self):
        self.checks = {}
        self.last_check = None

    def register_check(self, name: str, check_func):
        """Registra uma função de health check"""
        self.checks[name] = check_func

    def run_checks(self) -> Dict[str, Any]:
        """Executa todos os health checks"""
        results = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }

        all_healthy = True

        for name, check_func in self.checks.items():
            try:
                start = time.time()
                result = check_func()
                duration = (time.time() - start) * 1000

                results['checks'][name] = {
                    'status': 'pass' if result else 'fail',
                    'duration_ms': round(duration, 2)
                }

                if not result:
                    all_healthy = False
            except Exception as e:
                results['checks'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
                all_healthy = False

        if not all_healthy:
            results['status'] = 'degraded'

        self.last_check = results
        return results


# Instância global de health checker
health_checker = HealthChecker()


# ===================================
# Funções Auxiliares
# ===================================

def log_conversation_event(
    event_type: str,
    user_id: str,
    state: Optional[str] = None,
    **kwargs
):
    """Helper para logar eventos de conversa"""
    logger.info(
        f"Conversation event: {event_type}",
        correlation_id=CorrelationContext.get_id(),
        event_type=event_type,
        user_id=user_id,
        state=state,
        **kwargs
    )

    metrics.increment(f'conversation.event.{event_type}')


def log_api_call(
    service: str,
    endpoint: str,
    status_code: int,
    duration_ms: float,
    **kwargs
):
    """Helper para logar chamadas de API externa"""
    logger.info(
        f"API call: {service}/{endpoint}",
        correlation_id=CorrelationContext.get_id(),
        service=service,
        endpoint=endpoint,
        status_code=status_code,
        duration_ms=duration_ms,
        **kwargs
    )

    metrics.timing(f'api.{service}.{endpoint}', duration_ms)
    if status_code >= 400:
        metrics.error(f'api.{service}')


# ===================================
# Inicialização
# ===================================

def initialize_observability():
    """Inicializa sistema de observabilidade"""
    logger.info("Observability system initialized")

    # Registrar health checks básicos
    def check_logs():
        return os.path.exists(LOG_FILE)

    health_checker.register_check('logs', check_logs)

    logger.info("Health checks registered")


# Inicializar automaticamente
initialize_observability()
