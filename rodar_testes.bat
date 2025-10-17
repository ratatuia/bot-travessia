@echo off
echo ========================================
echo   TESTES DO BOT TRAVESSIA DOS SONHOS
echo ========================================
echo.

REM Instala dependências de teste se necessário
echo [1/3] Instalando dependencias de teste...
pip install -q pytest pytest-cov pytest-html

echo.
echo [2/3] Executando testes...
echo.

REM Roda os testes com relatório HTML
pytest test_bot_fluxo.py -v --html=relatorio_testes.html --self-contained-html --tb=short

echo.
echo [3/3] Testes finalizados!
echo.
echo Relatorio completo salvo em: relatorio_testes.html
echo Abra o arquivo no navegador para ver os resultados detalhados.
echo.
pause
