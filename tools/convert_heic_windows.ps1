param(
  [string]$SourceDir = ".",
  [string]$OutputDir = ""
)
$ErrorActionPreference = "Stop"
if (-not $OutputDir) { $OutputDir = Join-Path $SourceDir "PSC_Converted" }
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$magick = Get-Command magick -ErrorAction SilentlyContinue
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $magick -and -not $ffmpeg) {
  throw "Install ImageMagick with HEIC support, or an HEIC-capable FFmpeg, and put it in PATH."
}

$count = 0
Get-ChildItem -LiteralPath $SourceDir -File | Where-Object { $_.Extension -match '^\.(heic|heif)$' } | ForEach-Object {
  $target = Join-Path $OutputDir ($_.Name + ".jpg")
  if ((Test-Path -LiteralPath $target) -and ((Get-Item $target).LastWriteTimeUtc -gt $_.LastWriteTimeUtc)) {
    Write-Host "Reusing: $target"
    return
  }
  Write-Host "Converting: $($_.FullName)"
  if ($magick) {
    & magick $_.FullName -auto-orient -quality 95 $target
  } else {
    & ffmpeg -loglevel error -y -i $_.FullName -frames:v 1 -q:v 2 $target
  }
  if ($LASTEXITCODE -ne 0) { throw "Conversion failed: $($_.FullName)" }
  $count++
}
Write-Host "Complete: $count converted. Originals were not changed."
Write-Host "Import this folder in Photo Story Creator: $OutputDir"
