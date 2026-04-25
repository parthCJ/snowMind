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
$setupSql = Join-Path $projectRoot 'sql\week2_cortex_setup.sql'
$searchSql = Join-Path $projectRoot 'sql\week2_cortex_search_service.sql'

if (-not (Test-Path $snowsqlExe)) {
    throw 'SnowSQL executable not found. Install SnowSQL first.'
}
if (-not (Test-Path $setupSql)) {
    throw 'SQL file not found at sql\week2_cortex_setup.sql'
}
if (-not (Test-Path $searchSql)) {
    throw 'SQL file not found at sql\week2_cortex_search_service.sql'
}

& (Join-Path $projectRoot 'scripts\set_d_drive_env.ps1')
& $snowsqlExe -a $Account -u $User -r $Role -w $Warehouse -o exit_on_error=true -f $setupSql
if ($LASTEXITCODE -ne 0) {
    throw 'Base Cortex setup failed.'
}

# Some trial accounts/regions may not have Cortex Search service enabled yet.
& $snowsqlExe -a $Account -u $User -r $Role -w $Warehouse -o exit_on_error=true -f $searchSql
if ($LASTEXITCODE -ne 0) {
    Write-Warning 'Cortex Search service creation failed. Base Week 2 setup is still complete.'
    Write-Host 'You can continue with fallback retrieval tests and enable Cortex Search later.'
} else {
    Write-Host 'Cortex Search service created successfully.'
}
