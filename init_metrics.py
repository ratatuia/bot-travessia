"""
Inicializa sistema de métricas
Cria estrutura inicial de logs e métricas
"""

import os
import json
from datetime import datetime

# Criar diretórios
os.makedirs('logs', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Criar arquivo de métricas inicial
metrics_data = {
    'uptime_seconds': 0,
    'counters': {},
    'gauges': {},
    'timings': {},
    'saved_at': datetime.now().isoformat()
}

with open('logs/metrics.json', 'w', encoding='utf-8') as f:
    json.dump(metrics_data, f, indent=2)

print("Sistema de metricas inicializado!")
print("Arquivo criado: logs/metrics.json")
print("Diretorios criados: logs/, templates/")
