## PowerShell Link Checker Script
## Scans markdown files for links and verifies they exist

# Parameters for the script
param(
    [Parameter(Mandatory = $false)]
    [string]$RootDirectory = (Get-Location),
    
    [Parameter(Mandatory = $false)]
    [switch]$GenerateCsv = $false,
    
    [Parameter(Mandatory = $false)]
    [string]$OutputCsv = "broken-links-report.csv"
)

# Function to check if a file exists
function Test-FileExists {
    param (
        [string]$BasePath,
        [string]$RelativePath
    )
    
    # Clean the path - remove any URL parameters or anchors
    $cleanPath = $RelativePath -replace '#.*$', '' -replace '\?.*$', ''
    
    # If it's a web URL, don't try to check it locally
    if ($cleanPath -match '^(http|https|ftp)://') {
        return $true # We'll assume web URLs are valid for now
    }

    # For local paths, resolve the full path
    try {
        # Normalize path separators to system standard
        $cleanPath = $cleanPath -replace '/', [IO.Path]::DirectorySeparatorChar
        
        # Construct the full path
        $fullPath = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($BasePath, $cleanPath))
        
        # Check if the file exists
        $exists = Test-Path -Path $fullPath -ErrorAction SilentlyContinue
        
        return $exists
    } 
    catch {
        Write-Warning "Error processing path: $cleanPath - $($_.Exception.Message)"
        return $false
    }
}

# Main function to test links
function Test-MarkdownLinks {
    param (
        [string]$Directory
    )
    
    Write-Host "Scanning for markdown files in: $Directory" -ForegroundColor Cyan
    
    # Find all markdown files in the directory and subdirectories
    $markdownFiles = Get-ChildItem -Path $Directory -Filter "*.md" -Recurse -File
    
    Write-Host "Found $($markdownFiles.Count) markdown files to check" -ForegroundColor Cyan
    
    # Counters for statistics
    $totalLinks = 0
    $brokenLinks = 0
    $filesWithBrokenLinks = @()
    
    foreach ($file in $markdownFiles) {
        $fileContent = Get-Content -Path $file.FullName -Raw
        $fileBasePath = [System.IO.Path]::GetDirectoryName($file.FullName)
        $localBrokenLinks = 0
        
        # Match all markdown links using regex
        $linkMatches = [regex]::Matches($fileContent, '\[(?:[^\[\]]|(?<Square>\[)|(?<-Square>\]))*\]\(([^)]+)\)')
        
        foreach ($match in $linkMatches) {
            $totalLinks++
            $linkTarget = $match.Groups[1].Value.Trim()
            
            # Check if the link is valid
            $exists = Test-FileExists -BasePath $fileBasePath -RelativePath $linkTarget
            
            if (-not $exists) {
                $brokenLinks++
                $localBrokenLinks++
                Write-Host "BROKEN LINK in $($file.Name): $linkTarget" -ForegroundColor Red
            }
        }
        
        if ($localBrokenLinks -gt 0) {
            $filesWithBrokenLinks += $file.FullName
        }
    }
    
    # Display summary
    Write-Host "`n--- Link Check Summary ---" -ForegroundColor Green
    Write-Host "Total links checked: $totalLinks" -ForegroundColor White
    Write-Host "Broken links found: $brokenLinks" -ForegroundColor $(if ($brokenLinks -gt 0) { 'Red' } else { 'Green' })
    Write-Host "Files with broken links: $($filesWithBrokenLinks.Count)" -ForegroundColor $(if ($filesWithBrokenLinks.Count -gt 0) { 'Red' } else { 'Green' })
    
    # List files with broken links
    if ($filesWithBrokenLinks.Count -gt 0) {
        Write-Host "`nFiles with broken links:" -ForegroundColor Yellow
        foreach ($brokenFile in $filesWithBrokenLinks) {
            Write-Host " - $brokenFile" -ForegroundColor Yellow
        }
    }
    
    # Generate CSV report if requested
    if ($GenerateCsv -and $brokenLinks -gt 0) {
        $brokenLinksData = @()
        
        foreach ($file in $markdownFiles) {
            $fileContent = Get-Content -Path $file.FullName -Raw
            $fileBasePath = [System.IO.Path]::GetDirectoryName($file.FullName)
            
            # Match all markdown links using regex
            $linkMatches = [regex]::Matches($fileContent, '\[(?:[^\[\]]|(?<Square>\[)|(?<-Square>\]))*\]\(([^)]+)\)')
            
            foreach ($match in $linkMatches) {
                $linkTarget = $match.Groups[1].Value.Trim()
                $exists = Test-FileExists -BasePath $fileBasePath -RelativePath $linkTarget
                
                if (-not $exists) {
                    # Get the link text as well
                    $linkText = $match.Value -replace '\[(.*?)\]\(.*?\)', '$1'
                    
                    # Create an object for the broken link
                    $brokenLink = [PSCustomObject]@{
                        SourceFile = $file.FullName
                        SourceFileName = $file.Name
                        BrokenLink = $linkTarget
                        LinkText = $linkText
                        RelativePath = [System.IO.Path]::GetRelativePath($RootDirectory, $file.FullName)
                    }
                    
                    $brokenLinksData += $brokenLink
                }
            }
        }
        
        # Export the data to CSV
        $brokenLinksData | Export-Csv -Path $OutputCsv -NoTypeInformation
        Write-Host "`nCSV report generated at: $OutputCsv" -ForegroundColor Cyan
    }
}

# Execute the main function
Test-MarkdownLinks -Directory $RootDirectory

Write-Host "`nLink checking completed!" -ForegroundColor Green
