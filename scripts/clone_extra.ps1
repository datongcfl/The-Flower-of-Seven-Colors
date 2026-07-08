$ErrorActionPreference = 'Continue'
$base = $PSScriptRoot
$log = Join-Path $base "clone_extra.log"
"=== clone_extra start $(Get-Date) ===" | Out-File -FilePath $log -Encoding utf8
$repos = @(
  @{url="https://github.com/KHALEDASHRAFH/HOTELHUB"; name="HOTELHUB"},
  @{url="https://github.com/DVARGAS2332/PMS-HOTEL"; name="PMS-HOTEL"},
  @{url="https://github.com/KAMRA-PMS/KAMRA-PMS"; name="KAMRA-PMS"}
)
foreach ($r in $repos) {
  $dest = Join-Path $base $r.name
  "--- cloning $($r.name) from $($r.url) ---" | Out-File -FilePath $log -Append -Encoding utf8
  git clone --depth 1 $r.url $dest 2>&1 | Out-File -FilePath $log -Append -Encoding utf8
  $g = Join-Path $dest ".git"
  if (Test-Path $g) {
    Remove-Item -Recurse -Force $g
    "stripped .git from $($r.name)" | Out-File -FilePath $log -Append -Encoding utf8
  } else {
    "WARN: .git not found for $($r.name) (clone may have failed)" | Out-File -FilePath $log -Append -Encoding utf8
  }
}
"=== clone_extra done $(Get-Date) ===" | Out-File -FilePath $log -Append -Encoding utf8
