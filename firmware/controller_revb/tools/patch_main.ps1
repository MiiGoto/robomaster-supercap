# Adds the three sc_app calls to the CubeMX-generated Core/Src/main.c (USER CODE sections).
# Safe to run again: lines that are already present are not added twice.
# Usage (PowerShell, in firmware/controller_revb):  powershell -ExecutionPolicy Bypass -File tools\patch_main.ps1
param([string]$Main = "Core\Src\main.c")
if (-not (Test-Path $Main)) { Write-Error "$Main not found. Generate code from SupercapRevB.ioc first."; exit 1 }
$text = Get-Content -Raw -Encoding UTF8 $Main
$edits = @(
  @{ Tag = "/* USER CODE BEGIN Includes */"; Line = '#include "sc_app.h"' },
  @{ Tag = "/* USER CODE BEGIN 2 */";        Line = "  sc_app_init();" },
  @{ Tag = "/* USER CODE BEGIN 3 */";        Line = "    sc_app_loop();" }
)
foreach ($e in $edits) {
  if ($text.Contains($e.Line.Trim())) { continue }
  $i = $text.IndexOf($e.Tag)
  if ($i -lt 0) { Write-Error "Marker not found: $($e.Tag)"; exit 1 }
  $j = $i + $e.Tag.Length
  $text = $text.Substring(0, $j) + "`r`n" + $e.Line + $text.Substring($j)
}
Set-Content -NoNewline -Encoding UTF8 -Path $Main -Value $text
Write-Output "main.c updated."
