# run_senses.ps1 - Main entry point for scheduled AI Employee tasks

# 1. Setup Paths
$ScriptDir = $PSScriptRoot
$RootDir = Split-Path -Parent $ScriptDir
Set-Location $RootDir

# 2. Start Logging (Taake hum errors dekh sakein)
$LogFile = Join-Path $RootDir "heartbeat_debug.log"
Start-Transcript -Path $LogFile -Append

Write-Host "--- Starting AI Employee Heartbeat ($(Get-Date)) ---" -ForegroundColor Cyan
Write-Host "Working Directory: $PWD"

# 3. Setup Environment
$env:PYTHONPATH = $RootDir

# 4. Run Senses
try {
    Write-Host "Checking Gmail..."
    & ".\.venv\Scripts\python.exe" "src/watchers/gmail_watcher.py" --once
    
    Write-Host "Checking WhatsApp..."
    # Run headless for scheduling
    & ".\.venv\Scripts\python.exe" "src/watchers/whatsapp_watcher.py" --once
    
    Write-Host "Checking File System..."
    & ".\.venv\Scripts\python.exe" "src/watchers/fs_watcher.py" --once
    
    Write-Host "Drafting Responses (AI)..."
    & ".\.venv\Scripts\python.exe" "src/agents/drafting_agent.py" --once

    Write-Host "Processing Approved Tasks..."
    & ".\.venv\Scripts\python.exe" "src/handlers/approval_handler.py" --once
}
catch {
    Write-Host "An error occurred: $_" -ForegroundColor Red
}

Write-Host "--- Heartbeat Complete ---" -ForegroundColor Green

Stop-Transcript
