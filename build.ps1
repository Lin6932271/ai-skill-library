$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonRunner = Join-Path $projectRoot '..\tools\runtime\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonRunner)) { $pythonRunner = Join-Path $projectRoot '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $pythonRunner)) { $pythonRunner = 'python' }
Push-Location -LiteralPath $projectRoot
try {
    & $pythonRunner -m PyInstaller --noconfirm --clean --onefile --windowed --name 'AISkillLibrary' --icon 'frontend\assets\app-icon.ico' --version-file 'version_info.txt' --collect-all webview --add-data 'frontend;frontend' --add-data 'skills;skills' --add-data 'runtime;runtime' 'main.py'
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    Write-Host (Join-Path $projectRoot 'dist\AISkillLibrary.exe')
} finally { Pop-Location }
