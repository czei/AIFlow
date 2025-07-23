"""
ProjectBuilder - Creates project directory structure for phase-driven development.
"""

import os
import json
from pathlib import Path
from datetime import datetime, timezone


class ProjectBuilder:
    """Creates standardized project structure for phase-driven development."""
    
    def __init__(self, project_name: str, project_path: str = None):
        self.project_name = project_name
        # Allow explicit path to be passed, default to cwd
        if project_path:
            self.project_path = Path(project_path).resolve()
        else:
            self.project_path = Path.cwd()
        
    def create_structure(self):
        """Create complete project directory structure."""
        # Create directories
        self._create_directories()
        
        # Create phase files
        self._create_phase_files()
        
        # Create documentation
        self._create_documentation()
        
        # Create Claude settings
        self._create_claude_settings()
        
    def _create_directories(self):
        """Create essential project directories."""
        dirs = ['phases', '.claude', 'logs', 'docs']
        for dir_name in dirs:
            try:
                dir_path = self.project_path / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise RuntimeError(f"Failed to create directory {dir_name}: {e}")
            
    def _create_phase_files(self):
        """Create default phase markdown files."""
        phases = {
            '01-planning.md': self._get_planning_phase(),
            '02-architecture.md': self._get_architecture_phase(),
            '03-implementation.md': self._get_implementation_phase(),
            '04-testing.md': self._get_testing_phase(),
            '05-deployment.md': self._get_deployment_phase()
        }
        
        # Ensure phases directory exists
        phases_dir = self.project_path / 'phases'
        if not phases_dir.exists():
            raise RuntimeError(f"Phases directory does not exist: {phases_dir}")
        
        for filename, content in phases.items():
            try:
                (phases_dir / filename).write_text(content)
            except OSError as e:
                raise RuntimeError(f"Failed to create phase file {filename}: {e}")
            
    def _create_documentation(self):
        """Create project documentation files."""
        # CLAUDE.md
        claude_md = f"""# {self.project_name} - Phase-Driven Development

## Project Context
This project follows a structured phase-driven development approach with automated workflow execution.

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

## Quality Gates
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

A phase-driven development project with automated workflow management.

## Project Structure
- `phases/` - Development phase definitions
- `.claude/` - Automation configuration
- `logs/` - Development logs
- `docs/` - Project documentation

## Getting Started
1. Customize phase files in `phases/`
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
        
    def _get_planning_phase(self):
        return f"""# Phase 01: Planning - {self.project_name}

## Status: Setup
- **Started**: Not started
- **Progress**: 0%
- **Current Step**: planning

## Objectives
- [ ] Requirements Analysis
- [ ] Technical Specifications
- [ ] Project Planning

## Prerequisites
- Project requirements defined
- Stakeholder approval
- Development environment ready

## Quality Gates
- Documentation review
- Specifications approved
- Timeline defined

## Success Criteria
- Requirements documented
- Technical specs complete
- Timeline established

CUSTOMIZE THIS FILE with project-specific objectives and requirements.
"""

    def _get_architecture_phase(self):
        return f"""# Phase 02: Architecture - {self.project_name}

## Status: Not Started
- **Started**: -
- **Progress**: 0%
- **Current Step**: -

## Objectives
- [ ] System Design
- [ ] Technology Selection
- [ ] API Design
- [ ] Database Schema

## Prerequisites
- Planning phase complete
- Requirements finalized

## Quality Gates
- Architecture review
- Technology validation
- Design approval

## Success Criteria
- Architecture documented
- Tech stack selected
- APIs defined

CUSTOMIZE THIS FILE with project-specific architecture goals.
"""

    def _get_implementation_phase(self):
        return f"""# Phase 03: Implementation - {self.project_name}

## Status: Not Started
- **Started**: -
- **Progress**: 0%
- **Current Step**: -

## Objectives
- [ ] Core Features
- [ ] API Implementation
- [ ] Database Setup
- [ ] Integration Points

## Prerequisites
- Architecture approved
- Development environment ready

## Quality Gates
- Code compilation
- Unit tests pass
- Code review
- Integration tests

## Success Criteria
- Features implemented
- Tests passing
- Code reviewed

CUSTOMIZE THIS FILE with specific implementation tasks.
"""

    def _get_testing_phase(self):
        return f"""# Phase 04: Testing - {self.project_name}

## Status: Not Started
- **Started**: -
- **Progress**: 0%
- **Current Step**: -

## Objectives
- [ ] Unit Testing
- [ ] Integration Testing
- [ ] Performance Testing
- [ ] User Acceptance Testing

## Prerequisites
- Implementation complete
- Test environment ready

## Quality Gates
- Test coverage >90%
- All tests passing
- Performance benchmarks met
- UAT sign-off

## Success Criteria
- Comprehensive test coverage
- No critical bugs
- Performance validated

CUSTOMIZE THIS FILE with testing requirements.
"""

    def _get_deployment_phase(self):
        return f"""# Phase 05: Deployment - {self.project_name}

## Status: Not Started
- **Started**: -
- **Progress**: 0%
- **Current Step**: -

## Objectives
- [ ] Production Setup
- [ ] Deployment Pipeline
- [ ] Monitoring Setup
- [ ] Documentation

## Prerequisites
- Testing complete
- Production access

## Quality Gates
- Deployment checklist
- Security review
- Performance validation
- Documentation complete

## Success Criteria
- Successfully deployed
- Monitoring active
- Documentation published

CUSTOMIZE THIS FILE with deployment specifics.
"""