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
$sqlFile = Join-Path $projectRoot 'sql\week1_setup.sql'

if (-not (Test-Path $snowsqlExe)) {
    throw 'SnowSQL executable not found. Install SnowSQL first.'
}
if (-not (Test-Path $sqlFile)) {
    throw 'SQL setup file not found at sql\week1_setup.sql'
}

# Keeps config and temp artifacts on D drive for this session.
& (Join-Path $projectRoot 'scripts\set_d_drive_env.ps1')

& $snowsqlExe -a $Account -u $User -r $Role -w $Warehouse -f $sqlFile
