# run_senses.ps1 - Main entry point for scheduled AI Employee tasks (GOLD TIER)

# 1. Setup Paths
$ScriptDir = $PSScriptRoot
$RootDir = Split-Path -Parent $ScriptDir
Set-Location $RootDir

# 2. Start Logging
$LogFile = Join-Path $RootDir "heartbeat_debug.log"
Start-Transcript -Path $LogFile -Append

Write-Host "--- Starting AI Employee Heartbeat ($(Get-Date)) ---" -ForegroundColor Cyan
Write-Host "Working Directory: $PWD"

# 3. Setup Environment
$env:PYTHONPATH = $RootDir

# 4. Guardian Watchdog Check (Self-Healing)
Write-Host "Checking Guardian Watchdog status..." -ForegroundColor Gray
$WatchdogProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*guardian.py*" }
if (-not $WatchdogProcess) {
    Write-Host "[WARN] Guardian is offline. Restarting in background..." -ForegroundColor Yellow
    Start-Process -FilePath "uv" -ArgumentList "run", "python", "src/watchers/guardian.py" -WindowStyle Hidden
} else {
    Write-Host "[OK] Guardian is active (PID: $($WatchdogProcess.Id))" -ForegroundColor Green
}

# 5. Run Senses & Agents
try {
    Write-Host "Step 1: Checking Gmail..."
    uv run python "src/watchers/gmail_watcher.py" --once
    
    Write-Host "Step 2: Checking WhatsApp..."
    uv run python "src/watchers/whatsapp_watcher.py" --once
    
    Write-Host "Step 3: Checking File System..."
    uv run python "src/watchers/fs_watcher.py" --once
    
    Write-Host "Step 4: AI Reasoning & Drafting (Odoo/Social)..."
    uv run python "src/agents/drafting_agent.py" --once

    Write-Host "Step 5: Executing Approved Tasks..."
    uv run python "src/handlers/approval_handler.py" --once

    # 6. Daily Insights (Silver Tier Skills)
    Write-Host "Step 6: Running Daily Insights and Vault Audit..." -ForegroundColor Gray
    uv run python ".claude/skills/briefing-genius/briefing_genius.py"
    uv run python ".claude/skills/vault-audit/vault_audit.py"

    # 7. Weekly CEO Briefing (Trigger on Sunday)
    $CurrentDay = (Get-Date).DayOfWeek
    if ($CurrentDay -eq "Sunday") {
        Write-Host "Step 7: Generating Weekly CEO Briefing (Sunday night)..." -ForegroundColor Yellow
        uv run python "src/agents/briefing_agent.py"
    }
}
catch {
    Write-Host "[ERROR] An error occurred during heartbeat: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "--- Gold Tier Heartbeat Complete ---" -ForegroundColor Green

Stop-Transcript
