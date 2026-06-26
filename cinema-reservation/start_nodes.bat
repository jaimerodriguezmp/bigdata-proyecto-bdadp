@echo off
echo ============================================
echo  Starting Cassandra nodes for cinema reservation
echo ============================================
docker-compose up -d
echo.
echo Waiting for nodes to start...
echo (This may take up to 60 seconds)
echo.
echo To check status: docker-compose ps
echo To see logs: docker-compose logs -f
echo.
echo Once nodes are ready, run:
echo   run_app.bat
echo   run_stress_tests.bat
echo ============================================
pause
