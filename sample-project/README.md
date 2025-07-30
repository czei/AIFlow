# Disney Wait Times App - AI-Driven Sprint Development with Claude Code

This guide demonstrates how to use Claude Code's automated sprint-based development system to build a complete Disney Wait Times application. The AI will handle most of the implementation while following structured workflows and pausing for human input at key decision points.

## Project Overview

**Goal**: Build a cross-platform desktop app that:
- Fetches wait times from the Queue-Times.com API
- Displays wait times for all 4 Disney World parks
- Updates automatically every 10 minutes
- Provides a clean, sortable interface
- Runs as a standalone desktop application

**Technology Stack**:
- Backend: Python with FastAPI
- Frontend: Vue.js 3
- Desktop: Electron
- API: Queue-Times.com public API

## Quick Start - Your First Sprint

### 1. Set Up the Project with Workflow Hooks
```bash
# First, ensure you've run the installation script from the parent directory
cd /path/to/ai-software-project-management
./install.sh

# Navigate to the sample project
cd sample-project

# Create a .claude directory for project settings
mkdir -p .claude

# Create settings.json to enable the workflow hooks
cat > .claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": {
      "command": "python3 ${HOME}/.claude/commands/project/hooks/pre_tool_use.py",
      "timeout": 5000
    },
    "PostToolUse": {
      "command": "python3 ${HOME}/.claude/commands/project/hooks/post_tool_use.py",
      "timeout": 3000
    },
    "Stop": {
      "command": "python3 ${HOME}/.claude/commands/project/hooks/stop.py",
      "timeout": 3000
    }
  }
}
EOF

# Initialize git repository
git init
git add .
git commit -m "Initial commit with workflow hook configuration"
```

### 2. Start Claude Code in Your Project
```bash
# Start Claude in the sample-project directory
claude
```

### 3. Begin Your First Sprint
Once Claude is running, say:
```
Let's start building the Disney Wait Times app. Begin with Sprint 01 using the file sprints/01-design.md
```

Claude will:
1. Read the sprint objectives
2. Start creating design documents
3. Pause and ask for your input (you'll hear a beep)
4. Continue based on your feedback

## How This AI-Driven System Works

1. **Claude Code Hooks**: The system uses hooks that monitor Claude's actions and enforce the 6-step workflow
2. **Automated Implementation**: Claude handles coding, testing, and documentation
3. **Human Checkpoints**: You provide guidance at key decision points (🔔 sound alerts)
4. **Sprint Progression**: Each sprint builds on the previous, with clear handoffs

## Prerequisites

1. **Understanding the Setup**:
   - `ai-software-project-management/` is the FRAMEWORK that provides workflow tools
   - `sample-project/` is YOUR PROJECT where you'll build the Disney app
   - Hooks are installed globally to `~/.claude/commands/project/hooks/`
   - Each project references these hooks via `.claude/settings.json`

2. **Installation Required**:
   ```bash
   # Run this first from the framework directory
   cd /path/to/ai-software-project-management
   ./install.sh
   ```
   This installs:
   - Commands to `~/.claude/commands/project/`
   - Hooks to `~/.claude/commands/project/hooks/`
   - Python modules to `~/.claude/commands/project/lib/`

3. **Development Tools** (Claude will verify these):
   - Python 3.8+ with pip
   - Node.js 16+ with npm  
   - Git (required for workflow commits)
   - Claude Code CLI installed

4. **Project Structure After Setup**:
   ```
   ai-software-project-management/     <-- Framework source
   ├── src/                           <-- Source code
   ├── scripts/                       <-- Installation scripts
   └── sample-project/                <-- YOUR PROJECT
       ├── sprints/                   <-- Sprint definitions
       └── .claude/                   <-- Project settings (created in step 1)
           └── settings.json          <-- Hook configuration
   
   ~/.claude/commands/project/         <-- Installed framework
   ├── *.md                           <-- Command files
   ├── hooks/                         <-- Hook scripts
   └── lib/                           <-- Python modules
   ```

5. **Key Understanding**:
   - Start Claude in `sample-project/` (where you're developing)
   - The hooks are referenced from their installed location
   - Each project needs its own `.claude/settings.json` to enable hooks

## Working with Claude Code - Command Reference

### Key Commands You'll Use

1. **Start a Sprint**:
   ```
   /user:project:start . sprints/01-design.md
   ```
   This tells Claude to begin working on the specified sprint in the current project.

2. **Check Progress**:
   ```
   /user:project:status .
   ```
   Shows current sprint status and completion percentage.

3. **Update State** (when hooks pause execution):
   ```
   /user:project:update .
   ```
   Used after manual interventions or to sync state.

4. **Emergency Override** (if Claude gets stuck):
   ```
   EMERGENCY OVERRIDE: [your instruction]
   ```
   Bypasses workflow rules temporarily (you'll hear 3 beeps).

Note: Since Claude is running in the project directory, use `.` to refer to the current project.

## Sprint-by-Sprint Claude Interactions

### Sprint 01: Design and Planning

**YOU SAY:**
```
Start Sprint 01 for the Disney Wait Times app. The sprint file is at 
sprints/01-design.md. Please begin the design phase.
```

**CLAUDE WILL:**
1. Read the sprint file and understand objectives
2. Follow the 6-step workflow for each objective:
   - **Planning**: Analyze requirements (may ask you questions)
   - **Implementation**: Create design documents
   - **Validation**: Check completeness
   - **Review**: *[PAUSE - requests your review]*
   - **Refinement**: Update based on feedback
   - **Integration**: Finalize documents

**WHEN CLAUDE PAUSES** (you'll hear a beep):
- Review the created documents
- Provide feedback: "The requirements look good, but add a section about offline mode"
- Or approve: "Looks good, continue to the next objective"

**DELIVERABLES CLAUDE CREATES:**
- `docs/REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/mockups/`
- `docs/PROJECT_PLAN.md`

### Sprint 02: Architecture Implementation

**YOU SAY:**
```
Continue to Sprint 02. Please set up the project architecture and development environment.
```

**CLAUDE WILL:**
1. Create backend structure with FastAPI
2. Initialize Vue.js frontend
3. Set up Electron desktop wrapper
4. *[PAUSE - May ask about preferences]*: "Do you prefer TypeScript or JavaScript for the frontend?"

**YOUR RESPONSES DURING SPRINT:**
- "Use TypeScript for better type safety"
- "Yes, include hot-reload for development"
- When Claude pauses after setup: "Verified the servers are running. Continue."

**WHAT TO WATCH FOR:**
- Claude will automatically run validation commands
- You'll see test servers starting
- The hooks will enforce proper testing before moving on
- If something fails, Claude will retry or ask for help

### Sprint 03: Core Implementation

**YOU SAY:**
```
Let's move to Sprint 03. Implement the core functionality - API integration, 
scheduler, and wait times display.
```

**CLAUDE WILL:**
1. Implement Queue-Times API client with caching
2. *[PAUSE]*: "I need the API endpoints. Should I use the Disney World park IDs 5,6,7,8?"
3. Create the update scheduler
4. Build Vue components for display
5. Run integration tests
6. *[PAUSE after tests]*: "Integration tests passing. Ready for review."

**YOUR INTERACTIONS:**
- "Yes, use those park IDs for Magic Kingdom, EPCOT, Hollywood Studios, and Animal Kingdom"
- "The table looks good but make the wait times stand out more with color coding"
- "Add a loading spinner while fetching data"

**HOOK INTERVENTIONS YOU'LL SEE:**
- 🔔 "Validation required: Please verify API responses match expected format"
- 🔔 "Code review needed: Check the scheduler implementation"
- The system ensures each component is tested before integration

### Sprint 04: Testing and Quality Assurance

**YOU SAY:**
```
Proceed to Sprint 04. Let's ensure comprehensive test coverage and fix any issues.
```

**CLAUDE WILL:**
1. Generate unit tests for all components
2. Create integration test suite
3. Run performance benchmarks
4. *[PAUSE]*: "Found 3 issues during testing. Should I fix them now?"
5. Apply fixes and re-run tests
6. Generate test coverage report

**YOUR ROLE:**
- "Yes, fix the issues and show me the solutions"
- "Run the 4-hour stability test"
- "The performance looks good. What's the memory usage pattern?"

**AUTOMATED VALIDATIONS:**
- Claude must achieve >90% test coverage
- All tests must pass before marking sprint complete
- Performance benchmarks are automatically checked

### Sprint 05: Deployment and Release

**YOU SAY:**
```
Final sprint! Let's package the application and prepare for release.
```

**CLAUDE WILL:**
1. Create production builds
2. *[PAUSE]*: "Ready to create installers. Which platforms do you need?"
3. Generate platform-specific installers
4. Create user documentation with screenshots
5. *[PAUSE]*: "Installers created. Should I prepare the GitHub release?"

**YOUR FINAL INTERACTIONS:**
- "Create installers for macOS and Windows"
- "Test the macOS installer on a clean system"
- "Yes, create the release with version 1.0.0"
- "Add a note about the Queue-Times API attribution"

## Understanding the Workflow System

### The 6-Step Workflow (Enforced by Hooks)

Every objective follows these steps:

1. **Planning** - Claude analyzes requirements
2. **Implementation** - Claude writes code/docs
3. **Validation** - Automated tests run
4. **Review** - 🔔 PAUSE for human review
5. **Refinement** - Claude applies feedback
6. **Integration** - Changes are finalized and committed to git

### Git Integration

The workflow automatically creates commits at key points:
- After each objective completion
- When sprint milestones are reached
- Before transitioning to next sprint

You'll see messages like:
```
Claude: "Committing changes: 'Sprint 01: Completed requirements documentation'"
```

### Hook Notifications You'll Hear

- **1 beep** (🔔): Human input required
- **2 beeps** (🔔🔔): Workflow paused, awaiting approval
- **3 beeps** (🔔🔔🔔): Emergency override activated
- **Success chime** (🎵): Objective completed

### Common Interaction Patterns

**When Claude asks for clarification:**
```
Claude: "Should I implement real-time updates using WebSockets or SSE?"
You: "Use SSE for simplicity since it's one-way communication"
```

**When reviewing code:**
```
Claude: "API client implemented. Please review the error handling."
You: "Add retry logic for network timeouts"
```

**When approving progress:**
```
Claude: "Unit tests complete with 95% coverage. Ready to proceed?"
You: "Approved, continue to integration testing"
```

## Troubleshooting Claude Code Interactions

### When Claude Gets Stuck

**Symptom**: Claude keeps trying the same action repeatedly
```
You: "EMERGENCY OVERRIDE: Skip the current validation and move to the next objective"
```
(You'll hear 3 beeps confirming override mode)

**Symptom**: Hook blocks progress unnecessarily
```
You: "The validation passed manually. Update the project state to reflect this."
Then: "/user:project:update sample-project"
```

### Common Intervention Points

1. **Missing Dependencies**
   - Claude: "Cannot find module 'axios'"
   - You: "Run npm install in the frontend directory"

2. **API Changes**
   - Claude: "API returning unexpected format"
   - You: "Check the API docs at [URL] for updates"

3. **Test Failures**
   - Claude: "3 tests failing in scheduler"
   - You: "Show me the failing tests and let's debug together"

### Using Project Commands Effectively

**Check overall status:**
```
/user:project:status .
```

**Force state sync after manual changes:**
```
/user:project:update .
```

**View current sprint details:**
```
/user:project:current .
```

**Note**: The `.` refers to the current directory since Claude is running in your project.

## Project Structure

After completing all sprints, your project should have:

```
sample-project/
├── backend/
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app
│   ├── tests/            # Test files
│   └── requirements.txt  # Dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # Vue components
│   │   ├── views/        # Page views
│   │   └── main.ts       # Entry point
│   ├── tests/            # Test files
│   └── package.json      # Dependencies
├── desktop/
│   ├── main.js           # Electron main process
│   ├── preload.js        # Preload script
│   └── package.json      # Electron config
├── docs/
│   ├── sprints/          # Sprint documentation
│   ├── ARCHITECTURE.md   # System design
│   ├── REQUIREMENTS.md   # Project requirements
│   └── USER_GUIDE.md     # End-user documentation
└── installers/           # Built applications
```

## Next Steps

After completing all sprints:

1. **Maintenance Phase**:
   - Monitor for API changes
   - Address user feedback
   - Plan feature enhancements

2. **Enhancements to Consider**:
   - Add park filtering
   - Historical wait time graphs
   - Favorite rides feature
   - Push notifications for low wait times

3. **Scaling Options**:
   - Mobile app version
   - Web-based version
   - Additional theme parks

## Resources

- API Documentation: https://queue-times.com/en-US/pages/api
- Vue.js Guide: https://vuejs.org/guide/
- Electron Documentation: https://www.electronjs.org/docs
- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/

---

Remember: Each sprint builds on the previous one. Complete sprints sequentially and ensure all objectives are met before proceeding. The sprint files in the `sprints/` directory contain detailed automation instructions for Claude Code to help you implement each phase. 
