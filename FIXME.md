# FIXME Checklist

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

> **Validation:** All data and code must be validated for correct formatting and correctness at every step.

This file tracks folders and files that need to be fixed, categorized by urgency. Items are addressed either immediately or scheduled for later, according to their importance.

## Urgent (fix straight away)
- [ ] Broken core system files
- [ ] Critical robotics/AI module errors
- [ ] Major documentation gaps in new modules
- [ ] [Multisensory Robotics Documentation](docs/robotics/advanced_system/multisensory_robotics.md) — use as reference for advanced robotics fixes

## Intermediate (mostly fixed, can finish later)
- [ ] Incomplete cross-links in robotics/AI docs
- [ ] Minor code/documentation errors in new fields of education modules
- [ ] Orphaned files (see scripts/verify_docs.py output)

## Less Urgent (can defer)
- [ ] Refactoring for code style consistency
- [ ] Additional examples for user guides
- [ ] Expanding advanced movement/interaction examples

---
**Reference:** See [Multisensory Robotics Documentation](docs/robotics/advanced_system/multisensory_robotics.md) and [multisensory_robotics.py](src/robotics/advanced_system/multisensory_robotics.py) for implementation and documentation standards for advanced robotics fixes.

