$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$tmpPath = Join-Path $projectRoot 'tmp'
$pipCachePath = Join-Path $projectRoot 'cache\pip'
$snowsqlConfigPath = Join-Path $projectRoot 'config\snowsql\config'

New-Item -ItemType Directory -Path $tmpPath -Force | Out-Null
New-Item -ItemType Directory -Path $pipCachePath -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path -Parent $snowsqlConfigPath) -Force | Out-Null

$env:TEMP = $tmpPath
$env:TMP = $tmpPath
$env:PIP_CACHE_DIR = $pipCachePath
$env:SNOWSQL_CONFIG = $snowsqlConfigPath

Write-Host "TEMP set to: $($env:TEMP)"
Write-Host "TMP set to: $($env:TMP)"
Write-Host "PIP_CACHE_DIR set to: $($env:PIP_CACHE_DIR)"
Write-Host "SNOWSQL_CONFIG set to: $($env:SNOWSQL_CONFIG)"
