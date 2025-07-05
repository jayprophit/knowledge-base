# Script to clean up quantum physics topics directory by removing duplicate _index.md files
# and ensuring consistent structure

# Set the base directory
$baseDir = "resources/documentation/docs/quantum_physics/topics"

# Get all topic directories
$topicDirs = Get-ChildItem -Path $baseDir -Directory

foreach ($dir in $topicDirs) {
    $indexPath = Join-Path -Path $dir.FullName -ChildPath "_index.md"
    $contentPath = Join-Path -Path $dir.FullName -ChildPath "$($dir.Name).md"
    
    # Check if both _index.md and topic_name.md exist
    if ((Test-Path $indexPath) -and (Test-Path $contentPath)) {
        Write-Host "Processing $($dir.Name)..."
        
        # Read both files
        $indexContent = Get-Content -Path $indexPath -Raw
        $contentContent = Get-Content -Path $contentPath -Raw
        
        # If the content is the same, remove _index.md
        if ($indexContent -eq $contentContent) {
            Write-Host "  - Removing duplicate _index.md (same content as $($dir.Name).md)"
            Remove-Item -Path $indexPath -Force
        } else {
            # If content is different, keep both but log a warning
            Write-Warning "  - Both _index.md and $($dir.Name).md exist with different content. Manual review needed."
        }
    }
    
    # If only _index.md exists, rename it to topic_name.md
    elseif ((Test-Path $indexPath) -and (-not (Test-Path $contentPath))) {
        Write-Host "Renaming $($dir.Name)/_index.md to $($dir.Name)/$($dir.Name).md"
        Rename-Item -Path $indexPath -NewName "$($dir.Name).md" -Force
    }
}

Write-Host "\nCleanup complete. Please review any warnings above."
