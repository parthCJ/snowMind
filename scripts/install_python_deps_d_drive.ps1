$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $projectRoot '.venv\Scripts\python.exe'
$requirements = Join-Path $projectRoot 'requirements.txt'

if (-not (Test-Path $pythonExe)) {
    throw 'Python venv not found at .venv. Create it first.'
}
if (-not (Test-Path $requirements)) {
    throw 'requirements.txt not found.'
}

# Keeps pip cache and temp artifacts on D drive for this session.
& (Join-Path $projectRoot 'scripts\set_d_drive_env.ps1')

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r $requirements
& $pythonExe -m pip install -e $projectRoot
