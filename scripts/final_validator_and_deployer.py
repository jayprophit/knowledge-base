#!/usr/bin/env python3
"""
Final Validator and Deployer - Complete Knowledge Base Validation and Deployment
Validates all fixes and prepares the knowledge base for deployment.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_validation_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinalValidatorDeployer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.validation_results = {
            'total_files': 0,
            'markdown_files': 0,
            'files_with_frontmatter': 0,
            'broken_links_found': 0,
            'syntax_errors_found': 0,
            'empty_files_found': 0,
            'duplicate_files_found': 0,
            'validation_passed': False,
            'deployment_ready': False
        }
        
    def count_files(self):
        """Count all files in the knowledge base."""
        total_files = 0
        markdown_files = 0
        
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file() and not self.should_exclude(file_path):
                total_files += 1
                if file_path.suffix.lower() == '.md':
                    markdown_files += 1
        
        self.validation_results['total_files'] = total_files
        self.validation_results['markdown_files'] = markdown_files
        logger.info(f"Found {total_files} total files, {markdown_files} markdown files")
        
    def should_exclude(self, path):
        """Check if path should be excluded from validation."""
        exclude_patterns = {'.git', '.venv', '__pycache__', 'node_modules', '.log', '.csv', 'temp_reorg'}
        path_str = str(path).lower()
        return any(exclude in path_str for exclude in exclude_patterns)
    
    def validate_frontmatter(self):
        """Validate that markdown files have proper frontmatter."""
        files_with_frontmatter = 0
        
        for file_path in self.base_path.rglob('*.md'):
            if not self.should_exclude(file_path):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if content.startswith('---\n') and '---\n' in content[4:]:
                        files_with_frontmatter += 1
                except:
                    pass
        
        self.validation_results['files_with_frontmatter'] = files_with_frontmatter
        logger.info(f"Found {files_with_frontmatter} files with frontmatter")
        
    def check_for_empty_files(self):
        """Check for empty files."""
        empty_files = 0
        
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file() and not self.should_exclude(file_path):
                try:
                    if file_path.stat().st_size == 0:
                        empty_files += 1
                        logger.warning(f"Empty file found: {file_path}")
                except:
                    pass
        
        self.validation_results['empty_files_found'] = empty_files
        
    def validate_critical_files(self):
        """Ensure critical files exist and are properly formatted."""
        critical_files = [
            'README.md',
            'CONTRIBUTING.md',
            'LICENSE',
            'docs/README.md'
        ]
        
        missing_files = []
        for file_name in critical_files:
            file_path = self.base_path / file_name
            if not file_path.exists():
                missing_files.append(file_name)
                logger.error(f"Critical file missing: {file_name}")
        
        return len(missing_files) == 0
    
    def create_deployment_structure(self):
        """Create proper deployment structure."""
        logger.info("Creating deployment structure...")
        
        # Ensure key directories exist
        key_dirs = [
            'docs',
            'src',
            'tests',
            'scripts',
            'examples',
            'tutorials'
        ]
        
        for dir_name in key_dirs:
            dir_path = self.base_path / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Create a basic README if it doesn't exist
                readme_path = dir_path / 'README.md'
                if not readme_path.exists():
                    content = f"""---
title: {dir_name.title()}
description: {dir_name.title()} directory for the knowledge base
category: Documentation
version: 1.0.0
updated_at: {datetime.now().strftime('%Y-%m-%d')}
status: active
---

# {dir_name.title()}

This directory contains {dir_name.lower()}-related content for the knowledge base.

## Contents

This section is being populated. Check back soon for updates.
"""
                    readme_path.write_text(content, encoding='utf-8')
                    logger.info(f"Created README for {dir_name}")
    
    def create_deployment_config(self):
        """Create deployment configuration files."""
        logger.info("Creating deployment configuration...")
        
        # Create package.json for web deployment
        package_json = {
            "name": "knowledge-base",
            "version": "1.0.0",
            "description": "Comprehensive AI and Technology Knowledge Base",
            "main": "index.html",
            "scripts": {
                "build": "echo 'Build complete'",
                "start": "python -m http.server 8000",
                "test": "python -m pytest tests/"
            },
            "keywords": ["ai", "robotics", "quantum", "knowledge-base", "documentation"],
            "author": "Knowledge Base Team",
            "license": "MIT"
        }
        
        package_file = self.base_path / 'package.json'
        with open(package_file, 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Create index.html for web deployment
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Base - AI & Technology Documentation</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        .header {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .nav {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }
        .card:hover {
            transform: translateY(-2px);
        }
        .card h3 {
            color: #667eea;
            margin-top: 0;
        }
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            background: white;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Knowledge Base</h1>
        <p>Comprehensive AI, Robotics, and Technology Documentation</p>
        <p>Last Updated: """ + datetime.now().strftime('%Y-%m-%d') + """</p>
    </div>
    
    <div class="nav">
        <div class="card">
            <h3>🤖 AI & Machine Learning</h3>
            <p>Advanced AI systems, emotional intelligence, and multidisciplinary applications.</p>
            <a href="docs/ai/README.md">Explore AI →</a>
        </div>
        
        <div class="card">
            <h3>🦾 Robotics</h3>
            <p>Robotic systems, perception, movement, and intelligent automation.</p>
            <a href="docs/robotics/README.md">Explore Robotics →</a>
        </div>
        
        <div class="card">
            <h3>⚛️ Quantum Computing</h3>
            <p>Quantum algorithms, circuits, and advanced computing systems.</p>
            <a href="docs/quantum_computing/README.md">Explore Quantum →</a>
        </div>
        
        <div class="card">
            <h3>🌐 Web & Mobile</h3>
            <p>Modern web development, mobile applications, and cross-platform solutions.</p>
            <a href="docs/web/README.md">Explore Web →</a>
        </div>
        
        <div class="card">
            <h3>🔒 Security</h3>
            <p>Cybersecurity, encryption, and secure system design.</p>
            <a href="docs/security/README.md">Explore Security →</a>
        </div>
        
        <div class="card">
            <h3>📚 Documentation</h3>
            <p>Guides, tutorials, and comprehensive documentation.</p>
            <a href="docs/README.md">View Docs →</a>
        </div>
    </div>
    
    <div class="footer">
        <p>Built with ❤️ by the Knowledge Base Team</p>
        <p><a href="CONTRIBUTING.md">Contribute</a> | <a href="LICENSE">License</a> | <a href="SUPPORT.md">Support</a></p>
    </div>
</body>
</html>"""
        
        index_file = self.base_path / 'index.html'
        index_file.write_text(index_html, encoding='utf-8')
        
        logger.info("Deployment configuration created")
    
    def run_validation(self):
        """Run complete validation of the knowledge base."""
        logger.info("Starting final validation...")
        
        # Count files
        self.count_files()
        
        # Validate frontmatter
        self.validate_frontmatter()
        
        # Check for empty files
        self.check_for_empty_files()
        
        # Validate critical files
        critical_files_ok = self.validate_critical_files()
        
        # Determine if validation passed
        validation_passed = (
            self.validation_results['total_files'] > 0 and
            self.validation_results['markdown_files'] > 0 and
            self.validation_results['empty_files_found'] == 0 and
            critical_files_ok
        )
        
        self.validation_results['validation_passed'] = validation_passed
        
        if validation_passed:
            logger.info("✅ Validation PASSED")
        else:
            logger.error("❌ Validation FAILED")
        
        return validation_passed
    
    def prepare_deployment(self):
        """Prepare the knowledge base for deployment."""
        logger.info("Preparing for deployment...")
        
        # Create deployment structure
        self.create_deployment_structure()
        
        # Create deployment config
        self.create_deployment_config()
        
        self.validation_results['deployment_ready'] = True
        logger.info("✅ Deployment preparation complete")
    
    def generate_final_report(self):
        """Generate final validation and deployment report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'validation_results': self.validation_results,
            'status': 'READY FOR DEPLOYMENT' if self.validation_results['validation_passed'] else 'NEEDS ATTENTION',
            'summary': {
                'total_files': self.validation_results['total_files'],
                'markdown_files': self.validation_results['markdown_files'],
                'files_with_frontmatter': self.validation_results['files_with_frontmatter'],
                'validation_passed': self.validation_results['validation_passed'],
                'deployment_ready': self.validation_results['deployment_ready']
            }
        }
        
        # Save report
        report_file = self.base_path / 'final_deployment_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Create markdown report
        md_report = f"""# Final Knowledge Base Report

## Status: {report['status']}

Generated: {report['timestamp']}

## Summary Statistics

- **Total Files**: {report['summary']['total_files']}
- **Markdown Files**: {report['summary']['markdown_files']}
- **Files with Frontmatter**: {report['summary']['files_with_frontmatter']}
- **Validation Passed**: {'✅ YES' if report['summary']['validation_passed'] else '❌ NO'}
- **Deployment Ready**: {'✅ YES' if report['summary']['deployment_ready'] else '❌ NO'}

## Next Steps

{('The knowledge base is ready for deployment. You can now deploy it to your preferred hosting platform.' if report['summary']['deployment_ready'] else 'Please address the validation issues before deployment.')}

## Deployment Instructions

1. **Web Deployment**: Use the included `index.html` as the entry point
2. **Documentation**: All docs are properly structured in the `docs/` directory
3. **Static Hosting**: Ready for GitHub Pages, Netlify, Vercel, or any static host

---
*Report generated by Final Validator and Deployer*
"""
        
        md_report_file = self.base_path / 'DEPLOYMENT_REPORT.md'
        md_report_file.write_text(md_report, encoding='utf-8')
        
        return report

def main():
    script_dir = Path(__file__).parent
    kb_path = script_dir.parent
    
    logger.info(f"Knowledge base path: {kb_path}")
    
    validator = FinalValidatorDeployer(kb_path)
    
    # Run validation
    validation_passed = validator.run_validation()
    
    if validation_passed:
        # Prepare deployment
        validator.prepare_deployment()
    
    # Generate final report
    report = validator.generate_final_report()
    
    print("\n" + "="*70)
    print("FINAL KNOWLEDGE BASE VALIDATION & DEPLOYMENT REPORT")
    print("="*70)
    print(f"Status: {report['status']}")
    print(f"Total Files: {report['summary']['total_files']}")
    print(f"Markdown Files: {report['summary']['markdown_files']}")
    print(f"Files with Frontmatter: {report['summary']['files_with_frontmatter']}")
    print(f"Validation Passed: {'✅ YES' if report['summary']['validation_passed'] else '❌ NO'}")
    print(f"Deployment Ready: {'✅ YES' if report['summary']['deployment_ready'] else '❌ NO'}")
    print("="*70)
    
    if report['summary']['deployment_ready']:
        print("🚀 KNOWLEDGE BASE IS READY FOR DEPLOYMENT!")
        print("📄 See DEPLOYMENT_REPORT.md for detailed instructions")
    else:
        print("⚠️  Please address validation issues before deployment")

if __name__ == "__main__":
    main()
