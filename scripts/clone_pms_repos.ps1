# Clone 6 open-source hotel PMS projects for code audit (no Chinese in this file)
$StripGit = $true
$base = $PSScriptRoot
$log  = Join-Path $base "clone_progress.log"

Start-Transcript -Path $log -Append | Out-Null
Write-Host "$(Get-Date) START clone task"

$repos = @(
    @{ url = "https://github.com/TelivityAI/haip";                    name = "haip" },
    @{ url = "https://github.com/Gifted87/erpnext_hospitality_core"; name = "erpnext_hospitality_core" },
    @{ url = "https://github.com/rstrlm/HPMS_Tiny";                  name = "HPMS_Tiny" },
    @{ url = "https://github.com/digital-druid/hoteldruid";          name = "hoteldruid" },
    @{ url = "https://github.com/Qloapps/QloApps";                   name = "QloApps" },
    @{ url = "https://github.com/minical/minical";                   name = "minical" }
)

foreach ($r in $repos) {
    $dest = Join-Path $base $r.name
    if (Test-Path $dest) {
        Write-Host "SKIP exists: $($r.name)"
        continue
    }
    Write-Host "=== [$(Get-Date)] clone $($r.name) ==="
    try {
        git clone --depth 1 $r.url $dest 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR clone failed: $($r.name)"
            continue
        }
        if ($StripGit -and (Test-Path (Join-Path $dest ".git"))) {
            Remove-Item -Recurse -Force (Join-Path $dest ".git")
            Write-Host "stripped .git"
        }
        Write-Host "DONE: $($r.name)"
    } catch {
        Write-Host "EXCEPTION: $_"
    }
    Write-Host ""
}

Write-Host "$(Get-Date) ALL DONE"
Write-Host "Directory listing:"
Get-ChildItem -Path $base -Force | Select-Object Name, Mode | Format-Table -AutoSize
Stop-Transcript | Out-Null
