# Project Doctor - Validate Project Setup

Validate project setup including git worktree configuration and phase customization.

Tasks:
1. Verify we're in a git worktree (not main repository)
2. Check current branch matches feature/* pattern
3. Confirm worktree is clean
4. Validate initial setup commit exists
5. Check .project-state.json exists and is valid JSON
6. Validate phases/ directory structure
7. Verify phase files are customized with detailed 6-step workflows
8. Check CLAUDE.md has project-specific content
9. Validate phase dependencies and numbering
10. Ensure automation hooks are properly configured
11. Verify WORKFLOW_SPECIFICATIONS.md exists and is complete
12. Validate quality gate definitions in phase files
13. Check that all phase files include automation instructions

Validation checks:
- No "TEMPLATE" or "CUSTOMIZE" text in phase files
- All Status fields are not "TEMPLATE_NOT_READY"
- Phase numbering is sequential with no gaps
- All phases have required sections:
  - Status with completion tracking
  - Prerequisites with verification criteria
  - Objectives with detailed 6-step workflow specifications
  - Quality gates with specific pass/fail criteria
  - Success criteria with measurable validation
  - Automation instructions for Claude Code behavior
  - Next Phase Trigger with advancement logic
- CLAUDE.md contains actual project context and standards
- WORKFLOW_SPECIFICATIONS.md is complete and accessible
- Git worktree is properly configured
- Quality gate thresholds are defined (test coverage, performance, etc.)

Output format:
```
Git Status:
✅ In git worktree: ../my-project
✅ Branch: feature/my-project  
✅ Worktree clean
✅ Setup commit present

Project Status:
✅ 4 phase files validated with 6-step workflows
✅ All phases customized (no templates)
✅ Quality gates defined with specific criteria
✅ CLAUDE.md updated with project context and standards
✅ WORKFLOW_SPECIFICATIONS.md complete
  ✅ Phase dependencies valid
  ✅ Automation instructions included in all phases
  ✅ Hooks configured for 6-step workflow

Status: Ready! All workflow specifications validated.
Run /user:project:start to begin automated 6-step development cycle.
```

If issues found, provides specific guidance on what to fix before starting automation.

Safety validation when using --dangerously-skip-permissions:
- Verify we're in correct project directory
- Check that automation boundaries are properly set
- Ensure no dangerous command patterns in hook configurations
