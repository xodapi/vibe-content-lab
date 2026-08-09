[CmdletBinding()]
param(
    [ValidateSet("bootstrap", "doctor", "check", "test", "ui", "api", "index", "eval")]
    [string]$Command = "doctor"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
$Node = (Get-Command node -ErrorAction Stop).Source

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Assert-File([string]$Path, [string]$Hint) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Path not found. $Hint"
    }
}

function Get-EnvStatus {
    $envFile = Join-Path $Root ".env"
    if (-not (Test-Path -LiteralPath $envFile)) {
        return @{ exists = $false; openai = $false; vibe = $false; webhook = $false }
    }
    $keys = Get-Content -LiteralPath $envFile |
        Where-Object { $_ -match "^[A-Z0-9_]+=" } |
        ForEach-Object { ($_ -split "=", 2)[0] }
    return @{
        exists = $true
        openai = $keys -contains "OPENAI_API_KEY"
        vibe = $keys -contains "VIBE_API_TOKEN"
        webhook = $keys -contains "VIBE_WEBHOOK_SECRET"
    }
}

Push-Location $Root
try {
    switch ($Command) {
        "bootstrap" {
            Write-Step "Creating Python virtual environment"
            py -m venv .venv
            & $Python -m pip install --upgrade pip
            if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }
            & $Python -m pip install -r backend/requirements-dev.txt
            if ($LASTEXITCODE -ne 0) { throw "Python dependency install failed" }
            Write-Step "Installing locked frontend dependencies"
            Push-Location frontend
            try {
                npm ci --ignore-scripts
                if ($LASTEXITCODE -ne 0) { throw "Frontend dependency install failed" }
            } finally { Pop-Location }
            Write-Step "Bootstrap complete"
        }
        "doctor" {
            Write-Step "Development environment"
            Write-Output "Python: $(& py --version)"
            Write-Output "Node: $(& $Node --version)"
            Write-Output "Docker: $(& docker --version)"
            $state = Get-EnvStatus
            Write-Output "Local .env: $($state.exists)"
            Write-Output "OpenAI key configured: $($state.openai)"
            Write-Output "Vibe key configured: $($state.vibe)"
            Write-Output "Webhook secret configured: $($state.webhook)"
            if (-not $state.exists) {
                Write-Output "Next: Copy-Item .env.example .env (never commit it)."
            }
        }
        "check" {
            Assert-File $Python "Run: .\scripts\harness.ps1 bootstrap"
            Write-Step "Python compile and Ruff"
            & $Python -m compileall -q backend rag
            if ($LASTEXITCODE -ne 0) { throw "Python compilation failed" }
            & $Python -m ruff check backend rag
            if ($LASTEXITCODE -ne 0) { throw "Ruff checks failed" }
            Write-Step "Workflow JSON"
            Get-Content n8n/daily-api-knowledge-digest.json -Raw | ConvertFrom-Json | Out-Null
            Get-Content rag/evaluation/ground_truth.json -Raw | ConvertFrom-Json | Out-Null
            Write-Step "React production build"
            Push-Location frontend
            try {
                & $Node ./node_modules/vite/bin/vite.js build
                if ($LASTEXITCODE -ne 0) { throw "React build failed" }
            } finally { Pop-Location }
            Write-Step "All checks passed"
        }
        "test" {
            Assert-File $Python "Run: .\scripts\harness.ps1 bootstrap"
            & $Python -m pytest
            if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
        }
        "ui" {
            Push-Location frontend
            try { & $Node ./node_modules/vite/bin/vite.js } finally { Pop-Location }
        }
        "api" {
            Assert-File $Python "Run: .\scripts\harness.ps1 bootstrap"
            & $Python -m uvicorn backend.app.main:app --reload --port 8000
        }
        "index" {
            Assert-File $Python "Run: .\scripts\harness.ps1 bootstrap"
            & $Python -m rag.ingest
        }
        "eval" {
            Assert-File $Python "Run: .\scripts\harness.ps1 bootstrap"
            & $Python -m rag.evaluation.run
        }
    }
}
finally {
    Pop-Location
}
