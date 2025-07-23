# AI Instructions for Creating Sprint Description Files

This document provides detailed instructions for AI assistants (particularly Claude Code) on how to create effective sprint description files for the sprint-driven development system.

## Purpose and Context

Sprint files are the core specification documents that guide the automation system through structured development work. Each sprint file defines:
- What work needs to be accomplished
- How to measure success
- What acceptance criteria must be passed
- How the story lifecycle applies to this specific sprint

## Sprint File Creation Guidelines

### 1. Sprint Naming and Structure

**File Naming Convention:**
- Use format: `NN-sprint-name.md` (e.g., `03-implementation.md`)
- Sprint numbers should be sequential (01, 02, 03, etc.)
- Sprint names should be clear, descriptive action words

**Required Sections** (in order):
1. **Sprint Title and Status**
2. **Status Tracking** (completion percentage, timestamps)
3. **Prerequisites** (what must be complete before starting)
4. **Objectives** (specific, measurable goals with checkboxes)
5. **Story Lifecycle Implementation** (how the universal workflow applies)
6. **Acceptance Criteria** (specific pass/fail criteria)
7. **Success Criteria** (measurable completion requirements)
8. **Progress Log** (automated updates during execution)
9. **Next Sprint Trigger** (conditions for advancement)
10. **Automation Instructions** (specific guidance for Claude Code)

### 2. Writing Effective Objectives

**Structure for Each Objective:**
```markdown
- [ ] **Objective Name**: Clear description of what needs to be accomplished
  - **Acceptance Criteria**: Specific, measurable requirements
  - **Story Lifecycle**: Brief note on how this user story follows plan→implement→validate→review→refine→integrate
  - **Acceptance Criteria**: Which gates apply (compilation, testing, review, etc.)
  - **Estimated Effort**: Time estimate and complexity assessment
```

**Guidelines for Good Objectives:**
- **Specific**: Clearly defined scope and deliverables
- **Measurable**: Objective success criteria that can be verified
- **Achievable**: Reasonable scope for a single user story
- **Relevant**: Directly supports the sprint goals
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
- [x] **Sprint NN (Name)**: COMPLETE - Brief description of what was accomplished
- [x] **Technical Requirement**: Status - Specific technical dependencies
- [ ] **External Dependency**: Status - Dependencies outside the development team
- [x] **Environment Setup**: Status - Required tools, configurations, or infrastructure
```

**Guidelines:**
- List ALL dependencies, both internal and external
- Use checkboxes to track completion status
- Include brief descriptions of why each prerequisite matters
- Distinguish between hard blockers and nice-to-haves

### 4. Acceptance Criteria Specification

**Required Acceptance Criteria for All Sprints:**
1. **Compilation Gate**: All code must compile without errors or warnings
2. **Test Gate**: Relevant tests must pass with adequate coverage
3. **Review Gate**: Code review completed with issues resolved
4. **Integration Gate**: Changes integrate properly with existing system
5. **Documentation Gate**: All changes properly documented
6. **Performance Gate**: Performance requirements met or justified

**Sprint-Specific Acceptance Criteria:**
- **Planning**: Requirements clarity, feasibility validation, stakeholder approval
- **Architecture**: Design completeness, technology justification, scalability assessment
- **Implementation**: Code quality, functionality completion, error handling
- **Testing**: Test coverage, bug resolution, performance validation
- **Deployment**: Security review, production readiness, rollback procedures

**Format for Acceptance Criteria:**
```markdown
## Acceptance Criteria:
### Mandatory Gates (All Objectives):
- **Compilation**: All code compiles cleanly without warnings
- **Testing**: Unit tests pass with >90% coverage for new code
- **Review**: Zen methodology code review completed with all issues resolved
- **Integration**: Changes integrate without breaking existing functionality
- **Documentation**: All changes documented with examples and rationale

### Sprint-Specific Gates:
- **[Sprint-specific gate]**: Specific criteria and validation methods
- **[Performance gate]**: Specific benchmarks and measurement criteria
```

### 5. Story Lifecycle Implementation

**For Each Sprint, Specify How the Universal Workflow Applies:**

```markdown
## Story Lifecycle Implementation

Each user story in this sprint follows the universal workflow:

### 1. Planning Step
- **For This Sprint**: Specific planning activities relevant to this sprint
- **Deliverables**: What planning outputs are expected
- **Validation**: How to verify planning is complete

### 2. Implementation Step  
- **For This Sprint**: Specific implementation activities
- **Standards**: Coding standards, architecture patterns to follow
- **Dependencies**: How to handle dependencies within this sprint

### 3. Validation Step
- **For This Sprint**: Specific validation activities beyond universal gates
- **Testing Strategy**: Types of testing required for this sprint
- **Performance Criteria**: Sprint-specific performance requirements

### 4. Review Step
- **For This Sprint**: What aspects to focus on during review
- **Review Criteria**: Sprint-specific review checklist
- **Stakeholders**: Who should be involved in review

### 5. Refinement Step
- **For This Sprint**: Common refinement patterns for this type of work
- **Quality Focus**: What quality aspects are most critical
- **Iteration Strategy**: How to approach refinement cycles

### 6. Integration Step
- **For This Sprint**: Integration considerations specific to this sprint
- **Documentation**: What documentation is required
- **Handoff**: How to prepare for next sprint
```

### 6. Automation Instructions for Claude Code

**Critical Section - Provide Specific Guidance:**
```markdown
## Automation Instructions for Claude Code:

### Command Execution Preferences:
- **Preferred Commands**: List of commands that are safe and effective for this sprint
- **Dangerous Commands**: Commands to avoid and safer alternatives
- **Sprint-Specific Tools**: Specialized tools that should be used in this sprint

### Decision Making Guidelines:
- **When to Pause**: Specific conditions that should trigger human intervention
- **Error Handling**: How to respond to common error scenarios
- **Quality Validation**: How to verify that work meets sprint requirements

### State Management:
- **Progress Tracking**: How to update sprint progress and state files
- **Checkpoint Creation**: When to create git commits and checkpoints
- **Rollback Conditions**: When and how to rollback work

### Communication:
- **Status Updates**: What information to include in status updates
- **Error Reporting**: How to report errors and request help
- **Human Escalation**: When to escalate to human oversight
```

## Sprint Creation Process

### Step 1: Analyze Project Requirements
- Understand the overall project scope and goals
- Identify the natural sprints of work (typically 4-7 sprints)
- Consider dependencies between sprints
- Estimate complexity and effort for each sprint

### Step 2: Define Sprint Boundaries
- Each sprint should be focused on a specific type of work
- Sprints should have clear, measurable completion criteria
- Dependencies between sprints should be minimal and well-defined
- Each sprint should be substantial enough to warrant the overhead

### Step 3: Create Sprint Files in Order
- Start with Sprint 01 (usually planning or requirements)
- Each subsequent sprint should build on previous sprints
- Ensure prerequisites properly reference previous sprints
- Validate that the sequence makes logical sense

### Step 4: Validate Sprint Design
- Check that all sprints combined accomplish the project goals
- Verify that acceptance criteria are consistent across sprints
- Ensure automation instructions are clear and actionable
- Confirm that success criteria are measurable

## Common Sprint Patterns

### Planning Sprint (01)
- **Focus**: Requirements, scope, technology decisions
- **Objectives**: Research, documentation, stakeholder alignment
- **Acceptance Criteria**: Clarity, feasibility, approval
- **Automation**: Read-only operations, research, documentation

### Architecture Sprint (02)  
- **Focus**: System design, technology setup, component definition
- **Objectives**: Design documents, technology selection, project structure
- **Acceptance Criteria**: Completeness, scalability, technology justification
- **Automation**: File creation, configuration, initial setup

### Implementation Sprint (03)
- **Focus**: Core functionality development
- **Objectives**: Feature implementation, business logic, API development
- **Acceptance Criteria**: Code quality, functionality, testing
- **Automation**: Code generation, testing, file operations

### Testing Sprint (04)
- **Focus**: Quality assurance, bug resolution, performance validation
- **Objectives**: Test suite development, bug fixes, performance optimization
- **Acceptance Criteria**: Coverage, performance, reliability
- **Automation**: Test execution, performance measurement, issue resolution

### Deployment Sprint (05)
- **Focus**: Production preparation, deployment automation
- **Objectives**: Deployment scripts, monitoring, production configuration
- **Acceptance Criteria**: Security, reliability, operational readiness
- **Automation**: Configuration management, deployment testing

## Quality Checklist for Sprint Files

Before considering a sprint file complete, verify:

**Structure and Format:**
- [ ] All required sections are present and properly formatted
- [ ] Markdown formatting is correct and readable
- [ ] Checkboxes are properly formatted for user story tracking
- [ ] Timestamps and status fields are included

**Content Quality:**
- [ ] Objectives are specific, measurable, and achievable
- [ ] Prerequisites are complete and accurate
- [ ] Quality gates are clearly defined with pass/fail criteria
- [ ] Success criteria are measurable and unambiguous
- [ ] story lifecycle is properly adapted to the sprint

**Automation Readiness:**
- [ ] Automation instructions are clear and actionable
- [ ] Command preferences and restrictions are specified
- [ ] Error handling guidance is provided
- [ ] Progress tracking mechanisms are defined

**Integration:**
- [ ] Sprint integrates properly with previous and subsequent sprints
- [ ] Dependencies are clearly identified and manageable
- [ ] Handoff criteria to next sprint are well-defined
- [ ] Overall project flow makes logical sense

## Example Sprint File Template

See `example-detailed-sprint.md` for a complete example that demonstrates all these principles in practice.

## Common Mistakes to Avoid

1. **Overly Broad Objectives**: Break large user stories into smaller, manageable pieces
2. **Vague Success Criteria**: Always include specific, measurable completion requirements
3. **Missing Acceptance Criteria**: Every user story needs clear validation criteria
4. **Inadequate Automation Instructions**: Claude Code needs specific guidance, not general principles
5. **Poor Dependency Management**: Prerequisites should be minimal and well-justified
6. **Inconsistent Workflow Application**: The 6-step process should be consistently applied
7. **Missing Error Handling**: Always include guidance for common failure scenarios
8. **Unrealistic Estimates**: Provide reasonable time and complexity estimates

Remember: Sprint files are the primary interface between human planning and AI execution. They must be precise, complete, and actionable to enable effective automation.
