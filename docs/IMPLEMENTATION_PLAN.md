# Implementation Plan: Build Missing Automated Sprint-Driven Development System

## OVERVIEW

Build the complete automated sprint-driven development system described in docs/PROJECT_DOCUMENTATION.md, bridging the gap between documentation and reality. This system will provide Claude Code hooks, project state management, and automated workflow execution.

## CRITICAL ARCHITECTURE UPDATE

Recent analysis revealed the current implementation fundamentally misunderstood Claude Code's architecture. The solution requires a three-layer approach:

1. **Commands**: Simple markdown triggers (10-20 lines) with YAML frontmatter
2. **Hooks**: Python scripts that enforce workflows and manage state
3. **StateManager**: Already built in Sprint 1, provides persistence

## ARCHITECTURE FOUNDATION

```
Current State:               Target State:
- Test framework only        - Full automation system
- 300+ line command files    - 20-line command triggers
- No hook usage              - Hooks enforce workflows
- Manual instructions        - Automated enforcement
- No state management        - StateManager integration
```

## PHASE 1: STATE MANAGEMENT CORE ✅ COMPLETED

### 1.1 Project State Schema Design
- Create comprehensive .project-state.json schema
- Fields: current_sprint, workflow_step, current_user story, automation_active, quality_gates, progress_tracking, timestamps, git_info
- Define state transitions between sprints and workflow steps
- Add validation rules and error handling specifications

### 1.2 StateManager Class Implementation
- Create src/state_manager.py with core operations:
  - create(): Initialize new project state
  - read(): Load and validate existing state
  - update(): Atomic state updates with validation
  - validate(): Schema and business rule validation
  - transition_sprint(): Controlled sprint transitions
- Add comprehensive error handling and logging integration
- Include atomic file operations for reliability

### 1.3 State Integration
- Update scripts/logged_secure_shell.py to use StateManager
- Create state utilities for common operations
- Add state backup and recovery mechanisms
- Integrate with existing logging architecture

**Success Criteria:** StateManager can create, read, update project state reliably. All existing code using state references works with real implementation.

## PHASE 2: COMMAND IMPLEMENTATION (REVISED)

### 2.1 Command Architecture Redesign
**Problem**: Current commands are 300+ line instruction manuals
**Solution**: Rewrite as simple 10-20 line markdown triggers

### 2.2 Command File Structure
Each command must have:
- YAML frontmatter with `allowed-tools` declaration
- Direct shell execution with `!` prefix
- Minimal logic (complex logic moves to hooks)

Example structure:
```markdown
---
allowed-tools: Bash(echo:*), Bash(jq:*), Bash(python3:*)
description: Start project automation
---

Start automated development for this project.

!`[ -f ".project-state.json" ] || { echo "❌ No project found"; exit 1; }`
!`python3 -c "from state_manager import StateManager; StateManager('.').update({'status': 'active', 'automation_active': True})"`

Automation activated. I'll now follow the story lifecycle.
```

### 2.3 Commands to Rewrite

**setup.md** (20 lines max)
- Signal to create project structure
- Let hooks handle complex logic

**start.md** (15 lines max)
- Update state to active
- Enable automation flag

**status.md** (20 lines max)
- Display current state
- Show workflow position

**pause.md** (15 lines max)
- Set paused state
- Disable automation

**resume.md** (15 lines max)
- Restore active state
- Re-enable automation

**stop.md** (15 lines max)
- Finalize project
- Generate summary

### 2.4 Supporting Python Modules
- Keep src/git_operations.py for hook usage
- Keep src/project_builder.py for hook usage
- Commands just trigger, hooks do the work

**Success Criteria:** All /user:project:* commands work manually. Projects can be created, managed, and monitored without automation.

## PHASE 3: HOOK INTEGRATION (CRITICAL PATH)

### 3.1 Hook Architecture
**Key Insight**: Hooks are where the complex logic lives, not commands

Available hooks:
- **PreToolUse**: Block/allow tools based on workflow state
- **PostToolUse**: Update state after tool execution
- **UserPromptSubmit**: Intercept user commands
- **Stop**: Advance workflow steps automatically

### 3.2 Hook Configuration
Create `.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": {
      "command": "python3 /path/to/hooks/pre_tool_use.py",
      "timeout": 5000
    },
    "PostToolUse": {
      "command": "python3 /path/to/hooks/post_tool_use.py"
    },
    "Stop": {
      "command": "python3 /path/to/hooks/stop.py"
    }
  }
}
```

### 3.3 Hook Implementations

**PreToolUse Hook (src/hooks/pre_tool_use.py)**
```python
#!/usr/bin/env python3
import json
import sys
from state_manager import StateManager

def main():
    event = json.loads(sys.stdin.read())
    state = StateManager(event['cwd']).read()
    
    # Workflow enforcement
    if state['workflow_step'] == 'planning':
        if event['tool'] in ['Write', 'Edit']:
            print(json.dumps({
                "allow": False,
                "message": "🚫 Planning sprint: Complete analysis first"
            }))
            return
    
    print(json.dumps({"allow": True}))
```

**PostToolUse Hook (src/hooks/post_tool_use.py)**
- Track acceptance criteria completion
- Update files modified list
- Record test results

**Stop Hook (src/hooks/stop.py)**
- Check if current step complete
- Advance to next workflow step
- Reset acceptance criteria for new step

### 3.4 Workflow State Machine
Implement in hooks, not separate engine:
1. **Planning**: Research only, no coding
2. **Implementation**: Allow code writing
3. **Validation**: Require tests before proceeding
4. **Review**: Trigger code review
5. **Refinement**: Address review feedback
6. **Integration**: Final checks and commit

**Success Criteria:** Claude Code follows story lifecycle automatically. Quality gates prevent progression without validation. Automation can be paused/resumed reliably.

## EXAMPLE WORKFLOW: "Fix Product Build" Sprint

Let's trace through a complete workflow to show how commands and hooks interact:

### Initial State
```json
{
  "project_name": "e-commerce-platform",
  "current_sprint": "03-fix-build",
  "status": "active",
  "automation_active": true,
  "workflow_step": "planning",
  "current_user story": "Fix product build compilation errors"
}
```

### Workflow Execution

**1. Planning Stage**
- User: "Fix the product build errors"
- PreToolUse: Allows Read, Grep; blocks Write, Edit
- Claude: Analyzes build logs, identifies root cause
- Stop Hook: Detects planning complete → advances to "implementation"

**2. Implementation Stage**
- PreToolUse: Now allows Write, Edit
- Claude: Fixes src/products/builder.py, config.yaml
- PostToolUse: Tracks modified files
- Stop Hook: Files modified → advances to "validation"

**3. Validation Stage**
- Claude: Runs build, tests
- PostToolUse: Marks "compilation", "existing_tests" gates
- PreToolUse: Blocks commit until new tests written
- Stop Hook: All tests pass → advances to "review"

**4. Review Stage**
- Claude: Uses zen code review
- PostToolUse: Marks "review" gate, captures findings
- Stop Hook: Review complete → advances to "refinement"

**5. Refinement Stage**
- Claude: Addresses review feedback
- PostToolUse: Tracks refinements
- Stop Hook: Issues resolved → advances to "integration"

**6. Integration Stage**
- Claude: Updates docs, final tests, commits
- PostToolUse: Marks final gates
- Stop Hook: Objective complete → resets to "planning" for next task

### Key Insights
- Commands are simple triggers
- Hooks enforce the entire workflow
- State drives all behavior
- Automatic progression through stages
- Quality gates enforced at each step

## PHASE 4: TESTING & VALIDATION

### 4.1 Unit Testing
- Test StateManager with comprehensive edge cases
- Test command implementations in isolation  
- Test git operations with various scenarios
- Mock hook API for automation engine testing

### 4.2 Integration Testing
- Add project management tests to existing 4-layer framework
- Test complete workflow from setup to completion
- Validate state persistence across operations
- Test error recovery and rollback scenarios

### 4.3 System Testing
- Create test projects with real Claude Code integration
- Validate automation in controlled environment
- Test hook behavior with various tool usage patterns
- Performance testing with complex projects

### 4.4 Safety Validation
- Test git worktree isolation effectiveness
- Validate --dangerously-skip-permissions safety measures
- Test rollback and recovery procedures
- Validate state corruption recovery

**Success Criteria:** Complete system tested and validated. All edge cases handled. Performance acceptable. Safety measures effective.

## PHASE 4: DOCUMENTATION & POLISH 🔄 IN PROGRESS

### 4.1 Documentation Alignment ✅ PARTIALLY COMPLETE
- ✅ Reorganized documentation (reduced from 27 to 15 active files)
- ✅ Created MANUAL_TESTING_GUIDE.md with comprehensive instructions
- ✅ Created TESTING_SCENARIOS_GUIDE.md for test procedures
- ✅ Consolidated Phase 3 achievements into PHASE_3_TESTING_FINAL_REPORT.md
- ✅ Enhanced POC_SETUP_GUIDE.md with complete setup instructions
- [ ] Update docs/PROJECT_DOCUMENTATION.md to reflect actual implementation
- [ ] Create comprehensive user guide for workflow system
- [ ] Add architecture diagrams and workflow visualizations

### 4.2 User Experience Polish
- [ ] Improve command output and progress indicators
- [ ] Add helpful error messages and recovery suggestions
- [ ] Create setup validation and diagnostic tools
- [ ] Add configuration options for different project types

### 4.3 Performance & Optimization
- [ ] Establish performance benchmarks
- [ ] Optimize hook execution time
- [ ] Add caching for common operations
- [ ] Create performance monitoring tools

**Success Criteria:** System is production-ready, well-documented, and provides excellent user experience. Documentation is clear, comprehensive, and maintainable.

## PHASE 5: ADVANCED FEATURES (FUTURE)

### 5.1 Multi-Repository Support
- Support for managing multiple projects simultaneously
- Cross-project dependency management
- Unified dashboard for all projects

### 5.2 Custom Workflows
- User-defined workflow steps beyond default 6-step
- Industry-specific workflow templates
- Workflow versioning and migration

### 5.3 AI Enhancements
- Advanced code review integration
- Predictive sprint planning
- Automated technical debt detection

**Success Criteria:** System supports enterprise-scale development with advanced customization options.

## IMPLEMENTATION SEQUENCE (COMPLETED THROUGH PHASE 3)

```
Phase 1: StateManager ✅ COMPLETED
Phase 2A: Command Rewrites ✅ COMPLETED
Phase 2B: Hook Development ✅ COMPLETED
Phase 2C: Integration ✅ COMPLETED
Phase 3: Testing & Validation ✅ COMPLETED
Phase 4: Documentation & Polish 🔄 IN PROGRESS (40% complete)
Phase 5: Advanced Features → FUTURE
```

### Recent Achievements (Phase 4)

**Documentation Reorganization (2025-07-28)**
- Archived 12 obsolete documents
- Created 3 new consolidated guides
- Enhanced setup documentation
- Established clear doc structure

**Remaining Phase 4 Work**
- User guide creation (2-3 days)
- Performance benchmarking (1-2 days)  
- UX improvements (2-3 days)
- Tutorial creation (2-3 days)

## CRITICAL DEPENDENCIES

1. **Claude Code Hook API** - Now understood; hooks can execute Python scripts
2. **StateManager** - ✅ Already implemented in Sprint 1
3. **Command Format** - Must use YAML frontmatter and `!` execution
4. **Hook Communication** - Via stdin/stdout JSON protocol

## RISK MITIGATION

- **Hook API Risk:** Build complete manual system first, layer automation on top
- **Complexity Risk:** Incremental implementation with working system at each sprint
- **Integration Risk:** Extensive testing with existing codebase
- **User Experience Risk:** Early validation and feedback incorporation

## DELIVERABLES SUMMARY

- Complete project state management system
- Working /user:project:* command implementation  
- Claude Code hook integration for automation
- Comprehensive testing and validation
- Production-ready documentation and user experience

This plan transforms the documented vision into a working automated development system while maintaining the robustness of the existing test framework.

## CURRENT STATUS

- **Date Created:** 2025-07-22
- **Date Updated:** 2025-07-28
- **Current Phase:** Phase 4 - Documentation & Polish
- **Next Milestone:** Complete user guide and tutorials
- **Recent Achievement:** Documentation reorganization completed

## PROGRESS TRACKING

- [x] Phase 1: State Management Core ✅ COMPLETED
- [x] Phase 2A: Command Rewrites ✅ COMPLETED
- [x] Phase 2B: Hook Development ✅ COMPLETED
- [x] Phase 2C: Integration ✅ COMPLETED
- [x] Phase 3: Testing & Validation ✅ COMPLETED (100% test coverage)
- [x] Phase 4: Documentation & Polish 🔄 IN PROGRESS
  - [x] Documentation reorganization (reduced 27 → 15 active docs)
  - [x] Manual testing guide created
  - [x] Testing scenarios guide created
  - [ ] User guide for workflow system
  - [ ] Performance benchmarking
- [ ] Phase 5: Advanced Features

## KEY ARCHITECTURE INSIGHTS

1. **Commands are triggers**: 10-20 lines, not 300+ line scripts
2. **Hooks are the engine**: All complex logic in Python hooks
3. **StateManager is the brain**: Already built, ready to use
4. **Workflow enforcement**: Automatic via hook interception
5. **Quality gates**: Mandatory checkpoints in hooks