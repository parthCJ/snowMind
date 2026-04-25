$ErrorActionPreference = 'Stop'

Write-Host 'Checking Python venv...'
if (-not (Test-Path '.venv\Scripts\python.exe')) {
  throw 'Virtual environment not found at .venv'
}

$py = Resolve-Path '.venv\Scripts\python.exe'
& $py -c "import langgraph, streamlit, snowflake.connector; print('Python deps OK')"

Write-Host 'Checking SnowSQL and Snowflake CLI...'
$snowsqlPath = 'C:\Program Files\Snowflake SnowSQL\snowsql.exe'
$snowCliPath = 'C:\Program Files\Snowflake CLI\snow.exe'

if (-not (Test-Path $snowsqlPath)) {
  throw 'SnowSQL not found at expected location.'
}
if (-not (Test-Path $snowCliPath)) {
  throw 'Snowflake CLI not found at expected location.'
}

& $snowsqlPath --version
& $snowCliPath --version

Write-Host 'Setup verification passed.'
