# MyWorkbench 一键安装依赖（首次运行执行一次）
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==> [1/2] 安装后端 Python 依赖（akshare 较大，请耐心等待）"
Push-Location (Join-Path $root "backend")
python -m pip install -r requirements.txt
Pop-Location

Write-Host "==> [2/2] 安装前端依赖"
Push-Location (Join-Path $root "frontend")
npm.cmd install
Pop-Location

Write-Host ""
Write-Host "依赖安装完成。运行 start.ps1 启动系统。"
