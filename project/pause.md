# Project Pause - Temporarily Stop Automation

Pause the automated phase workflow to allow manual intervention.
Preserves all project state for later resumption.

Tasks:
1. Update .project-state.json to set automation_active: false
2. Update .workflow-state.json to set automation_active: false
3. Disable automation hooks temporarily
4. Create pause timestamp and reason
5. Display current state and context
6. Show how to resume automation

Pause behavior:
- Stops the automated 6-step workflow cycle at current step
- Preserves exact workflow position (1-6) and quality gate status
- Allows manual work without automation interference
- Maintains all project state, progress, and quality metrics
- Can be resumed at exact workflow step where paused

Output:
```
🚫 AUTOMATION PAUSED

Current Context:
  Phase: 03 - Implementation  
  Objective: Business logic API endpoints
  Workflow Step: 4 (Review) - Zen code review in progress
  Quality Gates: ✅ Compile ✅ Test ✅ Integration ⏳ Review ⏳ Documentation ⏳ Performance
  Last Activity: Code review initiated
  
State Preserved:
  ✅ Project state saved
  ✅ Workflow position saved
  ✅ Automation hooks disabled
  ✅ Git state clean
  
Manual Control:
  You can now work manually in this project.
  Claude Code will not automatically continue.
  
To Resume:
  Run /user:project:resume when ready to continue automation
  Or run /user:project:stop to end the project
```

Use cases for pausing:
- Need to investigate an unexpected issue
- Want to manually implement a complex feature
- External dependencies or blockers
- Review automation decisions before continuing
- Temporary shift to different priorities

The project remains in a clean, resumable state during the pause.
