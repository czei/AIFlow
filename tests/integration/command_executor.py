#!/usr/bin/env python3
"""
CommandExecutor - Simulates user command execution for integration testing.

Provides utilities to execute /user:project:* commands and simulate
Claude Code tool usage through hooks.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re


class CommandExecutor:
    """Execute user commands and simulate Claude Code interactions."""
    
    def __init__(self, working_dir: str):
        """
        Initialize CommandExecutor.
        
        Args:
            working_dir: Directory to execute commands in
        """
        self.working_dir = Path(working_dir).resolve()
        self.src_path = Path(__file__).parent.parent.parent / 'src'
        self.commands_path = self.src_path / 'commands'
        
    def run_user_command(self, command: str, args: List[str] = None) -> Tuple[int, str, str]:
        """
        Execute a /user:project:* command.
        
        Args:
            command: Command name (e.g., 'start', 'pause')
            args: Optional command arguments
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        # Map command to markdown file
        command_file = self.commands_path / f"{command}.md"
        if not command_file.exists():
            return 1, "", f"Command not found: {command}"
        
        # Read markdown file and extract bash commands
        with open(command_file, 'r') as f:
            content = f.read()
            
        # Extract and execute bash commands
        # Look for lines starting with !` and ending with `
        bash_pattern = r'^!`(.+?)`$'
        commands = re.findall(bash_pattern, content, re.MULTILINE)
        
        if not commands:
            return 1, "", "No executable commands found in markdown"
        
        # Execute commands in sequence
        combined_stdout = []
        combined_stderr = []
        
        for cmd in commands:
            # Replace arguments if provided
            if args and '{1}' in cmd:
                cmd = cmd.replace('{1}', args[0] if args else '')
                
            # Fix Python path for test environment
            if 'git rev-parse --show-toplevel' in cmd:
                # Replace git command with actual src path
                project_root = str(self.src_path.parent)
                cmd = cmd.replace("$(git rev-parse --show-toplevel)", project_root)
                
            # Execute command
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    combined_stdout.append(result.stdout)
                if result.stderr:
                    combined_stderr.append(result.stderr)
                    
                # Stop on first error
                if result.returncode != 0:
                    return result.returncode, '\n'.join(combined_stdout), '\n'.join(combined_stderr)
                    
            except Exception as e:
                return 1, '\n'.join(combined_stdout), f"Command execution failed: {e}"
        
        # Add success message from markdown
        success_lines = [line for line in content.split('\n') 
                        if not line.startswith('!`') and not line.startswith('#') 
                        and not line.startswith('---') and line.strip()]
        if success_lines:
            combined_stdout.extend(success_lines)
            
        return 0, '\n'.join(combined_stdout), '\n'.join(combined_stderr)
        
    def simulate_tool_use(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate Claude Code calling a tool through hooks.
        
        Args:
            tool: Tool name (e.g., 'Write', 'Bash')
            params: Tool parameters
            
        Returns:
            Hook response dict
        """
        # Create event data matching Claude Code format
        event = {
            "cwd": str(self.working_dir),
            "tool": tool,
            "input": params
        }
        
        # Run pre_tool_use hook
        hook_path = self.src_path / 'hooks' / 'pre_tool_use.py'
        
        try:
            result = subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(event),
                capture_output=True,
                text=True,
                cwd=self.working_dir
            )
            
            if result.returncode != 0:
                return {
                    "decision": "error",
                    "message": f"Hook failed: {result.stderr}"
                }
                
            # Parse response
            if result.stdout:
                return json.loads(result.stdout)
            else:
                return {"decision": "allow", "message": "No response from hook"}
                
        except json.JSONDecodeError:
            return {
                "decision": "error", 
                "message": f"Invalid JSON response: {result.stdout}"
            }
        except Exception as e:
            return {
                "decision": "error",
                "message": f"Hook execution failed: {e}"
            }
            
    def simulate_post_tool_use(self, tool: str, params: Dict[str, Any], 
                              exit_code: int = 0) -> Dict[str, Any]:
        """
        Simulate post-tool-use hook execution.
        
        Args:
            tool: Tool that was used
            params: Tool parameters
            exit_code: Tool execution result
            
        Returns:
            Hook response dict
        """
        event = {
            "cwd": str(self.working_dir),
            "tool": tool,
            "input": params,
            "exit_code": exit_code
        }
        
        hook_path = self.src_path / 'hooks' / 'post_tool_use.py'
        
        try:
            result = subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(event),
                capture_output=True,
                text=True,
                cwd=self.working_dir
            )
            
            if result.stdout:
                return json.loads(result.stdout)
            else:
                return {"status": "success"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def simulate_stop_hook(self, response: str = "Task complete") -> Dict[str, Any]:
        """
        Simulate Stop hook execution.
        
        Args:
            response: Claude's response text
            
        Returns:
            Hook response dict
        """
        event = {
            "cwd": str(self.working_dir),
            "response": response
        }
        
        hook_path = self.src_path / 'hooks' / 'stop.py'
        
        try:
            result = subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps(event),
                capture_output=True,
                text=True,
                cwd=self.working_dir
            )
            
            if result.stdout:
                return json.loads(result.stdout)
            else:
                return {"status": "success"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def extract_command_from_markdown(self, markdown_path: str) -> List[str]:
        """
        Extract executable commands from markdown file.
        
        Args:
            markdown_path: Path to markdown command file
            
        Returns:
            List of bash commands to execute
        """
        with open(markdown_path, 'r') as f:
            content = f.read()
            
        # Extract commands between !` and `
        bash_pattern = r'^!`(.+?)`$'
        commands = re.findall(bash_pattern, content, re.MULTILINE)
        
        return commands