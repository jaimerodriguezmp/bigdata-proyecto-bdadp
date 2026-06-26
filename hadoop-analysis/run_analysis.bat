@echo off
echo ============================================
echo  CAR DATA ANALYSIS WITH HADOOP
echo ============================================
echo 1. Run with Python (all analyses)
echo 2. Run with Python (interactive mode)
echo 3. Run with Hadoop Streaming
echo 4. Regenerate dataset
echo 0. Exit
echo ============================================
set /p choice="Select an option: "

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
