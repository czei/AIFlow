"""
ProjectBuilder - Creates project directory structure for sprint-based development.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime, timezone


class ProjectBuilder:
    """Creates standardized project structure for sprint-based development."""
    
    def __init__(self, project_name: str, project_path: str = None):
        self.project_name = self.validate_project_name(project_name)
        # Allow explicit path to be passed, default to cwd
        if project_path:
            self.project_path = Path(project_path).resolve()
        else:
            self.project_path = Path.cwd()
    
    @staticmethod
    def validate_project_name(name: str) -> str:
        """Validate and sanitize project name to prevent command injection.
        
        Args:
            name: Project name to validate
            
        Returns:
            Validated project name
            
        Raises:
            ValueError: If project name contains invalid characters
        """
        if not name:
            raise ValueError("Project name cannot be empty")
            
        # Allow only alphanumeric characters, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValueError(
                "Project name must contain only letters, numbers, hyphens, and underscores. "
                f"Got: '{name}'"
            )
            
        # Check length
        if len(name) > 100:
            raise ValueError("Project name must be 100 characters or less")
            
        return name
        
    def create_structure(self):
        """Create complete project directory structure."""
        # Create directories
        self._create_directories()
        
        # Create sprint files
        self._create_sprint_files()
        
        # Create documentation
        self._create_documentation()
        
        # Create Claude settings
        self._create_claude_settings()
        
    def _create_directories(self):
        """Create essential project directories."""
        dirs = ['sprints', '.claude', 'logs', 'docs']
        for dir_name in dirs:
            try:
                dir_path = self.project_path / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise RuntimeError(f"Failed to create directory {dir_name}: {e}")
            
    def _create_sprint_files(self):
        """Create default sprint markdown files."""
        sprints = {
            '01-planning.md': self._get_planning_sprint(),
            '02-architecture.md': self._get_architecture_sprint(),
            '03-implementation.md': self._get_implementation_sprint(),
            '04-testing.md': self._get_testing_sprint(),
            '05-deployment.md': self._get_deployment_sprint()
        }
        
        # Ensure sprints directory exists
        sprints_dir = self.project_path / 'sprints'
        if not sprints_dir.exists():
            raise RuntimeError(f"Sprints directory does not exist: {sprints_dir}")
        
        for filename, content in sprints.items():
            try:
                (sprints_dir / filename).write_text(content)
            except OSError as e:
                raise RuntimeError(f"Failed to create sprint file {filename}: {e}")
            
    def _create_documentation(self):
        """Create project documentation files."""
        # CLAUDE.md
        claude_md = f"""# {self.project_name} - Phase-Driven Development

## Project Context
This project follows a structured sprint-driven development approach with automated workflow execution.

**Project**: {self.project_name}
**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Methodology**: 6-Step Universal Workflow with Quality Gates

## Current Status
**Phase**: 01 - Planning
**Status**: Setup
**Automation**: Disabled (use /user:project:start to enable)

## Development Workflow
Every development objective follows these 6 steps:
1. **Planning** - Analyze requirements, design approach
2. **Implementation** - Write production code
3. **Validation** - Test and verify
4. **Review** - Code review and analysis
5. **Refinement** - Address feedback
6. **Integration** - Final tests and commit

## Acceptance Criteria
- ✅ Compilation - Code builds without errors
- ✅ Tests - All tests pass with coverage
- ✅ Review - Code review completed
- ✅ Integration - Changes integrate cleanly
- ✅ Documentation - Docs updated
- ✅ Performance - Benchmarks met

## Commands
- `/user:project:status` - Show progress
- `/user:project:start` - Begin automation
- `/user:project:pause` - Pause automation
- `/user:project:resume` - Resume from pause
- `/user:project:stop` - Complete project
"""
        (self.project_path / 'CLAUDE.md').write_text(claude_md)
        
        # README.md
        readme = f"""# {self.project_name}

A sprint-driven development project with automated workflow management.

## Project Structure
- `sprints/` - Development sprint definitions
- `.claude/` - Automation configuration
- `logs/` - Development logs
- `docs/` - Project documentation

## Getting Started
1. Customize sprint files in `sprints/`
2. Run `/user:project:doctor` to validate
3. Run `/user:project:start` to begin
"""
        (self.project_path / 'README.md').write_text(readme)
        
    def _create_claude_settings(self):
        """Create Claude automation settings."""
        settings = {
            "version": "1.0.0",
            "project_name": self.project_name,
            "automation_enabled": False,
            "hooks": {
                "PreToolUse": None,
                "PostToolUse": None,
                "Stop": None
            },
            "workflow": {
                "steps": ["planning", "implementation", "validation", "review", "refinement", "integration"],
                "quality_gates": ["compilation", "existing_tests", "new_tests", "review", "integration", "documentation", "performance"]
            }
        }
        
        settings_path = self.project_path / '.claude' / 'settings.json'
        settings_path.write_text(json.dumps(settings, indent=2))
        
    def _get_planning_sprint(self):
        return f"""# Sprint 01: Planning - {self.project_name}

## Status: Setup
- **Started**: Not started
- **Progress**: 0%
- **Current Step**: planning

## User Stories
- [ ] Requirements Analysis
- [ ] Technical Specifications
- [ ] Project Planning

## Dependencies
- Project requirements defined
- Stakeholder approval
- Development environment ready

## Acceptance Criteria
- Documentation review
- Specifications approved
- Timeline defined

## Definition of Done
- Requirements documented
- Technical specs complete
- Timeline established

CUSTOMIZE THIS FILE with project-specific user stories and requirements.
"""

    def _get_architecture_sprint(self):
        return f"""# Sprint 02: Architecture - {self.project_name}

## Status: Not Started
- **Started**: -
- **Progress**: 0%
- **Current Step**: -

## User Stories
- [ ] System Design
- [ ] Technology Selection
- [ ] API Design
- [ ] Database Schema

## Dependencies
- Planning sprint complete
- Requirements finalized

## Acceptance Criteria
- Architecture review
- Technology validation
- Design approval

## Definition of Done
- Architecture documented
- Tech stack selected
- APIs defined

CUSTOMIZE THIS FILE with project-specific architecture goals.
"""

    def _get_implementation_sprint(self):
        return f"""# Sprint 03: Implementation - {self.project_name}

## Status: Not Started
- **Started**: -
- **Progress**: 0%
- **Current Step**: -

## User Stories
- [ ] Core Features
- [ ] API Implementation
- [ ] Database Setup
- [ ] Integration Points

## Dependencies
- Architecture approved
- Development environment ready

## Acceptance Criteria
- Code compilation
- Unit tests pass
- Code review
- Integration tests

## Definition of Done
- Features implemented
- Tests passing
- Code reviewed

CUSTOMIZE THIS FILE with specific implementation tasks.
"""

    def _get_testing_sprint(self):
        return f"""# Sprint 04: Testing - {self.project_name}

## Status: Not Started
- **Started**: -
- **Progress**: 0%
- **Current Step**: -

## User Stories
- [ ] Unit Testing
- [ ] Integration Testing
- [ ] Performance Testing
- [ ] User Acceptance Testing

## Dependencies
- Implementation complete
- Test environment ready

## Acceptance Criteria
- Test coverage >90%
- All tests passing
- Performance benchmarks met
- UAT sign-off

## Definition of Done
- Comprehensive test coverage
- No critical bugs
- Performance validated

CUSTOMIZE THIS FILE with testing requirements.
"""

    def _get_deployment_sprint(self):
        return f"""# Sprint 05: Deployment - {self.project_name}

## Status: Not Started
- **Started**: -
- **Progress**: 0%
- **Current Step**: -

## User Stories
- [ ] Production Setup
- [ ] Deployment Pipeline
- [ ] Monitoring Setup
- [ ] Documentation

## Dependencies
- Testing complete
- Production access

## Acceptance Criteria
- Deployment checklist
- Security review
- Performance validation
- Documentation complete

## Definition of Done
- Successfully deployed
- Monitoring active
- Documentation published

CUSTOMIZE THIS FILE with deployment specifics.
"""
