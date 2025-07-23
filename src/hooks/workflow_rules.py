#!/usr/bin/env python3
"""
Workflow Rules Engine for Sprint-Driven Development

This module defines rules for each workflow step and provides utilities
for rule evaluation, context analysis, and emergency overrides.
"""

import re
from typing import Dict, List, Tuple, Optional, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import workflow as workflow_config, messages


class WorkflowRules:
    """Rule engine for enforcing the 6-step workflow."""
    
    # Tool categories from config
    READ_TOOLS = workflow_config.READ_TOOLS
    WRITE_TOOLS = workflow_config.WRITE_TOOLS
    EXEC_TOOLS = workflow_config.EXEC_TOOLS
    GIT_TOOLS = workflow_config.GIT_TOOLS
    
    # Workflow step rules
    WORKFLOW_RULES = {
        'planning': {
            'allowed': READ_TOOLS + ['TodoWrite'],
            'blocked': WRITE_TOOLS + EXEC_TOOLS,
            'message': "🚫 Planning sprint: Complete requirements analysis before writing code.",
            'suggestions': [
                "Read existing code to understand the architecture",
                "Search for similar implementations",
                "Create a todo list of implementation tasks"
            ]
        },
        'implementation': {
            'allowed': '*',  # All tools allowed
            'blocked': [],
            'message': "✅ Implementation sprint: All tools available.",
            'track': ['files_modified', 'tests_created']
        },
        'validation': {
            'allowed': READ_TOOLS + EXEC_TOOLS + ['Edit'],  # Allow minor fixes
            'blocked': ['Write'],  # No new files during validation
            'message': "🧪 Validation sprint: Focus on testing and verification.",
            'suggestions': [
                "Run existing tests",
                "Create new test cases",
                "Check for edge cases"
            ]
        },
        'review': {
            'allowed': READ_TOOLS + ['TodoWrite'],
            'blocked': WRITE_TOOLS + EXEC_TOOLS,
            'message': "👀 Review sprint: Analyze code quality and architecture.",
            'suggestions': [
                "Review code for quality issues",
                "Check for security vulnerabilities",
                "Assess performance implications"
            ]
        },
        'refinement': {
            'allowed': READ_TOOLS + ['Edit', 'MultiEdit'] + EXEC_TOOLS,
            'blocked': ['Write'],  # No new files, only refinements
            'message': "🔧 Refinement sprint: Apply review feedback.",
            'track': ['review_items_addressed']
        },
        'integration': {
            'allowed': READ_TOOLS + GIT_TOOLS + EXEC_TOOLS,
            'blocked': WRITE_TOOLS,
            'message': "🔀 Integration sprint: Prepare for merge.",
            'suggestions': [
                "Run final tests",
                "Update documentation",
                "Commit and push changes"
            ]
        }
    }
    
    # Emergency override patterns
    EMERGENCY_PATTERNS = [
        r'EMERGENCY:',
        r'HOTFIX:',
        r'CRITICAL:',
        r'OVERRIDE:',
        r'production.*down',
        r'security.*vulnerability',
        r'data.*loss'
    ]
    
    @classmethod
    def evaluate_tool_use(cls, workflow_step: str, tool_name: str, 
                         context: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
        """
        Evaluate if a tool use is allowed in the current workflow step.
        
        Args:
            workflow_step: Current workflow step
            tool_name: Name of the tool being called
            context: Additional context (event data, arguments, etc.)
            
        Returns:
            Tuple of (allowed, message, suggestions)
        """
        # Check for emergency override
        if cls._check_emergency_override(context):
            return True, "⚡ Emergency override accepted.", []
        
        # Get rules for current step
        rules = cls.WORKFLOW_RULES.get(workflow_step, {})
        if not rules:
            return True, "✅ No rules defined for this step.", []
        
        # Check if all tools are allowed
        allowed_tools = rules.get('allowed', [])
        if allowed_tools == '*':
            return True, rules.get('message', ''), []
        
        # Check blocked tools
        blocked_tools = rules.get('blocked', [])
        if tool_name in blocked_tools:
            suggestions = rules.get('suggestions', [])
            return False, rules.get('message', ''), suggestions
        
        # Check allowed tools
        if tool_name in allowed_tools:
            return True, rules.get('message', ''), []
        
        # Default deny for tools not explicitly allowed
        return False, f"🚫 {tool_name} not allowed in {workflow_step} sprint.", []
    
    @classmethod
    def _check_emergency_override(cls, context: Dict[str, Any]) -> bool:
        """Check if the context contains emergency override indicators."""
        # Check commit message or command arguments
        text_to_check = []
        
        if 'event' in context:
            event = context['event']
            # Check bash commands
            if event.get('tool') == 'Bash':
                command = event.get('input', {}).get('command', '')
                if command:
                    text_to_check.append(command)
            # Check commit messages
            if 'message' in event:
                text_to_check.append(event['message'])
        
        # Check for emergency patterns
        for text in text_to_check:
            for pattern in cls.EMERGENCY_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        
        return False
    
    @classmethod
    def get_step_completion_indicators(cls, workflow_step: str) -> Dict[str, Any]:
        """
        Get indicators that suggest a workflow step is complete.
        
        Returns dict with:
            - required_actions: Actions that must occur
            - completion_signals: Patterns that indicate completion
            - next_step: What step should come next
        """
        completion_map = {
            'planning': {
                'required_actions': ['TodoWrite with implementation tasks'],
                'completion_signals': [
                    'todo list created',
                    'requirements documented',
                    'plan approved'
                ],
                'next_step': 'implementation'
            },
            'implementation': {
                'required_actions': ['Code written', 'Tests created'],
                'completion_signals': [
                    'feature complete',
                    'tests written',
                    'ready for validation'
                ],
                'next_step': 'validation'
            },
            'validation': {
                'required_actions': ['Tests executed'],
                'completion_signals': [
                    'tests pass',
                    'validation complete',
                    'ready for review'
                ],
                'next_step': 'review'
            },
            'review': {
                'required_actions': ['Code reviewed'],
                'completion_signals': [
                    'review complete',
                    'feedback provided',
                    'issues identified'
                ],
                'next_step': 'refinement'
            },
            'refinement': {
                'required_actions': ['Review feedback addressed'],
                'completion_signals': [
                    'issues resolved',
                    'refinements complete',
                    'ready to integrate'
                ],
                'next_step': 'integration'
            },
            'integration': {
                'required_actions': ['Changes committed'],
                'completion_signals': [
                    'committed',
                    'pushed',
                    'merged'
                ],
                'next_step': 'planning'  # Next sprint
            }
        }
        
        return completion_map.get(workflow_step, {})
    
    @classmethod
    def calculate_compliance_score(cls, metrics: Dict[str, Any]) -> float:
        """
        Calculate workflow compliance score (0-100).
        
        Args:
            metrics: Dictionary containing:
                - tools_blocked: Number of blocked tool uses
                - tools_allowed: Number of allowed tool uses
                - emergency_overrides: Number of emergency overrides
                - workflow_violations: Number of out-of-order transitions
        """
        blocked = metrics.get('tools_blocked', 0)
        allowed = metrics.get('tools_allowed', 0)
        overrides = metrics.get('emergency_overrides', 0)
        violations = metrics.get('workflow_violations', 0)
        
        total_actions = blocked + allowed
        if total_actions == 0:
            return 100.0
        
        # Calculate base compliance
        compliance = (allowed / total_actions) * 100
        
        # Deduct for violations (heavy penalty)
        compliance -= violations * 10
        
        # Small deduction for overrides (they're allowed but tracked)
        compliance -= overrides * 2
        
        # Ensure score is between 0 and 100
        return max(0, min(100, compliance))
    
    @classmethod
    def is_step_complete(cls, workflow_step: str, step_progress: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Determine if a workflow step is complete based on progress indicators.
        
        Args:
            workflow_step: Current workflow step name
            step_progress: Progress tracking dictionary for the step
            
        Returns:
            Tuple of (is_complete, completion_message)
        """
        if workflow_step == 'planning':
            # Planning is complete when todo list is created
            if step_progress.get('planning_complete', False):
                return True, "Planning complete - todo list created"
                
        elif workflow_step == 'implementation':
            # Implementation complete when code is written
            files_modified = step_progress.get('files_modified', [])
            if len(files_modified) > 0:
                return True, f"Implementation complete - {len(files_modified)} files modified"
                
        elif workflow_step == 'validation':
            # Validation complete when tests are run
            if step_progress.get('tests_run', False):
                return True, "Validation complete - tests executed"
                
        elif workflow_step == 'review':
            # Review complete when code review is done
            if step_progress.get('review_complete', False):
                return True, "Review complete - code reviewed"
                
        elif workflow_step == 'refinement':
            # Refinement complete when files are edited after review
            if 'Edit' in step_progress.get('tools_used', []) or 'MultiEdit' in step_progress.get('tools_used', []):
                return True, "Refinement complete - changes applied"
                
        elif workflow_step == 'integration':
            # Integration complete when git operations are used
            tools_used = step_progress.get('tools_used', [])
            git_tools = [t for t in tools_used if 'Git' in t or 'git' in t]
            if git_tools or ('Bash' in tools_used and step_progress.get('git_commands_run', False)):
                return True, "Integration complete - changes committed"
        
        return False, ""