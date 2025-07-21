# Project Phase Management

Create, edit, list, or manage project phases dynamically.

Arguments: $ARGUMENTS (action: create, edit, list, or phase number)

Usage examples:
- /user:project:phase list (show all phases and status)
- /user:project:phase create (create new phase interactively)
- /user:project:phase edit 3 (edit phase 3)
- /user:project:phase 4 (jump to and display phase 4)

## List Action
Shows comprehensive phase overview:
```
📋 PROJECT PHASES

Phase Overview:
  ✅ 01: Planning (COMPLETE - 2 days ago)
  ✅ 02: Architecture (COMPLETE - 1 day ago)  
  🔄 03: Implementation (IN_PROGRESS - current)
      Progress: 7 of 10 objectives complete
  ⏳ 04: Testing (PENDING)
  ⏳ 05: Deployment (PENDING)
  
Current Focus: Phase 03 - API development
Next Milestone: Complete authentication system
Estimated Completion: 1.5 days remaining
```

## Create Action
Interactive phase creation:
1. Prompts for phase number and title
2. Generates template with standard sections
3. Opens for immediate editing
4. Updates project dependencies
5. Integrates with current automation

## Edit Action
Opens specified phase file for modification:
- Updates phase objectives
- Modifies success criteria
- Adjusts prerequisites
- Changes status if needed

## Jump Action (number only)
Displays detailed information about specific phase:
```
📋 PHASE 03: IMPLEMENTATION

Status: IN_PROGRESS (started 18 hours ago)
Prerequisites: ✅ Phase 02 (Architecture) complete

Objectives:
  ✅ Database layer implementation
  ✅ User authentication system
  ✅ Core API endpoints (users, auth)
  🔄 Business logic API endpoints (3 of 6 complete)
  ⏳ Error handling and validation
  ⏳ API documentation
  ⏳ Integration tests

Success Criteria:
  - All API endpoints functional and tested
  - Comprehensive error handling
  - API documentation complete
  - Integration with frontend possible

Next Phase Trigger:
  - All objectives marked complete
  - Integration tests passing
  - Code review completed

Recent Activity:
  - Payment endpoint implementation (2 hours ago)
  - Authentication middleware review (4 hours ago)
  - Database optimization (6 hours ago)
```

Dynamic phase management:
- Supports adding phases mid-project
- Handles phase reordering
- Manages dependencies automatically
- Integrates with automation system

Safety features:
- Validates phase dependencies before changes
- Prevents deletion of phases with completed work
- Maintains phase history and audit trail
- Warns about automation impacts
