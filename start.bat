@echo off
echo Starting AI Agents Swarm System...
echo.

REM Set the working directory
cd /d "%~dp0"

REM Check if conda is available
conda --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Conda is not installed or not in PATH
    echo Please install Anaconda/Miniconda and try again
    pause
    exit /b 1
)

REM Check if ai environment exists
conda info --envs | findstr /i "ai" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: 'ai' conda environment not found
    echo Please create the environment first: conda create -n ai python=3.10
    pause
    exit /b 1
)

echo Installing/updating dependencies...
conda run --live-stream --name ai pip install -r requirements.txt

echo.
echo Starting API server...
start "API Server" cmd /c "conda run --live-stream --name ai python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for API server to start...
timeout /t 3 /nobreak >nul

echo.
echo Starting Streamlit Dashboard...
start "Streamlit Dashboard" cmd /c "conda run --live-stream --name ai streamlit run ui/dashboard.py --server.port 8501 --server.headless false"

echo Waiting for dashboard to start...
timeout /t 3 /nobreak >nul

echo.
echo Starting Agent Orchestrator...
start "Agent Orchestrator" cmd /c "conda run --live-stream --name ai python agents/main.py"

echo.
echo System started successfully!
echo - API Server: http://localhost:8000
echo - Dashboard: http://localhost:8501
echo.
echo Press any key to open dashboard in browser...
pause >nul

REM Open dashboard in default browser
start http://localhost:8501

echo.
echo All components are running. Press any key to exit...
pause >nul
