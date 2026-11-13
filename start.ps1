# MyWorkbench 一键启动（后端 + 前端，各自独立窗口）
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==> 启动后端 http://127.0.0.1:8000 ..."
Start-Process -FilePath "python" -ArgumentList "run.py" `
  -WorkingDirectory (Join-Path $root "backend")

Write-Host "==> 启动前端 http://127.0.0.1:5173 ..."
Start-Process -FilePath "npm.cmd" -ArgumentList "run","dev" `
  -WorkingDirectory (Join-Path $root "frontend")

Start-Sleep 4
Write-Host ""
Write-Host "=============================================="
Write-Host "  MyWorkbench 已启动"
Write-Host "  Web 控制台 : http://127.0.0.1:5173"
Write-Host "  API 文档   : http://127.0.0.1:8000/docs"
Write-Host "  默认管理员 : admin / admin123456"
Write-Host "=============================================="
Write-Host "  关闭：直接关闭两个弹出的窗口即可。"
