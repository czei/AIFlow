# Project Resume - Restart Automation

Resume the automated phase workflow from current state after a pause.

Prerequisites:
- Project must be in "paused" state
- Working directory must be clean
- No conflicting manual changes that break automation assumptions

Tasks:
1. Validate project is in pausable/resumable state
2. Update .project-state.json to set automation_active: true
3. Update .workflow-state.json to set automation_active: true
4. Re-enable automation hooks
5. Display current context and next planned action
6. Resume automated workflow from current step

Resume behavior:
- Continues from exact workflow step (1-6) where automation was paused
- Resumes the 6-step workflow cycle with quality gate validation
- Accounts for any manual work done during pause period
- Validates current state and quality gates before proceeding
- Re-establishes automation context and workflow position
- Provides smooth transition back to structured automation

Output:
```
🔄 AUTOMATION RESUMED

Resuming From:
  Phase: 03 - Implementation
  Objective: Business logic API endpoints
  Workflow Step: 4 (Review) - Zen code review
  Quality Gates: ✅ Compile ✅ Test ✅ Integration ⏳ Review ⏳ Documentation ⏳ Performance
  
State Validation:
  ✅ Project state consistent
  ✅ No conflicting manual changes
  ✅ Automation hooks re-enabled
  ✅ Ready to continue
  
Next Action:
  Continue Step 4 (Review) - Complete zen code review for business logic endpoints
  Will continue with: Review → Refine → Integrate → next objective's 6-step cycle
  
Manual changes detected during pause:
  - Updated API documentation
  - Fixed minor formatting issues
  These changes have been integrated into automation context.
```

Smart resume features:
- Analyzes what changed during pause
- Integrates manual work into automation flow
- Adjusts planning based on current state
- Maintains phase objectives and progress tracking

If conflicts detected:
- Shows specific issues that need resolution
- Suggests fixes before automation can resume
- Protects against automation working on inconsistent state

The automation seamlessly picks up where it left off.
