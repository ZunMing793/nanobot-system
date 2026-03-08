<#
.SYNOPSIS
    NanoBot Multi-Bot System Manager
    用于管理多个 bot 进程的启动、停止、重启和状态查看

.DESCRIPTION
    管理多个 NanoBot 进程的生命周期

.EXAMPLE
    .\bot_manager.ps1 start bot1_core
    .\bot_manager.ps1 status
    .\bot_manager.ps1 start-all
#>

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$BotId,
    
    [Parameter(Position=2)]
    [int]$Lines = 100
)

$ErrorActionPreference = "Stop"

$BotRoot = Split-Path -Parent $PSScriptRoot
$PidDir = Join-Path $env:TEMP "nanobot"
$Bots = @("bot1_core", "bot2_health", "bot3_finance", "bot4_emotion", "bot5_media")

if (-not (Test-Path $PidDir)) {
    New-Item -ItemType Directory -Path $PidDir -Force | Out-Null
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-BotRunning {
    param([string]$BotId)
    
    $pidFile = Join-Path $PidDir "$BotId.pid"
    
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($pid) {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                return $true
            }
        }
    }
    return $false
}

function Get-BotStatus {
    param([string]$BotId)
    
    if (Test-BotRunning -BotId $BotId) {
        return "运行中"
    }
    return "已停止"
}

function Start-Bot {
    param([string]$BotId)
    
    $botDir = Join-Path $BotRoot $BotId
    $pidFile = Join-Path $PidDir "$BotId.pid"
    $logFile = Join-Path $botDir "logs\bot.log"
    
    if (Test-BotRunning -BotId $BotId) {
        Write-ColorOutput "$BotId 已经在运行" "Yellow"
        return
    }
    
    if (-not (Test-Path $botDir)) {
        Write-ColorOutput "错误: $BotId 目录不存在" "Red"
        return
    }
    
    Write-ColorOutput "启动 $BotId..." "Cyan"
    
    Push-Location $botDir
    
    $logsDir = Join-Path $botDir "logs"
    if (-not (Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }
    
    $process = Start-Process -FilePath "python" -ArgumentList "-m", "nanobot", "agent", "--config", "config.json" -RedirectStandardOutput $logFile -RedirectStandardError (Join-Path $logsDir "error.log") -PassThru -NoNewWindow
    
    $process.Id | Out-File -FilePath $pidFile -Encoding utf8
    
    Start-Sleep -Seconds 2
    
    if (Test-BotRunning -BotId $BotId) {
        Write-ColorOutput "$BotId 启动成功 (PID: $($process.Id))" "Green"
    } else {
        Write-ColorOutput "$BotId 启动失败，请检查日志: $logFile" "Red"
        Remove-Item $pidFile -ErrorAction SilentlyContinue
    }
    
    Pop-Location
}

function Stop-Bot {
    param([string]$BotId)
    
    $pidFile = Join-Path $PidDir "$BotId.pid"
    
    if (-not (Test-BotRunning -BotId $BotId)) {
        Write-ColorOutput "$BotId 未在运行" "Yellow"
        return
    }
    
    $pid = Get-Content $pidFile
    Write-ColorOutput "停止 $BotId (PID: $pid)..." "Cyan"
    
    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($process) {
        $process | Stop-Process -Force
    }
    
    Remove-Item $pidFile -ErrorAction SilentlyContinue
    Write-ColorOutput "$BotId 已停止" "Green"
}

function Restart-Bot {
    param([string]$BotId)
    
    Stop-Bot -BotId $BotId
    Start-Sleep -Seconds 2
    Start-Bot -BotId $BotId
}

function Show-Status {
    param([string]$BotId)
    
    if ($BotId) {
        $status = Get-BotStatus -BotId $BotId
        Write-Host "$BotId`: $status"
    } else {
        Write-Host "Bot 状态:"
        Write-Host "----------------------------------------"
        foreach ($bot in $Bots) {
            $status = Get-BotStatus -BotId $bot
            $pidInfo = ""
            if (Test-BotRunning -BotId $bot) {
                $pidFile = Join-Path $PidDir "$bot.pid"
                $pid = Get-Content $pidFile
                $pidInfo = " (PID: $pid)"
            }
            $color = if ($status -eq "运行中") { "Green" } else { "Red" }
            Write-Host "  $bot`: " -NoNewline
            Write-Host $status$pidInfo -ForegroundColor $color
        }
        Write-Host "----------------------------------------"
    }
}

function Show-Logs {
    param([string]$BotId, [int]$Lines)
    
    $logFile = Join-Path $BotRoot "$BotId\logs\bot.log"
    
    if (-not (Test-Path $logFile)) {
        Write-ColorOutput "日志文件不存在: $logFile" "Red"
        return
    }
    
    Write-ColorOutput "=== $BotId 最近 $Lines 行日志 ===" "Cyan"
    Get-Content $logFile -Tail $Lines
}

function Start-AllBots {
    Write-ColorOutput "启动所有 bot..." "Cyan"
    foreach ($bot in $Bots) {
        Start-Bot -BotId $bot
        Start-Sleep -Seconds 1
    }
    Write-ColorOutput "所有 bot 启动完成" "Green"
    Show-Status
}

function Stop-AllBots {
    Write-ColorOutput "停止所有 bot..." "Cyan"
    foreach ($bot in $Bots) {
        Stop-Bot -BotId $bot
    }
    Write-ColorOutput "所有 bot 已停止" "Green"
}

function Restart-AllBots {
    Stop-AllBots
    Start-Sleep -Seconds 2
    Start-AllBots
}

function Print-Help {
    Write-Host "NanoBot Multi-Bot System Manager"
    Write-Host ""
    Write-Host "Usage: .\bot_manager.ps1 <command> [bot_id]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  start <bot_id>    启动指定 bot"
    Write-Host "  stop <bot_id>     停止指定 bot"
    Write-Host "  restart <bot_id>  重启指定 bot"
    Write-Host "  status [bot_id]   查看状态（不指定则显示所有）"
    Write-Host "  logs <bot_id>     查看指定 bot 日志"
    Write-Host "  start-all         启动所有 bot"
    Write-Host "  stop-all          停止所有 bot"
    Write-Host "  restart-all       重启所有 bot"
    Write-Host ""
    Write-Host "Bot IDs:"
    foreach ($bot in $Bots) {
        Write-Host "  $bot"
    }
}

switch ($Command) {
    "start" {
        if (-not $BotId) { Write-Host "错误: 请指定 bot_id"; Print-Help; exit 1 }
        Start-Bot -BotId $BotId
    }
    "stop" {
        if (-not $BotId) { Write-Host "错误: 请指定 bot_id"; Print-Help; exit 1 }
        Stop-Bot -BotId $BotId
    }
    "restart" {
        if (-not $BotId) { Write-Host "错误: 请指定 bot_id"; Print-Help; exit 1 }
        Restart-Bot -BotId $BotId
    }
    "status" {
        Show-Status -BotId $BotId
    }
    "logs" {
        if (-not $BotId) { Write-Host "错误: 请指定 bot_id"; Print-Help; exit 1 }
        Show-Logs -BotId $BotId -Lines $Lines
    }
    "start-all" {
        Start-AllBots
    }
    "stop-all" {
        Stop-AllBots
    }
    "restart-all" {
        Restart-AllBots
    }
    "help" { Print-Help }
    default { Print-Help; exit 1 }
}
