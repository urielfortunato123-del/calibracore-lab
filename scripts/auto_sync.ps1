$path = (Get-Item -Path ".\").FullName
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $path
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

# Filter out common folders
$exclude = @(".git", "node_modules", "venv", "__pycache__", "uploads", ".gemini")

$action = {
    $itemPath = $Event.SourceEventArgs.FullPath
    $name = $Event.SourceEventArgs.Name
    
    # Check if we should ignore this path
    foreach ($pattern in $exclude) {
        if ($name -match [regex]::Escape($pattern)) { return }
    }

    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] Alteração detectada em: $name" -ForegroundColor Cyan
    
    # Wait for file locks to release and bundle multiple rapid changes
    Start-Sleep -Seconds 5
    
    try {
        Write-Host "Iniciando Sincronismo com GitHub..." -ForegroundColor Yellow
        git add .
        $commitMsg = "Auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git commit -m $commitMsg
        
        Write-Host "Enviando para o servidor..." -ForegroundColor Yellow
        git push origin main
        
        Write-Host "Sucesso! Tudo sincronizado." -ForegroundColor Green
        Write-Host "Aguardando novas alterações..." -ForegroundColor Gray
    } catch {
        Write-Host "Erro ao sincronizar: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Clear previous events
Unregister-Event -SourceIdentifier "FileChanged" -ErrorAction SilentlyContinue

$handlers = @()
$handlers += Register-ObjectEvent $watcher "Changed" -SourceIdentifier "FileChangedChanged" -Action $action
$handlers += Register-ObjectEvent $watcher "Created" -SourceIdentifier "FileChangedCreated" -Action $action
$handlers += Register-ObjectEvent $watcher "Deleted" -SourceIdentifier "FileChangedDeleted" -Action $action
$handlers += Register-ObjectEvent $watcher "Renamed" -SourceIdentifier "FileChangedRenamed" -Action $action

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  CALIBRACORE LAB - AUTO-SYNC GITHUB      " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Monitorando: $path"
Write-Host "Status: ATIVO (Pressione Ctrl+C para parar)" -ForegroundColor Green
Write-Host "------------------------------------------"

while ($true) { Start-Sleep -Seconds 1 }
