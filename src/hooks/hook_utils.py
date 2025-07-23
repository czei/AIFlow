#!/usr/bin/env python3
"""
Hook Utilities - Shared functions for all hooks.

Provides common functionality like configuration loading, logging,
and state management helpers.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple


class HookConfig:
    """Configuration loader for hooks."""
    
    _config = None
    _emergency_overrides = None
    
    @classmethod
    def load(cls) -> Dict[str, Any]:
        """Load hook configuration."""
        if cls._config is None:
            config_path = Path(__file__).parent / 'config.json'
            try:
                with open(config_path, 'r') as f:
                    cls._config = json.load(f)
            except FileNotFoundError:
                cls._config = cls._default_config()
            except json.JSONDecodeError:
                cls._config = cls._default_config()
        return cls._config
    
    @classmethod
    def load_emergency_overrides(cls) -> Dict[str, Any]:
        """Load emergency override configuration."""
        if cls._emergency_overrides is None:
            overrides_path = Path(__file__).parent / 'emergency_overrides.json'
            try:
                with open(overrides_path, 'r') as f:
                    cls._emergency_overrides = json.load(f)
            except FileNotFoundError:
                cls._emergency_overrides = {'patterns': [], 'context_patterns': []}
            except json.JSONDecodeError:
                cls._emergency_overrides = {'patterns': [], 'context_patterns': []}
        return cls._emergency_overrides
    
    @classmethod
    def _default_config(cls) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'workflow_enforcement': {
                'mode': 'guided_flexibility',
                'allow_emergency_override': True,
                'compliance_tracking': True
            },
            'metrics': {
                'track_compliance': True,
                'track_tool_usage': True,
                'track_progress': True
            }
        }


class HookLogger:
    """Simple logger for hooks."""
    
    @staticmethod
    def log(message: str, level: str = 'INFO'):
        """Log a message to stderr."""
        timestamp = datetime.now(timezone.utc).isoformat()
        print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)
    
    @staticmethod
    def debug(message: str):
        """Log debug message."""
        if os.environ.get('HOOK_DEBUG'):
            HookLogger.log(message, 'DEBUG')
    
    @staticmethod
    def error(message: str):
        """Log error message."""
        HookLogger.log(message, 'ERROR')


class EventParser:
    """Parse and validate hook events."""
    
    @staticmethod
    def parse_stdin() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Parse JSON event from stdin.
        
        Returns:
            Tuple of (event_dict, error_message)
        """
        try:
            event_data = sys.stdin.read()
            event = json.loads(event_data)
            return event, None
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return None, f"Error reading event: {str(e)}"
    
    @staticmethod
    def get_tool_info(event: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Extract tool name and input from event.
        
        Returns:
            Tuple of (tool_name, tool_input)
        """
        tool = event.get('tool', '')
        tool_input = event.get('input', {})
        return tool, tool_input


class ResponseBuilder:
    """Build standardized hook responses."""
    
    @staticmethod
    def allow(message: Optional[str] = None) -> str:
        """Build an allow response."""
        response = {"decision": "allow"}
        if message:
            response["message"] = message
        return json.dumps(response)
    
    @staticmethod
    def deny(reason: str, suggestions: Optional[list] = None) -> str:
        """Build a deny/block response."""
        response = {
            "decision": "block",
            "reason": reason
        }
        if suggestions:
            response["suggestions"] = suggestions
        return json.dumps(response)
    
    @staticmethod
    def error(error_message: str) -> str:
        """Build an error response (allows operation but logs warning)."""
        return json.dumps({
            "decision": "allow",
            "message": error_message
        })


def format_time_delta(seconds: int) -> str:
    """Format seconds into human-readable time."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"


def safe_state_update(state_manager, updates: Dict[str, Any]) -> bool:
    """
    Safely update state without blocking hook execution.
    
    Returns:
        True if update succeeded, False otherwise
    """
    try:
        state_manager.update(updates)
        return True
    except Exception as e:
        HookLogger.error(f"Failed to update state: {str(e)}")
        return False