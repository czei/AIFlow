# Project Status - Display Current Progress

Display comprehensive status of the current phase-driven project.

Tasks:
1. Read .project-state.json for current phase and automation status
2. Read .workflow-state.json for current workflow step (1-6)
3. Display completed phases and quality gate passage
4. Show current phase objectives and workflow step progress
5. Display current objective's quality gate status
6. Show automation status (active/paused/stopped)
7. Display recent activity and workflow step completions
8. Show git worktree and branch information
9. Calculate quality metrics and workflow efficiency statistics

Status dashboard format:
```
=== PROJECT STATUS ===

Git Context:
  Worktree: ../my-awesome-app
  Branch: feature/my-awesome-app
  Last Commit: 2 hours ago
  
Project Progress:
  Current Phase: 03 - Implementation
  Automation: ACTIVE
  Workflow Step: 4 (Review) - Business logic API endpoints
  
Phase Status:
  ✅ Phase 01: Planning (completed 2 days ago) - All quality gates passed
  ✅ Phase 02: Architecture (completed 1 day ago) - All quality gates passed
  🔄 Phase 03: Implementation (in progress)
      ✅ Database layer complete (6-step workflow: ALL PASSED)
      ✅ Authentication module complete (6-step workflow: ALL PASSED)
      🔄 API endpoints (3 of 8 complete)
          Current: Business logic endpoints
          Workflow: Step 4 (Review) - Zen code review in progress
          Quality Gates: ✅ Compile ✅ Test ✅ Integration ⏳ Review ⏳ Documentation ⏳ Performance
      ⏳ Testing suite (pending)
  ⏳ Phase 04: Deployment (pending)
  
Recent Activity:
  - 15:45: Step 4 (Review) - Zen code review initiated for business logic endpoints
  - 15:30: Step 3 (Validation) - All tests passing, performance benchmarks met
  - 15:15: Step 2 (Implementation) - Business logic endpoints coded
  - 15:00: Step 1 (Planning) - Planned business logic endpoint implementation
  - 14:45: Step 6 (Integration) - Auth module completed, all quality gates passed

Next Actions:
  - Complete Step 4 (Review) for current objective
  - Execute Step 5 (Refinement) based on review feedback
  - Step 6 (Integration) when all quality gates pass
  - Begin next objective: Error handling and validation
  
Quality Statistics:
  - Project started: 3 days ago
  - Objectives completed: 3 of 8 (37.5%)
  - Quality gates passed: 18 of 18 (100%)
  - Code review issues resolved: 12
  - Test coverage: 94% (target: >90%)
  - Performance benchmarks met: 3 of 3
  - Automation workflow cycles: 23
```

Human intervention flags:
- Shows if manual attention is needed
- Displays any error conditions
- Indicates when to pause/resume automation

Use this command anytime to check project health and progress.
