# Project Advance - Force Phase Advancement

Manually advance to the next phase, marking current phase as complete.
Use when current phase is ready but automation hasn't detected completion.

Arguments: $ARGUMENTS (optional: specific phase number to jump to)

Tasks:
1. Validate current phase state and readiness
2. Mark current phase as COMPLETE in phase file
3. Update .project-state.json with next phase
4. Archive current phase progress
5. Display next phase objectives and context
6. Resume automation if it was active
7. Handle phase transition logic

Usage examples:
- /user:project:advance (advance to next sequential phase)
- /user:project:advance 5 (jump to specific phase 5)

Validation checks:
- Verify current phase objectives are reasonably complete
- Check for no critical blockers or incomplete work
- Ensure next phase prerequisites are met
- Confirm no automation conflicts

Output:
```
📈 PHASE ADVANCEMENT

From: Phase 03 - Implementation
To: Phase 04 - Testing & Deployment

Current Phase Completion:
  ✅ Core implementation finished
  ✅ API endpoints functional
  ✅ Database integration complete
  ⚠️  Documentation partially complete
  
Phase 03 Status: MANUALLY_COMPLETED
Reason: Core objectives met, ready for testing phase

Next Phase Preview:
  Phase 04: Testing & Deployment
  Objectives:
    - Comprehensive test suite
    - Performance testing
    - Deployment pipeline
    - Production readiness
    
Automation Status:
  🔄 Resuming automation for Phase 04
  Next Step: Planning testing strategy
```

Safety features:
- Prevents advancing if critical work is incomplete
- Warns about potential issues with early advancement
- Allows rollback if advancement was premature
- Maintains audit trail of manual interventions

Edge cases handled:
- Jumping multiple phases (with validation)
- Advancing when automation is paused
- Handling dependencies between phases
- Managing incomplete objectives

Use when automation gets stuck or when you determine a phase is functionally complete even if all checkboxes aren't marked.
