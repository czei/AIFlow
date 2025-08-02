#!/usr/bin/env python3
"""
Hook Import Helper - Handles imports for both global and project-level installations.

This module provides a unified way to import AIFlow modules regardless of
whether the hooks are installed globally or at the project level.
"""

import sys
import os
from pathlib import Path


def setup_imports():
    """
    Set up Python path for imports based on installation type.
    
    Returns:
        bool: True if imports were set up successfully, False otherwise
    """
    hook_file = Path(__file__).resolve()
    hook_dir = hook_file.parent
    
    # Check if this is a project-level installation
    # Project structure: .claude/hooks/hook_import_helper.py
    if hook_dir.parent.name == '.claude':
        # Project-level installation
        project_root = hook_dir.parent.parent
        commands_dir = project_root / '.claude' / 'commands' / 'project'
        lib_dir = commands_dir / 'lib'
        
        if lib_dir.exists():
            sys.path.insert(0, str(lib_dir))
            return True
    
    # Check if this is a global installation
    # Global structure: ~/.claude/commands/project/hooks/hook_import_helper.py
    if hook_dir.name == 'hooks' and hook_dir.parent.name == 'project':
        # Global installation
        project_dir = hook_dir.parent
        lib_dir = project_dir / 'lib'
        
        if lib_dir.exists():
            sys.path.insert(0, str(lib_dir))
            return True
    
    # Fallback: try to find lib directory relative to hooks
    # This handles development/testing scenarios
    for parent in hook_dir.parents:
        lib_dir = parent / 'lib'
        if lib_dir.exists() and (lib_dir / 'src' / 'state_manager.py').exists():
            sys.path.insert(0, str(lib_dir))
            return True
    
    return False


def get_installation_type():
    """
    Determine the installation type.
    
    Returns:
        str: 'project' for project-level, 'global' for global, 'unknown' otherwise
    """
    hook_file = Path(__file__).resolve()
    hook_dir = hook_file.parent
    
    if hook_dir.parent.name == '.claude':
        return 'project'
    elif hook_dir.name == 'hooks' and hook_dir.parent.name == 'project':
        return 'global'
    else:
        return 'unknown'


def get_project_root():
    """
    Get the project root directory.
    
    Returns:
        Path: Project root directory or None if not found
    """
    hook_file = Path(__file__).resolve()
    hook_dir = hook_file.parent
    
    if hook_dir.parent.name == '.claude':
        # Project-level installation
        return hook_dir.parent.parent
    else:
        # For global installation, return current working directory
        return Path.cwd()