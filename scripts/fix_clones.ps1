# Fix missing/empty clones (ASCII only). QloApps re-clone, minical substitute.
$base = $PSScriptRoot
$log  = Join-Path $base "fix_clones.log"
Start-Transcript -Path $log -Append | Out-Null
Write-Host "$(Get-Date) FIX clones start"

# QloApps: remove empty dir and re-clone
$qlo = Join-Path $base "QloApps"
if (Test-Path $qlo) {
    $cnt = (Get-ChildItem $qlo -Recurse -Force | Measure-Object).Count
    Write-Host "QloApps exists with $cnt items; removing to re-clone"
    Remove-Item -Recurse -Force $qlo
}
Write-Host "=== clone QloApps ==="
git clone --depth 1 https://github.com/Qloapps/QloApps $qlo 2>&1
if ($LASTEXITCODE -eq 0) {
    if (Test-Path (Join-Path $qlo ".git")) { Remove-Item -Recurse -Force (Join-Path $qlo ".git"); Write-Host "stripped QloApps .git" }
    Write-Host "QloApps DONE"
} else { Write-Host "QloApps FAILED" }

# minical substitute: online-booking-engine
$mini = Join-Path $base "minical"
if (-not (Test-Path $mini)) {
    Write-Host "=== clone minical/online-booking-engine ==="
    git clone --depth 1 https://github.com/minical/online-booking-engine $mini 2>&1
    if ($LASTEXITCODE -eq 0) {
        if (Test-Path (Join-Path $mini ".git")) { Remove-Item -Recurse -Force (Join-Path $mini ".git"); Write-Host "stripped minical .git" }
        Write-Host "minical DONE"
    } else { Write-Host "minical FAILED" }
} else { Write-Host "minical exists SKIP" }

Write-Host "$(Get-Date) FIX done"
Write-Host "Final listing:"
Get-ChildItem -Path $base -Force | Select-Object Name, Mode | Format-Table -AutoSize
Stop-Transcript | Out-Null
