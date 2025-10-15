<#
.SYNOPSIS
Run backend pytest with test DB and Redis launched via docker-compose.test.yml.

.DESCRIPTION
This script will:
 - start the test docker-compose stack (Postgres + Redis)
 - wait for Postgres to accept connections on localhost:5433
 - run the DB seed script at backend/tests/seed_db.py
 - run pytest with verbose output
 - tear down the test stack

Use from the repository root or the backend folder.
#>

Set-StrictMode -Version Latest
Push-Location -Path $PSScriptRoot

$composeFile = Join-Path $PSScriptRoot '..\docker-compose.test.yml'
Write-Host "Using compose file: $composeFile"

Write-Host "Starting test services (Postgres, Redis)..."
docker compose -f $composeFile up -d

# Wait for Postgres on localhost:5433
$maxSeconds = 120
$elapsed = 0
while ($elapsed -lt $maxSeconds) {
    try {
        $conn = Test-NetConnection -ComputerName 'localhost' -Port 5433 -WarningAction SilentlyContinue
        if ($conn.TcpTestSucceeded) {
            Write-Host "Postgres is accepting connections on localhost:5433"
            break
        }
    } catch {
        # ignore
    }
    Start-Sleep -Seconds 2
    $elapsed += 2
    Write-Host "Waiting for Postgres... $elapsed/$maxSeconds seconds"
}

if ($elapsed -ge $maxSeconds) {
    Write-Error "Postgres did not become available after $maxSeconds seconds"
    docker compose -f $composeFile down -v
    Pop-Location
    exit 1
}

Write-Host "Seeding test database..."
python (Join-Path $PSScriptRoot 'tests\seed_db.py')

Write-Host "Running pytest..."
pytest -vv -s --durations=10
$exitCode = $LASTEXITCODE

Write-Host "Stopping test services..."
docker compose -f $composeFile down -v

Pop-Location
exit $exitCode
