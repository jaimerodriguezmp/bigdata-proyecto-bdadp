@echo off
echo ============================================
echo  ANALISIS DE DATOS DE COCHES CON HADOOP
echo ============================================
echo 1. Ejecutar con Python (todos los analisis)
echo 2. Ejecutar con Python (modo interactivo)
echo 3. Ejecutar con Hadoop Streaming
echo 4. Regenerar dataset
echo 0. Salir
echo ============================================
set /p choice="Selecciona una opcion: "

if "%choice%"=="1" (
    python analysis.py
    pause
) else if "%choice%"=="2" (
    python analysis.py --interactive
    pause
) else if "%choice%"=="3" (
    python hadoop_runner.py
    pause
) else if "%choice%"=="4" (
    python generate_data.py
    pause
)
