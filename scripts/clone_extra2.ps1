$ErrorActionPreference = 'Continue'
$base = $PSScriptRoot
$log = Join-Path $base "clone_extra2.log"
"=== clone_extra2 start $(Get-Date) ===" | Out-File -FilePath $log -Encoding utf8
$repos = @(
  @{url="https://github.com/yangzongzhuan/RuoYi"; name="RuoYi"},
  @{url="https://github.com/SHOURYAJ98/HOTEL-MANAGEMENT-PROJECT-JAVA"; name="HOTEL-MANAGEMENT-PROJECT-JAVA"},
  @{url="https://github.com/MYNAMEISLY/HOTELMANAGEMENT"; name="HOTELMANAGEMENT-VueSpringBoot"}
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
"=== clone_extra2 done $(Get-Date) ===" | Out-File -FilePath $log -Append -Encoding utf8
