$venv = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "Starting backend  -> http://localhost:8000"
$backend = Start-Process -FilePath $venv `
    -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000" `
    -WorkingDirectory $PSScriptRoot -PassThru -NoNewWindow

Write-Host "Starting frontend -> http://localhost:8501"
$frontend = Start-Process -FilePath $venv `
    -ArgumentList "-m", "streamlit", "run", "frontend/app.py", "--server.port=8501" `
    -WorkingDirectory $PSScriptRoot -PassThru -NoNewWindow

Write-Host "Press Ctrl+C to stop both services`n"

try {
    while ($true) {
        Start-Sleep -Seconds 1
        if ($backend.HasExited -or $frontend.HasExited) { break }
    }
} finally {
    if (-not $backend.HasExited)  { $backend.Kill()  }
    if (-not $frontend.HasExited) { $frontend.Kill() }
    Write-Host "Stopped."
}
