"""
Database Layer - Bot Travessia dos Sonhos
Suporta SQLite (desenvolvimento) e PostgreSQL (produção)
"""

import json
import os
from datetime import datetime
from contextlib import contextmanager

# Detecta qual banco usar baseado na variável DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    # PostgreSQL
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import pool
    USE_POSTGRES = True
    print("🐘 Usando PostgreSQL")

    # Connection Pool - mantém 5 conexões sempre abertas, máximo 20
    try:
        connection_pool = pool.ThreadedConnectionPool(
            minconn=5,
            maxconn=20,
            dsn=DATABASE_URL,
            sslmode='require'
        )
        print("✅ Connection pool criado: 5-20 conexões")
    except Exception as e:
        print(f"❌ Erro ao criar connection pool: {e}")
        connection_pool = None
else:
    # SQLite (desenvolvimento)
    import sqlite3
    from config import DB_PATH
    USE_POSTGRES = False
    connection_pool = None
    print("📁 Usando SQLite (desenvolvimento)")


# ===================================
# Connection Manager
# ===================================

@contextmanager
def get_connection():
    """Context manager para gerenciar conexões de banco com pooling"""
    if USE_POSTGRES:
        # Usa connection pool se disponível
        if connection_pool:
            conn = connection_pool.getconn()
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                # Devolve conexão ao pool ao invés de fechar
                connection_pool.putconn(conn)
        else:
            # Fallback: conexão direta sem pool
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
    else:
        conn = sqlite3.connect(DB_PATH)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


def get_cursor(conn):
    """Retorna cursor apropriado para o tipo de banco"""
    if USE_POSTGRES:
        return conn.cursor(cursor_factory=RealDictCursor)
    else:
        return conn.cursor()


# ===================================
# Inicialização
# ===================================

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    with get_connection() as conn:
        cursor = get_cursor(conn)

        if USE_POSTGRES:
            # PostgreSQL
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                telefone TEXT PRIMARY KEY,
                nome TEXT,
                email TEXT,
                estado TEXT,
                dados JSONB,
                ultima_interacao TIMESTAMP
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensagens (
                id SERIAL PRIMARY KEY,
                telefone TEXT,
                mensagem_cliente TEXT,
                mensagem_bot TEXT,
                timestamp TIMESTAMP,
                precisa_atendimento BOOLEAN DEFAULT FALSE
            )
            ''')

            # Criar índices para performance
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_mensagens_telefone
            ON mensagens(telefone)
            ''')

            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_mensagens_timestamp
            ON mensagens(timestamp DESC)
            ''')

        else:
            # SQLite
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

    print("✅ Banco de dados inicializado com sucesso!")


# ===================================
# Operações de Cliente
# ===================================

def get_client_state(telefone):
    """Obtém o estado do cliente"""
    with get_connection() as conn:
        cursor = get_cursor(conn)

        cursor.execute(
            "SELECT nome, email, estado, dados FROM clientes WHERE telefone = %s" if USE_POSTGRES
            else "SELECT nome, email, estado, dados FROM clientes WHERE telefone = ?",
            (telefone,)
        )

        result = cursor.fetchone()

        if not result:
            return None

        if USE_POSTGRES:
            # PostgreSQL retorna dict
            nome = result['nome']
            email = result['email']
            estado = result['estado']
            dados = result['dados'] if result['dados'] else {}
        else:
            # SQLite retorna tuple
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
    with get_connection() as conn:
        cursor = get_cursor(conn)

        nome = estado_dict.get("nome")
        email = estado_dict.get("email")
        estado = estado_dict.get("estado")

        # Remove campos que são colunas da tabela
        dados_dict = {k: v for k, v in estado_dict.items() if k not in ["nome", "email", "estado"]}

        if USE_POSTGRES:
            # PostgreSQL usa JSONB
            cursor.execute(
                """
                INSERT INTO clientes
                (telefone, nome, email, estado, dados, ultima_interacao)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (telefone) DO UPDATE SET
                    nome = EXCLUDED.nome,
                    email = EXCLUDED.email,
                    estado = EXCLUDED.estado,
                    dados = EXCLUDED.dados,
                    ultima_interacao = EXCLUDED.ultima_interacao
                """,
                (telefone, nome, email, estado, json.dumps(dados_dict), datetime.now())
            )
        else:
            # SQLite
            dados_json = json.dumps(dados_dict)
            cursor.execute(
                """
                INSERT OR REPLACE INTO clientes
                (telefone, nome, email, estado, dados, ultima_interacao)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (telefone, nome, email, estado, dados_json, datetime.now())
            )


# ===================================
# Operações de Mensagens
# ===================================

def save_message(telefone, mensagem_cliente, mensagem_bot, precisa_atendimento=False, info_adicional=None):
    """Salva a mensagem no histórico"""
    with get_connection() as conn:
        cursor = get_cursor(conn)

        if USE_POSTGRES:
            cursor.execute(
                """
                INSERT INTO mensagens
                (telefone, mensagem_cliente, mensagem_bot, timestamp, precisa_atendimento)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (telefone, mensagem_cliente, mensagem_bot, datetime.now(), precisa_atendimento)
            )
        else:
            cursor.execute(
                """
                INSERT INTO mensagens
                (telefone, mensagem_cliente, mensagem_bot, timestamp, precisa_atendimento)
                VALUES (?, ?, ?, ?, ?)
                """,
                (telefone, mensagem_cliente, mensagem_bot, datetime.now(), precisa_atendimento)
            )


def get_client_conversation(telefone, limit=10):
    """Obtém as últimas mensagens do cliente"""
    with get_connection() as conn:
        cursor = get_cursor(conn)

        cursor.execute(
            """
            SELECT mensagem_cliente, mensagem_bot, timestamp
            FROM mensagens
            WHERE telefone = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """ if USE_POSTGRES else """
            SELECT mensagem_cliente, mensagem_bot, timestamp
            FROM mensagens
            WHERE telefone = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (telefone, limit)
        )

        result = cursor.fetchall()

        if USE_POSTGRES:
            return [
                {
                    "cliente": msg['mensagem_cliente'],
                    "bot": msg['mensagem_bot'],
                    "timestamp": msg['timestamp']
                }
                for msg in result
            ]
        else:
            return [
                {
                    "cliente": msg_cliente,
                    "bot": msg_bot,
                    "timestamp": timestamp
                }
                for msg_cliente, msg_bot, timestamp in result
            ]


# ===================================
# Estatísticas e Queries Complexas
# ===================================

def get_database_stats():
    """Retorna estatísticas do banco de dados"""
    with get_connection() as conn:
        cursor = get_cursor(conn)

        stats = {}

        # Total de clientes
        cursor.execute("SELECT COUNT(*) FROM clientes")
        result = cursor.fetchone()
        stats['total_clients'] = result[0] if not USE_POSTGRES else result['count']

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
        stats['messages_24h'] = result[0] if not USE_POSTGRES else result['count']

        # Clientes em atendimento
        cursor.execute("""
            SELECT COUNT(*) FROM clientes
            WHERE estado = %s
        """ if USE_POSTGRES else """
            SELECT COUNT(*) FROM clientes
            WHERE estado = ?
        """, ('atendimento_solicitado',))
        result = cursor.fetchone()
        stats['clients_waiting'] = result[0] if not USE_POSTGRES else result['count']

        return stats


# ===================================
# Migração de Dados
# ===================================

def migrate_from_sqlite(sqlite_path):
    """Migra dados do SQLite para PostgreSQL"""
    if not USE_POSTGRES:
        print("⚠️ Esta função só funciona quando DATABASE_URL está configurado")
        return False

    if not os.path.exists(sqlite_path):
        print(f"⚠️ Arquivo SQLite não encontrado: {sqlite_path}")
        return False

    print(f"🔄 Iniciando migração de {sqlite_path}...")

    # Conectar ao SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()

    try:
        with get_connection() as pg_conn:
            pg_cursor = pg_conn.cursor()

            # Migrar clientes
            sqlite_cursor.execute("SELECT * FROM clientes")
            clientes = sqlite_cursor.fetchall()

            migrated_clients = 0
            for cliente in clientes:
                telefone, nome, email, estado, dados_json, ultima_interacao = cliente
                pg_cursor.execute(
                    """
                    INSERT INTO clientes
                    (telefone, nome, email, estado, dados, ultima_interacao)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (telefone) DO NOTHING
                    """,
                    (telefone, nome, email, estado, dados_json, ultima_interacao)
                )
                migrated_clients += 1

            print(f"✅ Migrados {migrated_clients} clientes")

            # Migrar mensagens
            sqlite_cursor.execute("SELECT telefone, mensagem_cliente, mensagem_bot, timestamp, precisa_atendimento FROM mensagens")
            mensagens = sqlite_cursor.fetchall()

            migrated_messages = 0
            for mensagem in mensagens:
                telefone, msg_cliente, msg_bot, timestamp, precisa_atend = mensagem
                pg_cursor.execute(
                    """
                    INSERT INTO mensagens
                    (telefone, mensagem_cliente, mensagem_bot, timestamp, precisa_atendimento)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (telefone, msg_cliente, msg_bot, timestamp, precisa_atend)
                )
                migrated_messages += 1

            print(f"✅ Migradas {migrated_messages} mensagens")

        print("✅ Migração concluída com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False
    finally:
        sqlite_conn.close()


# ===================================
# Teste de Conexão
# ===================================

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        with get_connection() as conn:
            cursor = get_cursor(conn)
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Conexão com banco de dados OK! Tipo: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
            return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Testando database layer...")
    test_connection()
    init_db()
