# AI Instructions for Creating Phase Description Files

This document provides detailed instructions for AI assistants (particularly Claude Code) on how to create effective phase description files for the phase-driven development system.

## Purpose and Context

Phase files are the core specification documents that guide the automation system through structured development work. Each phase file defines:
- What work needs to be accomplished
- How to measure success
- What quality gates must be passed
- How the 6-step workflow applies to this specific phase

## Phase File Creation Guidelines

### 1. Phase Naming and Structure

**File Naming Convention:**
- Use format: `NN-phase-name.md` (e.g., `03-implementation.md`)
- Phase numbers should be sequential (01, 02, 03, etc.)
- Phase names should be clear, descriptive action words

**Required Sections** (in order):
1. **Phase Title and Status**
2. **Status Tracking** (completion percentage, timestamps)
3. **Prerequisites** (what must be complete before starting)
4. **Objectives** (specific, measurable goals with checkboxes)
5. **6-Step Workflow Implementation** (how the universal workflow applies)
6. **Quality Gates** (specific pass/fail criteria)
7. **Success Criteria** (measurable completion requirements)
8. **Progress Log** (automated updates during execution)
9. **Next Phase Trigger** (conditions for advancement)
10. **Automation Instructions** (specific guidance for Claude Code)

### 2. Writing Effective Objectives

**Structure for Each Objective:**
```markdown
- [ ] **Objective Name**: Clear description of what needs to be accomplished
  - **Acceptance Criteria**: Specific, measurable requirements
  - **6-Step Workflow**: Brief note on how this objective follows plan→implement→validate→review→refine→integrate
  - **Quality Gates**: Which gates apply (compilation, testing, review, etc.)
  - **Estimated Effort**: Time estimate and complexity assessment
```

**Guidelines for Good Objectives:**
- **Specific**: Clearly defined scope and deliverables
- **Measurable**: Objective success criteria that can be verified
- **Achievable**: Reasonable scope for a single objective
- **Relevant**: Directly supports the phase goals
- **Time-bound**: Reasonable completion estimates

**Examples of Good vs. Bad Objectives:**

❌ **Bad**: "Implement user authentication"
✅ **Good**: "Implement JWT-based user authentication system with login, logout, and token refresh endpoints, including unit tests and integration with existing user database"

❌ **Bad**: "Fix bugs"
✅ **Good**: "Resolve authentication middleware issues: fix token expiration handling, add proper error responses for invalid tokens, and implement rate limiting for login attempts"

❌ **Bad**: "Add tests"
✅ **Good**: "Create comprehensive test suite for payment processing module with >90% code coverage, including unit tests for validation logic, integration tests for payment gateway, and error scenario testing"

### 3. Prerequisites Definition

**Format for Prerequisites:**
```markdown
## Prerequisites:
- [x] **Phase NN (Name)**: COMPLETE - Brief description of what was accomplished
- [x] **Technical Requirement**: Status - Specific technical dependencies
- [ ] **External Dependency**: Status - Dependencies outside the development team
- [x] **Environment Setup**: Status - Required tools, configurations, or infrastructure
```

**Guidelines:**
- List ALL dependencies, both internal and external
- Use checkboxes to track completion status
- Include brief descriptions of why each prerequisite matters
- Distinguish between hard blockers and nice-to-haves

### 4. Quality Gates Specification

**Required Quality Gates for All Phases:**
1. **Compilation Gate**: All code must compile without errors or warnings
2. **Test Gate**: Relevant tests must pass with adequate coverage
3. **Review Gate**: Code review completed with issues resolved
4. **Integration Gate**: Changes integrate properly with existing system
5. **Documentation Gate**: All changes properly documented
6. **Performance Gate**: Performance requirements met or justified

**Phase-Specific Quality Gates:**
- **Planning**: Requirements clarity, feasibility validation, stakeholder approval
- **Architecture**: Design completeness, technology justification, scalability assessment
- **Implementation**: Code quality, functionality completion, error handling
- **Testing**: Test coverage, bug resolution, performance validation
- **Deployment**: Security review, production readiness, rollback procedures

**Format for Quality Gates:**
```markdown
## Quality Gates:
### Mandatory Gates (All Objectives):
- **Compilation**: All code compiles cleanly without warnings
- **Testing**: Unit tests pass with >90% coverage for new code
- **Review**: Zen methodology code review completed with all issues resolved
- **Integration**: Changes integrate without breaking existing functionality
- **Documentation**: All changes documented with examples and rationale

### Phase-Specific Gates:
- **[Phase-specific gate]**: Specific criteria and validation methods
- **[Performance gate]**: Specific benchmarks and measurement criteria
```

### 5. 6-Step Workflow Implementation

**For Each Phase, Specify How the Universal Workflow Applies:**

```markdown
## 6-Step Workflow Implementation

Each objective in this phase follows the universal workflow:

### 1. Planning Step
- **For This Phase**: Specific planning activities relevant to this phase
- **Deliverables**: What planning outputs are expected
- **Validation**: How to verify planning is complete

### 2. Implementation Step  
- **For This Phase**: Specific implementation activities
- **Standards**: Coding standards, architecture patterns to follow
- **Dependencies**: How to handle dependencies within this phase

### 3. Validation Step
- **For This Phase**: Specific validation activities beyond universal gates
- **Testing Strategy**: Types of testing required for this phase
- **Performance Criteria**: Phase-specific performance requirements

### 4. Review Step
- **For This Phase**: What aspects to focus on during review
- **Review Criteria**: Phase-specific review checklist
- **Stakeholders**: Who should be involved in review

### 5. Refinement Step
- **For This Phase**: Common refinement patterns for this type of work
- **Quality Focus**: What quality aspects are most critical
- **Iteration Strategy**: How to approach refinement cycles

### 6. Integration Step
- **For This Phase**: Integration considerations specific to this phase
- **Documentation**: What documentation is required
- **Handoff**: How to prepare for next phase
```

### 6. Automation Instructions for Claude Code

**Critical Section - Provide Specific Guidance:**
```markdown
## Automation Instructions for Claude Code:

### Command Execution Preferences:
- **Preferred Commands**: List of commands that are safe and effective for this phase
- **Dangerous Commands**: Commands to avoid and safer alternatives
- **Phase-Specific Tools**: Specialized tools that should be used in this phase

### Decision Making Guidelines:
- **When to Pause**: Specific conditions that should trigger human intervention
- **Error Handling**: How to respond to common error scenarios
- **Quality Validation**: How to verify that work meets phase requirements

### State Management:
- **Progress Tracking**: How to update phase progress and state files
- **Checkpoint Creation**: When to create git commits and checkpoints
- **Rollback Conditions**: When and how to rollback work

### Communication:
- **Status Updates**: What information to include in status updates
- **Error Reporting**: How to report errors and request help
- **Human Escalation**: When to escalate to human oversight
```

## Phase Creation Process

### Step 1: Analyze Project Requirements
- Understand the overall project scope and goals
- Identify the natural phases of work (typically 4-7 phases)
- Consider dependencies between phases
- Estimate complexity and effort for each phase

### Step 2: Define Phase Boundaries
- Each phase should be focused on a specific type of work
- Phases should have clear, measurable completion criteria
- Dependencies between phases should be minimal and well-defined
- Each phase should be substantial enough to warrant the overhead

### Step 3: Create Phase Files in Order
- Start with Phase 01 (usually planning or requirements)
- Each subsequent phase should build on previous phases
- Ensure prerequisites properly reference previous phases
- Validate that the sequence makes logical sense

### Step 4: Validate Phase Design
- Check that all phases combined accomplish the project goals
- Verify that quality gates are consistent across phases
- Ensure automation instructions are clear and actionable
- Confirm that success criteria are measurable

## Common Phase Patterns

### Planning Phase (01)
- **Focus**: Requirements, scope, technology decisions
- **Objectives**: Research, documentation, stakeholder alignment
- **Quality Gates**: Clarity, feasibility, approval
- **Automation**: Read-only operations, research, documentation

### Architecture Phase (02)  
- **Focus**: System design, technology setup, component definition
- **Objectives**: Design documents, technology selection, project structure
- **Quality Gates**: Completeness, scalability, technology justification
- **Automation**: File creation, configuration, initial setup

### Implementation Phase (03)
- **Focus**: Core functionality development
- **Objectives**: Feature implementation, business logic, API development
- **Quality Gates**: Code quality, functionality, testing
- **Automation**: Code generation, testing, file operations

### Testing Phase (04)
- **Focus**: Quality assurance, bug resolution, performance validation
- **Objectives**: Test suite development, bug fixes, performance optimization
- **Quality Gates**: Coverage, performance, reliability
- **Automation**: Test execution, performance measurement, issue resolution

### Deployment Phase (05)
- **Focus**: Production preparation, deployment automation
- **Objectives**: Deployment scripts, monitoring, production configuration
- **Quality Gates**: Security, reliability, operational readiness
- **Automation**: Configuration management, deployment testing

## Quality Checklist for Phase Files

Before considering a phase file complete, verify:

**Structure and Format:**
- [ ] All required sections are present and properly formatted
- [ ] Markdown formatting is correct and readable
- [ ] Checkboxes are properly formatted for objective tracking
- [ ] Timestamps and status fields are included

**Content Quality:**
- [ ] Objectives are specific, measurable, and achievable
- [ ] Prerequisites are complete and accurate
- [ ] Quality gates are clearly defined with pass/fail criteria
- [ ] Success criteria are measurable and unambiguous
- [ ] 6-step workflow is properly adapted to the phase

**Automation Readiness:**
- [ ] Automation instructions are clear and actionable
- [ ] Command preferences and restrictions are specified
- [ ] Error handling guidance is provided
- [ ] Progress tracking mechanisms are defined

**Integration:**
- [ ] Phase integrates properly with previous and subsequent phases
- [ ] Dependencies are clearly identified and manageable
- [ ] Handoff criteria to next phase are well-defined
- [ ] Overall project flow makes logical sense

## Example Phase File Template

See `example-detailed-phase.md` for a complete example that demonstrates all these principles in practice.

## Common Mistakes to Avoid

1. **Overly Broad Objectives**: Break large objectives into smaller, manageable pieces
2. **Vague Success Criteria**: Always include specific, measurable completion requirements
3. **Missing Quality Gates**: Every objective needs clear validation criteria
4. **Inadequate Automation Instructions**: Claude Code needs specific guidance, not general principles
5. **Poor Dependency Management**: Prerequisites should be minimal and well-justified
6. **Inconsistent Workflow Application**: The 6-step process should be consistently applied
7. **Missing Error Handling**: Always include guidance for common failure scenarios
8. **Unrealistic Estimates**: Provide reasonable time and complexity estimates

Remember: Phase files are the primary interface between human planning and AI execution. They must be precise, complete, and actionable to enable effective automation.
