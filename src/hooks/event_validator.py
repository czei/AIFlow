#!/usr/bin/env python3
"""
Event Validator - Validates Claude Code event data structures.

Provides schema validation for hook events to ensure data integrity
and prevent errors from malformed input.
"""

from typing import Dict, Any, Tuple, Optional


class EventValidator:
    """Validates event data against expected schemas."""
    
    # Event schemas for different hooks
    PRE_TOOL_USE_SCHEMA = {
        "required": ["cwd", "tool", "input"],
        "optional": ["user", "timestamp"],
        "types": {
            "cwd": str,
            "tool": str,
            "input": dict,
            "user": str,
            "timestamp": str
        }
    }
    
    POST_TOOL_USE_SCHEMA = {
        "required": ["cwd", "tool", "input", "exit_code"],
        "optional": ["output", "error", "duration", "user", "timestamp"],
        "types": {
            "cwd": str,
            "tool": str,
            "input": dict,
            "exit_code": int,
            "output": str,
            "error": str,
            "duration": (int, float),
            "user": str,
            "timestamp": str
        }
    }
    
    STOP_SCHEMA = {
        "required": ["cwd"],
        "optional": ["response", "user", "timestamp"],
        "types": {
            "cwd": str,
            "response": str,
            "user": str,
            "timestamp": str
        }
    }
    
    # Tool-specific input schemas
    TOOL_INPUT_SCHEMAS = {
        "Write": {
            "required": ["file_path", "content"],
            "types": {"file_path": str, "content": str}
        },
        "Edit": {
            "required": ["file_path", "old_string", "new_string"],
            "optional": ["replace_all"],
            "types": {
                "file_path": str,
                "old_string": str,
                "new_string": str,
                "replace_all": bool
            }
        },
        "MultiEdit": {
            "required": ["file_path", "edits"],
            "types": {"file_path": str, "edits": list}
        },
        "Read": {
            "required": ["file_path"],
            "optional": ["offset", "limit"],
            "types": {"file_path": str, "offset": int, "limit": int}
        },
        "Bash": {
            "required": ["command"],
            "optional": ["timeout", "description"],
            "types": {"command": str, "timeout": int, "description": str}
        },
        "TodoWrite": {
            "required": ["todos"],
            "types": {"todos": list}
        }
    }
    
    @classmethod
    def validate_pre_tool_use(cls, event: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate PreToolUse event data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, error = cls._validate_schema(event, cls.PRE_TOOL_USE_SCHEMA)
        if not is_valid:
            return False, error
            
        # Validate tool-specific input if known
        tool = event.get("tool", "")
        if tool in cls.TOOL_INPUT_SCHEMAS:
            tool_input = event.get("input", {})
            is_valid, error = cls._validate_schema(
                tool_input, 
                cls.TOOL_INPUT_SCHEMAS[tool]
            )
            if not is_valid:
                return False, f"Invalid input for {tool}: {error}"
                
        return True, None
        
    @classmethod
    def validate_post_tool_use(cls, event: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate PostToolUse event data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, error = cls._validate_schema(event, cls.POST_TOOL_USE_SCHEMA)
        if not is_valid:
            return False, error
            
        # Validate exit code is reasonable
        exit_code = event.get("exit_code", 0)
        if not isinstance(exit_code, int) or exit_code < -255 or exit_code > 255:
            return False, f"Invalid exit_code: {exit_code}"
            
        return True, None
        
    @classmethod
    def validate_stop(cls, event: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate Stop event data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        return cls._validate_schema(event, cls.STOP_SCHEMA)
        
    @classmethod
    def _validate_schema(cls, data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate data against a schema definition.
        
        Args:
            data: Data to validate
            schema: Schema with required, optional, and types
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Event data must be a dictionary"
            
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        # Check types
        types = schema.get("types", {})
        for field, expected_type in types.items():
            if field in data:
                value = data[field]
                if isinstance(expected_type, tuple):
                    # Multiple allowed types
                    if not any(isinstance(value, t) for t in expected_type):
                        return False, f"Field {field} must be one of {expected_type}, got {type(value).__name__}"
                else:
                    # Single type
                    if not isinstance(value, expected_type):
                        return False, f"Field {field} must be {expected_type.__name__}, got {type(value).__name__}"
                        
        # Check for unknown fields (warn but don't fail)
        known_fields = set(schema.get("required", [])) | set(schema.get("optional", []))
        unknown_fields = set(data.keys()) - known_fields
        if unknown_fields:
            # Just a warning, not a failure
            pass
            
        return True, None