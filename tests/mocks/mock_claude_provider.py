#!/usr/bin/env python3
"""
MockClaudeProvider - Simulates Claude AI for integration testing.
Provides predictable responses for testing AI-driven workflows.
"""

import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import re


class MockClaudeProvider:
    """Mock implementation of Claude AI for testing"""
    
    def __init__(self, response_mode: str = "deterministic"):
        """
        Initialize mock provider.
        
        Args:
            response_mode: One of 'deterministic', 'random', 'failure'
        """
        self.response_mode = response_mode
        self.debug = False  # Initialize debug attribute
        self.call_history: List[Dict[str, Any]] = []
        self.response_templates = self._load_response_templates()
        
    def _load_response_templates(self) -> Dict[str, Any]:
        """Load predefined response templates for different scenarios"""
        return {
            "project_setup": {
                "command": "mkdir -p {project_name}",
                "explanation": "Creating project directory structure",
                "files_to_create": ["README.md", "requirements.txt", ".gitignore"]
            },
            "code_implementation": {
                "function": """def {function_name}({params}):
    \"\"\"Mock implementation of {function_name}\"\"\"
    # TODO: Implement actual logic
    return {return_value}""",
                "test": """def test_{function_name}():
    result = {function_name}({test_params})
    assert result == {expected_result}"""
            },
            "code_review": {
                "issues": [
                    {"severity": "high", "message": "Missing error handling"},
                    {"severity": "medium", "message": "Consider adding type hints"},
                    {"severity": "low", "message": "Add docstring"}
                ]
            },
            "error_analysis": {
                "diagnosis": "The error occurs due to {reason}",
                "fix": "To fix this, {solution}",
                "prevention": "Prevent by {prevention_method}"
            }
        }
        
    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query and return mock response.
        
        Args:
            prompt: The prompt to process
            context: Optional context information
            
        Returns:
            Mock response dictionary
        """
        # Validate prompt length
        MAX_PROMPT_LENGTH = 10000
        if len(prompt) > MAX_PROMPT_LENGTH:
            return {
                "type": "error",
                "error": f"Prompt too long: {len(prompt)} characters (max {MAX_PROMPT_LENGTH})",
                "message": "Please reduce the prompt length"
            }
        # Record the call
        call_record = {
            "timestamp": time.time(),
            "prompt": prompt,
            "context": context,
            "response_mode": self.response_mode
        }
        
        # Generate response based on mode
        if self.response_mode == "failure":
            response = self._generate_failure_response()
        elif self.response_mode == "random":
            response = self._generate_random_response(prompt)
        else:
            response = self._generate_deterministic_response(prompt, context)
            
        call_record["response"] = response
        self.call_history.append(call_record)
        
        return response
        
    def _generate_deterministic_response(self, prompt: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate predictable response based on prompt patterns"""
        prompt_lower = prompt.lower()
        
        # Debug logging
        if self.debug:
            print(f"DEBUG MockClaudeProvider: Processing prompt: {prompt[:100]}...")
            print(f"DEBUG MockClaudeProvider: Context: {context}")
        
        # Project setup requests
        if "setup" in prompt_lower or "set up" in prompt_lower or "create project" in prompt_lower:
            project_name = context.get("project_name", "test_project") if context else "test_project"
            return {
                "type": "project_setup",
                "commands": [
                    f"mkdir -p {project_name}/src",
                    f"mkdir -p {project_name}/tests",
                    f"touch {project_name}/README.md",
                    f"echo # {project_name} > {project_name}/README.md"
                ],
                "explanation": f"Setting up project structure for {project_name}"
            }
            
        # Code review requests (check before implementation)
        elif "review" in prompt_lower or "check code" in prompt_lower:
            return {
                "type": "code_review",
                "issues": self.response_templates["code_review"]["issues"],
                "summary": "Found 3 issues: 1 high, 1 medium, 1 low severity. The code needs improvement in error handling and documentation.",
                "recommendation": "request_changes",
                "positive_aspects": ["Code structure is clean", "Function names are descriptive"]
            }
            
        # Code implementation requests
        elif any(keyword in prompt_lower for keyword in ["implement", "create", "generate", "write"]) or "class" in prompt_lower or "function" in prompt_lower:
            # Extract function/class name from prompt
            func_match = re.search(r"function\s+(\w+)", prompt)
            class_match = re.search(r"class\s+(?:for\s+)?(?:a\s+)?(\w+)", prompt)
            
            if class_match:
                name = class_match.group(1)
                is_class = True
            elif func_match:
                name = func_match.group(1)
                is_class = False
            else:
                name = "process_data"
                is_class = False
            
            # For contract tests, return appropriate type based on prompt
            if "class" in prompt_lower:
                response_type = "class"
            elif "function" in prompt_lower:
                response_type = "function"
            else:
                response_type = "code_implementation"
                
            # Determine the language from context or default to python
            language = context.get("language", "python") if context else "python"
            
            # Map response types to valid enum values
            type_mapping = {
                "function": "function",
                "class": "class",
                "code_implementation": "code_implementation"
            }
            
            # Generate appropriate code based on type
            if is_class:
                code = f"""class {name}:
    \"\"\"Mock implementation of {name}\"\"\"
    
    def __init__(self):
        self.balance = 0
    
    def deposit(self, amount):
        \"\"\"Add money to account\"\"\"
        self.balance += amount
        return self.balance
    
    def withdraw(self, amount):
        \"\"\"Remove money from account\"\"\"
        if amount <= self.balance:
            self.balance -= amount
            return self.balance
        raise ValueError("Insufficient funds")"""
                explanation = f"Implemented {name} class with basic structure including deposit and withdraw methods."
                usage_example = f"account = {name}()\naccount.deposit(100)\naccount.withdraw(50)"
            else:
                code = self.response_templates["code_implementation"]["function"].format(
                    function_name=name,
                    params="data",
                    return_value="processed_data"
                )
                explanation = f"Implemented {name} with basic structure. This function takes data as input and returns processed_data."
                usage_example = f"{name}('sample_data')  # Returns: 'processed_data'"
            
            return {
                "type": type_mapping.get(response_type, "code_generation"),
                "code": code,
                "language": language,
                "explanation": explanation,
                "test_code": self.response_templates["code_implementation"]["test"].format(
                    function_name=name,
                    test_params="'test_data'",
                    expected_result="'processed_data'"
                ),
                "dependencies": ["typing"] if language == "python" else [],
                "usage_example": usage_example
            }
            
        # Error analysis requests
        elif "error" in prompt_lower or "debug" in prompt_lower:
            return {
                "type": "error_analysis",
                "diagnosis": "The error appears to be a type mismatch between the expected and actual data types",
                "fix": "Convert the input to the expected type before processing",
                "code_fix": "data = str(data)  # Ensure data is string type",
                "explanation": "Type conversion will resolve the immediate issue by ensuring the data matches the expected format",
                "error_type": "type",
                "root_cause": "Function expects string input but received a different type",
                "prevention": "Add type hints and input validation to catch type mismatches early",
                "confidence": 0.85
            }
            
        # Minimal code generation (e.g., "x = 1")
        elif "=" in prompt and len(prompt) < 50:
            return {
                "type": "code_generation",
                "code": prompt.strip(),
                "language": "python",
                "explanation": "This is a simple variable assignment or expression."
            }
            
        # Default response
        else:
            return {
                "type": "general",
                "response": "I understand your request. Here's my response.",
                "suggestions": ["Consider breaking this into smaller tasks", "Add error handling", "Write tests"],
                "confidence": 0.85
            }
            
    def _generate_random_response(self, prompt: str) -> Dict[str, Any]:
        """Generate semi-random but valid responses"""
        import random
        
        response_types = ["code", "explanation", "command", "analysis"]
        chosen_type = random.choice(response_types)
        
        if chosen_type == "code":
            return {
                "type": "code",
                "language": "python",
                "code": f"# Random response for: {prompt[:30]}...\nprint('Mock implementation')"
            }
        elif chosen_type == "command":
            return {
                "type": "command",
                "commands": ["echo 'Processing...'", "sleep 1", "echo 'Done'"]
            }
        else:
            return {
                "type": chosen_type,
                "content": f"Mock {chosen_type} response for testing purposes"
            }
            
    def _generate_failure_response(self) -> Dict[str, Any]:
        """Generate failure responses for testing error handling"""
        return {
            "type": "error",
            "error": "Mock provider failure",
            "message": "Simulated API failure for testing",
            "retry_after": 5
        }
        
    def get_call_history(self) -> List[Dict[str, Any]]:
        """Return history of all calls made to the provider"""
        return self.call_history
        
    def clear_history(self):
        """Clear call history"""
        self.call_history = []
        
    def set_response_mode(self, mode: str):
        """Change response mode"""
        if mode not in ["deterministic", "random", "failure"]:
            raise ValueError(f"Invalid mode: {mode}")
        self.response_mode = mode
        
    def inject_response(self, pattern: str, response: Dict[str, Any]):
        """Inject custom response for specific prompt pattern"""
        # This allows tests to define specific responses
        if not hasattr(self, "custom_responses"):
            self.custom_responses = {}
        self.custom_responses[pattern] = response


class MockClaudeProviderWithState(MockClaudeProvider):
    """Extended mock provider that maintains state across calls"""
    
    def __init__(self, response_mode: str = "deterministic"):
        super().__init__(response_mode)
        self.state = {
            "project_sprint": "planning",
            "completed_tasks": [],
            "current_context": {},
            "error_count": 0
        }
        
    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process query with state tracking"""
        # Update state based on prompt
        self._update_state(prompt, context)
        
        # Get base response
        response = super().query(prompt, context)
        
        # Enhance response with state information
        response["state"] = self.state.copy()
        
        return response
        
    def _update_state(self, prompt: str, context: Optional[Dict[str, Any]]):
        """Update internal state based on interactions"""
        prompt_lower = prompt.lower()
        
        # Track sprint transitions
        if "implement" in prompt_lower:
            self.state["project_sprint"] = "implementation"
        elif "test" in prompt_lower:
            self.state["project_sprint"] = "testing"
        elif "deploy" in prompt_lower:
            self.state["project_sprint"] = "deployment"
            
        # Track completed tasks
        if "completed" in prompt_lower or "done" in prompt_lower:
            task = context.get("task", "unknown") if context else "unknown"
            self.state["completed_tasks"].append(task)
            
        # Track errors
        if "error" in prompt_lower:
            self.state["error_count"] += 1
            
        # Update context
        if context:
            self.state["current_context"].update(context)
            
    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return self.state.copy()
        
    def reset_state(self):
        """Reset state to initial values"""
        self.state = {
            "project_sprint": "planning",
            "completed_tasks": [],
            "current_context": {},
            "error_count": 0
        }