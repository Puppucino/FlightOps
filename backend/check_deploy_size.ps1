# Check what files will be included in Vercel deployment
# This excludes files based on .vercelignore patterns

Write-Host "Checking files that will be deployed to Vercel..." -ForegroundColor Cyan
Write-Host ""

$excludePatterns = @(
    '__pycache__',
    '\.pyc$',
    'venv',
    '\.venv',
    '\.env',
    '\.git',
    '\.vercel',
    '\.DS_Store',
    'Thumbs\.db',
    '\.log$',
    '\.db$',
    '\.sqlite',
    'scripts',
    'demo_',
    '\.md$',
    'alembic/versions'
)

$files = Get-ChildItem -Recurse -File | Where-Object {
    $path = $_.FullName
    $excluded = $false
    foreach ($pattern in $excludePatterns) {
        if ($path -match $pattern) {
            $excluded = $true
            break
        }
    }
    return -not $excluded
}

$totalSize = ($files | Measure-Object -Property Length -Sum).Sum
$totalSizeMB = [math]::Round($totalSize / 1MB, 2)

Write-Host "Total files to deploy: $($files.Count)" -ForegroundColor Yellow
Write-Host "Total size: $totalSizeMB MB" -ForegroundColor $(if ($totalSizeMB -gt 300) { "Red" } else { "Green" })
Write-Host ""

if ($totalSizeMB -gt 300) {
    Write-Host "⚠️  WARNING: Size exceeds Vercel's 300MB limit!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Largest files:" -ForegroundColor Yellow
    $files | Sort-Object Length -Descending | Select-Object -First 10 | ForEach-Object {
        $sizeMB = [math]::Round($_.Length / 1MB, 2)
        Write-Host "  $($_.FullName.Replace((Get-Location).Path + '\', '')) - $sizeMB MB" -ForegroundColor Gray
    }
} else {
    Write-Host "✅ Size is within Vercel's 300MB limit" -ForegroundColor Green
}

Write-Host ""
Write-Host "Model files:" -ForegroundColor Cyan
Get-ChildItem -Path "models" -File -ErrorAction SilentlyContinue | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  $($_.Name) - $sizeMB MB" -ForegroundColor $(if ($sizeMB -gt 50) { "Yellow" } else { "Gray" })
}
