# Script to update internal links in markdown files to reflect the new quantum physics topic structure

# Set the base directories
$docsDir = "resources/documentation/docs"
$quantumTopicsDir = "$docsDir/quantum_physics/topics"

# Get all markdown files in the documentation directory
$markdownFiles = Get-ChildItem -Path $docsDir -Recurse -Filter "*.md" -File | 
    Where-Object { $_.FullName -notlike "*\node_modules\*" }

# Get all quantum topic directories
$quantumTopics = Get-ChildItem -Path $quantumTopicsDir -Directory | Select-Object -ExpandProperty Name

# Create a hashtable of old paths to new paths
$pathMappings = @{}
foreach ($topic in $quantumTopics) {
    $oldPath = "quantum_physics/topics/$topic/_index.md"
    $newPath = "quantum_physics/topics/$topic/$topic.md"
    $pathMappings[$oldPath] = $newPath
    
    # Also add variations with and without leading slash
    $pathMappings["/$oldPath"] = "/$newPath"
    $pathMappings["$oldPath"] = "$newPath"
}

# Counter for tracking updates
$updateCount = 0

# Process each markdown file
foreach ($file in $markdownFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    $originalContent = $content
    
    # Check if the file contains any of the old paths
    $hasUpdates = $false
    foreach ($oldPath in $pathMappings.Keys) {
        if ($content -match $oldPath) {
            $newPath = $pathMappings[$oldPath]
            $content = $content -replace [regex]::Escape($oldPath), $newPath
            $hasUpdates = $true
        }
    }
    
    # If updates were made, write the file back
    if ($hasUpdates) {
        $updateCount++
        Set-Content -Path $file.FullName -Value $content -NoNewline
        Write-Host "Updated links in $($file.FullName)" -ForegroundColor Green
    }
}

Write-Host "`nLink update complete. Updated $updateCount files." -ForegroundColor Cyan
