"""
Rotas do Dashboard Web - Bot Travessia dos Sonhos
API endpoints para alimentar o dashboard de observabilidade
"""

from flask import Blueprint, render_template, jsonify
import os
import json
from datetime import datetime, timedelta

# Importa funções do database.py que já suportam PostgreSQL/SQLite
from database import get_connection, get_cursor, USE_POSTGRES

# Blueprint para rotas do dashboard
dashboard_bp = Blueprint('dashboard', __name__)

# Paths
DB_PATH = "travessia_bot.db"
METRICS_FILE = "logs/metrics.json"


# ===================================
# Funções Auxiliares
# ===================================

def load_metrics():
    """Carrega métricas do arquivo JSON"""
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass

    return {
        'uptime_seconds': 0,
        'counters': {},
        'gauges': {},
        'timings': {}
    }


def get_database_stats():
    """Carrega estatísticas do banco de dados (PostgreSQL ou SQLite)"""
    try:
        with get_connection() as conn:
            cursor = get_cursor(conn)

            stats = {}

            # Total de clientes
            cursor.execute("SELECT COUNT(*) FROM clientes")
            result = cursor.fetchone()
            stats['total_clients'] = result['count'] if USE_POSTGRES else result[0]

            # Clientes nas últimas 24h
            if USE_POSTGRES:
                cursor.execute("""
                    SELECT COUNT(*) FROM clientes
                    WHERE ultima_interacao >= NOW() - INTERVAL '1 day'
                """)
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM clientes
                    WHERE datetime(ultima_interacao) >= datetime('now', '-1 day')
                """)
            result = cursor.fetchone()
            stats['clients_24h'] = result['count'] if USE_POSTGRES else result[0]

            # Mensagens nas últimas 24h
            if USE_POSTGRES:
                cursor.execute("""
                    SELECT COUNT(*) FROM mensagens
                    WHERE timestamp >= NOW() - INTERVAL '1 day'
                """)
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM mensagens
                    WHERE datetime(timestamp) >= datetime('now', '-1 day')
                """)
            result = cursor.fetchone()
            stats['messages_24h'] = result['count'] if USE_POSTGRES else result[0]

            # Taxa de conversão (clientes que solicitaram atendimento)
            cursor.execute(
                "SELECT COUNT(*) FROM clientes WHERE estado = %s" if USE_POSTGRES
                else "SELECT COUNT(*) FROM clientes WHERE estado = ?",
                ('atendimento_solicitado',)
            )
            result = cursor.fetchone()
            completed = result['count'] if USE_POSTGRES else result[0]
            stats['conversion_rate'] = (completed / stats['total_clients'] * 100) if stats['total_clients'] > 0 else 0

            # Clientes por estado
            cursor.execute("SELECT estado, COUNT(*) as count FROM clientes WHERE estado IS NOT NULL GROUP BY estado")
            results = cursor.fetchall()
            if USE_POSTGRES:
                stats['clients_by_state'] = {row['estado']: row['count'] for row in results}
            else:
                stats['clients_by_state'] = dict(results)

            # Atividade por hora (últimas 24h)
            if USE_POSTGRES:
                cursor.execute("""
                    SELECT
                        TO_CHAR(timestamp, 'HH24') as hour,
                        COUNT(*) as count
                    FROM mensagens
                    WHERE timestamp >= NOW() - INTERVAL '1 day'
                    GROUP BY TO_CHAR(timestamp, 'HH24')
                    ORDER BY hour
                """)
            else:
                cursor.execute("""
                    SELECT
                        strftime('%H', timestamp) as hour,
                        COUNT(*) as count
                    FROM mensagens
                    WHERE datetime(timestamp) >= datetime('now', '-1 day')
                    GROUP BY hour
                    ORDER BY hour
                """)
            results = cursor.fetchall()
            if USE_POSTGRES:
                stats['activity_by_hour'] = {row['hour']: row['count'] for row in results}
            else:
                stats['activity_by_hour'] = dict(results)

            return stats

    except Exception as e:
        print(f"Erro ao carregar stats do banco: {e}")
        import traceback
        traceback.print_exc()
        return {
            'total_clients': 0,
            'clients_24h': 0,
            'messages_24h': 0,
            'conversion_rate': 0,
            'clients_by_state': {},
            'activity_by_hour': {}
        }


def get_health_status():
    """Verifica saúde dos componentes"""
    # Database check - tenta conexão
    database_ok = False
    try:
        with get_connection() as conn:
            cursor = get_cursor(conn)
            cursor.execute("SELECT 1")
            database_ok = True
    except:
        database_ok = False

    return {
        'database': database_ok,
        'logs': os.path.exists('logs/bot.log'),
        'metrics': os.path.exists(METRICS_FILE)
    }


# ===================================
# Rotas
# ===================================

@dashboard_bp.route('/dashboard')
def dashboard():
    """Página principal do dashboard"""
    return render_template('dashboard.html')


@dashboard_bp.route('/api/dashboard/data')
def dashboard_data():
    """API endpoint com todos os dados do dashboard"""
    metrics = load_metrics()
    db_stats = get_database_stats()
    health = get_health_status()

    return jsonify({
        'metrics': metrics,
        'db_stats': db_stats,
        'health': health,
        'timestamp': datetime.now().isoformat()
    })


@dashboard_bp.route('/api/dashboard/metrics')
def api_metrics():
    """Endpoint específico para métricas"""
    return jsonify(load_metrics())


@dashboard_bp.route('/api/dashboard/stats')
def api_stats():
    """Endpoint específico para estatísticas do banco"""
    return jsonify(get_database_stats())


@dashboard_bp.route('/api/dashboard/health')
def api_health():
    """Endpoint específico para health checks"""
    health = get_health_status()

    all_healthy = all(health.values())

    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'components': health,
        'timestamp': datetime.now().isoformat()
    })


# ===================================
# Health Check Detalhado
# ===================================

@dashboard_bp.route('/api/health/detailed')
def detailed_health():
    """Health check detalhado com métricas adicionais"""
    health = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }

    # Database check (PostgreSQL ou SQLite)
    try:
        with get_connection() as conn:
            cursor = get_cursor(conn)
            cursor.execute("SELECT COUNT(*) FROM clientes")
            result = cursor.fetchone()
            count = result['count'] if USE_POSTGRES else result[0]

            db_type = "PostgreSQL" if USE_POSTGRES else "SQLite"
            health['checks']['database'] = {
                'status': 'pass',
                'message': f'{count} clientes registrados ({db_type})'
            }
    except Exception as e:
        health['checks']['database'] = {
            'status': 'error',
            'message': str(e)
        }
        health['status'] = 'degraded'

    # Logs check
    if os.path.exists('logs/bot.log'):
        log_size = os.path.getsize('logs/bot.log') / 1024 / 1024  # MB
        health['checks']['logs'] = {
            'status': 'pass',
            'message': f'Log file size: {log_size:.2f} MB'
        }
    else:
        health['checks']['logs'] = {
            'status': 'fail',
            'message': 'Log file not found'
        }
        health['status'] = 'degraded'

    # Metrics check
    if os.path.exists(METRICS_FILE):
        metrics = load_metrics()
        uptime_hours = metrics.get('uptime_seconds', 0) / 3600
        health['checks']['metrics'] = {
            'status': 'pass',
            'message': f'Uptime: {uptime_hours:.1f}h'
        }
    else:
        health['checks']['metrics'] = {
            'status': 'warn',
            'message': 'Metrics file not found (will be created)'
        }

    return jsonify(health)
