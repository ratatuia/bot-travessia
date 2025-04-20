import json
import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        telefone TEXT PRIMARY KEY,
        nome TEXT,
        email TEXT,
        estado TEXT,
        dados TEXT,
        ultima_interacao TIMESTAMP
    )
    ''')
    
    # Tabela de mensagens
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mensagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telefone TEXT,
        mensagem_cliente TEXT,
        mensagem_bot TEXT,
        timestamp TIMESTAMP,
        precisa_atendimento BOOLEAN DEFAULT 0
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

def get_client_state(telefone):
    """Obtém o estado do cliente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT nome, email, estado, dados FROM clientes WHERE telefone = ?", (telefone,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    nome, email, estado, dados_json = result
    dados = json.loads(dados_json) if dados_json else {}
    
    estado_completo = {
        "nome": nome,
        "email": email,
        "estado": estado
    }
    estado_completo.update(dados)
    
    return estado_completo

def update_client_state(telefone, estado_dict):
    """Atualiza o estado do cliente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    nome = estado_dict.get("nome")
    email = estado_dict.get("email")
    estado = estado_dict.get("estado")
    
    # Remove campos que são colunas da tabela
    dados_dict = {k: v for k, v in estado_dict.items() if k not in ["nome", "email", "estado"]}
    dados_json = json.dumps(dados_dict)
    
    cursor.execute(
        """
        INSERT OR REPLACE INTO clientes 
        (telefone, nome, email, estado, dados, ultima_interacao) 
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (telefone, nome, email, estado, dados_json, datetime.now())
    )
    
    conn.commit()
    conn.close()

def save_message(telefone, mensagem_cliente, mensagem_bot, precisa_atendimento=False, info_adicional=None):
    """Salva a mensagem no histórico"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO mensagens 
        (telefone, mensagem_cliente, mensagem_bot, timestamp, precisa_atendimento)
        VALUES (?, ?, ?, ?, ?)
        """,
        (telefone, mensagem_cliente, mensagem_bot, datetime.now(), precisa_atendimento)
    )
    
    conn.commit()
    conn.close()

def get_client_conversation(telefone, limit=10):
    """Obtém as últimas mensagens do cliente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT mensagem_cliente, mensagem_bot, timestamp 
        FROM mensagens 
        WHERE telefone = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
        """,
        (telefone, limit)
    )
    
    result = cursor.fetchall()
    conn.close()
    
    return [
        {
            "cliente": msg_cliente,
            "bot": msg_bot,
            "timestamp": timestamp
        }
        for msg_cliente, msg_bot, timestamp in result
    ]