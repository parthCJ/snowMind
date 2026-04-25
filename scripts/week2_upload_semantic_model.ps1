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
$semanticModel = (Join-Path $projectRoot 'config\analyst\semantic_model.yaml') -replace '\\', '/'

if (-not (Test-Path $snowsqlExe)) {
    throw 'SnowSQL executable not found. Install SnowSQL first.'
}
if (-not (Test-Path ($semanticModel -replace '/', '\\'))) {
    throw 'Semantic model file missing at config\analyst\semantic_model.yaml'
}

& (Join-Path $projectRoot 'scripts\set_d_drive_env.ps1')

$tmpSql = Join-Path $projectRoot 'tmp\week2_upload_semantic_model.sql'
$sql = @"
USE ROLE $Role;
USE WAREHOUSE $Warehouse;
USE DATABASE SNOWMIND_DB;
PUT file://$semanticModel @SNOWMIND_DB.PUBLIC.STG_UNSTRUCTURED AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
LIST @SNOWMIND_DB.PUBLIC.STG_UNSTRUCTURED;
"@
Set-Content -Path $tmpSql -Value $sql -Encoding Ascii

& $snowsqlExe -a $Account -u $User -r $Role -w $Warehouse -f $tmpSql
