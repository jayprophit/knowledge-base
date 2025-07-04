# GitHub Actions Documentation

## Overview
This document outlines the GitHub Actions workflows used to automate processes within the knowledge base repository. These workflows help maintain quality, consistency, and up-to-date content.

## Current Workflows

### 1. Link Validation Workflow

**Purpose**: Automatically check for broken internal and external links.

**Trigger**: 
- Runs on push to main branch
- Runs on schedule (weekly)
- Can be run manually

**Configuration**:
```yaml
name: Validate Links

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Run weekly at midnight on Sunday
  workflow_dispatch:  # Allow manual trigger

jobs:
  validate-links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install markdown-link-check
          
      - name: Check internal links
        run: |
          python scripts/validate_internal_links.py
          
      - name: Check external links
        run: |
          find . -name "*.md" -type f -print0 | xargs -0 markdown-link-check
          
      - name: Report issues
        if: failure()
        run: |
          echo "::warning::Broken links detected. See detailed output above."
```

### 2. Changelog Update Workflow

**Purpose**: Automatically update the changelog when new content is added or modified.

**Trigger**: 
- Runs on pull request to main branch
- Can be run manually

**Configuration**:
```yaml
name: Update Changelog

on:
  pull_request:
    branches: [ main ]
    types: [opened, synchronize]
  workflow_dispatch:

jobs:
  update-changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install gitpython pyyaml
          
      - name: Update changelog
        run: |
          python scripts/update_changelog.py
          
      - name: Commit changes
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "Update changelog [skip ci]"
          file_pattern: "changelog.md"
```

### 3. README Update Workflow

**Purpose**: Keep the README.md updated with the latest content structure.

**Trigger**: 
- Runs on push to main branch
- Runs on schedule (daily)
- Can be run manually

**Configuration**:
```yaml
name: Update README

on:
  push:
    branches: [ main ]
    paths-ignore:
      - 'README.md'
  schedule:
    - cron: '0 0 * * *'  # Run daily at midnight
  workflow_dispatch:

jobs:
  update-readme:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml
          
      - name: Update README
        run: |
          python scripts/update_readme.py
          
      - name: Commit changes
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "Update README [skip ci]"
          file_pattern: "README.md"
```

## Implementing New Workflows

### Prerequisites
- GitHub repository must have Actions enabled
- Required secrets (if any) must be configured in repository settings
- Scripts referenced in workflows must exist in the repository

### Creating a New Workflow
1. Create a new YAML file in the `.github/workflows` directory
2. Define the workflow name, triggers, and jobs
3. Test the workflow by manually triggering it
4. Document the workflow in this file

### Workflow Best Practices
- Include appropriate triggers (push, pull request, schedule, manual)
- Add concise comments to explain complex steps
- Use appropriate timeouts to prevent hung workflows
- Implement proper error handling and reporting
- Configure notifications for workflow failures

## Script Dependencies
Scripts used by these workflows are located in the `/scripts` directory:
- `validate_internal_links.py` - Checks internal markdown links
- `update_changelog.py` - Updates changelog based on commits
- `update_readme.py` - Updates README with latest structure

## Future Workflow Ideas
- Content quality checks (spelling, grammar)
- Automated content formatting
- Generation of content statistics and reports
- Scheduled reviews for outdated content
- Integration with external knowledge systems

## References
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Update Scripts Documentation](update_scripts.md)
- [Contribution Guide](../process/contribution_guide.md)
- [Changelog Standards](../meta/changelog_standards.md)
