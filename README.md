# Claude Code Project Management Commands

This directory contains a complete set of Claude Code slash commands for managing phase-driven development projects with comprehensive quality assurance workflows.

## Installation

Run these commands in your terminal:

```bash
# Make the install script executable
chmod +x /Users/czei/claude-project-commands/install.sh

# Run the installation
/Users/czei/claude-project-commands/install.sh
```

Or manually copy the commands:

```bash
# Create the commands directory
mkdir -p ~/.claude/commands/project

# Copy all command files
cp -r /Users/czei/claude-project-commands/project/* ~/.claude/commands/project/
```

## Available Commands

After installation, these commands will be available in any Claude Code session:

- `/user:project:setup <project-name>` - Create new project worktree and structure
- `/user:project:doctor` - Validate project setup and workflow configuration
- `/user:project:start` - Begin automated phase-driven development
- `/user:project:status` - Show comprehensive project progress and workflow state
- `/user:project:pause` - Temporarily pause automation
- `/user:project:resume` - Resume automation from exact workflow position
- `/user:project:stop` - End project cleanly with quality summary
- `/user:project:update` - Update project state and objective completion
- `/user:project:advance [phase]` - Force advancement to next/specific phase
- `/user:project:phase <action>` - Manage phases (list, create, edit, jump)

## Quick Start

1. Navigate to an existing git repository
2. Run: `/user:project:setup my-awesome-project`
3. Customize the generated phase files for your specific project requirements
4. Review `docs/WORKFLOW_SPECIFICATIONS.md` for detailed workflow methodology
5. Run: `/user:project:doctor` to validate setup
6. Run: `/user:project:start` to begin automated development

## Core Workflow Methodology

The system implements a rigorous **6-step workflow** for every development objective:

1. **Planning** - Context review, task breakdown, risk assessment, approach design
2. **Implementation** - Production-quality code development following standards  
3. **Validation** - Compilation, testing (unit + integration), manual verification, performance check
4. **Review** - Self-review + zen methodology comprehensive code review
5. **Refinement** - Address feedback, re-test, optimize, resolve all issues
6. **Integration** - Final testing, documentation updates, clean commits, progress tracking

### Quality Gates

Each objective must pass these mandatory gates:
- ✅ **Compilation Gate** - Code builds without errors/warnings
- ✅ **Test Gate** - All tests pass + >90% coverage for new code  
- ✅ **Review Gate** - Code review completed with all issues resolved
- ✅ **Integration Gate** - Clean integration with existing system
- ✅ **Documentation Gate** - All changes properly documented
- ✅ **Performance Gate** - Meets established benchmarks

## Important Notes

- **Quality-First Approach**: Every change goes through comprehensive validation
- **Automated Testing**: Built-in unit and integration testing requirements
- **Code Review**: Mandatory zen methodology review for all code
- **Documentation**: Required documentation updates for all changes
- **Performance Validation**: Built-in performance benchmarking
- **Git Worktree Isolation**: Projects run in isolated environments for safety
- **State Persistence**: Complete workflow state tracking and resumability
- **Current Security Model**: Uses `--dangerously-skip-permissions` with git worktree isolation
- **Future Security Enhancement**: OPA-based command validation (see SECURITY_ARCHITECTURE.md)

## Architecture Overview

The system creates comprehensive project structure:
- **Git worktrees** for project isolation and safety
- **Phase-driven development** with detailed workflow specifications
- **Automated workflow** with Claude Code hooks and quality gates
- **Multi-layered state management** for resumable automation
- **Quality assurance** built into every development step

## Documentation

- **[HOOK_DOCUMENTATION.md](docs/HOOK_DOCUMENTATION.md)** - Complete hook system documentation
- **[HOOK_QUICK_REFERENCE.md](docs/HOOK_QUICK_REFERENCE.md)** - Quick reference for workflow phases
- **[PROJECT_STATE_SCHEMA.md](docs/PROJECT_STATE_SCHEMA.md)** - State file specification
- **[IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)** - Development roadmap
- **[FIX_COMMANDS_PLAN.md](docs/FIX_COMMANDS_PLAN.md)** - Command implementation details

## Project Structure Created

```
my-project/ (git worktree)
├── phases/
│   ├── 01-planning.md         (Requirements, architecture design)
│   ├── 02-architecture.md     (System design, technology selection)
│   ├── 03-implementation.md   (Feature development, coding)
│   ├── 04-testing.md         (Quality assurance, test coverage)
│   └── 05-deployment.md      (Production preparation)
├── .project-state.json        (Master project status)
├── .workflow-state.json       (Current workflow position)
├── .claude/
│   └── settings.json          (Automation hooks)
├── CLAUDE.md                  (Project context)
└── WORKFLOW_SPECIFICATIONS.md (Detailed methodology)
```

## Safety and Quality Features

- **Isolated Execution**: Git worktrees prevent impact to main repository
- **Comprehensive Validation**: Multiple quality gates prevent poor-quality advancement
- **State Persistence**: Complete workflow tracking enables pause/resume at any point
- **Audit Trail**: Full history of decisions, validations, and quality metrics
- **Manual Override**: Human control available at every step
- **Rollback Capability**: Git history enables return to any previous state

## Workflow Specifications

Each phase includes detailed workflow guidance:
- **Phase-specific variations** of the 6-step universal workflow
- **Quality gate definitions** with specific pass/fail criteria
- **Success criteria** with measurable validation requirements
- **Automation instructions** for Claude Code behavior
- **Progress tracking** with workflow step visibility

## Usage Scenarios

### Ideal For:
- **Feature Development** - Systematic implementation with built-in quality assurance
- **Refactoring Projects** - Quality-focused code improvement with comprehensive testing
- **Migration Work** - Step-by-step transitions with validation at every stage
- **Integration Projects** - Complex multi-system work with rigorous testing
- **Learning Projects** - Structured exploration with professional development practices

### Quality Benefits:
- **Consistent Standards** - Uniform development approach across projects
- **Technical Debt Prevention** - Built-in testing and review prevent accumulation
- **Knowledge Transfer** - Standardized workflow enables team consistency
- **Reliable Output** - Systematic validation ensures production-quality results

## Documentation

All documentation has been organized in the `docs/` directory:

- **docs/POC_SETUP_GUIDE.md** - Quick start guide for proof-of-concept testing
- **docs/PROJECT_DOCUMENTATION.md** - Comprehensive system overview and design
- **docs/WORKFLOW_SPECIFICATIONS.md** - Detailed 6-step methodology and phase variations
- **docs/PHASE_CREATION_INSTRUCTIONS.md** - AI instructions for creating effective phase files
- **docs/SECURITY_ARCHITECTURE.md** - Future OPA-based security implementation
- **docs/LOGGING_ARCHITECTURE.md** - Comprehensive logging and debugging infrastructure
- **docs/TESTING.md** - Comprehensive testing framework documentation
- **docs/SECURITY_FIXES_SUMMARY.md** - Summary of security improvements
- **docs/example-detailed-phase.md** - Template showing workflow integration in phase files
- **docs/phase-template-with-state.md** - State tracking and progress management examples

## Prerequisites

- Claude Code installed and configured
- Git repository for development work
- Understanding of `--dangerously-skip-permissions` risks (current security model)
- Commitment to following structured development methodology
- **Note**: Future versions will eliminate `--dangerously-skip-permissions` through OPA integration

## Support and Customization

The system is highly customizable:
- **Phase definitions** can be adapted to any project type
- **Quality gates** can be adjusted for project requirements
- **Workflow steps** can be modified for specific technologies
- **Automation behavior** can be fine-tuned through phase instructions

This comprehensive framework transforms Claude Code into a disciplined development partner that maintains professional quality standards while providing the automation benefits needed for complex, long-running projects.
