# Script to identify stub files in the documentation

# Set the base directories
$docsDir = "docs"

# Common stub phrases to search for
$stubPhrases = @(
    "This is an auto-generated stub file",
    "This is a placeholder",
    "This is a stub",
    "Stub documentation for",
    "TODO: Add content",
    "Content to be added",
    "Documentation coming soon"
)

# Function to check if a file is a stub
function Test-IsStubFile {
    param (
        [string]$filePath
    )
    
    try {
        $content = Get-Content -Path $filePath -Raw -ErrorAction Stop
        
        # Check if content is too short (potential stub)
        if ($content.Trim().Length -lt 500) {
            return $true
        }
        
        # Check for stub phrases
        foreach ($phrase in $stubPhrases) {
            if ($content -match [regex]::Escape($phrase)) {
                return $true
            }
        }
        
        return $false
    }
    catch {
        Write-Warning "Error reading file: $filePath"
        return $false
    }
}

# Get all markdown files in the documentation directory
$markdownFiles = Get-ChildItem -Path $docsDir -Recurse -Filter "*.md" -File | 
    Where-Object { $_.FullName -notlike "*\node_modules\*" }

# Find stub files
$stubFiles = @()
foreach ($file in $markdownFiles) {
    if (Test-IsStubFile -filePath $file.FullName) {
        $stubFiles += $file
    }
}

# Display results
if ($stubFiles.Count -gt 0) {
    Write-Host "`nFound $($stubFiles.Count) potential stub files:" -ForegroundColor Yellow
    $stubFiles | ForEach-Object {
        $relativePath = $_.FullName.Substring((Resolve-Path $PWD).Path.Length + 1)
        Write-Host "- $relativePath" -ForegroundColor Red
    }
    
    # Export to CSV for reference
    $csvPath = "$PSScriptRoot\stub_files_report.csv"
    $stubFiles | Select-Object FullName, LastWriteTime, Length | 
        Export-Csv -Path $csvPath -NoTypeInformation
    
    Write-Host "`nStub files report saved to: $csvPath" -ForegroundColor Green
} else {
    Write-Host "No stub files found in the documentation." -ForegroundColor Green
}

# Also check for empty or nearly empty directories
$emptyDirs = Get-ChildItem -Path $docsDir -Recurse -Directory | 
    Where-Object { (Get-ChildItem -Path $_.FullName -Recurse -File).Count -eq 0 }

if ($emptyDirs.Count -gt 0) {
    Write-Host "`nFound $($emptyDirs.Count) empty or nearly empty directories:" -ForegroundColor Yellow
    $emptyDirs | ForEach-Object {
        $relativePath = $_.FullName.Substring((Resolve-Path $PWD).Path.Length + 1)
        Write-Host "- $relativePath" -ForegroundColor Red
    }
} else {
    Write-Host "`nNo empty directories found." -ForegroundColor Green
}

Write-Host "`nStub file identification complete." -ForegroundColor Cyan
