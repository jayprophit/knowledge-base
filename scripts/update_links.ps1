# PowerShell script to update internal links in markdown files
# to reflect the new directory structure

# Define the base directory
$baseDir = "c:\Users\jpowe\CascadeProjects\github\knowledge-base"

# Define the file mappings (old path -> new path)
$fileMappings = @{
    "architecture.md" = "docs/design/architecture.md"
    "system_design.md" = "docs/design/system_design.md"
    "UNIFIED_SYSTEM_ARCHITECTURE.md" = "docs/design/UNIFIED_SYSTEM_ARCHITECTURE.md"
    "deployment.md" = "docs/operations/deployment.md"
    "DEPLOYMENT_GUIDE.md" = "docs/operations/DEPLOYMENT_GUIDE.md"
    "checklist.md" = "docs/operations/checklist.md"
    "RELEASE_CHECKLIST.md" = "docs/operations/RELEASE_CHECKLIST.md"
    "TROUBLESHOOTING.md" = "docs/operations/TROUBLESHOOTING.md"
    "SECURITY.md" = "docs/operations/SECURITY.md"
    "SUPPORT.md" = "docs/operations/SUPPORT.md"
    "FAQ.md" = "docs/operations/FAQ.md"
    "CODE_OF_CONDUCT.md" = "docs/operations/CODE_OF_CONDUCT.md"
    "GOVERNANCE.md" = "docs/operations/GOVERNANCE.md"
    "safety_ethics.md" = "docs/operations/safety_ethics.md"
    "task_list.md" = "docs/operations/task_list.md"
    "current_goal.md" = "docs/operations/current_goal.md"
    "plan.md" = "docs/operations/plan.md"
    "rollback.md" = "docs/operations/rollback.md"
    "development.md" = "docs/development/development.md"
    "environment.md" = "docs/development/environment.md"
    "integration.md" = "docs/development/integration.md"
    "CONTRIBUTING.md" = "docs/development/CONTRIBUTING.md"
    "TODO.md" = "docs/development/TODO.md"
    "FIXME.md" = "docs/development/FIXME.md"
    "notes.md" = "docs/development/notes.md"
    "CROSS_PLATFORM_README.md" = "docs/development/CROSS_PLATFORM_README.md"
    "FULL_STACK_IMPLEMENTATION.md" = "docs/development/FULL_STACK_IMPLEMENTATION.md"
    "api_gateway.md" = "docs/api/api_gateway.md"
    "advanced_emotional_ai.md" = "docs/reference/advanced_emotional_ai.md"
    "advanced_physics.md" = "docs/reference/advanced_physics.md"
    "advanced_system.md" = "docs/reference/advanced_system.md"
    "changelog.md" = "docs/reference/changelog.md"
    "fairlearn.md" = "docs/reference/fairlearn.md"
    "inherit.md" = "docs/reference/inherit.md"
    "keras-rl2.md" = "docs/reference/keras-rl2.md"
    "memories.md" = "docs/reference/memories.md"
    "method.md" = "docs/reference/method.md"
    "neural_network_predictions.md" = "docs/reference/neural_network_predictions.md"
    "proxy.md" = "docs/reference/proxy.md"
    "qiskit.md" = "docs/reference/qiskit.md"
    "scapy.md" = "docs/reference/scapy.md"
    "web3.md" = "docs/reference/web3.md"
    "3d_model_generation.md" = "docs/design/3d_model_generation.md"
    "3d_printing_export.md" = "docs/design/3d_printing_export.md"
    "cnc_machining_export.md" = "docs/design/cnc_machining_export.md"
    "fea_analysis.md" = "docs/design/fea_analysis.md"
    "gan_design_generation.md" = "docs/design/gan_design_generation.md"
    "generative_design.md" = "docs/design/generative_design.md"
    "genetic_algorithm_optimization.md" = "docs/design/genetic_algorithm_optimization.md"
    "iot_manufacturing.md" = "docs/design/iot_manufacturing.md"
    "multi_material_design.md" = "docs/design/multi_material_design.md"
    "openscad_automation.md" = "docs/design/openscad_automation.md"
}

# Get all markdown files in the repository
try {
    $files = Get-ChildItem -Path $baseDir -Filter "*.md" -Recurse -File -ErrorAction Stop | 
             Where-Object { $_.FullName -notlike '*\.git\*' -and $_.FullName -notlike '*\node_modules\*' }
    
    Write-Host "Found $($files.Count) markdown files to process."
    
    $updatedFiles = 0
    
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($baseDir.Length).TrimStart('\')
        
        # Skip files in the docs directory to avoid modifying our new structure
        if ($relativePath -like 'docs\*') {
            continue
        }
        
        $content = Get-Content -Path $file.FullName -Raw
        $originalContent = $content
        
        foreach ($mapping in $fileMappings.GetEnumerator()) {
            $oldPath = $mapping.Key
            $newPath = $mapping.Value
            
            # Update links with the old filename
            $content = $content -replace "\]\($([regex]::Escape($oldPath))([^)]*)\)", "](/docs/$($mapping.Value)`$1)"
            
            # Update links with the old filename in the same directory
            $oldFileName = [System.IO.Path]::GetFileNameWithoutExtension($oldPath)
            $content = $content -replace "\]\($([regex]::Escape($oldFileName))\.md([^)]*)\)", "](/docs/$($mapping.Value)`$1)"
        }
        
        # Save the file if changes were made
        if ($content -ne $originalContent) {
            Set-Content -Path $file.FullName -Value $content -NoNewline
            Write-Host "Updated links in $relativePath"
            $updatedFiles++
        }
    }
    
    Write-Host "Processing complete. Updated $updatedFiles files."
    
} catch {
    Write-Error "An error occurred: $_"
    exit 1
}
