@echo off
echo ============================================
echo  Iniciando nodos Cassandra para reservas de cine
echo ============================================
docker-compose up -d
echo.
echo Esperando a que los nodos se inicien...
echo (Esto puede tomar hasta 60 segundos)
echo.
echo Para ver el estado: docker-compose ps
echo Para ver logs: docker-compose logs -f
echo.
echo Una vez que los nodos esten listos, ejecuta:
echo   run_app.bat
echo   run_stress_tests.bat
echo ============================================
pause
