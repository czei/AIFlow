# Enhanced Security Architecture for Claude Code Sprint-Driven Development

## Layer 1: Docker Sandbox (Foundation)

```dockerfile
FROM python:3.11-slim

# Install essential development tools
RUN apt-get update && apt-get install -y \
    git \
    nodejs \
    npm \
    make \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install requests

# Install OPA
RUN curl -L -o opa https://openpolicyagent.org/downloads/v0.58.0/opa_linux_amd64_static \
    && chmod +x opa \
    && mv opa /usr/local/bin/

# Create application structure
RUN mkdir -p /app/policy /app/workdir /app/bin

# Copy security infrastructure
COPY secure_shell.py /app/bin/
COPY security_policy.rego /app/policy/
COPY safe_commands/ /app/bin/safe_commands/

# Make secure_shell accessible
RUN ln -s /app/bin/secure_shell.py /usr/local/bin/secure_shell
RUN chmod +x /app/bin/secure_shell.py

# Set working directory
WORKDIR /app/workdir

# Network security: limit outbound connections
# (Requires docker run with --network=custom_network)

# Start OPA server and keep container running
CMD ["sh", "-c", "opa run --server --addr=0.0.0.0:8181 /app/policy/ & tail -f /dev/null"]
```

## Layer 2: Enhanced OPA Policy Engine

```rego
# security_policy.rego (Production Version)
package commands

import future.keywords.if
import future.keywords.in

# Sprint-based command allowlist with argument validation
allowed_commands := {
  "planning": {
    "cat": {"max_args": 10, "path_restricted": true},
    "ls": {"max_args": 5, "path_restricted": true},
    "find": {"max_args": 20, "path_restricted": true},
    "grep": {"max_args": 10, "path_restricted": false},
    "git": {"allowed_subcommands": ["status", "log", "show", "diff"]}
  },
  "implementation": {
    "cat": {"max_args": 10, "path_restricted": true},
    "ls": {"max_args": 5, "path_restricted": true},
    "git": {"allowed_subcommands": ["add", "commit", "status", "diff"]},
    "touch": {"max_args": 5, "path_restricted": true},
    "mkdir": {"max_args": 3, "path_restricted": true},
    "cp": {"max_args": 10, "path_restricted": true},
    "mv": {"max_args": 10, "path_restricted": true}
  },
  "validation": {
    "npm": {"allowed_subcommands": ["test", "run"]},
    "pytest": {"max_args": 20, "path_restricted": true},
    "make": {"allowed_subcommands": ["test", "build"]},
    "git": {"allowed_subcommands": ["status", "diff"]}
  },
  "review": {
    "git": {"allowed_subcommands": ["diff", "show", "log", "status"]},
    "cat": {"max_args": 10, "path_restricted": true},
    "ls": {"max_args": 5, "path_restricted": true}
  }
}

# Main policy decision
allow if {
  # Verify sprint exists
  input.sprint in object.keys(allowed_commands)
  
  # Verify command is allowed in this sprint
  input.command in object.keys(allowed_commands[input.sprint])
  
  # Apply command-specific validation
  command_is_valid
}

# Command-specific validation rules
command_is_valid if {
  command_config := allowed_commands[input.sprint][input.command]
  
  # Check argument count if specified
  not command_config.max_args
  or count(input.args) <= command_config.max_args
  
  # Check path restrictions if specified
  not command_config.path_restricted
  or all_paths_within_workdir
  
  # Check subcommand restrictions for complex commands
  not command_config.allowed_subcommands
  or subcommand_is_allowed(command_config.allowed_subcommands)
}

# Path restriction validation
all_paths_within_workdir if {
  # Check that all file/directory arguments are within workdir
  every arg in input.args {
    not startswith(arg, "/")    # No absolute paths
    not contains(arg, "..")     # No directory traversal
  }
}

# Subcommand validation (for git, npm, etc.)
subcommand_is_allowed(allowed_list) if {
  count(input.args) > 0
  input.args[0] in allowed_list
}

# Audit logging (for security monitoring)
audit_log := {
  "timestamp": time.now_ns(),
  "sprint": input.sprint,
  "command": input.command,
  "args": input.args,
  "allowed": allow,
  "workdir": input.workdir
}
```

## Layer 3: Hardened Command Proxy

```python
#!/usr/bin/env python3
# secure_shell.py (Production Version)

import subprocess
import json
import requests
import sys
import shlex
import os
import time
from pathlib import Path

class SecureShell:
    def __init__(self):
        self.opa_url = "http://localhost:8181/v1/data/commands"
        self.workdir = "/app/workdir"
        self.state_file = os.path.join(self.workdir, ".project-state.json")
        
    def load_project_state(self):
        """Load current project state with error handling"""
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  State file not found, defaulting to 'planning' sprint.", 
                  file=sys.stderr)
            return {"workflow_step": "planning"}
        except json.JSONDecodeError as e:
            print(f"🚨 Invalid state file format: {e}", file=sys.stderr)
            return {"workflow_step": "planning"}
    
    def check_opa_policy(self, command, args, sprint):
        """Check command against OPA policy with comprehensive error handling"""
        policy_data = {
            "input": {
                "command": command,
                "args": args,
                "sprint": sprint,
                "workdir": self.workdir,
                "timestamp": int(time.time())
            }
        }
        
        try:
            response = requests.post(
                f"{self.opa_url}/allow",
                json=policy_data,
                timeout=5
            )
            response.raise_for_status()
            result = response.json()
            
            # Log the decision for audit trail
            self.log_decision(policy_data["input"], result.get("result", False))
            
            return result.get("result", False)
            
        except requests.exceptions.RequestException as e:
            print(f"🚨 OPA policy check failed: {e}", file=sys.stderr)
            return False  # Fail-safe: deny if policy engine is unavailable
        except json.JSONDecodeError as e:
            print(f"🚨 Invalid OPA response: {e}", file=sys.stderr)
            return False
    
    def log_decision(self, input_data, decision):
        """Log policy decisions for security audit"""
        log_entry = {
            "timestamp": time.time(),
            "sprint": input_data["sprint"],
            "command": f"{input_data['command']} {' '.join(input_data['args'])}",
            "decision": "ALLOW" if decision else "DENY"
        }
        
        # Append to audit log
        log_file = os.path.join(self.workdir, ".security-audit.log")
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def execute_command(self, command_parts):
        """Execute command with security boundaries"""
        try:
            # Execute with restricted environment
            env = os.environ.copy()
            env["PATH"] = "/app/bin/safe_commands:/usr/local/bin:/usr/bin:/bin"
            
            result = subprocess.run(
                command_parts,
                cwd=self.workdir,
                check=True,
                env=env,
                capture_output=False,  # Allow output to flow through
                timeout=300  # 5 minute timeout for any single command
            )
            return result.returncode
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed with exit code {e.returncode}", 
                  file=sys.stderr)
            return e.returncode
        except subprocess.TimeoutExpired:
            print("❌ Command timed out after 5 minutes", file=sys.stderr)
            return 124  # Standard timeout exit code
        except Exception as e:
            print(f"🚨 Unexpected error executing command: {e}", 
                  file=sys.stderr)
            return 1
    
    def main(self):
        if len(sys.argv) < 2:
            print("Usage: secure_shell <command>", file=sys.stderr)
            return 1
            
        full_command_str = " ".join(sys.argv[1:])
        
        # Parse command safely
        try:
            command_parts = shlex.split(full_command_str)
        except ValueError as e:
            print(f"❌ Invalid command string: {e}", file=sys.stderr)
            return 1
        
        if not command_parts:
            print("❌ Empty command provided", file=sys.stderr)
            return 1
            
        command = command_parts[0]
        args = command_parts[1:]
        
        # Load project state
        project_state = self.load_project_state()
        sprint = project_state.get("workflow_step", "planning")
        
        print(f"🔍 Sprint: {sprint}, Command: {full_command_str}")
        
        # Check policy
        if self.check_opa_policy(command, args, sprint):
            print(f"✅ Command approved")
            return self.execute_command(command_parts)
        else:
            print(f"❌ Command blocked by security policy")
            return 1

if __name__ == "__main__":
    shell = SecureShell()
    exit_code = shell.main()
    sys.exit(exit_code)
```

## Integration with Sprint-Driven System

Update the command files to use the secure shell:

```markdown
<!-- Example: Updated start.md -->
Tasks:
1. Initialize Docker security container with OPA policy engine
2. Validate project state and sprint definitions
3. Configure secure command execution through policy layer
4. Enable automation hooks with security validation
5. Begin Sprint 01 with secure story lifecycle

All automation commands will be executed through the security layer:
- Each command validated against current sprint policy
- Shell injection prevention through command parsing
- Audit trail generation for all security decisions
- Container isolation for safe autonomous operation

Security Architecture Active:
✅ Docker sandbox isolation
✅ OPA policy enforcement
✅ Command injection prevention
✅ Audit logging enabled
✅ Path restriction validation
```
