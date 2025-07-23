#!/usr/bin/env python3
"""
Basic logging infrastructure for phase-driven development proof of concept.
Provides comprehensive logging without external dependencies for easy integration.
"""

import subprocess
import json
import sys
import shlex
import os
import time
import uuid
from pathlib import Path
from datetime import datetime, timezone

class BasicLogger:
    """Simple but comprehensive logging for automation debugging"""
    
    def __init__(self, project_dir=".", correlation_id=None):
        self.project_dir = Path(project_dir)
        self.logs_dir = self.project_dir / ".logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Correlation ID for tracking related events
        self.correlation_id = correlation_id or str(uuid.uuid4())
        
        # Initialize log files
        self.log_files = {
            'automation': self.logs_dir / 'automation.log',
            'workflow': self.logs_dir / 'workflow.log', 
            'commands': self.logs_dir / 'commands.log',
            'quality-gates': self.logs_dir / 'quality-gates.log',
            'phase-transitions': self.logs_dir / 'phase-transitions.log',
            'errors': self.logs_dir / 'errors.log',
            'performance': self.logs_dir / 'performance.log'
        }
        
        # Log logger initialization
        self.log_event('automation', 'INFO', 'logger_initialized', {
            'project_dir': str(self.project_dir),
            'correlation_id': self.correlation_id,
            'log_files_created': list(self.log_files.keys())
        })
    
    def log_event(self, category, level, event, details=None, **kwargs):
        """Log structured event with full context"""
        
        # Load current project state for context
        try:
            state_file = self.project_dir / '.project-state.json'
            with open(state_file, 'r') as f:
                project_state = json.load(f)
        except:
            project_state = {}
            
        # Build structured log entry
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "category": category,
            "correlation_id": self.correlation_id,
            "phase": project_state.get("current_sprint", "unknown"),
            "workflow_step": project_state.get("workflow_step", "unknown"), 
            "objective": project_state.get("current_objective", "unknown"),
            "event": event,
            "details": details or {},
            **kwargs
        }
        
        # Write to appropriate log file
        log_file = self.log_files.get(category, self.log_files['automation'])
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, separators=(',', ':')) + '\n')
            
        # Also write to console for immediate feedback
        console_msg = f"[{level}] {category}: {event}"
        if details:
            console_msg += f" - {json.dumps(details, separators=(',', ':'))}"
        print(console_msg, file=sys.stderr)

class LoggedSecureShell:
    """Secure shell with comprehensive logging for PoC"""
    
    def __init__(self, project_dir="."):
        self.workdir = project_dir
        self.state_file = Path(project_dir) / ".project-state.json"
        
        # Initialize logger
        self.logger = BasicLogger(project_dir)
        
        # Log shell initialization  
        self.logger.log_event('automation', 'INFO', 'secure_shell_initialized', {
            'workdir': self.workdir,
            'pid': os.getpid(),
            'command_args': sys.argv
        })
        
    def load_project_state(self):
        """Load project state with detailed logging"""
        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
                
            self.logger.log_event('automation', 'DEBUG', 'project_state_loaded', {
                'state_file': str(self.state_file),
                'current_sprint': state.get('current_sprint'),
                'workflow_step': state.get('workflow_step'),
                'automation_active': state.get('automation_active')
            })
            return state
            
        except FileNotFoundError:
            self.logger.log_event('errors', 'WARNING', 'state_file_not_found', {
                'state_file': str(self.state_file),
                'recovery_action': 'defaulting_to_planning'
            })
            return {"workflow_step": "planning"}
            
        except json.JSONDecodeError as e:
            self.logger.log_event('errors', 'ERROR', 'invalid_state_file', {
                'state_file': str(self.state_file),
                'error': str(e),
                'recovery_action': 'defaulting_to_planning'
            })
            return {"workflow_step": "planning"}
    
    def validate_command_phase(self, command, args, phase):
        """Basic phase validation with comprehensive logging"""
        start_time = time.time()
        
        # Simple phase-based validation (expanded for PoC)
        allowed_commands = {
            "planning": ["cat", "ls", "find", "grep", "git", "head", "tail", "wc", "sort"],
            "implementation": [
                "cat", "ls", "git", "touch", "mkdir", "cp", "mv", "rm", 
                "python", "python3", "npm", "node", "pip", "make", "echo", "tee"
            ],
            "validation": [
                "npm", "pytest", "python", "python3", "make", "git", 
                "node", "jest", "test", "coverage"
            ],
            "review": ["git", "cat", "ls", "head", "tail", "diff", "grep"],
            "refine": [
                "cat", "ls", "git", "touch", "cp", "mv", "python", "python3",
                "npm", "sed", "awk", "sort"
            ],
            "integration": ["git", "cat", "ls", "cp", "mv", "make", "npm"]
        }
        
        phase_commands = allowed_commands.get(phase, [])
        is_allowed = command in phase_commands
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Log validation decision with full context
        self.logger.log_event('quality-gates', 'INFO', 'command_phase_validation', {
            'command': command,
            'args_preview': args[:3] + (['...'] if len(args) > 3 else []),
            'args_count': len(args),
            'phase': phase,
            'allowed_commands': phase_commands,
            'validation_result': 'ALLOWED' if is_allowed else 'DENIED',
            'duration_ms': round(duration_ms, 2),
            'reason': f"Command {'is' if is_allowed else 'is not'} in {phase} allowlist"
        })
        
        return is_allowed
    
    def execute_command(self, command_parts):
        """Execute command with comprehensive logging and error handling"""
        start_time = time.time()
        command_str = ' '.join(command_parts)
        
        self.logger.log_event('commands', 'INFO', 'command_execution_start', {
            'command': command_parts[0],
            'full_command': command_str,
            'args_count': len(command_parts) - 1,
            'cwd': self.workdir,
            'start_time': datetime.now(timezone.utc).isoformat()
        })
        
        try:
            # Execute with timeout and capture
            result = subprocess.run(
                command_parts,
                cwd=self.workdir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                input=""  # Prevent hanging on interactive prompts
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Determine log level based on exit code
            log_level = 'INFO' if result.returncode == 0 else 'WARNING'
            
            # Log execution results with comprehensive details
            self.logger.log_event('commands', log_level, 'command_execution_complete', {
                'command': command_parts[0],
                'exit_code': result.returncode,
                'duration_ms': round(duration_ms, 2),
                'stdout_lines': len(result.stdout.splitlines()) if result.stdout else 0,
                'stderr_lines': len(result.stderr.splitlines()) if result.stderr else 0,
                'stdout_size': len(result.stdout) if result.stdout else 0,
                'stderr_size': len(result.stderr) if result.stderr else 0,
                'stdout_preview': result.stdout[:300] + ('...' if len(result.stdout) > 300 else '') if result.stdout else None,
                'stderr_preview': result.stderr[:300] + ('...' if len(result.stderr) > 300 else '') if result.stderr else None,
                'success': result.returncode == 0
            })
            
            # Log performance metrics separately
            self.logger.log_event('performance', 'DEBUG', 'command_performance', {
                'command': command_parts[0],
                'duration_ms': round(duration_ms, 2),
                'success': result.returncode == 0,
                'output_size_bytes': len(result.stdout) + len(result.stderr),
                'cpu_intensive': duration_ms > 5000,  # Flag slow commands
                'memory_intensive': len(result.stdout) + len(result.stderr) > 100000  # Flag large output
            })
            
            # Print output for user visibility
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='', file=sys.stderr)
                
            return result.returncode
            
        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_event('errors', 'ERROR', 'command_timeout', {
                'command': command_parts[0],
                'timeout_seconds': 300,
                'duration_ms': round(duration_ms, 2),
                'impact': 'high',
                'recommended_action': 'investigate_long_running_process'
            })
            
            print(f"❌ Command timed out after 5 minutes: {command_str}", file=sys.stderr)
            return 124  # Standard timeout exit code
            
        except FileNotFoundError:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_event('errors', 'ERROR', 'command_not_found', {
                'command': command_parts[0],
                'duration_ms': round(duration_ms, 2),
                'path': os.environ.get('PATH', ''),
                'recommended_action': 'check_command_installation'
            })
            
            print(f"❌ Command not found: {command_parts[0]}", file=sys.stderr)
            return 127  # Command not found exit code
            
        except PermissionError:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_event('errors', 'ERROR', 'permission_denied', {
                'command': command_parts[0],
                'duration_ms': round(duration_ms, 2),
                'cwd': self.workdir,
                'recommended_action': 'check_file_permissions'
            })
            
            print(f"❌ Permission denied: {command_str}", file=sys.stderr)
            return 126  # Permission denied exit code
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_event('errors', 'ERROR', 'command_execution_error', {
                'command': command_parts[0],
                'error_type': type(e).__name__,
                'error_message': str(e),
                'duration_ms': round(duration_ms, 2),
                'unexpected': True,
                'recommended_action': 'investigate_system_issue'
            })
            
            print(f"🚨 Unexpected error executing {command_str}: {e}", file=sys.stderr)
            return 1
    
    def main(self):
        """Main execution with comprehensive logging"""
        
        if len(sys.argv) < 2:
            self.logger.log_event('errors', 'ERROR', 'invalid_usage', {
                'message': 'No command provided',
                'usage': 'logged_secure_shell <command>',
                'args_received': sys.argv
            })
            print("Usage: logged_secure_shell <command>", file=sys.stderr)
            return 1
            
        full_command_str = " ".join(sys.argv[1:])
        
        # Parse command with error handling
        try:
            command_parts = shlex.split(full_command_str)
        except ValueError as e:
            self.logger.log_event('errors', 'ERROR', 'command_parse_error', {
                'command_string': full_command_str,
                'error': str(e),
                'recommended_action': 'check_quote_balancing'
            })
            print(f"❌ Invalid command string: {e}", file=sys.stderr)
            return 1
        
        if not command_parts:
            self.logger.log_event('errors', 'ERROR', 'empty_command', {
                'command_string': full_command_str
            })
            print("❌ Empty command provided", file=sys.stderr)
            return 1
            
        command = command_parts[0]
        args = command_parts[1:]
        
        # Load and validate project state
        project_state = self.load_project_state()
        phase = project_state.get("workflow_step", "planning")
        
        self.logger.log_event('workflow', 'INFO', 'command_validation_start', {
            'command': command,
            'phase': phase,
            'args_count': len(args),
            'project_active': project_state.get('automation_active', False)
        })
        
        # Validate command against current phase
        if self.validate_command_phase(command, args, phase):
            self.logger.log_event('automation', 'INFO', 'command_approved', {
                'command': command,
                'phase': phase,
                'validation_method': 'phase_based_allowlist',
                'next_action': 'execute_command'
            })
            
            exit_code = self.execute_command(command_parts)
            
            # Log final outcome
            self.logger.log_event('automation', 'INFO', 'command_session_complete', {
                'command': command,
                'exit_code': exit_code,
                'success': exit_code == 0
            })
            
            return exit_code
            
        else:
            self.logger.log_event('automation', 'WARNING', 'command_blocked', {
                'command': command,
                'phase': phase,
                'reason': 'command_not_allowed_in_current_phase',
                'recommended_action': 'check_phase_progression_or_use_different_command'
            })
            
            print(f"❌ Command '{command}' blocked: not allowed in {phase} phase", file=sys.stderr)
            return 1

if __name__ == "__main__":
    # Determine project directory (current directory or from environment)
    project_dir = os.environ.get('PROJECT_DIR', '.')
    
    # Initialize and run logged shell
    shell = LoggedSecureShell(project_dir)
    exit_code = shell.main()
    
    # Log session completion
    shell.logger.log_event('automation', 'INFO', 'secure_shell_session_end', {
        'exit_code': exit_code,
        'total_correlation_events': 'see_correlation_id_for_full_session'
    })
    
    sys.exit(exit_code)
