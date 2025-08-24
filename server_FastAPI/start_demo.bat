@echo off
echo ====================================================
echo           OmniSearch AI Demo Startup
echo ====================================================

echo 🔍 Running system diagnostics...
python diagnose_resources.py

echo.
echo 🔧 Starting FastAPI Server (Safe Demo Mode)...
echo Server will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs

echo.
echo 🚀 Starting services...
echo.

REM Start FastAPI server in background
start "FastAPI Server" cmd /c "python run_server.py --safe-demo --port 8000 & pause"

REM Wait 5 seconds for server to start
timeout /t 5 /nobreak

REM Start Streamlit frontend
echo 🌐 Starting Streamlit Frontend...
echo Frontend will be available at: http://localhost:8501
cd ..\streamlit_frontend
start "Streamlit Frontend" cmd /c "streamlit run app.py --server.port 8501 & pause"

echo.
echo ✅ Both services are starting!
echo.
echo 📊 Access Points:
echo    FastAPI Server: http://localhost:8000
echo    API Documentation: http://localhost:8000/docs  
echo    Streamlit Frontend: http://localhost:8501
echo.
echo 🛑 To stop services, close the terminal windows
echo.
pause
