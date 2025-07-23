# NPM Packaging Plan for AI Software Project Management System

## Executive Summary

Based on consensus analysis from multiple AI models, the recommendation is to keep the Python implementation while creating an npm distribution layer. This provides the ease of installation that Claude Code users expect (`npm install -g @anthropic-ai/claude-pm`) without requiring a costly rewrite of working code.

## Background

The AI Software Project Management System is currently implemented in Python with:
- Core logic in Python (state_manager.py, hooks/*.py)
- Commands as markdown files with YAML frontmatter
- Installation via bash script copying files to ~/.claude/commands/
- No package manager integration

Since Claude Code itself is distributed via npm (`@anthropic-ai/claude-code`), users reasonably expect extensions to follow the same pattern.

## Consensus Findings

### Key Points of Agreement:
1. **No Complete Rewrite** - Rewriting existing Python code for npm distribution alone is wasteful
2. **Distribution is the Real Issue** - This is a packaging problem, not a language problem
3. **Hybrid Approaches Have Merit** - Python core + Node.js distribution is viable
4. **Alternative Methods Exist** - Docker, pip, and other options were considered

### Why Not Full Node.js Rewrite:
- Significant effort for minimal benefit
- Python excels at file operations and subprocess management
- Current implementation is tested and working
- Would create maintenance burden without adding value

### Why Not Docker/pip:
- Claude Code users already have npm
- Docker adds complexity for a simple tool
- pip requires Python knowledge that users may lack
- npm provides the most frictionless experience

## Recommended Solution

Create an npm package that wraps and distributes the Python implementation.

### Package Structure

```
@anthropic-ai/claude-pm/
├── package.json              # npm package manifest
├── README.md                 # npm-specific documentation
├── LICENSE                   # MIT license
├── bin/
│   └── claude-pm.js         # CLI entry point
├── lib/
│   ├── installer.js         # Handles Python script installation
│   ├── updater.js           # Version management
│   ├── python-check.js      # Python availability checker
│   └── paths.js             # Cross-platform path handling
├── scripts/
│   ├── setup.js             # Post-install setup
│   └── test.js              # Installation verification
└── python/                   # Bundled Python implementation
    ├── src/                  # All Python source files
    ├── project/              # Command markdown files
    └── docs/                 # Documentation
```

### package.json Configuration

```json
{
  "name": "@anthropic-ai/claude-pm",
  "version": "1.0.0",
  "description": "AI Software Project Management System for Claude Code",
  "keywords": ["claude-code", "ai", "project-management", "workflow", "automation"],
  "homepage": "https://github.com/anthropics/claude-pm",
  "bugs": {
    "url": "https://github.com/anthropics/claude-pm/issues"
  },
  "license": "MIT",
  "author": "Anthropic",
  "main": "lib/index.js",
  "bin": {
    "claude-pm": "./bin/claude-pm.js"
  },
  "files": [
    "bin/",
    "lib/",
    "python/",
    "scripts/"
  ],
  "scripts": {
    "postinstall": "node scripts/setup.js",
    "test": "node scripts/test.js",
    "update": "npm update && node scripts/setup.js"
  },
  "engines": {
    "node": ">=14.0.0"
  },
  "dependencies": {
    "chalk": "^4.1.2",
    "commander": "^9.0.0",
    "fs-extra": "^11.0.0",
    "semver": "^7.3.8",
    "which": "^3.0.0"
  },
  "devDependencies": {
    "@types/node": "^18.0.0",
    "eslint": "^8.0.0"
  }
}
```

### Implementation Details

#### 1. CLI Entry Point (bin/claude-pm.js)

```javascript
#!/usr/bin/env node
const { program } = require('commander');
const { version } = require('../package.json');
const { checkPython, installCommands, updateCommands } = require('../lib');

program
  .version(version)
  .description('AI Software Project Management for Claude Code');

program
  .command('install')
  .description('Install Claude PM commands')
  .action(installCommands);

program
  .command('update')
  .description('Update Claude PM to latest version')
  .action(updateCommands);

program
  .command('doctor')
  .description('Check installation health')
  .action(checkHealth);

program.parse();
```

#### 2. Post-Install Setup (scripts/setup.js)

```javascript
const { checkPython, installCommands } = require('../lib');

async function setup() {
  console.log('Setting up Claude PM...');
  
  // Check Python availability
  const pythonInfo = await checkPython();
  if (!pythonInfo.available) {
    console.error('Python 3 is required but not found.');
    console.error('Please install Python 3.6+ from https://python.org');
    process.exit(1);
  }
  
  // Install commands to ~/.claude/commands/
  await installCommands();
  
  console.log('✅ Claude PM installed successfully!');
  console.log('Commands are now available in Claude Code.');
}

setup().catch(console.error);
```

#### 3. Python Checker (lib/python-check.js)

```javascript
const which = require('which');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

async function checkPython() {
  const candidates = ['python3', 'python'];
  
  for (const cmd of candidates) {
    try {
      const path = await which(cmd);
      const { stdout } = await execAsync(`${cmd} --version`);
      const version = stdout.match(/Python (\d+\.\d+\.\d+)/)?.[1];
      
      if (version && version >= '3.6.0') {
        return {
          available: true,
          command: cmd,
          path,
          version
        };
      }
    } catch (e) {
      // Try next candidate
    }
  }
  
  return { available: false };
}
```

## Implementation Sprints

### Sprint 1: Basic npm Package (Week 1)
- Create package structure
- Implement basic installer copying Python files
- Test on Mac/Linux
- Publish to npm as beta

### Sprint 2: Enhanced Features (Week 2)
- Add Windows support
- Implement update mechanism
- Add health check command
- Improve error messages

### Sprint 3: Polish & Release (Week 3)
- Add progress indicators
- Create migration guide from bash install
- Update main documentation
- Official release

## User Experience

### Installation
```bash
# Simple one-line install
npm install -g @anthropic-ai/claude-pm

# Verify installation
claude-pm doctor
```

### Usage
After installation, all commands are available in Claude Code:
- `/user:project:setup <name>`
- `/user:project:start`
- `/user:project:status`
- etc.

### Updates
```bash
# Check for updates
npm outdated -g @anthropic-ai/claude-pm

# Update to latest
npm update -g @anthropic-ai/claude-pm
```

## Risk Mitigation

### Risk 1: Python Not Installed
**Mitigation:**
- Clear error message with installation link
- Future: Consider bundling minimal Python runtime
- Document Python requirement prominently

### Risk 2: File Permission Issues
**Mitigation:**
- Use user's home directory only
- Check permissions before writing
- Provide fix instructions if needed

### Risk 3: Windows Path Issues
**Mitigation:**
- Use Node's path.join() everywhere
- Test extensively on Windows
- Handle both forward and back slashes

### Risk 4: Version Conflicts
**Mitigation:**
- Embed version in Python files
- Check compatibility on update
- Support rollback if needed

## Success Metrics

1. **Installation Success Rate**: >95% of npm installs should succeed
2. **Python Detection**: Successfully detect Python on >90% of developer machines
3. **Cross-Platform**: Works on Windows, Mac, Linux
4. **Update Adoption**: >80% of users on latest version within 30 days
5. **User Satisfaction**: Positive feedback on ease of installation

## Alternative Approaches Considered

1. **Full Node.js Rewrite**: Rejected due to high cost and working Python code
2. **Docker Distribution**: Too heavy for a simple tool
3. **pip Package**: Doesn't align with Claude Code ecosystem
4. **Git Submodule**: Too manual for users
5. **Standalone Executable**: Complex cross-platform building

## Conclusion

The npm wrapper approach provides the best balance of:
- User convenience (one-line npm install)
- Developer efficiency (no rewrite needed)
- Ecosystem alignment (consistent with Claude Code)
- Future flexibility (can evolve over time)

This solution directly addresses the user's installation concerns while preserving the existing, working Python implementation.