# Project State Schema Documentation

## Overview

The `.project-state.json` file maintains the complete state of an automated phase-driven development project. This file enables resumable automation, progress tracking, and workflow coordination across extended development sessions.

## Schema Definition

### Core Structure

```json
{
  "project_name": "string",
  "current_phase": "string", 
  "status": "enum",
  "automation_active": "boolean",
  "workflow_step": "enum",
  "current_objective": "string|null",
  "quality_gates_passed": "array[string]",
  "completed_phases": "array[string]",
  "automation_cycles": "integer",
  "started": "iso8601_timestamp",
  "last_updated": "iso8601_timestamp",
  "git_branch": "string|null",
  "git_worktree": "string",
  "version": "string"
}
```

## Field Specifications

### Required Fields

#### `project_name` (string)
- **Description**: Human-readable project identifier
- **Constraints**: Non-empty string, no special characters recommended
- **Example**: `"user-authentication-feature"`

#### `current_phase` (string)
- **Description**: Current development phase identifier
- **Constraints**: Typically numeric (01, 02, etc.) but allows custom identifiers
- **Example**: `"03"`

#### `status` (enum)
- **Description**: Overall project state
- **Valid Values**: 
  - `"setup"` - Project initialized but not started
  - `"active"` - Automation running or ready to run
  - `"paused"` - Temporarily stopped, can be resumed
  - `"stopped"` - Cleanly ended, requires manual restart
  - `"completed"` - All phases finished successfully
  - `"error"` - Stopped due to unrecoverable error
- **Example**: `"active"`

#### `automation_active` (boolean)
- **Description**: Whether automation hooks are currently enabled
- **Example**: `true`

#### `workflow_step` (enum)
- **Description**: Current position in 6-step workflow
- **Valid Values**: `"planning"`, `"implementation"`, `"validation"`, `"review"`, `"refinement"`, `"integration"`
- **Example**: `"validation"`

#### `quality_gates_passed` (array[string])
- **Description**: Quality gates passed for current objective
- **Valid Gate Types**: `"compilation"`, `"existing_tests"`, `"new_tests"`, `"review"`, `"integration"`, `"documentation"`, `"performance"`
- **Example**: `["compilation", "existing_tests"]`

#### `completed_phases` (array[string])
- **Description**: List of phases that have been fully completed
- **Example**: `["01", "02"]`

#### `automation_cycles` (integer)
- **Description**: Number of automation cycles executed
- **Constraints**: Non-negative integer
- **Example**: `47`

#### `started` (iso8601_timestamp)
- **Description**: When the project was first initialized
- **Format**: ISO 8601 with timezone
- **Example**: `"2025-07-21T09:00:00Z"`

#### `last_updated` (iso8601_timestamp)
- **Description**: Last modification timestamp
- **Format**: ISO 8601 with timezone
- **Example**: `"2025-07-21T15:30:00Z"`

### Optional Fields

#### `current_objective` (string|null)
- **Description**: Current task or objective being worked on
- **Example**: `"Business logic API endpoints"`

#### `git_branch` (string|null)
- **Description**: Associated git branch name
- **Example**: `"feature/user-auth"`

#### `git_worktree` (string)
- **Description**: Path to git worktree directory
- **Example**: `"/Users/dev/projects/my-feature"`

#### `version` (string)
- **Description**: Schema version for migration support
- **Example**: `"1.0.0"`

## Example Complete State

```json
{
  "project_name": "user-authentication-system",
  "current_phase": "03",
  "status": "active",
  "automation_active": true,
  "workflow_step": "validation", 
  "current_objective": "Business logic API endpoints",
  "quality_gates_passed": ["compilation", "existing_tests"],
  "completed_phases": ["01", "02"],
  "automation_cycles": 47,
  "started": "2025-07-21T09:00:00Z",
  "last_updated": "2025-07-21T15:30:00Z",
  "git_branch": "feature/user-auth",
  "git_worktree": "/Users/dev/projects/user-auth-feature",
  "version": "1.0.0"
}
```

## State Transitions

### Status Transitions

```
setup → active    (via /user:project:start)
active → paused   (via /user:project:pause)
paused → active   (via /user:project:resume)  
active → stopped  (via /user:project:stop)
active → completed (automatic when all phases done)
any → error       (on unrecoverable failure)
```

### Workflow Step Progression

```
planning → implementation → validation → review → refinement → integration
                                ↑                                    ↓
                                └── (cycle back on failed gates) ←──┘
```

### Phase Advancement

- Phases advance only when all objectives complete with quality gates passed
- `current_phase` updates to next phase identifier
- Previous phase added to `completed_phases` array
- `workflow_step` resets to `"planning"`
- `quality_gates_passed` resets to empty array

## Validation Rules

### Schema Validation
- All required fields must be present
- Field types must match specifications
- Enum values must be from valid sets
- Timestamps must be valid ISO 8601 format
- Arrays must contain valid element types

### Business Logic Validation
- `automation_cycles` must be non-negative
- `last_updated` must be >= `started`
- `current_phase` must not be in `completed_phases`
- Quality gates must be from valid set
- Phase identifiers should follow project conventions

### State Consistency
- Status must align with automation_active state
- Workflow step must be valid for current status
- Quality gates should be appropriate for workflow step
- Git information should match actual repository state

## Error Handling

### Validation Errors
- **Missing Fields**: Clear error indicating required field
- **Invalid Types**: Type mismatch with expected format
- **Invalid Values**: Enum values not in valid set
- **Business Rule Violations**: Inconsistent state combinations

### Recovery Strategies
- **Automatic Backup**: State backed up before each update
- **Rollback Capability**: Restore from backup on corruption
- **Manual Override**: Force state updates with validation bypass
- **State Repair**: Utilities to fix common inconsistencies

## Usage with StateManager

```python
from src.state_manager import StateManager

# Initialize manager
manager = StateManager("/path/to/project")

# Create initial state
state = manager.create("my-project")

# Read current state
current = manager.read()

# Update specific fields
updated = manager.update({
    "workflow_step": "implementation",
    "current_objective": "User login endpoint"
})

# Transition phases
next_phase = manager.transition_phase("04")

# Validate state
is_valid = manager.validate()
```

## Migration and Versioning

### Version 1.0.0 (Current)
- Initial schema implementation
- Core workflow and phase management
- Basic quality gate tracking

### Future Versions
- Enhanced quality gate definitions
- Custom workflow configurations
- Multi-project support
- Performance metrics tracking

### Migration Strategy
- Version field enables automated migration
- Backward compatibility maintained where possible
- Migration utilities provided for major changes
- State backup required before migration

## Security Considerations

### File Permissions
- State file should be readable/writable by project owner only
- Backup files inherit same permissions
- Temporary files created with restricted access

### Validation Security
- Input sanitization for all string fields
- Path validation for git_worktree field
- Timestamp validation to prevent injection
- Array length limits to prevent memory issues

### Audit Trail
- All state changes logged with timestamps
- Git integration provides additional audit trail
- Backup files maintain change history
- Quality gate progression tracked for compliance

This schema provides the foundation for reliable, resumable automated development with comprehensive state tracking and validation.