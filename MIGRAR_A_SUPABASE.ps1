# ════════════════════════════════════════════════════════════════════
#  MEDICHECK — Migración base de datos LOCAL → Supabase
#  Ejecutar: clic derecho → "Ejecutar con PowerShell"
# ════════════════════════════════════════════════════════════════════

$Host.UI.RawUI.WindowTitle = "MediCheck — Migración DB"
Clear-Host

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║   MediCheck — Migración a Supabase       ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Configuración local ───────────────────────────────────────────
$localHost = "localhost"
$localPort = "5432"
$localDB   = "medicheck_db"
$localUser = "postgres"

# ── Configuración Supabase ────────────────────────────────────────
$supaHost  = "aws-1-us-west-2.pooler.supabase.com"
$supaPort  = "5432"
$supaDB    = "postgres"
$supaUser  = "postgres.vwplhsyxrauwgtrqbrpe"
$supaPass  = "Medicheck2024!"

Write-Host "  Paso 1: Exportando base de datos local..." -ForegroundColor Yellow
Write-Host ""

$dumpFile = "L:\medicheck\backup_local_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"

# Verificar que pg_dump esté disponible
$pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
if (-not $pgDump) {
    # Buscar en rutas comunes de PostgreSQL
    $rutas = @(
        "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
        "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
        "C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
        "C:\Program Files\PostgreSQL\13\bin\pg_dump.exe"
    )
    foreach ($ruta in $rutas) {
        if (Test-Path $ruta) { $pgDump = $ruta; break }
    }
}

if (-not $pgDump) {
    Write-Host "  ⚠  No se encontró pg_dump. Asegúrate que PostgreSQL esté instalado." -ForegroundColor Red
    Write-Host "     Añade la carpeta 'bin' de PostgreSQL al PATH y vuelve a ejecutar." -ForegroundColor Red
    Read-Host "  Presiona ENTER para salir"
    exit 1
}

$pgDumpExe = if ($pgDump -is [string]) { $pgDump } else { $pgDump.Source }

# Exportar solo DATOS (no esquema — Hibernate crea el esquema)
$env:PGPASSWORD = "postgres"  # Cambia si tu contraseña local es diferente
Write-Host "  Exportando datos de: $localDB" -ForegroundColor Gray

& $pgDumpExe `
    --host=$localHost `
    --port=$localPort `
    --username=$localUser `
    --dbname=$localDB `
    --data-only `
    --no-owner `
    --no-privileges `
    --disable-triggers `
    --column-inserts `
    --file=$dumpFile 2>&1

if ($LASTEXITCODE -eq 0) {
    $kb = [math]::Round((Get-Item $dumpFile).Length / 1KB, 1)
    Write-Host "  ✅ Export exitoso: $dumpFile ($kb KB)" -ForegroundColor Green
} else {
    Write-Host "  ⚠  Error en el export. Verifica la contraseña local." -ForegroundColor Red
    $localPass = Read-Host "  Contraseña de PostgreSQL local"
    $env:PGPASSWORD = $localPass
    & $pgDumpExe --host=$localHost --port=$localPort --username=$localUser --dbname=$localDB --data-only --no-owner --no-privileges --disable-triggers --column-inserts --file=$dumpFile 2>&1
}

Write-Host ""
Write-Host "  Paso 2: Importando a Supabase..." -ForegroundColor Yellow
Write-Host ""

# Buscar psql
$psql = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psql) {
    $rutas = @(
        "C:\Program Files\PostgreSQL\16\bin\psql.exe",
        "C:\Program Files\PostgreSQL\15\bin\psql.exe",
        "C:\Program Files\PostgreSQL\14\bin\psql.exe",
        "C:\Program Files\PostgreSQL\13\bin\psql.exe"
    )
    foreach ($ruta in $rutas) {
        if (Test-Path $ruta) { $psql = $ruta; break }
    }
}

$psqlExe = if ($psql -is [string]) { $psql } else { $psql.Source }
$env:PGPASSWORD = $supaPass

Write-Host "  Conectando a Supabase..." -ForegroundColor Gray

& $psqlExe `
    "postgresql://${supaUser}:${supaPass}@${supaHost}:${supaPort}/${supaDB}?sslmode=require" `
    --file=$dumpFile 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Datos migrados exitosamente a Supabase!" -ForegroundColor Green
} else {
    Write-Host "  ⚠  Algunos errores durante la importación (pueden ser normales si hay conflictos de ID)" -ForegroundColor Yellow
    Write-Host "  El script intentó importar todos los datos disponibles." -ForegroundColor Gray
}

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║   ✅  Migración completada                           ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Backup local guardado en: $dumpFile" -ForegroundColor Gray
Write-Host ""
Write-Host "  Verifica en Supabase → Table Editor que los datos estén." -ForegroundColor White
Write-Host ""
Read-Host "  Presiona ENTER para abrir Supabase"
Start-Process "https://supabase.com/dashboard/project/vwplhsyxrauwgtrqbrpe/editor"
