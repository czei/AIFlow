# Project Start - Begin Automated Development

Start automated phase-driven development workflow in current git worktree.
Only works after successful /user:project:setup and /user:project:doctor validation.

Prerequisites:
- Must be in git worktree (not main repository)
- Project must be in "setup" status
- /user:project:doctor must show no errors
- Phase files must be customized with detailed workflow specifications
- Working directory must be clean

Tasks:
1. Run safety validation checks
2. Verify /user:project:doctor passes all checks
3. Update .project-state.json status from "setup" to "active"
4. Enable automation hooks in .claude/settings.json
5. Initialize .workflow-state.json for workflow automation
6. Load WORKFLOW_SPECIFICATIONS.md for automation guidance
7. Create "project-start" commit
8. Begin Phase 01 with planning step of 6-step workflow

## 6-Step Automation Workflow

Each development objective follows this rigorous cycle:

### 1. Plan Step
- Read current objective and acceptance criteria
- Break down into specific implementation tasks
- Assess risks, dependencies, and technical challenges
- Design implementation approach following project architecture
- Define testing strategy and success criteria

### 2. Implement Step  
- Write production-quality code following established patterns
- Ensure architecture compliance and coding standards adherence
- Implement comprehensive error handling and edge cases
- Add inline documentation for complex logic
- Follow project conventions and naming standards

### 3. Validate Step
- **Compilation Check**: Verify code compiles without errors/warnings
- **Existing Tests**: Run full existing test suite to prevent regressions
- **New Unit Tests**: Write comprehensive unit tests (>90% coverage)
- **Integration Tests**: Execute relevant integration tests
- **Manual Testing**: Basic smoke testing and edge case validation
- **Performance Check**: Validate against established benchmarks

### 4. Review Step
- **Self Review**: Thorough review of all changes
- **Zen Code Review**: Comprehensive analysis including:
  - Logic correctness and algorithm efficiency
  - Edge case handling and error conditions
  - Code organization, readability, maintainability
  - Security implications and vulnerability assessment
  - Performance characteristics and optimization opportunities
  - Test coverage adequacy and quality
- **Architectural Review**: Verify alignment with system architecture

### 5. Refine Step
- **Issue Resolution**: Address all code review feedback
- **Code Quality**: Implement suggested improvements and optimizations
- **Test Enhancement**: Improve tests based on review suggestions
- **Documentation**: Update documentation per review recommendations
- **Regression Testing**: Re-run full test suite after changes
- **Validation**: Confirm all review issues properly resolved

### 6. Integrate Step
- **Final Testing**: Execute complete test suite
- **Documentation Update**: Update project docs, README, API docs
- **Commit Creation**: Create clean, descriptive commit messages
- **Progress Update**: Update project state and phase tracking
- **Quality Verification**: Confirm objective meets all success criteria

## Quality Gates Enforced

Each step includes mandatory quality gates:
- **Compilation Gate**: All code must compile cleanly
- **Test Gate**: Full test suite passes with adequate coverage  
- **Review Gate**: Code review completed with critical issues resolved
- **Integration Gate**: Changes integrate properly with existing system
- **Documentation Gate**: All changes properly documented
- **Performance Gate**: Performance benchmarks met

## Automation Behavior

The project will now operate autonomously with:
- **Structured Execution**: Every objective follows complete 6-step workflow
- **Quality Enforcement**: No advancement without passing all quality gates  
- **State Tracking**: Detailed progress monitoring at workflow step level
- **Context Preservation**: Maintains project context across long sessions
- **Error Handling**: Escalates to human when workflows cannot complete
- **Resumability**: Can pause/resume at any workflow step

Control commands available during automation:
- /user:project:status - Monitor detailed progress and current workflow step
- /user:project:pause - Temporarily stop automation preserving state
- /user:project:resume - Continue automation from exact pause point
- /user:project:update - Manual state corrections and progress updates
- /user:project:stop - Clean project completion with comprehensive summary

Git workflow integration:
- Each complete objective creates logical commits with phase context
- Commit messages include workflow step and quality gate confirmation
- Automated branch management within worktree boundaries
- Safe isolation from main repository

Warning: This command enables autonomous operation with --dangerously-skip-permissions
The 6-step workflow with quality gates provides structured safety, but ensure you 
understand the scope and risks before proceeding.

Starting Phase 01 with rigorous 6-step workflow automation...
