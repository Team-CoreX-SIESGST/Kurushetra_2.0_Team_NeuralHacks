# Test API Endpoints Script

Write-Host "=== API Endpoint Testing Started ===" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "✅ Health Check: $($healthResponse.status)" -ForegroundColor Green
    Write-Host "Services: $($healthResponse.services | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Supported Formats
Write-Host "`n2. Testing Supported Formats Endpoint..." -ForegroundColor Yellow
try {
    $formatsResponse = Invoke-RestMethod -Uri "http://localhost:8000/supported-formats" -Method GET
    Write-Host "✅ Supported Formats Retrieved" -ForegroundColor Green
    Write-Host "Formats: $($formatsResponse.supported_formats -join ', ')" -ForegroundColor Gray
} catch {
    Write-Host "❌ Supported Formats Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: File Processing (using System.Net.Http.HttpClient)
Write-Host "`n3. Testing File Processing Endpoint..." -ForegroundColor Yellow
try {
    Add-Type -AssemblyName System.Net.Http
    
    $httpClientHandler = New-Object System.Net.Http.HttpClientHandler
    $httpClient = New-Object System.Net.Http.HttpClient($httpClientHandler)
    
    $multipartContent = New-Object System.Net.Http.MultipartFormDataContent
    
    $fileContent = [System.IO.File]::ReadAllBytes("test_document.txt")
    $byteArrayContent = New-Object System.Net.Http.ByteArrayContent($fileContent)
    $byteArrayContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("text/plain")
    
    $multipartContent.Add($byteArrayContent, "file", "test_document.txt")
    
    $response = $httpClient.PostAsync("http://localhost:8000/process-file", $multipartContent).Result
    $responseContent = $response.Content.ReadAsStringAsync().Result
    
    if ($response.IsSuccessStatusCode) {
        Write-Host "✅ File Processing Successful" -ForegroundColor Green
        $jsonResponse = $responseContent | ConvertFrom-Json
        Write-Host "Content Type: $($jsonResponse.content_type)" -ForegroundColor Gray
        Write-Host "File Size: $($jsonResponse.file_metadata.file_size) bytes" -ForegroundColor Gray
    } else {
        Write-Host "❌ File Processing Failed: $($response.StatusCode)" -ForegroundColor Red
        Write-Host "Response: $responseContent" -ForegroundColor Red
    }
    
    $httpClient.Dispose()
} catch {
    Write-Host "❌ File Processing Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Process and Summarize
Write-Host "`n4. Testing Process and Summarize Endpoint..." -ForegroundColor Yellow
try {
    Add-Type -AssemblyName System.Net.Http
    
    $httpClientHandler = New-Object System.Net.Http.HttpClientHandler
    $httpClient = New-Object System.Net.Http.HttpClient($httpClientHandler)
    
    # Set a longer timeout for AI processing
    $httpClient.Timeout = [TimeSpan]::FromMinutes(2)
    
    $multipartContent = New-Object System.Net.Http.MultipartFormDataContent
    
    $fileContent = [System.IO.File]::ReadAllBytes("test_document.txt")
    $byteArrayContent = New-Object System.Net.Http.ByteArrayContent($fileContent)
    $byteArrayContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("text/plain")
    
    $multipartContent.Add($byteArrayContent, "file", "test_document.txt")
    
    Write-Host "Processing file with AI summarization (this may take a moment)..." -ForegroundColor Gray
    
    $response = $httpClient.PostAsync("http://localhost:8000/process-and-summarize", $multipartContent).Result
    $responseContent = $response.Content.ReadAsStringAsync().Result
    
    if ($response.IsSuccessStatusCode) {
        Write-Host "✅ Process and Summarize Successful" -ForegroundColor Green
        $jsonResponse = $responseContent | ConvertFrom-Json
        Write-Host "Generated Summaries:" -ForegroundColor Gray
        if ($jsonResponse.summary.summaries) {
            foreach ($summaryType in $jsonResponse.summary.summaries.PSObject.Properties.Name) {
                Write-Host "  - $summaryType" -ForegroundColor Gray
            }
        }
        if ($jsonResponse.summary.metadata) {
            Write-Host "Generated at: $($jsonResponse.summary.metadata.generated_at)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Process and Summarize Failed: $($response.StatusCode)" -ForegroundColor Red
        Write-Host "Response: $responseContent" -ForegroundColor Red
    }
    
    $httpClient.Dispose()
} catch {
    Write-Host "❌ Process and Summarize Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Process and Summarize with URLs (Enhanced Feature)
Write-Host "`n5. Testing Process and Summarize with URLs Endpoint..." -ForegroundColor Yellow
try {
    Add-Type -AssemblyName System.Net.Http
    
    $httpClientHandler = New-Object System.Net.Http.HttpClientHandler
    $httpClient = New-Object System.Net.Http.HttpClient($httpClientHandler)
    
    # Set a longer timeout for AI processing + web search
    $httpClient.Timeout = [TimeSpan]::FromMinutes(3)
    
    $multipartContent = New-Object System.Net.Http.MultipartFormDataContent
    
    $fileContent = [System.IO.File]::ReadAllBytes("test_document.txt")
    $byteArrayContent = New-Object System.Net.Http.ByteArrayContent($fileContent)
    $byteArrayContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("text/plain")
    
    $multipartContent.Add($byteArrayContent, "file", "test_document.txt")
    
    Write-Host "Processing file with AI summarization + web URLs (this may take longer)..." -ForegroundColor Gray
    
    $response = $httpClient.PostAsync("http://localhost:8000/process-and-summarize-with-urls", $multipartContent).Result
    $responseContent = $response.Content.ReadAsStringAsync().Result
    
    if ($response.IsSuccessStatusCode) {
        Write-Host "✅ Process and Summarize with URLs Successful" -ForegroundColor Green
        $jsonResponse = $responseContent | ConvertFrom-Json
        Write-Host "Generated Summaries:" -ForegroundColor Gray
        if ($jsonResponse.summary.summaries) {
            foreach ($summaryType in $jsonResponse.summary.summaries.PSObject.Properties.Name) {
                Write-Host "  - $summaryType" -ForegroundColor Gray
            }
        }
        if ($jsonResponse.summary.related_web_resources) {
            Write-Host "Related Web Resources Found:" -ForegroundColor Gray
            if ($jsonResponse.summary.related_web_resources.urls) {
                Write-Host "  Total URLs: $($jsonResponse.summary.related_web_resources.urls.Count)" -ForegroundColor Gray
                # Show first few URLs
                for ($i = 0; $i -lt [Math]::Min(3, $jsonResponse.summary.related_web_resources.urls.Count); $i++) {
                    $url = $jsonResponse.summary.related_web_resources.urls[$i]
                    Write-Host "  - $($url.title): $($url.url)" -ForegroundColor Gray
                }
            }
        }
        if ($jsonResponse.summary.metadata) {
            Write-Host "Generated at: $($jsonResponse.summary.metadata.generated_at)" -ForegroundColor Gray
            Write-Host "Includes web resources: $($jsonResponse.summary.metadata.includes_web_resources)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Process and Summarize with URLs Failed: $($response.StatusCode)" -ForegroundColor Red
        Write-Host "Response: $responseContent" -ForegroundColor Red
    }
    
    $httpClient.Dispose()
} catch {
    Write-Host "❌ Process and Summarize with URLs Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Streamlit App Check
Write-Host "`n6. Testing Streamlit App..." -ForegroundColor Yellow
try {
    $streamlitResponse = Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing -TimeoutSec 10
    if ($streamlitResponse.StatusCode -eq 200) {
        Write-Host "✅ Streamlit App is accessible" -ForegroundColor Green
        Write-Host "Status Code: $($streamlitResponse.StatusCode)" -ForegroundColor Gray
    } else {
        Write-Host "❌ Streamlit App returned status: $($streamlitResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Streamlit App Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== API Endpoint Testing Completed ===" -ForegroundColor Cyan
Write-Host "`nAccess your applications at:" -ForegroundColor White
Write-Host "• FastAPI Backend: http://localhost:8000" -ForegroundColor Blue
Write-Host "• API Documentation: http://localhost:8000/docs" -ForegroundColor Blue  
Write-Host "• Streamlit Frontend: http://localhost:8501" -ForegroundColor Blue
