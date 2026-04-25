param(
    [Parameter(Mandatory = $true)]
    [string]$Account,

    [Parameter(Mandatory = $true)]
    [string]$User,

    [string]$Role = 'ACCOUNTADMIN',
    [string]$Warehouse = 'COMPUTE_WH'
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$snowsqlExe = 'C:\Program Files\Snowflake SnowSQL\snowsql.exe'
$testSql = Join-Path $projectRoot 'sql\week2_cortex_tests.sql'
$previewSql = Join-Path $projectRoot 'sql\week2_cortex_search_preview.sql'

if (-not (Test-Path $snowsqlExe)) {
    throw 'SnowSQL executable not found. Install SnowSQL first.'
}
if (-not (Test-Path $testSql)) {
    throw 'SQL file not found at sql\week2_cortex_tests.sql'
}
if (-not (Test-Path $previewSql)) {
    throw 'SQL file not found at sql\week2_cortex_search_preview.sql'
}

& (Join-Path $projectRoot 'scripts\set_d_drive_env.ps1')
& $snowsqlExe -a $Account -u $User -r $Role -w $Warehouse -o exit_on_error=true -f $testSql
if ($LASTEXITCODE -ne 0) {
    throw 'Base Week 2 tests failed.'
}

# Optional: run Cortex Search preview only when service exists and feature is enabled.
& $snowsqlExe -a $Account -u $User -r $Role -w $Warehouse -o exit_on_error=true -f $previewSql
if ($LASTEXITCODE -ne 0) {
    Write-Warning 'Cortex Search preview did not run. Base retrieval tests still passed.'
} else {
    Write-Host 'Cortex Search preview executed successfully.'
}
