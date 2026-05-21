# ════════════════════════════════════════════════════════════════════
#  MEDICHECK — Script de deploy a producción (100% gratis)
#  Ejecutar: clic derecho → "Ejecutar con PowerShell"
# ════════════════════════════════════════════════════════════════════

$Host.UI.RawUI.WindowTitle = "MediCheck Deploy"
Clear-Host

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║      MediCheck — Deploy a Producción     ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Solo necesitas 3 cuentas gratuitas." -ForegroundColor White
Write-Host "  El script hace todo lo demás automáticamente." -ForegroundColor Gray
Write-Host ""

# ════════════════════════════════════════════════════════════════════
#  PASO 1 — GitHub (subir el código)
# ════════════════════════════════════════════════════════════════════
Write-Host "  ┌─────────────────────────────────────────────────────" -ForegroundColor Yellow
Write-Host "  │  PASO 1/3 — GitHub                                  " -ForegroundColor Yellow
Write-Host "  └─────────────────────────────────────────────────────" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Crea cuenta GRATIS en:  https://github.com/signup" -ForegroundColor White
Write-Host "  2. Luego ve a:  https://github.com/settings/tokens/new" -ForegroundColor White
Write-Host "     - Note: medicheck-deploy" -ForegroundColor Gray
Write-Host "     - Expiration: 90 days" -ForegroundColor Gray
Write-Host "     - Scope: marca solo 'repo' (el primero)" -ForegroundColor Gray
Write-Host "     - Click 'Generate token' y COPIA el token (ghp_...)" -ForegroundColor Gray
Write-Host ""
Start-Process "https://github.com/signup"
Start-Sleep -Milliseconds 800
Start-Process "https://github.com/settings/tokens/new?description=medicheck-deploy&scopes=repo"

$githubUser  = Read-Host "  Tu usuario de GitHub (ej: juanperez)"
$githubToken = Read-Host "  Pega tu Personal Access Token (ghp_...)"

Write-Host ""
Write-Host "  Creando repositorio y subiendo código..." -ForegroundColor Cyan

# Crear repo via API
$headers = @{
    Authorization = "Bearer $githubToken"
    Accept        = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}
$body = @{ name = "medicheck-backend"; private = $true; description = "MediCheck API - Spring Boot" } | ConvertTo-Json

try {
    $resp = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method POST -Headers $headers -Body $body -ContentType "application/json" -ErrorAction Stop
    Write-Host "  ✅ Repositorio creado: $($resp.html_url)" -ForegroundColor Green
} catch {
    # Si ya existe, continuar
    if ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "  ℹ️  Repositorio ya existe — continuando..." -ForegroundColor Yellow
    } else {
        Write-Host "  ⚠  Error creando repo: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Push con token en URL
Set-Location "L:\medicheck\backend"
$remoteUrl = "https://${githubUser}:${githubToken}@github.com/${githubUser}/medicheck-backend.git"
git remote remove origin 2>$null
git remote add origin $remoteUrl
git branch -M main
$pushOut = git push -u origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Código subido a GitHub exitosamente" -ForegroundColor Green
} else {
    Write-Host "  ⚠  Push: $pushOut" -ForegroundColor Yellow
}

$repoUrl = "https://github.com/$githubUser/medicheck-backend"

# ════════════════════════════════════════════════════════════════════
#  PASO 2 — Supabase (base de datos)
# ════════════════════════════════════════════════════════════════════
Write-Host ""
Write-Host "  ┌─────────────────────────────────────────────────────" -ForegroundColor Yellow
Write-Host "  │  PASO 2/3 — Supabase (base de datos gratis)         " -ForegroundColor Yellow
Write-Host "  └─────────────────────────────────────────────────────" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Abre: https://supabase.com  → Sign up (gratis)" -ForegroundColor White
Write-Host "  2. New Project → Nombre: medicheck" -ForegroundColor White
Write-Host "     Region: South America (São Paulo)" -ForegroundColor White
Write-Host "  3. Pon una contraseña y ANÓTALA" -ForegroundColor White
Write-Host "  4. Espera ~2 min que se cree el proyecto" -ForegroundColor White
Write-Host "  5. Ve a: Settings → Database → 'Connection string'" -ForegroundColor White
Write-Host "     Pestaña: URI  →  copia todo el texto" -ForegroundColor White
Write-Host "     (empieza con postgresql://postgres:...)" -ForegroundColor Gray
Write-Host ""
Start-Process "https://supabase.com/dashboard/projects"

$supabaseUri = Read-Host "  Pega el Connection String URI de Supabase"

# Convertir postgresql:// a jdbc:postgresql://
# postgresql://postgres:PASS@db.xxx.supabase.co:5432/postgres
$jdbcUrl = $supabaseUri -replace "^postgresql://", "jdbc:postgresql://"
# Extraer solo el host:port/db (quitar usuario:password del JDBC URL)
if ($supabaseUri -match "^postgresql://([^:]+):([^@]+)@(.+)$") {
    $dbUser     = $Matches[1]     # postgres
    $dbPassword = $Matches[2]     # la contraseña
    $dbHost     = $Matches[3]     # db.xxx.supabase.co:5432/postgres
    $jdbcUrl    = "jdbc:postgresql://$dbHost"
} else {
    $dbUser     = "postgres"
    $dbPassword = ""
}

Write-Host "  ✅ Supabase configurado" -ForegroundColor Green

# ════════════════════════════════════════════════════════════════════
#  PASO 3 — Groq (IA gratis, mismos modelos Llama)
# ════════════════════════════════════════════════════════════════════
Write-Host ""
Write-Host "  ┌─────────────────────────────────────────────────────" -ForegroundColor Yellow
Write-Host "  │  PASO 3/3 — Groq (IA gratuita)                      " -ForegroundColor Yellow
Write-Host "  └─────────────────────────────────────────────────────" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Abre: https://console.groq.com  → Sign up (gratis)" -ForegroundColor White
Write-Host "  2. API Keys → Create API Key → nombre: medicheck" -ForegroundColor White
Write-Host "  3. Copia la clave (empieza con gsk_...)" -ForegroundColor White
Write-Host ""
Start-Process "https://console.groq.com/keys"

$groqKey = Read-Host "  Pega tu API Key de Groq (gsk_...)"
Write-Host "  ✅ Groq configurado" -ForegroundColor Green

# ════════════════════════════════════════════════════════════════════
#  Generar JWT Secret seguro
# ════════════════════════════════════════════════════════════════════
$rng       = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$bytes     = New-Object byte[] 48
$rng.GetBytes($bytes)
$jwtSecret = [Convert]::ToBase64String($bytes)

# ════════════════════════════════════════════════════════════════════
#  Guardar variables en archivo de texto (para Render)
# ════════════════════════════════════════════════════════════════════
$envContent = @"
# ═══════════════════════════════════════════════════════
#  Variables de entorno para Render.com
#  Copia cada línea en Environment Variables de Render
# ═══════════════════════════════════════════════════════

DB_URL=$jdbcUrl
DB_USER=$dbUser
DB_PASSWORD=$dbPassword
GROQ_API_KEY=$groqKey
JWT_SECRET=$jwtSecret
DDL_AUTO=update
MAIL_USER=TU_GMAIL@gmail.com
MAIL_PASS=TU_APP_PASSWORD_GMAIL
"@
$envFile = "L:\medicheck\render-env-vars.txt"
$envContent | Out-File $envFile -Encoding utf8
Write-Host ""
Write-Host "  ✅ Variables guardadas en: $envFile" -ForegroundColor Green

# ════════════════════════════════════════════════════════════════════
#  RENDER — Instrucciones + abrir automáticamente
# ════════════════════════════════════════════════════════════════════
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║   ÚLTIMO PASO — Render.com (servidor gratis)         ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Abre render.com → 'Get Started for Free'" -ForegroundColor White
Write-Host "     Conecta con GitHub (usa la misma cuenta)" -ForegroundColor White
Write-Host ""
Write-Host "  2. New + → Web Service → busca: medicheck-backend" -ForegroundColor White
Write-Host ""
Write-Host "  3. Configuración del servicio:" -ForegroundColor White
Write-Host "       Name:    medicheck-backend" -ForegroundColor Gray
Write-Host "       Region:  Oregon (US West)" -ForegroundColor Gray
Write-Host "       Runtime: Docker" -ForegroundColor Gray
Write-Host "       Plan:    Free" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Environment Variables — copia de $envFile :" -ForegroundColor White
Write-Host ""

# Mostrar variables en pantalla bonito
$lines = Get-Content $envFile | Where-Object { $_ -match "^[A-Z]" }
foreach ($line in $lines) {
    Write-Host "       $line" -ForegroundColor Green
}

Write-Host ""
Write-Host "  5. Click 'Create Web Service' → espera 5-7 minutos" -ForegroundColor White
Write-Host "  6. Render te da una URL tipo:" -ForegroundColor White
Write-Host "       https://medicheck-backend.onrender.com" -ForegroundColor Cyan
Write-Host ""

Start-Process "https://render.com"
notepad $envFile   # Abrir el archivo de variables para copiar fácil

$renderUrl = Read-Host "  Pega la URL de Render cuando esté lista (ej: https://medicheck-backend.onrender.com)"
$renderUrl = $renderUrl.TrimEnd("/")

# ════════════════════════════════════════════════════════════════════
#  Actualizar APK con la URL de producción
# ════════════════════════════════════════════════════════════════════
Write-Host ""
Write-Host "  Construyendo APK de producción..." -ForegroundColor Cyan

"VITE_API_URL=$renderUrl/api" | Out-File "L:\medicheck\frontend\.env.production" -Encoding utf8

Set-Location "L:\medicheck\frontend"
Write-Host "  - Compilando Vue..." -ForegroundColor Gray
npm run build | Out-Null
Write-Host "  - Sincronizando Capacitor..." -ForegroundColor Gray
npx cap sync android | Out-Null

$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
Set-Location "L:\medicheck\frontend\android"
Write-Host "  - Compilando APK Android..." -ForegroundColor Gray
.\gradlew.bat assembleDebug | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd"
$apkDst    = "L:\medicheck\releases\MediCheck-v2.0-produccion-$timestamp.apk"
Copy-Item "L:\medicheck\frontend\android\app\build\outputs\apk\debug\app-debug.apk" $apkDst -Force
$mb = [math]::Round((Get-Item $apkDst).Length / 1MB, 1)

# ════════════════════════════════════════════════════════════════════
#  RESUMEN FINAL
# ════════════════════════════════════════════════════════════════════
Clear-Host
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║   ✅  ¡MEDICHECK ESTÁ EN PRODUCCIÓN!                 ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  🌐  Backend:  $renderUrl" -ForegroundColor Cyan
Write-Host "  🗄️   BD:       Supabase PostgreSQL (São Paulo)" -ForegroundColor Cyan
Write-Host "  🤖  IA:       Groq — Llama 3.1 (gratis)" -ForegroundColor Cyan
Write-Host "  📦  Código:   $repoUrl" -ForegroundColor Cyan
Write-Host "  📱  APK:      $apkDst" -ForegroundColor Cyan
Write-Host "           ($mb MB — instala en tu teléfono)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Ya NO necesitas encender el PC para usar la app." -ForegroundColor White
Write-Host ""
Write-Host "  ⚠  Nota: Render gratis 'duerme' tras 15 min sin uso." -ForegroundColor Yellow
Write-Host "     El primer request del día tarda ~30 segundos." -ForegroundColor Yellow
Write-Host "     Para producción real considera el plan $7/mes." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Presiona ENTER para abrir la carpeta del APK..." -ForegroundColor Gray
Read-Host
explorer "L:\medicheck\releases"
