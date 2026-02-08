# PowerShell deployment script for Todo Chat Bot on Minikube

Write-Host "🚀 Starting local deployment of Todo Chat Bot..." -ForegroundColor Green

# Check if minikube is running
try {
    $minikubeStatus = minikube status --format="{{.Host}}"
    if ($minikubeStatus -ne "Running") {
        Write-Host "❌ Minikube is not running. Please start minikube first:" -ForegroundColor Red
        Write-Host "   minikube start" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Minikube is not running. Please start minikube first:" -ForegroundColor Red
    Write-Host "   minikube start" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Minikube is running" -ForegroundColor Green

# Set Docker environment to use minikube's Docker daemon
Write-Host "🐳 Setting Docker environment to minikube..." -ForegroundColor Cyan
& minikube docker-env --shell powershell | Invoke-Expression

# Build frontend image
Write-Host "🏗️  Building frontend image..." -ForegroundColor Cyan
Set-Location "../frontend"
& docker build -t todo-frontend:latest . --no-cache
Set-Location "../../todo-chat-bot"

# Build backend image
Write-Host "🏗️  Building backend image..." -ForegroundColor Cyan
Set-Location "../backend"
& docker build -t todo-backend:latest . --no-cache
Set-Location "../todo-chat-bot"

Write-Host "✅ Images built successfully" -ForegroundColor Green

# Check if Helm release already exists
$releaseExists = $null
try {
    $releaseStatus = & helm status todo-app
    $releaseExists = $true
} catch {
    $releaseExists = $false
}

if ($releaseExists) {
    Write-Host "🔄 Updating existing release..." -ForegroundColor Yellow
    & helm upgrade todo-app todo-chat-bot -f values-local.yaml
} else {
    Write-Host "📦 Installing new release..." -ForegroundColor Cyan
    & helm install todo-app todo-chat-bot -f values-local.yaml
}

Write-Host "🎉 Deployment completed!" -ForegroundColor Green

Write-Host ""
Write-Host "📱 To access the application:" -ForegroundColor White
try {
    $frontendUrl = & minikube service todo-chat-bot-frontend --url 2>$null
    Write-Host "   Frontend: $frontendUrl" -ForegroundColor White
} catch {
    Write-Host "   Frontend: kubectl port-forward svc/todo-chat-bot-frontend 3000:3000" -ForegroundColor White
}

try {
    $backendUrl = & minikube service todo-chat-bot-backend --url 2>$null
    Write-Host "   Backend:  $backendUrl" -ForegroundColor White
} catch {
    Write-Host "   Backend:  kubectl port-forward svc/todo-chat-bot-backend 7860:7860" -ForegroundColor White
}

Write-Host ""
Write-Host "📊 To check status:" -ForegroundColor White
Write-Host "   kubectl get pods" -ForegroundColor White
Write-Host "   kubectl get services" -ForegroundColor White
Write-Host "   kubectl get ingress" -ForegroundColor White

Write-Host ""
Write-Host "🧹 To cleanup:" -ForegroundColor White
Write-Host "   helm uninstall todo-app" -ForegroundColor White