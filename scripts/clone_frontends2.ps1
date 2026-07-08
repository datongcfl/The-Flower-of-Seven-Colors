$ErrorActionPreference = "Continue"
$base = $PSScriptRoot
$log = Join-Path $base "clone_frontends2.log"
"=== clone_frontends2 start $(Get-Date) ===" | Out-File -FilePath $log -Encoding utf8

$repos = @(
  @{repo="MERSADREZAZADEH/HOTEL-ADMIN"; dir="HOTEL-ADMIN-React"},
  @{repo="windingtree/rooms"; dir="windingtree-rooms"}
)

foreach ($r in $repos) {
  $target = Join-Path $base $r.dir
  if (Test-Path $target) { "SKIP exists: $($r.dir)" | Out-File -FilePath $log -Append utf8; continue }
  ">> cloning $($r.repo) -> $($r.dir)" | Out-File -FilePath $log -Append utf8
  try {
    $p = Start-Process -FilePath "git" -ArgumentList @("-C",$base,"clone","--depth","1","https://github.com/$($r.repo).git",$r.dir) -Wait -PassThru -NoNewWindow
    "   exit=$($p.ExitCode)" | Out-File -FilePath $log -Append utf8
    $g = Join-Path $target ".git"
    if (Test-Path $g) { Remove-Item -Recurse -Force $g; "   stripped .git" | Out-File -FilePath $log -Append utf8 }
  } catch {
    "   ERROR cloning $($r.repo): $_" | Out-File -FilePath $log -Append utf8
  }
}
"=== clone_frontends2 done $(Get-Date) ===" | Out-File -FilePath $log -Append utf8
