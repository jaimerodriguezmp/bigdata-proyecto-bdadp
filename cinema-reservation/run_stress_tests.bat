@echo off
echo ============================================
echo  PRUEBAS DE STRESS - SISTEMA DE RESERVAS
echo  Asegurate de que los nodos Cassandra
echo  esten corriendo (start_nodes.bat)
echo ============================================
python stress_tests.py
pause
