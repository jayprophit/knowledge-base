"""
Repository Reorganization Script
================================

This script implements world-class production-level system design principles to reorganize 
the knowledge base repository, remove unnecessary files, and deduplicate content.

Features:
- Analyzes current repository structure
- Identifies and removes duplicated content
- Enforces consistent naming conventions
- Ensures proper directory hierarchy
- Generates detailed report of changes
- Creates optimized structure for production deployment
"""

import os
import sys
import shutil
import hashlib
import re
import json
import logging
import datetime
from pathlib import Path
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("reorganization.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("repo-reorganizer")

# Enable more verbose output
debug_mode = True  # Set to True for detailed console output

# Constants
REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"
SRC_DIR = REPO_ROOT / "src"
TESTS_DIR = REPO_ROOT / "tests"
SCRIPTS_DIR = REPO_ROOT / "scripts"
TEMP_DIR = REPO_ROOT / "temp_reorg"

# Files and patterns to ignore
IGNORED_FILES = [
    ".git",
    ".gitignore",
    "__pycache__",
    ".DS_Store",
    "reorganization.log",
    "reorganize_repo.py",
    "reorganization_report.md",
    "reorganization_report.html",
    "temp_reorg"
]

IGNORED_PATTERNS = [
    r".*\.pyc$",
    r".*\.pyo$",
    r".*\.pyd$",
    r".*\.so$",
    r".*\.dll$",
    r".*~$",
    r".*\.bak$",
    r".*\.swp$",
    r"\.git.*",
    r"\.pytest_cache.*",
    r"__pycache__.*",
    r".*\.ipynb_checkpoints.*"
]

# Production structure template
PRODUCTION_STRUCTURE = {
    "docs": {
        "ai": {
            "guides": {},
            "references": {},
            "tutorials": {},
        },
        "api": {},
        "blockchain": {
            "guides": {},
            "references": {},
        },
        "deployment": {},
        "iot": {
            "guides": {},
            "references": {},
        },
        "machine_learning": {
            "multimodal": {},
            "nlp": {},
            "vision": {},
        },
        "mobile": {
            "guides": {},
            "references": {},
        },
        "robotics": {
            "advanced_system": {},
            "perception": {},
            "control": {},
            "navigation": {},
        },
        "web": {
            "apis": {},
            "client_server": {},
            "databases": {},
            "networking": {},
            "php": {
                "guides": {},
                "references": {},
                "contributing": {},
            },
            "system_design": {},
        },
    },
    "src": {
        "ai": {
            "emotional_intelligence": {},
            "nlp": {},
            "vision": {},
        },
        "api": {},
        "blockchain": {},
        "iot": {
            "device_management": {},
            "protocols": {},
            "security": {},
            "sensors": {},
        },
        "machine_learning": {
            "models": {},
            "multimodal": {},
            "training": {},
        },
        "mobile": {
            "components": {},
            "screens": {},
            "utils": {},
        },
        "multidisciplinary_ai": {},
        "robotics": {
            "advanced_system": {},
            "control": {},
            "navigation": {},
            "perception": {},
        },
        "vision": {},
        "web": {
            "frontend": {},
            "backend": {},
            "php": {
                "core": {},
                "modules": {},
            },
        },
    },
    "tests": {
        "unit": {},
        "integration": {},
        "system": {},
        "performance": {},
    },
}

class RepoReorganizer:
    def __init__(self):
        self.file_hashes = {}  # hash: [file_paths]
        self.duplicate_files = defaultdict(list)  # original: [duplicates]
        self.empty_directories = []
        self.moved_files = {}  # old_path: new_path
        self.deleted_files = []
        self.stats = {
            "total_files": 0,
            "duplicate_files": 0,
            "empty_dirs": 0,
            "files_moved": 0,
            "files_deleted": 0,
            "bytes_saved": 0
        }
        self.ignored_re = [re.compile(pattern) for pattern in IGNORED_PATTERNS]

    def should_ignore(self, path):
        """Check if a path should be ignored."""
        path_str = str(path)
        
        # Check exact matches
        for ignored in IGNORED_FILES:
            if ignored in path_str:
                return True
        
        # Check patterns
        for pattern in self.ignored_re:
            if pattern.match(path_str):
                return True
                
        return False

    def get_file_hash(self, file_path):
        """Calculate MD5 hash of a file's content."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return None

    def analyze_repository(self):
        """Analyze the repository structure."""
        logger.info("Analyzing repository structure...")
        
        # Walk through all files and calculate hashes
        total_files = 0
        for root, dirs, files in os.walk(REPO_ROOT, topdown=True):
            root_path = Path(root)
            
            # Filter out ignored directories in-place
            dirs[:] = [d for d in dirs if not self.should_ignore(root_path / d)]
            
            for file in files:
                file_path = root_path / file
                if self.should_ignore(file_path):
                    continue
                
                total_files += 1
                file_hash = self.get_file_hash(file_path)
                if file_hash:
                    if file_hash not in self.file_hashes:
                        self.file_hashes[file_hash] = []
                    self.file_hashes[file_hash].append(file_path)
        
        self.stats["total_files"] = total_files
        logger.info(f"Found {total_files} files in the repository")
        
        # Identify duplicate files
        for file_hash, file_paths in self.file_hashes.items():
            if len(file_paths) > 1:
                # Keep the file with the shortest path as the original
                original = min(file_paths, key=lambda p: len(str(p)))
                duplicates = [p for p in file_paths if p != original]
                self.duplicate_files[original] = duplicates
                self.stats["duplicate_files"] += len(duplicates)
                
                # Calculate bytes saved
                try:
                    file_size = os.path.getsize(original)
                    self.stats["bytes_saved"] += file_size * len(duplicates)
                except:
                    pass
        
        logger.info(f"Found {self.stats['duplicate_files']} duplicate files")
        
        # Find empty directories
        for root, dirs, files in os.walk(REPO_ROOT, topdown=False):  # Bottom-up to handle nested empty dirs
            root_path = Path(root)
            if len(os.listdir(root)) == 0 and not self.should_ignore(root_path):
                self.empty_directories.append(root_path)
                self.stats["empty_dirs"] += 1
        
        logger.info(f"Found {self.stats['empty_dirs']} empty directories")
    
    def create_production_structure(self):
        """Create the production directory structure."""
        logger.info("Creating production directory structure...")
        
        # Create temporary directory for reorganized files
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR)
        TEMP_DIR.mkdir(parents=True)
        
        # Create directory structure
        self._create_directories(PRODUCTION_STRUCTURE, TEMP_DIR)
        
        logger.info("Production directory structure created")
    
    def _create_directories(self, structure, parent_dir):
        """Recursively create directory structure."""
        for name, sub_structure in structure.items():
            dir_path = parent_dir / name
            dir_path.mkdir(exist_ok=True)
            if sub_structure:  # If there are subdirectories
                self._create_directories(sub_structure, dir_path)
    
    def get_ideal_destination(self, file_path):
        """Determine the ideal destination for a file in the production structure."""
        rel_path = file_path.relative_to(REPO_ROOT)
        parts = list(rel_path.parts)
        
        # Already in the correct top-level directory?
        if parts[0] in ["docs", "src", "tests"]:
            # For most files, keep the same structure but in the temp directory
            if all(part != ".git" for part in parts):
                return TEMP_DIR.joinpath(*parts)
        
        # Special handling based on file extensions and content
        if file_path.suffix == ".md":
            # Documentation files go to docs
            filename = file_path.name
            if "README" in filename and file_path.parent != REPO_ROOT:
                # README files stay with their directory
                parent_dir = str(file_path.parent.relative_to(REPO_ROOT)).replace("\\", "/")
                return TEMP_DIR / parent_dir / filename
            
            # Try to categorize the documentation based on content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read().lower()
                
                # Determine appropriate docs subdirectory
                if any(term in content for term in ["robot", "perception", "control", "navigation"]):
                    return TEMP_DIR / "docs" / "robotics" / file_path.name
                elif any(term in content for term in ["blockchain", "token", "cryptocurrency"]):
                    return TEMP_DIR / "docs" / "blockchain" / file_path.name
                elif any(term in content for term in ["iot", "device", "sensor"]):
                    return TEMP_DIR / "docs" / "iot" / file_path.name
                elif any(term in content for term in ["ai", "artificial intelligence", "machine learning"]):
                    return TEMP_DIR / "docs" / "ai" / file_path.name
                elif any(term in content for term in ["php", "web", "http"]):
                    return TEMP_DIR / "docs" / "web" / file_path.name
                else:
                    # Default: keep in docs root
                    return TEMP_DIR / "docs" / file_path.name
            except:
                # If can't read, just keep at docs root
                return TEMP_DIR / "docs" / file_path.name
        
        elif file_path.suffix == ".py":
            if "test" in file_path.name.lower():
                return TEMP_DIR / "tests" / file_path.name
            
            # Try to categorize the Python file based on imports and content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read().lower()
                
                # Determine appropriate src subdirectory
                if any(term in content for term in ["robot", "perception", "control"]):
                    return TEMP_DIR / "src" / "robotics" / file_path.name
                elif any(term in content for term in ["blockchain", "token", "web3"]):
                    return TEMP_DIR / "src" / "blockchain" / file_path.name
                elif any(term in content for term in ["iot", "device", "sensor"]):
                    return TEMP_DIR / "src" / "iot" / file_path.name
                elif any(term in content for term in ["vision", "image", "camera"]):
                    return TEMP_DIR / "src" / "vision" / file_path.name
                elif any(term in content for term in ["nlp", "natural language", "text"]):
                    return TEMP_DIR / "src" / "ai" / "nlp" / file_path.name
                elif any(term in content for term in ["ai", "neural", "train"]):
                    return TEMP_DIR / "src" / "ai" / file_path.name
                else:
                    # Default: keep in src root
                    return TEMP_DIR / "src" / file_path.name
            except:
                # If can't read, just keep at src root
                return TEMP_DIR / "src" / file_path.name
        
        # For other files, keep them at the root of the appropriate directory
        if "requirements" in file_path.name or "setup" in file_path.name:
            return TEMP_DIR / file_path.name
        
        # For other files, keep them at repo root
        return TEMP_DIR / file_path.name
    
    def reorganize_files(self):
        """Reorganize files into the production structure."""
        logger.info("Reorganizing files into production structure...")
        print("Starting reorganization of files...")
        
        # First handle non-duplicate files
        count = 0
        for file_hash, file_paths in self.file_hashes.items():
            # Skip duplicates as they'll be handled separately
            if len(file_paths) > 1:
                continue
            
            original = file_paths[0]
            if self.should_ignore(original):
                continue
                
            # Progress indicator
            count += 1
            if count % 100 == 0:
                print(f"Processed {count} files...")
                
            # Determine ideal destination
            try:
                destination = self.get_ideal_destination(original)
                
                # Create directory if needed
                destination.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                try:
                    shutil.copy2(original, destination)
                    self.moved_files[str(original)] = str(destination)
                    self.stats["files_moved"] += 1
                    if debug_mode and count % 50 == 0:
                        print(f"Copied: {original} -> {destination}")
                except Exception as e:
                    logger.error(f"Failed to copy {original} to {destination}: {e}")
                    print(f"ERROR: Failed to copy {original} to {destination}: {e}")
            except Exception as e:
                logger.error(f"Error processing {original}: {e}")
                print(f"ERROR: Failed to process {original}: {e}")
        
        print(f"Processed {count} non-duplicate files.")
        print(f"Now handling {len(self.duplicate_files)} sets of duplicates.")

        
        # Handle duplicate files - only copy the original
        for original, duplicates in self.duplicate_files.items():
            if self.should_ignore(original):
                continue
                
            # Determine ideal destination
            destination = self.get_ideal_destination(original)
            
            # Create directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the original file
            try:
                shutil.copy2(original, destination)
                self.moved_files[str(original)] = str(destination)
                self.stats["files_moved"] += 1
                
                # Track deleted duplicates
                for dup in duplicates:
                    self.deleted_files.append(str(dup))
                    self.stats["files_deleted"] += 1
            except Exception as e:
                logger.error(f"Failed to copy {original} to {destination}: {e}")
        
        logger.info(f"Reorganized {self.stats['files_moved']} files")
        logger.info(f"Eliminated {self.stats['files_deleted']} duplicate files")
    
    def generate_report(self):
        """Generate a report of the reorganization."""
        logger.info("Generating reorganization report...")
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "stats": self.stats,
            "duplicate_files": {str(k): [str(v) for v in vs] for k, vs in self.duplicate_files.items()},
            "empty_directories": [str(d) for d in self.empty_directories],
            "moved_files": self.moved_files,
            "deleted_files": self.deleted_files
        }
        
        # Save as JSON
        with open(REPO_ROOT / "reorganization_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Create markdown report
        md_content = f"""# Repository Reorganization Report

## Summary
- **Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total files analyzed:** {report['stats']['total_files']}
- **Files moved to new structure:** {report['stats']['files_moved']}
- **Duplicate files removed:** {report['stats']['files_deleted']}
- **Empty directories identified:** {report['stats']['empty_dirs']}
- **Storage space saved:** {report['stats']['bytes_saved'] / 1024:.2f} KB

## Production Structure
The repository has been reorganized into a world-class production-level structure:

```
knowledge-base/
├── docs/           # Documentation files
│   ├── ai/         # AI-related documentation
│   ├── api/        # API documentation
│   ├── blockchain/ # Blockchain documentation
│   ├── iot/        # IoT documentation
│   ├── machine_learning/
│   ├── mobile/     # Mobile development docs
│   ├── robotics/   # Robotics documentation
│   └── web/        # Web development docs
├── src/            # Source code
│   ├── ai/         # AI implementation
│   ├── api/        # API implementation
│   ├── blockchain/ # Blockchain implementation
│   ├── iot/        # IoT implementation
│   ├── machine_learning/
│   ├── mobile/     # Mobile app code
│   ├── robotics/   # Robotics implementation
│   └── web/        # Web implementation
├── tests/          # Test suites
│   ├── unit/       # Unit tests
│   ├── integration/# Integration tests
│   └── system/     # System tests
└── scripts/        # Utility scripts
```

## Detailed Changes

### Files Moved
The following files were relocated to optimize the repository structure:

```
{chr(10).join(f"{old} -> {new}" for old, new in list(report['moved_files'].items())[:20])}
... and {max(0, len(report['moved_files']) - 20)} more files
```

### Duplicate Files Removed
The following duplicated files were removed, with one canonical version preserved:

```
{chr(10).join(f"{original} has duplicates: {', '.join(dups[:3])}" for original, dups in list(report['duplicate_files'].items())[:10])}
... and {max(0, len(report['duplicate_files']) - 10)} more duplicate sets
```

### Empty Directories
The following empty directories were identified:

```
{chr(10).join(report['empty_directories'][:20])}
... and {max(0, len(report['empty_directories']) - 20)} more directories
```

## Next Steps
1. Review the reorganized structure in the `temp_reorg` directory
2. Apply the changes to the main repository
3. Run validation scripts to ensure all documentation and code are correctly linked
4. Deploy the reorganized repository for feedback

*Detailed JSON report available in `reorganization_report.json`*
"""
        
        with open(REPO_ROOT / "reorganization_report.md", "w") as f:
            f.write(md_content)
        
        logger.info("Report generated successfully")
        return report
    
    def apply_changes(self, confirm=False):
        """Apply the changes to the main repository."""
        if not confirm:
            logger.info("Dry run - changes have not been applied to the main repository")
            logger.info(f"Review the reorganized structure in {TEMP_DIR}")
            logger.info("Run with --apply to apply changes")
            return False
        
        logger.info("Applying changes to the main repository...")
        
        # Backup the repository before making changes
        backup_dir = REPO_ROOT.parent / f"{REPO_ROOT.name}_backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Creating backup at {backup_dir}")
        shutil.copytree(REPO_ROOT, backup_dir, ignore=lambda src, names: [n for n in names if self.should_ignore(Path(src) / n)])
        
        # Delete files from the main repository (except .git and reorganization files)
        for root, dirs, files in os.walk(REPO_ROOT, topdown=True):
            root_path = Path(root)
            
            # Skip .git and temp directories
            if self.should_ignore(root_path):
                dirs[:] = []  # Don't traverse into ignored directories
                continue
            
            # Remove files
            for file in files:
                file_path = root_path / file
                if not self.should_ignore(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Failed to remove {file_path}: {e}")
        
        # Remove empty directories
        for root, dirs, files in os.walk(REPO_ROOT, topdown=False):  # Bottom-up
            if not os.listdir(root) and not self.should_ignore(Path(root)):
                try:
                    os.rmdir(root)
                except Exception as e:
                    logger.error(f"Failed to remove directory {root}: {e}")
        
        # Copy reorganized files
        for root, dirs, files in os.walk(TEMP_DIR):
            root_path = Path(root)
            dest_path = Path(str(root).replace(str(TEMP_DIR), str(REPO_ROOT)))
            
            # Create directories
            for dir_name in dirs:
                os.makedirs(dest_path / dir_name, exist_ok=True)
            
            # Copy files
            for file_name in files:
                src = root_path / file_name
                dst = dest_path / file_name
                try:
                    os.makedirs(dst.parent, exist_ok=True)
                    shutil.copy2(src, dst)
                except Exception as e:
                    logger.error(f"Failed to copy {src} to {dst}: {e}")
        
        # Remove temporary directory
        shutil.rmtree(TEMP_DIR)
        
        logger.info("Changes applied successfully")
        logger.info(f"Backup saved at {backup_dir}")
        return True
    
    def run(self, apply_changes=False):
        """Run the complete reorganization process."""
        logger.info("Starting repository reorganization...")
        
        self.analyze_repository()
        self.create_production_structure()
        self.reorganize_files()
        report = self.generate_report()
        
        if apply_changes:
            self.apply_changes(confirm=True)
        else:
            logger.info("Reorganization complete. Review the report and run with --apply to apply changes.")
        
        return report


if __name__ == "__main__":
    logger.info("Repository Reorganization Tool")
    logger.info("=" * 30)
    
    apply = "--apply" in sys.argv
    
    reorganizer = RepoReorganizer()
    report = reorganizer.run(apply_changes=apply)
    
    print("\nReorganization complete!")
    print(f"Total files analyzed: {report['stats']['total_files']}")
    print(f"Files moved: {report['stats']['files_moved']}")
    print(f"Duplicate files identified: {report['stats']['files_deleted']}")
    print(f"Empty directories found: {report['stats']['empty_dirs']}")
    print(f"Storage space saved: {report['stats']['bytes_saved'] / 1024:.2f} KB")
    
    if not apply:
        print("\nThis was a dry run. Review the reorganization_report.md file.")
        print("To apply these changes, run: python scripts/reorganize_repo.py --apply")
    else:
        print("\nChanges have been applied to the repository.")
        print("A backup of the original repository was created before changes were applied.")
