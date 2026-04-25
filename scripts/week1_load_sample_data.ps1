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

if (-not (Test-Path $snowsqlExe)) {
    throw 'SnowSQL executable not found. Install SnowSQL first.'
}

& (Join-Path $projectRoot 'scripts\set_d_drive_env.ps1')

$ordersPath = (Join-Path $projectRoot 'data\structured\orders.csv') -replace '\\', '/'
$usersPath = (Join-Path $projectRoot 'data\structured\users.csv') -replace '\\', '/'
$eventsPath = (Join-Path $projectRoot 'data\structured\events.json') -replace '\\', '/'
$docPath = (Join-Path $projectRoot 'data\unstructured\refund_policy.md') -replace '\\', '/'

$sqlScript = @"
USE ROLE $Role;
USE WAREHOUSE $Warehouse;
USE DATABASE SNOWMIND_DB;

PUT file://$ordersPath @SNOWMIND_DB.PUBLIC.STG_STRUCTURED AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://$usersPath @SNOWMIND_DB.PUBLIC.STG_STRUCTURED AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://$eventsPath @SNOWMIND_DB.PUBLIC.STG_STRUCTURED/events AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://$docPath @SNOWMIND_DB.PUBLIC.STG_UNSTRUCTURED AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

COPY INTO SNOWMIND_DB.SALES.ORDERS
  FROM @SNOWMIND_DB.PUBLIC.STG_STRUCTURED/orders.csv
  FILE_FORMAT = (FORMAT_NAME = SNOWMIND_DB.PUBLIC.FF_CSV)
  ON_ERROR = CONTINUE;

COPY INTO SNOWMIND_DB.USERS.PROFILES
  FROM @SNOWMIND_DB.PUBLIC.STG_STRUCTURED/users.csv
  FILE_FORMAT = (FORMAT_NAME = SNOWMIND_DB.PUBLIC.FF_CSV)
  ON_ERROR = CONTINUE;

COPY INTO SNOWMIND_DB.EVENTS.APP_EVENTS(payload)
  FROM @SNOWMIND_DB.PUBLIC.STG_STRUCTURED/events
  FILE_FORMAT = (FORMAT_NAME = SNOWMIND_DB.PUBLIC.FF_JSON)
  ON_ERROR = CONTINUE;

SELECT 'orders' AS table_name, COUNT(*) AS row_count FROM SNOWMIND_DB.SALES.ORDERS
UNION ALL
SELECT 'profiles' AS table_name, COUNT(*) AS row_count FROM SNOWMIND_DB.USERS.PROFILES
UNION ALL
SELECT 'events' AS table_name, COUNT(*) AS row_count FROM SNOWMIND_DB.EVENTS.APP_EVENTS;
"@

$tmpSqlPath = Join-Path $projectRoot 'tmp\week1_load_sample_data.sql'
Set-Content -Path $tmpSqlPath -Value $sqlScript -Encoding Ascii

& $snowsqlExe -a $Account -u $User -r $Role -w $Warehouse -f $tmpSqlPath
