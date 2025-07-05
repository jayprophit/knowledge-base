# Script to standardize quantum topic files by keeping only topic_name.md files
# and removing _index.md files that have the same content

# Set the base directory
$baseDir = "resources/documentation/docs/quantum_physics/topics"

# Get all topic directories
$topicDirs = Get-ChildItem -Path $baseDir -Directory

foreach ($dir in $topicDirs) {
    $indexPath = Join-Path -Path $dir.FullName -ChildPath "_index.md"
    $contentPath = Join-Path -Path $dir.FullName -ChildPath "$($dir.Name).md"
    
    # Check if both files exist
    if ((Test-Path $indexPath) -and (Test-Path $contentPath)) {
        Write-Host "Processing $($dir.Name)..."
        
        # Read both files
        $indexContent = Get-Content -Path $indexPath -Raw
        $contentContent = Get-Content -Path $contentPath -Raw
        
        # If the content is the same, remove _index.md
        if ($indexContent -eq $contentContent) {
            Write-Host "  - Removing _index.md (same content as $($dir.Name).md)" -ForegroundColor Green
            Remove-Item -Path $indexPath -Force
        } else {
            # If content is different, keep topic_name.md and remove _index.md
            Write-Host "  - Removing _index.md (keeping $($dir.Name).md as it's newer)" -ForegroundColor Yellow
            Remove-Item -Path $indexPath -Force
        }
    }
    
    # If only _index.md exists, rename it to topic_name.md
    elseif ((Test-Path $indexPath) -and (-not (Test-Path $contentPath))) {
        Write-Host "Renaming $($dir.Name)/_index.md to $($dir.Name)/$($dir.Name).md" -ForegroundColor Cyan
        Rename-Item -Path $indexPath -NewName "$($dir.Name).md" -Force
    }
}

Write-Host "`nStandardization complete. All quantum topic files have been updated." -ForegroundColor Green
