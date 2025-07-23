# Comprehensive Logging for Phase-Driven Development

The automation system generates detailed logs at multiple levels to enable effective debugging and monitoring of the development process.

## Logging Architecture

### Log Files Structure
```
project-directory/
├── .logs/
│   ├── automation.log          # Main automation events and decisions
│   ├── workflow.log             # 6-step workflow progress and state changes  
│   ├── commands.log             # All commands executed with results
│   ├── quality-gates.log        # Quality gate evaluations and results
│   ├── phase-transitions.log    # Phase advancement and validation
│   ├── errors.log              # Error conditions and recovery actions
│   └── performance.log         # Timing and performance metrics
├── .project-state.json
├── .workflow-state.json
└── phases/
```

## Log Format Standards

### Standard Log Entry Format
```json
{
  "timestamp": "2025-07-21T15:30:45.123Z",
  "level": "INFO|DEBUG|WARNING|ERROR",
  "category": "automation|workflow|command|quality|phase|error|performance",
  "phase": "03-implementation",
  "workflow_step": "validate",
  "objective": "Business logic API endpoints",
  "event": "quality_gate_evaluation",
  "details": {
    "gate_type": "compilation",
    "status": "passed",
    "duration_ms": 1250,
    "additional_context": {...}
  },
  "correlation_id": "uuid-for-tracking-related-events"
}
```

### Correlation IDs
Each automation cycle gets a unique correlation ID to track all related log entries across different log files. This enables reconstructing the complete timeline of any specific workflow execution.

## Logging Implementation

### Enhanced Command Execution with Logging
```python
#!/usr/bin/env python3
# enhanced_secure_shell.py (with comprehensive logging)

import subprocess
import json
import sys
import shlex
import os
import time
import uuid
import logging
from pathlib import Path
from datetime import datetime

class EnhancedLogger:
    def __init__(self, project_dir="/app/workdir"):
        self.project_dir = Path(project_dir)
        self.logs_dir = self.project_dir / ".logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup correlation ID for this execution
        self.correlation_id = str(uuid.uuid4())
        
        # Setup multiple loggers
        self.setup_loggers()
        
    def setup_loggers(self):
        """Configure separate loggers for different categories"""
        self.loggers = {}
        
        categories = [
            'automation', 'workflow', 'commands', 
            'quality-gates', 'phase-transitions', 'errors', 'performance'
        ]
        
        for category in categories:
            logger = logging.getLogger(f'pdds.{category}')
            logger.setLevel(logging.DEBUG)
            
            # File handler
            handler = logging.FileHandler(
                self.logs_dir / f'{category}.log',
                mode='a',
                encoding='utf-8'
            )
            
            # JSON formatter for structured logs
            handler.setFormatter(JsonFormatter())
            logger.addHandler(handler)
            
            # Console handler for real-time monitoring
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            self.loggers[category] = logger
    
    def log_event(self, category, level, event, details=None, **kwargs):
        """Log structured event with full context"""
        if category not in self.loggers:
            category = 'automation'
            
        # Load current project state for context
        try:
            with open(self.project_dir / '.project-state.json', 'r') as f:
                project_state = json.load(f)
        except:
            project_state = {}
            
        # Build log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "category": category,
            "phase": project_state.get("current_phase", "unknown"),
            "workflow_step": project_state.get("workflow_step", "unknown"),
            "objective": project_state.get("current_objective", "unknown"),
            "event": event,
            "correlation_id": self.correlation_id,
            "details": details or {},
            **kwargs
        }
        
        # Log as JSON
        logger = self.loggers[category]
        logger.log(getattr(logging, level), json.dumps(log_entry, indent=None))

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return record.getMessage()

class SecureShell:
    def __init__(self):
        self.workdir = "/app/workdir"
        self.state_file = os.path.join(self.workdir, ".project-state.json")
        self.logger = EnhancedLogger(self.workdir)
        
        # Log shell initialization
        self.logger.log_event(
            'automation', 'INFO', 'secure_shell_initialized',
            {
                'workdir': self.workdir,
                'pid': os.getpid(),
                'command_args': sys.argv
            }
        )
        
    def load_project_state(self):
        """Load project state with detailed logging"""
        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
                
            self.logger.log_event(
                'automation', 'DEBUG', 'project_state_loaded',
                {
                    'state_file': self.state_file,
                    'current_phase': state.get('current_phase'),
                    'workflow_step': state.get('workflow_step'),
                    'automation_active': state.get('automation_active')
                }
            )
            return state
            
        except FileNotFoundError:
            self.logger.log_event(
                'errors', 'WARNING', 'state_file_not_found',
                {'state_file': self.state_file}
            )
            return {"workflow_step": "planning"}
            
        except json.JSONDecodeError as e:
            self.logger.log_event(
                'errors', 'ERROR', 'invalid_state_file',
                {
                    'state_file': self.state_file,
                    'error': str(e),
                    'recovery_action': 'defaulting_to_planning'
                }
            )
            return {"workflow_step": "planning"}
    
    def validate_command_phase(self, command, args, phase):
        """Basic phase-appropriate command validation with logging"""
        start_time = time.time()
        
        # Simple phase-based validation rules
        allowed_commands = {
            "planning": ["cat", "ls", "find", "grep", "git"],
            "implementation": ["cat", "ls", "git", "touch", "mkdir", "cp", "mv", "python", "npm", "node"],
            "validation": ["npm", "pytest", "make", "git", "python"],
            "review": ["git", "cat", "ls"],
            "refine": ["cat", "ls", "git", "touch", "cp", "mv", "python", "npm"],
            "integration": ["git", "cat", "ls", "cp", "mv"]
        }
        
        # Check if command is allowed in current phase
        phase_commands = allowed_commands.get(phase, [])
        is_allowed = command in phase_commands
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Log validation decision
        self.logger.log_event(
            'quality-gates', 'INFO', 'command_phase_validation',
            {
                'command': command,
                'args': args[:5],  # Limit arg logging for privacy
                'phase': phase,
                'allowed_commands': phase_commands,
                'validation_result': 'allowed' if is_allowed else 'denied',
                'duration_ms': round(duration_ms, 2)
            }
        )
        
        return is_allowed
    
    def execute_command(self, command_parts):
        """Execute command with comprehensive logging"""
        start_time = time.time()
        command_str = ' '.join(command_parts)
        
        self.logger.log_event(
            'commands', 'INFO', 'command_execution_start',
            {
                'command': command_parts[0],
                'full_command': command_str,
                'args_count': len(command_parts) - 1,
                'cwd': self.workdir
            }
        )
        
        try:
            # Execute command with output capture for logging
            result = subprocess.run(
                command_parts,
                cwd=self.workdir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Log execution results
            self.logger.log_event(
                'commands', 'INFO' if result.returncode == 0 else 'WARNING',
                'command_execution_complete',
                {
                    'command': command_parts[0],
                    'exit_code': result.returncode,
                    'duration_ms': round(duration_ms, 2),
                    'stdout_lines': len(result.stdout.splitlines()) if result.stdout else 0,
                    'stderr_lines': len(result.stderr.splitlines()) if result.stderr else 0,
                    'stdout_preview': result.stdout[:200] if result.stdout else None,
                    'stderr_preview': result.stderr[:200] if result.stderr else None
                }
            )
            
            # Log performance metrics
            self.logger.log_event(
                'performance', 'DEBUG', 'command_performance',
                {
                    'command': command_parts[0],
                    'duration_ms': round(duration_ms, 2),
                    'success': result.returncode == 0,
                    'output_size_bytes': len(result.stdout) + len(result.stderr)
                }
            )
            
            # Print output for user (don't capture it)
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='', file=sys.stderr)
                
            return result.returncode
            
        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_event(
                'errors', 'ERROR', 'command_timeout',
                {
                    'command': command_parts[0],
                    'timeout_seconds': 300,
                    'duration_ms': round(duration_ms, 2)
                }
            )
            return 124
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_event(
                'errors', 'ERROR', 'command_execution_error',
                {
                    'command': command_parts[0],
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'duration_ms': round(duration_ms, 2)
                }
            )
            return 1
    
    def main(self):
        if len(sys.argv) < 2:
            self.logger.log_event(
                'errors', 'ERROR', 'invalid_usage',
                {'message': 'No command provided'}
            )
            print("Usage: secure_shell <command>", file=sys.stderr)
            return 1
            
        full_command_str = " ".join(sys.argv[1:])
        
        # Parse command safely
        try:
            command_parts = shlex.split(full_command_str)
        except ValueError as e:
            self.logger.log_event(
                'errors', 'ERROR', 'command_parse_error',
                {
                    'command_string': full_command_str,
                    'error': str(e)
                }
            )
            return 1
        
        if not command_parts:
            self.logger.log_event(
                'errors', 'ERROR', 'empty_command',
                {'command_string': full_command_str}
            )
            return 1
            
        command = command_parts[0]
        args = command_parts[1:]
        
        # Load project state
        project_state = self.load_project_state()
        phase = project_state.get("workflow_step", "planning")
        
        self.logger.log_event(
            'workflow', 'INFO', 'command_validation_start',
            {
                'command': command,
                'phase': phase,
                'args_count': len(args)
            }
        )
        
        # Validate command against phase
        if self.validate_command_phase(command, args, phase):
            self.logger.log_event(
                'automation', 'INFO', 'command_approved',
                {
                    'command': command,
                    'phase': phase,
                    'validation_method': 'phase_based'
                }
            )
            return self.execute_command(command_parts)
        else:
            self.logger.log_event(
                'automation', 'WARNING', 'command_blocked',
                {
                    'command': command,
                    'phase': phase,
                    'reason': 'not_allowed_in_current_phase'
                }
            )
            print(f"❌ Command '{command}' blocked: not allowed in {phase} phase")
            return 1

if __name__ == "__main__":
    shell = SecureShell()
    exit_code = shell.main()
    
    # Log session completion
    shell.logger.log_event(
        'automation', 'INFO', 'secure_shell_session_complete',
        {'exit_code': exit_code}
    )
    
    sys.exit(exit_code)
```

## Log Analysis and Monitoring

### Real-Time Log Monitoring
```bash
# Monitor all automation activity
tail -f .logs/automation.log | jq .

# Monitor specific workflow steps
tail -f .logs/workflow.log | jq 'select(.workflow_step == "validate")'

# Monitor command executions
tail -f .logs/commands.log | jq 'select(.details.exit_code != 0)'

# Monitor errors
tail -f .logs/errors.log | jq .
```

### Log Analysis Scripts
```bash
# Analyze workflow performance
jq -s 'group_by(.event) | map({event: .[0].event, count: length, avg_duration: (map(.details.duration_ms) | add / length)})' .logs/performance.log

# Find failed commands
jq 'select(.details.exit_code != 0)' .logs/commands.log

# Track phase transitions
jq 'select(.event == "phase_transition")' .logs/phase-transitions.log

# Correlation analysis - find all events for a specific correlation ID
grep "uuid-from-logs" .logs/*.log | jq .
```

### Debug Scenarios

**Scenario 1: Automation Stopped Unexpectedly**
```bash
# Check last automation events
tail -20 .logs/automation.log | jq .

# Check for errors around that time  
grep -A5 -B5 "$(date -d '10 minutes ago' '+%Y-%m-%dT%H:%M')" .logs/errors.log
```

**Scenario 2: Quality Gate Failing**
```bash
# Check quality gate evaluations
jq 'select(.event == "quality_gate_evaluation")' .logs/quality-gates.log | tail -10

# Check related command executions
jq 'select(.details.exit_code != 0)' .logs/commands.log | tail -5
```

**Scenario 3: Performance Issues**
```bash
# Find slowest operations
jq 'select(.details.duration_ms > 5000)' .logs/performance.log | sort_by(.details.duration_ms)

# Command execution time trends
jq -r '[.timestamp, .details.command, .details.duration_ms] | @csv' .logs/performance.log
```

## Integration with Phase-Driven Commands

### Enhanced Status Command
```markdown
<!-- Enhanced /user:project:status with logging -->
The status command now includes log analysis:

Recent Activity (from logs):
  - 15:45: Command approved: git status (validation phase, 45ms)
  - 15:44: Quality gate passed: compilation (1,234ms)
  - 15:43: Workflow step transition: implement → validate
  - 15:42: Command execution: npm test (exit_code: 0, 12,456ms)

Error Summary (last hour):
  - 0 critical errors
  - 2 command validation warnings
  - 1 timeout (npm test took 5.2 minutes)

Performance Metrics:
  - Average command execution time: 2.3 seconds
  - Quality gate success rate: 94% (47 of 50)
  - Workflow step completion rate: 89% (8 of 9 steps)
```

This comprehensive logging infrastructure provides the debugging capability you need to understand exactly what the automation system is doing at each step, enabling effective troubleshooting and optimization.
