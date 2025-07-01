> **Main Files Policy:** This file is one of the main, critical files for the knowledge base. Any change to this file must be reflected in all other main files, both before and after any process. All main files are cross-linked and referenced. See [README.md](README.md#main-files-policy-critical-requirement) for details.

> **Traceability:** All data inputs and amendments are timestamped for traceability and rollback. See also [memories.md](memories.md), [changelog.md](changelog.md), and [rollback.md](rollback.md).

**Main Files:**
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
- [notes.md](notes.md)
- [current_goal.md](current_goal.md)
- [task_list.md](task_list.md)
- [inherit.md](inherit.md)

# TODO List

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

This file tracks all next actions and outstanding tasks for the knowledge base. For full context, see also: [checklist.md](checklist.md), [plan.md](plan.md), [changelog.md](changelog.md).

## Immediate Next Actions
- [ ] Run a deep analysis scan for undocumented data/components (see plan.md)
- [ ] Add documentation/code for any uncovered data, ensuring cross-links and references
- [ ] Verify there are no empty directories, duplicate files, or folders
- [ ] Merge/clean data as needed, fix all errors
- [ ] Run repo-wide verification for gaps, broken links, or orphaned files (see scripts/verify_docs.py)
- [ ] Update all main files ([README.md](README.md), [architecture.md](architecture.md), [changelog.md](changelog.md), [memories.md](memories.md), [method.md](method.md), [plan.md](plan.md), [rollback.md](rollback.md), [system_design.md](system_design.md), [FIXME.md](FIXME.md), [checklist.md](checklist.md)) after each process

## Ongoing
- [ ] Keep all documentation and code in sync with plan.md and changelog.md
- [ ] Ensure every process/feature is reflected in all main files
- [ ] Maintain and update cross-references between all main and sub-files

---
*Last updated: 2025-07-01*