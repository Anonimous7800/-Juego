@echo off
chcp 65001 > nul
title ☀ ^| Chronicles Of Two Suns T2
echo ========================================================
echo       ☀ CHRONICLES OF TWO SUNS T2 - PYGAME EDITION
echo ========================================================
echo Iniciando juego...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocurrio un error al iniciar. Asegurate de tener pygame instalado:
    echo pip install pygame-ce
    pause
)
