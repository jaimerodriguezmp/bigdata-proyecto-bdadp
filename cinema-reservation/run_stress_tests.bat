@echo off
echo ============================================
echo  STRESS TESTS - RESERVATION SYSTEM
echo  Make sure Cassandra nodes are running
echo  (start_nodes.bat)
echo ============================================
python stress_tests.py
pause
