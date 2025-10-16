"""
Rotas do Dashboard Web - Bot Travessia dos Sonhos
API endpoints para alimentar o dashboard de observabilidade
"""

from flask import Blueprint, render_template, jsonify
import os
import json
import sqlite3
from datetime import datetime, timedelta

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
    """Carrega estatísticas do banco de dados"""
    if not os.path.exists(DB_PATH):
        return {
            'total_clients': 0,
            'clients_24h': 0,
            'messages_24h': 0,
            'conversion_rate': 0,
            'clients_by_state': {},
            'activity_by_hour': {}
        }

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        stats = {}

        # Total de clientes
        cursor.execute("SELECT COUNT(*) FROM clientes")
        stats['total_clients'] = cursor.fetchone()[0]

        # Clientes nas últimas 24h
        cursor.execute("""
            SELECT COUNT(*) FROM clientes
            WHERE datetime(ultima_interacao) >= datetime('now', '-1 day')
        """)
        stats['clients_24h'] = cursor.fetchone()[0]

        # Mensagens nas últimas 24h
        cursor.execute("""
            SELECT COUNT(*) FROM mensagens
            WHERE datetime(timestamp) >= datetime('now', '-1 day')
        """)
        stats['messages_24h'] = cursor.fetchone()[0]

        # Taxa de conversão
        cursor.execute("""
            SELECT COUNT(*) FROM clientes
            WHERE json_extract(dados, '$.estado') = 'atendimento_solicitado'
        """)
        completed = cursor.fetchone()[0]
        stats['conversion_rate'] = (completed / stats['total_clients'] * 100) if stats['total_clients'] > 0 else 0

        # Clientes por estado
        cursor.execute("""
            SELECT
                json_extract(dados, '$.estado') as estado,
                COUNT(*) as count
            FROM clientes
            WHERE dados IS NOT NULL AND json_extract(dados, '$.estado') IS NOT NULL
            GROUP BY estado
        """)
        stats['clients_by_state'] = dict(cursor.fetchall())

        # Atividade por hora (últimas 24h)
        cursor.execute("""
            SELECT
                strftime('%H', timestamp) as hour,
                COUNT(*) as count
            FROM mensagens
            WHERE datetime(timestamp) >= datetime('now', '-1 day')
            GROUP BY hour
            ORDER BY hour
        """)
        stats['activity_by_hour'] = dict(cursor.fetchall())

        conn.close()
        return stats

    except Exception as e:
        print(f"Erro ao carregar stats do banco: {e}")
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
    return {
        'database': os.path.exists(DB_PATH),
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

    # Database check
    try:
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clientes")
            count = cursor.fetchone()[0]
            conn.close()

            health['checks']['database'] = {
                'status': 'pass',
                'message': f'{count} clientes registrados'
            }
        else:
            health['checks']['database'] = {
                'status': 'fail',
                'message': 'Database file not found'
            }
            health['status'] = 'degraded'
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
