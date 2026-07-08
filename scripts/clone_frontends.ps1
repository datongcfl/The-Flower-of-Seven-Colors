$ErrorActionPreference = "Continue"
$base = $PSScriptRoot
$log = Join-Path $base "clone_frontends.log"
"=== clone_frontends start $(Get-Date) ===" | Out-File -FilePath $log -Encoding utf8

$repos = @(
  @{repo="ONYXDEVS/react-hotel-reservation-system"; dir="react-hotel-reservation-system"},
  @{repo="JACKFIALLOS/HOTELMANAGEMENTSYSTEM"; dir="HOTELMANAGEMENTSYSTEM-Angular"},
  @{repo="SUDEEPMAHATO16/THE-WILD-OASIS"; dir="THE-WILD-OASIS"},
  @{repo="windingtree/rooms"; dir="windingtree-rooms"},
  @{repo="MERSADREZAZADEH/HOTEL-ADMIN"; dir="HOTEL-ADMIN-React"}
)

foreach ($r in $repos) {
  $target = Join-Path $base $r.dir
  if (Test-Path $target) { "SKIP exists: $($r.dir)" | Out-File -FilePath $log -Append utf8; continue }
  ">> cloning $($r.repo) -> $($r.dir)" | Out-File -FilePath $log -Append utf8
  try {
    git -C $base clone --depth 1 "https://github.com/$($r.repo).git" $r.dir 2>&1 | Out-File -FilePath $log -Append utf8
    # strip .git to avoid nested repo
    $g = Join-Path $target ".git"
    if (Test-Path $g) { Remove-Item -Recurse -Force $g; "   stripped .git" | Out-File -FilePath $log -Append utf8 }
  } catch {
    "   ERROR cloning $($r.repo): $_" | Out-File -FilePath $log -Append utf8
  }
}
"=== clone_frontends done $(Get-Date) ===" | Out-File -FilePath $log -Append utf8
