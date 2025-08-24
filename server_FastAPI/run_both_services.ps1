#!/usr/bin/env powershell

Write-Host "🚀 Starting OmniSearch AI Full-Stack Demo" -ForegroundColor Blue
Write-Host "=========================================" -ForegroundColor Blue

# Check if we're in the right directory
if (!(Test-Path "app/main.py")) {
    Write-Host "❌ Please run this script from the server_FastAPI directory" -ForegroundColor Red
    exit 1
}

# Run diagnostics first
Write-Host "`n🔍 Running system diagnostics..." -ForegroundColor Yellow
python diagnose_resources.py --quiet

Write-Host "`n🖥️  Starting FastAPI Server (Port 8000)..." -ForegroundColor Green

# Start FastAPI server in background
$serverJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python run_server.py --safe-demo --port 8000 --no-reload
}

# Wait for server to start
Write-Host "⏱️  Waiting for server startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test server connectivity
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ FastAPI Server is running at http://localhost:8000" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  FastAPI Server starting... (may take a moment)" -ForegroundColor Yellow
}

Write-Host "`n🌐 Starting Streamlit Frontend (Port 8501)..." -ForegroundColor Green

# Start Streamlit in background
$streamlitJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWD\..\streamlit_frontend"
    streamlit run app.py --server.port 8501 --server.headless true
}

# Wait for Streamlit to start
Write-Host "⏱️  Waiting for Streamlit startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test Streamlit connectivity
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Streamlit Frontend is running at http://localhost:8501" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Streamlit Frontend starting... (may take a moment)" -ForegroundColor Yellow
}

Write-Host "`n🎉 Both services are now running!" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Blue
Write-Host "📊 ACCESS POINTS:" -ForegroundColor Cyan
Write-Host "   🔍 Streamlit UI:    http://localhost:8501" -ForegroundColor White
Write-Host "   ⚡ FastAPI Server:  http://localhost:8000" -ForegroundColor White
Write-Host "   📖 API Docs:        http://localhost:8000/docs" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Blue

Write-Host "`n🚀 Demo is ready! Open your browser and navigate to:" -ForegroundColor Green
Write-Host "   👆 http://localhost:8501 (Main Interface)" -ForegroundColor Yellow

Write-Host "`n📋 Service Status:" -ForegroundColor Cyan
Write-Host "   FastAPI Job ID: $($serverJob.Id)" -ForegroundColor Gray
Write-Host "   Streamlit Job ID: $($streamlitJob.Id)" -ForegroundColor Gray

Write-Host "`n🛑 To stop services:" -ForegroundColor Red
Write-Host "   Stop-Job $($serverJob.Id); Stop-Job $($streamlitJob.Id)" -ForegroundColor Gray
Write-Host "   Or press Ctrl+C and close terminal" -ForegroundColor Gray

Write-Host "`n💡 Monitor logs with:" -ForegroundColor Blue
Write-Host "   Receive-Job $($serverJob.Id) -Keep" -ForegroundColor Gray
Write-Host "   Receive-Job $($streamlitJob.Id) -Keep" -ForegroundColor Gray

# Keep script running
Write-Host "`n⌨️  Press Ctrl+C to stop all services..." -ForegroundColor Yellow

try {
    # Keep the jobs alive
    while ($true) {
        Start-Sleep -Seconds 10
        
        # Check job status
        $serverState = (Get-Job $serverJob.Id).State
        $streamlitState = (Get-Job $streamlitJob.Id).State
        
        if ($serverState -eq "Failed" -or $streamlitState -eq "Failed") {
            Write-Host "❌ One or more services failed. Check logs:" -ForegroundColor Red
            if ($serverState -eq "Failed") {
                Write-Host "FastAPI Error:" -ForegroundColor Red
                Receive-Job $serverJob.Id
            }
            if ($streamlitState -eq "Failed") {
                Write-Host "Streamlit Error:" -ForegroundColor Red
                Receive-Job $streamlitJob.Id
            }
            break
        }
    }
} finally {
    Write-Host "`nStopping services..." -ForegroundColor Red
    Stop-Job $serverJob.Id -ErrorAction SilentlyContinue
    Stop-Job $streamlitJob.Id -ErrorAction SilentlyContinue
    Remove-Job $serverJob.Id -ErrorAction SilentlyContinue
    Remove-Job $streamlitJob.Id -ErrorAction SilentlyContinue
    Write-Host "✅ Services stopped" -ForegroundColor Green
}
