# Project Setup - Create Worktree and Structure

Create a new git worktree and branch for a phase-driven project.
Assumes you're already in a git repository.

Arguments: $ARGUMENTS (project/branch name)

Tasks:
1. Validate we're in a git repository
2. Create new branch: feature/$ARGUMENTS
3. Create git worktree in ../$ARGUMENTS directory
4. Switch to the new worktree
5. Create phases/ directory with template phase files
6. Create .project-state.json in "setup" mode
7. Create template CLAUDE.md with phase workflow instructions
8. Create initial commit with project structure
9. Reference PHASE_CREATION_INSTRUCTIONS.md for guidance on customizing phase files
10. Set up branch tracking if remote exists

Git operations:
```bash
git worktree add ../$ARGUMENTS -b feature/$ARGUMENTS
cd ../$ARGUMENTS
```

Project structure created in worktree:
```
../$ARGUMENTS/ (git worktree)
├── phases/
│   ├── 01-planning-template.md
│   ├── 02-architecture-template.md  
│   ├── 03-implementation-template.md
│   └── README.md
├── .project-state.json (status: "setup")
├── .claude/
│   └── settings.json (hooks disabled)
├── CLAUDE.md (template)
└── README-PHASES.md
```

Branch: feature/$ARGUMENTS
Worktree: ../$ARGUMENTS

Phase files will include detailed workflow specifications:
- 6-step universal workflow: plan → implement → validate → review → refine → integrate
- Phase-specific workflow variations
- Quality gates and success criteria  
- Automation instructions for Claude Code
- Comprehensive validation requirements

Next steps:
1. Customize phase files with your project-specific objectives using PHASE_CREATION_INSTRUCTIONS.md
2. Review workflow specifications in generated WORKFLOW_SPECIFICATIONS.md
3. Edit CLAUDE.md with project context and specific requirements
4. Run /user:project:doctor to validate setup
5. Run /user:project:start to begin automated development

Generated files include detailed workflow guidance:
- Each phase file contains complete workflow steps
- WORKFLOW_SPECIFICATIONS.md provides comprehensive methodology
- Quality gates ensure consistent development standards
- Automation instructions guide Claude Code behavior

Safety note: This workflow is designed for use with --dangerously-skip-permissions
Ensure you're in a git repository and understand the risks.
