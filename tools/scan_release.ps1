param(
    [Parameter(Mandatory=$true)][string]$Exe,
    [Parameter(Mandatory=$true)][string]$Out
)
$ErrorActionPreference = 'Stop'
$sample = Get-Item -LiteralPath $Exe
if ($sample.PSIsContainer) { throw 'An executable file is required' }
$outputDirectory = [System.IO.Path]::GetFullPath($Out)
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
$beforeHash = (Get-FileHash -LiteralPath $sample.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
$statusBefore = Get-MpComputerStatus
$signature = Get-AuthenticodeSignature -LiteralPath $sample.FullName
$platformRoot = Join-Path $env:ProgramData 'Microsoft\Windows Defender\Platform'
$platform = Get-ChildItem -LiteralPath $platformRoot -Directory | Sort-Object Name -Descending | Select-Object -First 1
$scanner = Join-Path $platform.FullName 'MpCmdRun.exe'
if (-not (Test-Path -LiteralPath $scanner)) { $scanner = Join-Path $env:ProgramFiles 'Windows Defender\MpCmdRun.exe' }
$started = [DateTimeOffset]::UtcNow.ToString('o')
$scanLog = Join-Path $outputDirectory 'defender-scan.log'
& $scanner -Scan -ScanType 3 -File $sample.FullName -DisableRemediation *> $scanLog
$returnCode = $LASTEXITCODE
$statusAfter = Get-MpComputerStatus
$afterHash = (Get-FileHash -LiteralPath $sample.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
$text = Get-Content -LiteralPath $scanLog -Raw
$record = [ordered]@{
    sample_sha256 = $beforeHash
    sample_unchanged = ($beforeHash -eq $afterHash)
    started_utc = $started
    finished_utc = [DateTimeOffset]::UtcNow.ToString('o')
    return_code = $returnCode
    output_reports_no_threats = ($text -match 'found no threats|no threats found')
    disable_remediation = $true
    authenticode_status = $signature.Status.ToString()
    platform_version = $statusAfter.AMProductVersion
    engine_version = $statusAfter.AMEngineVersion
    intelligence_version = $statusAfter.AntivirusSignatureVersion
    intelligence_updated_utc = $statusAfter.AntivirusSignatureLastUpdated.ToUniversalTime().ToString('o')
    antivirus_enabled = $statusAfter.AntivirusEnabled
    realtime_protection_enabled = $statusAfter.RealTimeProtectionEnabled
    protection_settings_unchanged = (($statusBefore.AntivirusEnabled -eq $statusAfter.AntivirusEnabled) -and ($statusBefore.RealTimeProtectionEnabled -eq $statusAfter.RealTimeProtectionEnabled))
    scope = 'Single local file; no explicit external multi-engine upload; no remediation or protection-setting changes'
}
$jsonPath = Join-Path $outputDirectory 'defender-result.json'
[System.IO.File]::WriteAllText($jsonPath, ($record | ConvertTo-Json -Depth 5), [System.Text.UTF8Encoding]::new($false))
$record | ConvertTo-Json -Depth 5
if ($beforeHash -ne $afterHash) { throw 'Sample changed during scan' }
if ($returnCode -ne 0) { exit $returnCode }
