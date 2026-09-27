param(
    [Parameter(Mandatory=$true)][string]$BuildRoot,
    [ValidateRange(1,64)][int]$Jobs = 4
)
$ErrorActionPreference = 'Stop'
$fpRepoRoot = Split-Path -Parent $PSScriptRoot
$fpBuildRoot = [IO.Path]::GetFullPath($BuildRoot)
$fpSource = Join-Path $fpRepoRoot 'experiments\next_token\baselines\kenlm'
$fpVswhere = Join-Path ([Environment]::GetFolderPath('ProgramFilesX86')) 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $fpVswhere)) {
    throw 'The Windows baseline build requires the registered Visual Studio toolchain.'
}
$fpVcpkg = (& $fpVswhere -latest -find '**\vcpkg.exe' | Select-Object -First 1)
$fpCmake = (& $fpVswhere -latest -find '**\cmake.exe' | Select-Object -First 1)
if (-not $fpVcpkg -or -not $fpCmake) { throw 'Visual Studio CMake and vcpkg are required.' }
New-Item -ItemType Directory -Path $fpBuildRoot -Force | Out-Null
$env:VCPKG_MAX_CONCURRENCY = [string]$Jobs
$fpInstallArgs = @('install', '--triplet=x64-windows-static', "--x-manifest-root=$fpSource",
    "--x-install-root=$fpBuildRoot\installed", "--x-buildtrees-root=$fpBuildRoot\buildtrees",
    "--x-packages-root=$fpBuildRoot\packages", "--downloads-root=$fpBuildRoot\downloads", '--disable-metrics')
& $fpVcpkg @fpInstallArgs
if ($LASTEXITCODE -ne 0) { throw 'Pinned KenLM installation failed.' }
# Refresh only this explicit CMake build cache when source moves between the
# temporary research worktree and the canonical checkout.
$fpConfigureArgs = @('--fresh', '-S', $fpSource, '-B', "$fpBuildRoot\report-build", '-G', 'Visual Studio 18 2026', '-A', 'x64',
    "-DCMAKE_PREFIX_PATH=$fpBuildRoot/installed/x64-windows-static", '-DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded')
& $fpCmake @fpConfigureArgs
if ($LASTEXITCODE -ne 0) { throw 'KenLM reporter configuration failed.' }
& $fpCmake --build "$fpBuildRoot\report-build" --config Release --parallel $Jobs
if ($LASTEXITCODE -ne 0) { throw 'KenLM reporter build failed.' }
Write-Output "Built: $fpBuildRoot\report-build\Release\fp_kenlm_report.exe"
