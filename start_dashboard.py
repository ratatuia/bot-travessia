"""
Launcher para Dashboard - Bot Travessia dos Sonhos
Escolha entre dashboard web ou Streamlit
"""

import sys
import os

def main():
    print("=" * 60)
    print("  Bot Travessia dos Sonhos - Dashboard Launcher")
    print("=" * 60)
    print()
    print("Escolha o dashboard:")
    print()
    print("1. Dashboard Web (Integrado ao Flask)")
    print("   - Moderno e leve")
    print("   - Roda em /dashboard")
    print("   - Auto-refresh 30s")
    print()
    print("2. Dashboard Streamlit (Avançado)")
    print("   - Análises mais profundas")
    print("   - Filtros e exportação")
    print("   - 5 seções interativas")
    print()

    choice = input("Digite 1 ou 2: ").strip()

    if choice == "1":
        print("\n Iniciando bot com dashboard web...")
        print(" Acesse: http://localhost:5000/dashboard")
        print()
        os.system("python app.py")

    elif choice == "2":
        print("\n Iniciando dashboard Streamlit...")
        print(" Acesse: http://localhost:8501")
        print()
        os.system("streamlit run dashboard_observability.py")

    else:
        print("\n Opcao invalida!")
        sys.exit(1)

if __name__ == "__main__":
    main()
