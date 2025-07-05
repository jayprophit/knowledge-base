# Script to check differences between _index.md and topic_name.md files
# and help decide which content to keep

# Set the base directory
$baseDir = "resources/documentation/docs/quantum_physics/topics"

# Get all topic directories
$topicDirs = Get-ChildItem -Path $baseDir -Directory

foreach ($dir in $topicDirs) {
    $indexPath = Join-Path -Path $dir.FullName -ChildPath "_index.md"
    $contentPath = Join-Path -Path $dir.FullName -ChildPath "$($dir.Name).md"
    
    # Check if both files exist
    if ((Test-Path $indexPath) -and (Test-Path $contentPath)) {
        Write-Host "`n=== $($dir.Name) ===" -ForegroundColor Cyan
        
        # Get file info
        $indexInfo = Get-Item $indexPath
        $contentInfo = Get-Item $contentPath
        
        # Compare last write times
        if ($indexInfo.LastWriteTime -gt $contentInfo.LastWriteTime) {
            Write-Host "  - _index.md is newer than $($dir.Name).md" -ForegroundColor Yellow
        } else {
            Write-Host "  - $($dir.Name).md is newer than _index.md" -ForegroundColor Green
        }
        
        # Get line counts
        $indexLines = (Get-Content $indexPath).Count
        $contentLines = (Get-Content $contentPath).Count
        
        Write-Host "  - _index.md lines: $indexLines"
        Write-Host "  - $($dir.Name).md lines: $contentLines"
        
        # Get first few lines of each file
        Write-Host "`n  _index.md preview:"
        Get-Content $indexPath -TotalCount 10 | ForEach-Object { "    $_" }
        
        Write-Host "`n  $($dir.Name).md preview:"
        Get-Content $contentPath -TotalCount 10 | ForEach-Object { "    $_" }
        
        Write-Host "`n  ---"
    }
}

Write-Host "`nComparison complete. Review the differences above to decide which files to keep."
