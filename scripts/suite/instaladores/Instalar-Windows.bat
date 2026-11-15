@echo off
chcp 65001 >nul
title Island Crew Marketing Suite - Instalacion
echo.
echo  Island Crew Marketing Suite
echo  Instalando en tu ordenador, un momento...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1"
if errorlevel 1 (
  echo.
  echo  Algo ha fallado. Hazle una foto a esta pantalla y escribe a hola@islandcrew.es
  pause
)
