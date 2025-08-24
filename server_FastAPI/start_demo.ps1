#!/usr/bin/env powershell

Write-Host "====================================================" -ForegroundColor Blue
Write-Host "           OmniSearch AI Demo Startup" -ForegroundColor Blue
Write-Host "====================================================" -ForegroundColor Blue

Write-Host "`n🔍 Running system diagnostics..." -ForegroundColor Yellow
python diagnose_resources.py

Write-Host "`n🔧 Starting FastAPI Server (Safe Demo Mode)..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`n🚀 Starting services..." -ForegroundColor Yellow

# Start FastAPI server in new PowerShell window
$fastApiScript = @"
Set-Location '$PWD'
Write-Host 'Starting FastAPI Server...' -ForegroundColor Green
python run_server.py --safe-demo --port 8000
Read-Host 'Press Enter to close'
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $fastApiScript -WindowStyle Normal

# Wait 5 seconds for server to start
Write-Host "⏱️ Waiting 5 seconds for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Streamlit frontend in new PowerShell window
$streamlitScript = @"
Set-Location '$PWD\..\streamlit_frontend'
Write-Host 'Starting Streamlit Frontend...' -ForegroundColor Green
streamlit run app.py --server.port 8501
Read-Host 'Press Enter to close'
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $streamlitScript -WindowStyle Normal

Write-Host "`n✅ Both services are starting!" -ForegroundColor Green
Write-Host "`n📊 Access Points:" -ForegroundColor Blue
Write-Host "   FastAPI Server: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan  
Write-Host "   Streamlit Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "`nTo stop services, close the PowerShell windows" -ForegroundColor Red
Write-Host "`nDemo ready! Open your browser and navigate to the URLs above." -ForegroundColor Magenta

Read-Host "`nPress Enter to exit this launcher"
