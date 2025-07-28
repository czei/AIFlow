# Manual Testing Guide for AI Software Project Management System

## Overview

This guide provides step-by-step instructions for manually testing the AI Software Project Management System. It covers setup, configuration, project specification, and validation of the automated development workflow.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Creating a Test Project](#creating-a-test-project)
4. [Defining Project Specifications](#defining-project-specifications)
5. [Running Manual Tests](#running-manual-tests)
6. [Test Scenarios](#test-scenarios)
7. [Validation Checklist](#validation-checklist)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting manual testing:

1. **Git Repository**: Must be in a git repository directory
2. **Claude Code**: Install Claude Code CLI tool
3. **Python 3.7+**: Required for scripts and hooks
4. **Directory Permissions**: Write access to parent directory for git worktrees
5. **Command Installation**: Commands installed in `~/.claude/commands/project/`

## Initial Setup

### 1. Install Commands

```bash
# Create commands directory
mkdir -p ~/.claude/commands/project

# Copy command files (adjust path as needed)
cp -r /path/to/ai-software-project-management/src/commands/* ~/.claude/commands/project/

# Copy supporting scripts
cp /path/to/ai-software-project-management/scripts/logged_secure_shell.py ~/.claude/commands/
chmod +x ~/.claude/commands/logged_secure_shell.py
```

### 2. Start Claude Code

```bash
# Navigate to your test git repository
cd /path/to/your/git-repo

# Start Claude Code with permissions flag
claude-code --dangerously-skip-permissions
```

### 3. Verify Installation

```bash
# Test command availability
/user:project:setup --help

# Should show available commands
```

## Creating a Test Project

### 1. Initialize Project Structure

```bash
# Create a new project (replace "test-webapp" with your project name)
/user:project:setup test-webapp

# This creates:
# - Git worktree at ../test-webapp/
# - Sprint templates in sprints/
# - CLAUDE.md for project context
# - State management files
```

### 2. Navigate to Project

```bash
cd ../test-webapp
```

### 3. Verify Project Structure

```bash
# Check created structure
ls -la

# Should show:
# sprints/
# .claude/
# docs/
# logs/
# CLAUDE.md
# README.md
# .project-state.json
# WORKFLOW_SPECIFICATIONS.md
```

## Defining Project Specifications

### 1. Customize Sprint Files

Navigate to the `sprints/` directory and customize each sprint file with your project details.

#### Example: 01-planning.md

```markdown
# Sprint 01: Planning and Requirements

## Status: NOT_STARTED
## Started: [Pending]
## Completion: 0%

## Prerequisites:
- [x] Project repository created
- [x] Development environment ready
- [x] Stakeholder requirements gathered

## Objectives:
- [ ] **Define User Authentication Requirements**
  - Analyze security requirements for user login
  - Define password policies and 2FA requirements
  - Document session management approach
  - Create API endpoint specifications
  
- [ ] **Design Database Schema**
  - Define user table structure
  - Plan for role-based access control
  - Design audit logging schema
  - Create migration strategy

- [ ] **Create Technical Specification**
  - Document technology choices (framework, database, etc.)
  - Define coding standards and conventions
  - Create component architecture diagram
  - Establish testing requirements

## Implementation Workflow:
[Follow standard 6-step workflow for each objective]

## Success Criteria:
- All requirements documented with acceptance criteria
- Database schema reviewed and approved
- Technical specification complete with diagrams
- All stakeholders signed off on approach
```

#### Example: 03-implementation.md

```markdown
# Sprint 03: Core Implementation

## Status: NOT_STARTED
## Started: [Pending]
## Completion: 0%

## Prerequisites:
- [x] Sprint 01 (Planning) COMPLETE
- [x] Sprint 02 (Architecture) COMPLETE
- [x] Database migrations ready
- [x] Development environment configured

## Objectives:
- [ ] **Implement User Model and Database Layer**
  - Create User model with all required fields
  - Implement password hashing with bcrypt
  - Add database migrations
  - Create unit tests with >90% coverage
  
- [ ] **Build Authentication API Endpoints**
  - POST /api/auth/register - User registration
  - POST /api/auth/login - User login with JWT
  - POST /api/auth/refresh - Token refresh
  - POST /api/auth/logout - Session termination
  - GET /api/auth/profile - Get current user
  
- [ ] **Implement Session Management**
  - JWT token generation and validation
  - Refresh token rotation strategy
  - Session timeout handling
  - Concurrent session limits

## Implementation Workflow:
[Standard 6-step workflow with focus on test-driven development]

## Acceptance Criteria:
- All endpoints return proper HTTP status codes
- Input validation on all fields
- Comprehensive error handling
- Security best practices followed
- All tests passing with >90% coverage
```

### 2. Edit CLAUDE.md

Add project-specific context to CLAUDE.md:

```markdown
# test-webapp - AI-Driven Development Project

## Project Overview

Building a modern web application with user authentication, role-based access control, and RESTful API. This project demonstrates automated development practices with comprehensive testing and security focus.

## Technology Stack

- **Backend**: Python 3.9 + FastAPI
- **Database**: PostgreSQL 14 with SQLAlchemy ORM
- **Authentication**: JWT with refresh tokens
- **Testing**: pytest, coverage.py
- **Documentation**: OpenAPI/Swagger

## Development Standards

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all functions
- Maximum line length: 88 characters (Black formatter)
- Docstrings for all public functions

### Git Conventions
- Feature branches: feature/description
- Commit messages: type(scope): description
- Squash commits before merging
- All tests must pass before merge

### Testing Requirements
- Minimum 90% code coverage for new code
- Unit tests for all business logic
- Integration tests for all API endpoints
- Performance tests for critical paths

## Security Requirements

- All passwords hashed with bcrypt (min 12 rounds)
- JWT tokens expire after 15 minutes
- Refresh tokens rotate on use
- Rate limiting on authentication endpoints
- Input validation on all user inputs

## Project-Specific Instructions

When implementing features:
1. Always start with tests (TDD approach)
2. Validate inputs at API boundary
3. Log all authentication events
4. Follow OWASP security guidelines
5. Document all API endpoints

For database changes:
1. Always use migrations (never direct SQL)
2. Include rollback procedures
3. Test migrations on copy of production data
4. Document schema changes
```

### 3. Validate Customization

```bash
# Run doctor command to check setup
/user:project:doctor

# Should show all green checkmarks if properly configured
```

## Running Manual Tests

### Test Scenario 1: Basic Project Lifecycle

```bash
# 1. Start automation
/user:project:start

# 2. Check initial status
/user:project:status

# 3. Let automation run for planning phase
# Watch for read-only operations during planning

# 4. Pause automation to verify state
/user:project:pause

# 5. Check current state
/user:project:status

# 6. Resume automation
/user:project:resume

# 7. Monitor progress
# Automation should advance through workflow steps
```

### Test Scenario 2: Workflow Enforcement

```bash
# 1. Start fresh project
/user:project:setup test-workflow
cd ../test-workflow

# 2. Customize sprints with simple objectives
# Edit sprints/01-planning.md with a basic task

# 3. Start automation
/user:project:start

# 4. Observe tool blocking
# During planning: Write/Edit tools should be blocked
# During implementation: Write/Edit tools should be allowed

# 5. Check logs for enforcement
tail -f logs/workflow.log | jq .
```

### Test Scenario 3: State Persistence

```bash
# 1. Start project and let it run
/user:project:start

# 2. After some progress, stop Claude Code
# Ctrl+C or close terminal

# 3. Restart Claude Code
claude-code --dangerously-skip-permissions

# 4. Check state was preserved
/user:project:status

# 5. Resume from where it left off
/user:project:resume
```

### Test Scenario 4: Manual Intervention

```bash
# 1. Start automation
/user:project:start

# 2. Pause when in implementation phase
/user:project:pause

# 3. Make manual changes
# Edit some files manually

# 4. Update state to reflect changes
/user:project:update

# 5. Resume automation
/user:project:resume
```

## Test Scenarios

### Scenario A: Complete Sprint Execution

**Objective**: Test full sprint lifecycle from planning to completion

1. Create project with single sprint
2. Define 2-3 simple objectives
3. Start automation and monitor:
   - Planning phase completion
   - Implementation with proper tools
   - Validation running tests
   - Review process execution
   - Refinement based on feedback
   - Integration and documentation

**Expected Results**:
- Sprint completes with all objectives checked
- State shows 100% completion
- All quality gates passed
- Progress tracked in logs

### Scenario B: Multi-Sprint Project

**Objective**: Test sprint transitions and dependencies

1. Create project with 3 sprints
2. Set dependencies between sprints
3. Run automation through multiple sprints
4. Verify prerequisite checking
5. Confirm state transitions

**Expected Results**:
- Sprints execute in order
- Prerequisites block premature execution
- State accurately tracks current sprint
- Smooth transitions between sprints

### Scenario C: Error Recovery

**Objective**: Test system resilience to errors

1. Introduce deliberate error (e.g., failing test)
2. Observe automation response
3. Fix error manually
4. Resume automation
5. Verify recovery

**Expected Results**:
- Automation detects error
- Appropriate error logged
- Human intervention requested
- Recovery successful after fix

## Validation Checklist

### Pre-Test Validation

- [ ] Commands installed correctly
- [ ] Git repository initialized
- [ ] Claude Code starts without errors
- [ ] Project setup creates all directories
- [ ] Sprint files are customizable
- [ ] CLAUDE.md is editable

### During Test Validation

- [ ] Workflow steps execute in order
- [ ] Tool restrictions work properly
- [ ] State updates after each step
- [ ] Logs capture all activities
- [ ] Progress percentages accurate
- [ ] Quality gates enforced

### Post-Test Validation

- [ ] Sprint marked complete
- [ ] All objectives checked off
- [ ] State file shows completion
- [ ] Logs show full history
- [ ] Git commits created
- [ ] Documentation updated

## Troubleshooting

### Common Issues and Solutions

#### 1. Commands Not Found
```bash
# Verify installation path
ls ~/.claude/commands/project/

# Check command permissions
chmod +x ~/.claude/commands/project/*.md
```

#### 2. Git Worktree Errors
```bash
# Clean up broken worktrees
git worktree prune

# List existing worktrees
git worktree list

# Remove specific worktree
git worktree remove ../project-name
```

#### 3. State File Corruption
```bash
# Backup corrupted state
cp .project-state.json .project-state.backup.json

# Reset to clean state
/user:project:update --reset

# Or manually edit JSON
vim .project-state.json
```

#### 4. Hook Execution Failures
```bash
# Check hook configuration
cat .claude/settings.json

# Test hooks manually
python3 ~/.claude/commands/project/hooks/pre_tool_use.py < test_event.json

# Check Python path
which python3
python3 --version
```

#### 5. Automation Stuck
```bash
# Force pause
/user:project:pause

# Check current state
/user:project:status

# Reset workflow step if needed
/user:project:update --step planning

# Resume
/user:project:resume
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Set debug environment variable
export DEBUG=1

# Run commands with debug output
/user:project:status

# Check detailed logs
tail -f logs/automation.log | jq '.level == "DEBUG"'
```

## Best Practices for Manual Testing

1. **Start Small**: Begin with single-objective sprints
2. **Incremental Complexity**: Add features gradually
3. **Document Issues**: Keep notes of any problems
4. **Save State**: Backup .project-state.json periodically
5. **Monitor Logs**: Keep log viewer open during tests
6. **Test Edge Cases**: Try unusual scenarios
7. **Verify Idempotency**: Commands should be safe to repeat

## Conclusion

This manual testing guide provides comprehensive instructions for validating the AI Software Project Management System. Follow these steps to ensure the system works correctly with your project specifications and handles various scenarios appropriately.

For automated testing, refer to the test suite documentation and run:
```bash
python tests/runners/test_runner_v2.py
```