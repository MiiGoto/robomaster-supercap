param(
    [Parameter(Mandatory=$true)][string]$CMake,
    [Parameter(Mandatory=$true)][string]$Ninja,
    [Parameter(Mandatory=$true)][string]$ArmTools,
    [Parameter(Mandatory=$true)][string]$HalRoot,
    [Parameter(Mandatory=$true)][string]$DeviceRoot,
    [Parameter(Mandatory=$true)][string]$CmsisRoot,
    [ValidateSet('SAFE_MONITOR_ONLY','LOW_ENERGY_COMMISSIONING','POWER_STAGE_CONTROL')]
    [string]$Mode='SAFE_MONITOR_ONLY',
    [string]$AliasRoot=(Join-Path $env:TEMP 'robomaster-supercap-fw-rev-a')
)
$ErrorActionPreference='Stop'
# Ninja on this Windows installation cannot resolve the Unicode workspace path.
# Junction aliases preserve the checkout; existing paths are never removed/replaced.
$controller=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$roots=@{controller=$controller; hal=$HalRoot; device=$DeviceRoot; cmsis=$CmsisRoot}
$alias= [IO.Path]::GetFullPath($AliasRoot)
if ($alias -match '[^\x00-\x7F]') {throw 'Use an ASCII AliasRoot for Windows Ninja'}
New-Item -ItemType Directory -Path $alias -Force | Out-Null
foreach($name in $roots.Keys) {
    $target=(Resolve-Path -LiteralPath $roots[$name]).Path
    $link=Join-Path $alias $name
    if(Test-Path -LiteralPath $link) {
        $item=Get-Item -LiteralPath $link
        $existingTarget=@($item.Target)[0]
        if($item.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath($existingTarget) -ne $target) {
            throw "Existing alias differs: $link; choose a new AliasRoot. Nothing was changed."
        }
    } else {New-Item -ItemType Junction -Path $link -Target $target | Out-Null}
}
$base=$alias.Replace('\','/')
$build="$base/build-$Mode"
& $CMake -S "$base/controller" -B $build -G Ninja "-DCMAKE_MAKE_PROGRAM=$Ninja" `
    "-DCMAKE_TOOLCHAIN_FILE=$base/controller/cmake/arm-gcc.cmake" `
    "-DARM_TOOLCHAIN_BIN=$ArmTools" "-DHAL_ROOT=$base/hal" `
    "-DDEVICE_ROOT=$base/device" "-DCMSIS_ROOT=$base/cmsis" "-DFW_MODE=$Mode"
if($LASTEXITCODE){throw 'CMake configure failed'}
& $CMake --build $build -j 4
if($LASTEXITCODE){throw 'Firmware build failed'}
Write-Output "Build only: $build/controller.elf; no flash/option-byte/hardware command"
