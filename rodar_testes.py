#!/usr/bin/env python3
"""
Script para rodar testes do Bot Travessia dos Sonhos

Uso:
    python rodar_testes.py              # Roda todos os testes
    python rodar_testes.py --rapido     # Roda apenas testes rápidos
    python rodar_testes.py --html       # Gera relatório HTML
    python rodar_testes.py --cobertura  # Mostra cobertura de código
"""

import subprocess
import sys
import os


def print_header(texto):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"  {texto}")
    print("=" * 70 + "\n")


def instalar_dependencias():
    """Instala dependências de teste"""
    print_header("INSTALANDO DEPENDÊNCIAS")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "pytest", "pytest-cov", "pytest-html"],
            check=True
        )
        print("✅ Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError:
        print("⚠️  Erro ao instalar dependências. Continuando mesmo assim...")


def rodar_testes(args):
    """Roda os testes com pytest"""
    print_header("EXECUTANDO TESTES")

    # Monta comando base
    cmd = [sys.executable, "-m", "pytest", "test_bot_fluxo.py", "-v"]

    # Adiciona flags baseado nos argumentos
    if "--rapido" in args:
        cmd.extend(["-m", "not slow"])
        print("🏃 Modo rápido: pulando testes lentos\n")

    if "--html" in args or "--relatorio" in args:
        cmd.extend(["--html=relatorio_testes.html", "--self-contained-html"])
        print("📊 Gerando relatório HTML\n")

    if "--cobertura" in args or "--cov" in args:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
        print("📈 Analisando cobertura de código\n")

    # Formatação de saída
    cmd.append("--tb=short")

    # Executa
    try:
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            print_header("✅ TODOS OS TESTES PASSARAM!")
        else:
            print_header("⚠️  ALGUNS TESTES FALHARAM")
            print(f"Código de retorno: {result.returncode}")

        return result.returncode

    except Exception as e:
        print_header("❌ ERRO AO EXECUTAR TESTES")
        print(f"Erro: {e}")
        return 1


def exibir_ajuda():
    """Mostra ajuda de uso"""
    print(__doc__)


def main():
    """Função principal"""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        exibir_ajuda()
        return 0

    # Instala dependências se necessário
    if "--sem-instalar" not in args:
        instalar_dependencias()

    # Roda os testes
    codigo_retorno = rodar_testes(args)

    # Mostra arquivos gerados
    print("\n" + "-" * 70)
    print("📁 ARQUIVOS GERADOS:")

    if os.path.exists("relatorio_testes.html"):
        print("   ✅ relatorio_testes.html - Relatório visual dos testes")

    if os.path.exists("htmlcov/index.html"):
        print("   ✅ htmlcov/index.html - Relatório de cobertura de código")

    print("-" * 70 + "\n")

    return codigo_retorno


if __name__ == "__main__":
    sys.exit(main())
