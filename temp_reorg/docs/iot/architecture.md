# Knowledge Base Architecture

## Critical Main Files

> **IMPORTANT:** The following main files are critical and must be kept in sync. Any change to one must be reflected in all others, both before and after any process. All must be cross-linked and referenced:
> - [README.md](README.md)
> - [architecture.md](architecture.md)
> - [changelog.md](changelog.md)
> - [memories.md](memories.md)
> - [method.md](method.md)
> - [plan.md](plan.md)
> - [rollback.md](rollback.md)
> - [system_design.md](system_design.md)
> - [FIXME.md](FIXME.md)
> - [TODO.md](TODO.md)
> - [checklist.md](checklist.md)
>
> **Validation:** All data and code must be validated for correct formatting and correctness at every step.

## Unified AI Assistant: Production Architecture

## System Overview

The Unified AI Assistant is a world-class, production-ready cross-platform system integrating advanced AI capabilities, knowledge retrieval, multimodal interaction, and secure networking. The system operates across web, mobile, desktop, and IoT devices with a unified codebase and synchronized user experience.

## Directory Structure

```
/knowledge-base/
  /docs/              # Core documentation files
    /workflow/        # ML workflow step documentation
    /models/          # Model-specific documentation
    /concepts/        # Concept explanations and theory
  /templates/         # Document templates
  /process/           # Process guides and workflows
  /automation/        # Automation documentation
  /meta/              # Meta documentation
  /maintenance/       # Maintenance guides
  /assets/            # Images, diagrams, and other assets
  /scripts/           # Automation scripts
  /anthropic/         # Anthropic-style data processing
    /templates/       # Anthropic-optimized templates
    /principles/      # Constitutional principles documentation
    /pipeline/        # Processing pipeline documentation
  /mcp/               # MCP and AI system integration
    /docs/            # MCP-optimized documents
    /schemas/         # JSON schemas for knowledge structures
    /api/             # API documentation and examples
    /vectorization/   # Vectorization protocols and embeddings
    /config/          # MCP server configuration for cross-platform setup
  /backups/           # Backup storage for files
  /logs/              # Log files from automated processes
  README.md           # Repository overview
  method.md           # Development methodology and approach
  plan.md             # Knowledge base plan
  changelog.md        # Record of changes
  system_design.md    # System design documentation
  architecture.md     # This file
  rollback.md         # Rollback procedures
```

## File Relationships

#### Documentation Relationships
- **ML Workflow Steps**: Each workflow step document relates to previous and next steps
  - Example: `preprocessing.md` → `data_splitting.md` → `model_building.md`
- **Models to Concepts**: Model documentation references relevant theoretical concepts
  - Example: `transformers.md` references `attention_mechanism.md`
- **Templates to Documents**: All documents follow standardized templates
  - Example: `document_template.md` → `preprocessing.md`

#### Meta-Documentation Relationships
- **System Design to Architecture**: Conceptual design guides physical organization
  - `system_design.md` → `architecture.md`
- **Plan to Documents**: Plan outlines tasks for document creation and maintenance
  - `plan.md` → Various documentation files
- **Changelog to All Files**: Changelog tracks changes across all files
  - `changelog.md` ↔ All updated files
- **Brain Plan to Knowledge Base Plan**: External brain plan syncs with knowledge base plan
  - `brain/plan.md` → `sync_brain_plan.py` → `plan.md`

#### Anthropic and MCP Integration
- **Anthropic Templates to MCP Docs**: Anthropic templates are used to create MCP-compatible documents
  - Example: `anthropic/templates/anthropic_document_template.md` → `mcp/docs/sample_neural_network.md`
- **Constitutional Principles to Documents**: All content follows constitutional principles
  - `anthropic/constitutional_principles.md` → All content files
- **MCP Integration to API**: MCP integration guides API implementation
  - `mcp/integration_guide.md` → `mcp/api/*`
- **MCP Config to Deployments**: MCP configuration for different platforms
  - `mcp/config/mcp_config.json` → Cross-platform deployments

## File Types and Conventions

### Documentation Files
- **Format**: Markdown (.md)
- **Naming**: snake_case.md
- **Structure**: 
  - Title (H1)
  - Overview (H2)
  - Main content sections (H2, H3)
  - References (H2)
  - Metadata (H2)

### Anthropic-Style Documentation Files
- **Format**: Markdown (.md) with machine-readable enhancements
- **Naming**: snake_case.md
- **Structure**:
  - Title with document ID (H1)
  - Section IDs for all headings
  - Knowledge units with explicit IDs
  - Constitutional metadata section
  - Machine-readable JSON metadata

### Template Files
- **Format**: Markdown (.md)
- **Naming**: template_name_template.md
- **Purpose**: Provide standardized structure for documentation

### Process Files
- **Format**: Markdown (.md)
- **Naming**: process_name.md
- **Purpose**: Define workflows and procedures

### Configuration Files
- **Format**: YAML (.yml) or JSON (.json)
- **Naming**: config_name.yml/json
- **Purpose**: Store configuration settings
- **MCP Config**: `mcp_config.json` contains server configuration for cross-platform setup

### Script Files
- **Format**: Python (.py)
- **Naming**: script_name.py
- **Purpose**: Automation and utilities
- **Requirements**: Listed in scripts/requirements.txt

## Creating New Files

When adding new files to the knowledge base, follow these location guidelines:

1. **Core knowledge content** → Place in appropriate `/docs` subdirectory
2. **New ML workflow step** → Add to `/docs/workflow/`
3. **New ML model documentation** → Add to `/docs/models/`
4. **System architecture content** → Add to `/docs/systems/`
5. **Process documentation** → Place in `/process/` directory
6. **Templates** → Place in `/templates/` directory

## Information Flow

### Documentation Development Flow
1. **Planning**: New documentation needs identified in `plan.md`
2. **Creation**: Document drafted using appropriate template from `/templates/`
3. **Constitutional Review**: Document checked against Anthropic constitutional principles
4. **Review**: Document reviewed according to process in `/process/review_process.md`
5. **MCP Optimization**: Document formatted for machine consumption if needed
6. **Publication**: Document finalized and added to appropriate directory
7. **Maintenance**: Regular updates according to maintenance schedule

### Update Flow
1. **Change Identification**: Need for update identified
2. **Documentation**: Change documented in `changelog.md`
3. **Implementation**: Changes made to affected files
4. **Cross-Reference**: Related documents updated if necessary
5. **Brain Plan Synchronization**: If plan changes, sync with brain plan using `sync_brain_plan.py`
6. **Review**: Changes validated according to review process

### Brain Plan Synchronization Flow
1. **Brain Plan Update**: Changes made to the brain plan
2. **Synchronization**: `sync_brain_plan.py` script run to update knowledge base plan
3. **Backup**: Previous version of plan backed up to `/backups/` directory
4. **Validation**: Plan consistency checked and verified
5. **Implementation**: Tasks from updated plan implemented

## Key Scripts

### sync_brain_plan.py
- **Purpose**: Synchronizes the external brain plan with the knowledge base plan
- **Location**: `/scripts/sync_brain_plan.py`
- **Usage**: `python scripts/sync_brain_plan.py`
- **Configuration**: Configurable via command line arguments or environment variables
- **Output**: Updated plan.md file with backup of previous version

### update_changelog.py
- **Purpose**: Updates changelog based on repository changes
- **Location**: `/scripts/update_changelog.py`
- **Usage**: `python scripts/update_changelog.py`

### update_readme.py
- **Purpose**: Updates README.md with current repository structure
- **Location**: `/scripts/update_readme.py`
- **Usage**: `python scripts/update_readme.py`

### auto_update_docs.py
- **Purpose**: Combined script to update both README.md and changelog.md
- **Location**: `/scripts/auto_update_docs.py`
- **Usage**: `python scripts/auto_update_docs.py [--commit] [--push]`

## Main Directory Update Points

After every process or major update, the following files must be reviewed and updated to maintain architectural integrity:
- [README.md](README.md)
- [architecture.md](architecture.md)
- [changelog.md](changelog.md)
- [memories.md](memories.md)
- [method.md](method.md)
- [plan.md](plan.md)
- [rollback.md](rollback.md)
- [system_design.md](system_design.md)
- [FIXME.md](FIXME.md)
- [TODO.md](TODO.md)
- [checklist.md](checklist.md)

See [plan.md](plan.md) and [checklist.md](checklist.md) for the update workflow and status tracking.

## References
- [System Design](system_design.md) - Conceptual system design
- [Plan](plan.md) - Current knowledge base plan
- [Changelog](changelog.md) - Record of changes to knowledge base
- [MCP Integration Guide](mcp/integration_guide.md) - MCP compatibility guidelines
- [MCP Configuration](mcp/config/README.md) - MCP server configuration guide
- [Anthropic Processing Pipeline](anthropic/processing_pipeline.md) - Anthropic data processing methodology
- [Automation Guide](automation/step_by_step_guide.md) - Step-by-step automation procedures
- [Rollback Procedures](rollback.md) - Recovery and rollback process
