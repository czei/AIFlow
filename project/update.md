# Project Update - Update Project and Phase Status

Update current project status, phase progress, and task completion.
This command maintains accurate state across all project files.

Arguments: $ARGUMENTS (optional: specific update type or task)

Usage examples:
- /user:project:update (interactive update of current status)
- /user:project:update task "Database layer implementation" (mark specific task complete)
- /user:project:update phase complete (mark current phase complete)
- /user:project:update progress (update progress percentages)

## Interactive Update Mode (no arguments)
Prompts for current status updates:
1. Review current phase objectives
2. Mark completed tasks with timestamps
3. Add progress notes
4. Update overall phase status
5. Calculate completion percentages
6. Update .project-state.json with latest info

## Specific Task Update
Updates individual objectives in current phase file:
- Marks task as complete with timestamp
- Updates progress counters
- Adds optional completion notes
- Recalculates phase completion percentage

## Phase Completion Update
When phase is finished:
- Marks current phase Status as COMPLETE
- Updates .project-state.json with completion
- Moves phase to completed_phases array
- Sets up transition to next phase
- Archives phase completion summary

## Progress Calculation
Automatically calculates and updates:
- Individual phase completion percentages
- Overall project progress
- Estimated completion time
- Velocity metrics (tasks/day, cycles/phase)

## State Synchronization
Ensures consistency between:
- .project-state.json (master status)
- Individual phase files (detailed progress)
- Git commit history (implementation record)
- Automation workflow state

## Update Output:
```
📊 PROJECT UPDATE

Current State:
  Phase: 03 - Implementation  
  Progress: 62% complete (5 of 8 objectives)
  Status: IN_PROGRESS
  
Recent Updates:
  ✅ Marked "User authentication system" complete
  📝 Added progress note: "Auth middleware optimized"
  📊 Phase 03 progress: 50% → 62%
  
Next Actions:
  🔄 Continue with "Business logic endpoints" 
  ⏳ 3 objectives remaining in current phase
  
State Files Updated:
  ✅ .project-state.json synchronized
  ✅ phases/03-implementation.md updated
  ✅ Progress timestamps recorded
```

## Automation Integration
The update command works with automation:
- Stop hooks can trigger automatic updates
- Progress tracking feeds back to planning
- Completion detection advances phases
- State changes affect automation decisions

## Data Integrity
Validation checks:
- Ensures phase files and state.json stay synchronized
- Prevents invalid status transitions
- Maintains referential integrity between phases
- Validates completion criteria before advancing

This command is essential for maintaining accurate project state throughout the automated development cycle.
