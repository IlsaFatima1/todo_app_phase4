# PowerShell validation script for Todo Chat Bot deployment

Write-Host "🔍 Validating Todo Chat Bot deployment prerequisites..." -ForegroundColor Cyan
Write-Host ""

$allChecksPassed = $true

# Check if command exists
function Test-Command {
    param($CommandName)

    try {
        if (Get-Command $CommandName -ErrorAction Stop) {
            Write-Host "✓ $CommandName is installed" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "✗ $CommandName is not installed" -ForegroundColor Red
        return $false
    }
}

# Check Minikube status
function Test-MinikubeRunning {
    try {
        $status = & minikube status --format="{{.Host}}" 2>$null
        if ($status -eq "Running") {
            Write-Host "✓ Minikube is running" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Minikube is not running" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Minikube is not running" -ForegroundColor Red
        return $false
    }
}

# Check Docker images
function Test-DockerImages {
    Write-Host "Checking Docker images in Minikube..." -ForegroundColor Cyan

    try {
        & minikube docker-env --shell powershell | Invoke-Expression

        $images = & docker images --format "{{.Repository}}" 2>$null

        if ($images -match "todo-frontend") {
            Write-Host "✓ Frontend image found" -ForegroundColor Green
        } else {
            Write-Host "⚠ Frontend image not found (will need to build)" -ForegroundColor Yellow
        }

        if ($images -match "todo-backend") {
            Write-Host "✓ Backend image found" -ForegroundColor Green
        } else {
            Write-Host "⚠ Backend image not found (will need to build)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ Could not check Docker images" -ForegroundColor Yellow
    }
}

# Run checks
Write-Host "Checking required tools..." -ForegroundColor Cyan
if (-not (Test-Command "minikube")) { $allChecksPassed = $false }
if (-not (Test-Command "kubectl")) { $allChecksPassed = $false }
if (-not (Test-Command "helm")) { $allChecksPassed = $false }
if (-not (Test-Command "docker")) { $allChecksPassed = $false }

if (-not $allChecksPassed) {
    Write-Host ""
    Write-Host "❌ Some required tools are missing. Please install them first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Checking Minikube status..." -ForegroundColor Cyan
if (-not (Test-MinikubeRunning)) {
    Write-Host ""
    Write-Host "Please start Minikube first: minikube start" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Test-DockerImages

Write-Host ""
Write-Host "Validating Helm chart..." -ForegroundColor Cyan
try {
    $lintOutput = & helm lint todo-chat-bot 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Helm chart validation passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Helm chart validation failed" -ForegroundColor Red
        Write-Host $lintOutput
        $allChecksPassed = $false
    }
} catch {
    Write-Host "✗ Helm chart validation failed" -ForegroundColor Red
    $allChecksPassed = $false
}

Write-Host ""
Write-Host "Testing Helm template rendering..." -ForegroundColor Cyan
try {
    $templateOutput = & helm template todo-app todo-chat-bot -f values-local.yaml 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Helm template rendering successful" -ForegroundColor Green
    } else {
        Write-Host "✗ Helm template rendering failed" -ForegroundColor Red
        Write-Host $templateOutput
        $allChecksPassed = $false
    }
} catch {
    Write-Host "✗ Helm template rendering failed" -ForegroundColor Red
    $allChecksPassed = $false
}

Write-Host ""
Write-Host "Checking Kubernetes cluster connectivity..." -ForegroundColor Cyan
try {
    $clusterInfo = & kubectl cluster-info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Kubernetes cluster is accessible" -ForegroundColor Green
    } else {
        Write-Host "✗ Cannot connect to Kubernetes cluster" -ForegroundColor Red
        $allChecksPassed = $false
    }
} catch {
    Write-Host "✗ Cannot connect to Kubernetes cluster" -ForegroundColor Red
    $allChecksPassed = $false
}

Write-Host ""
if ($allChecksPassed) {
    Write-Host "✅ All validation checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now proceed with deployment:" -ForegroundColor White
    Write-Host "  .\deploy-local.ps1" -ForegroundColor Yellow
} else {
    Write-Host "❌ Some validation checks failed. Please fix the issues above." -ForegroundColor Red
    exit 1
}