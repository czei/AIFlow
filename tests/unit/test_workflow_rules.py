#!/usr/bin/env python3
"""
Unit tests for WorkflowRules - the rule engine for enforcing the 6-step workflow.
"""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.hooks.workflow_rules import WorkflowRules


class TestWorkflowRules:
    """Test the WorkflowRules engine."""
    
    # Test Tool Evaluation
    
    def test_planning_blocks_write_tools(self):
        """Test that planning step blocks write operations."""
        # Test Write tool
        allowed, message, suggestions = WorkflowRules.evaluate_tool_use(
            'planning', 'Write', {}
        )
        assert not allowed
        assert 'Planning sprint' in message
        assert len(suggestions) > 0
        
        # Test Edit tool
        allowed, message, suggestions = WorkflowRules.evaluate_tool_use(
            'planning', 'Edit', {}
        )
        assert not allowed
        
        # Test MultiEdit tool
        allowed, message, suggestions = WorkflowRules.evaluate_tool_use(
            'planning', 'MultiEdit', {}
        )
        assert not allowed
    
    def test_planning_allows_read_tools(self):
        """Test that planning step allows read operations."""
        # Test Read tool
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'planning', 'Read', {}
        )
        assert allowed
        
        # Test Grep tool
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'planning', 'Grep', {}
        )
        assert allowed
        
        # Test TodoWrite tool (special case)
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'planning', 'TodoWrite', {}
        )
        assert allowed
    
    def test_implementation_allows_all_tools(self):
        """Test that implementation step allows all tools."""
        tools = ['Read', 'Write', 'Edit', 'Bash', 'Grep', 'TodoWrite']
        for tool in tools:
            allowed, message, _ = WorkflowRules.evaluate_tool_use(
                'implementation', tool, {}
            )
            assert allowed
            assert 'Implementation sprint' in message
    
    def test_validation_blocks_new_files(self):
        """Test that validation blocks Write but allows Edit."""
        # Write should be blocked
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'validation', 'Write', {}
        )
        assert not allowed
        assert 'Validation sprint' in message
        
        # Edit should be allowed (for minor fixes)
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'validation', 'Edit', {}
        )
        assert allowed
        
        # Bash should be allowed (for running tests)
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'validation', 'Bash', {}
        )
        assert allowed
    
    def test_review_blocks_execution(self):
        """Test that review step blocks execution tools."""
        # Bash should be blocked
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'review', 'Bash', {}
        )
        assert not allowed
        assert 'Review sprint' in message
        
        # Read should be allowed
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'review', 'Read', {}
        )
        assert allowed
    
    def test_refinement_blocks_new_files(self):
        """Test that refinement only allows edits, not new files."""
        # Write should be blocked
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'refinement', 'Write', {}
        )
        assert not allowed
        assert 'Refinement sprint' in message
        
        # Edit and MultiEdit should be allowed
        for tool in ['Edit', 'MultiEdit']:
            allowed, message, _ = WorkflowRules.evaluate_tool_use(
                'refinement', tool, {}
            )
            assert allowed
    
    def test_integration_allows_git_tools(self):
        """Test that integration step allows git operations."""
        # Git-related tools (simulated via context)
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'integration', 'Bash', {'event': {'tool': 'Bash', 'input': {'command': 'git status'}}}
        )
        assert allowed
        assert 'Integration sprint' in message
        
        # Write tools should be blocked
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'integration', 'Write', {}
        )
        assert not allowed
    
    # Test Emergency Override
    
    def test_emergency_prefix_overrides_rules(self):
        """Test that EMERGENCY: prefix overrides workflow rules."""
        context = {
            'event': {
                'tool': 'Bash',
                'input': {'command': 'EMERGENCY: fix production issue'}
            }
        }
        
        # Should allow even in planning step
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'planning', 'Bash', context
        )
        assert allowed
        assert 'Emergency override' in message
    
    def test_hotfix_prefix_overrides_rules(self):
        """Test that HOTFIX: prefix overrides workflow rules."""
        context = {
            'event': {
                'tool': 'Write',
                'input': {'file_path': 'fix.py', 'content': '# HOTFIX: critical bug'}
            }
        }
        
        # Check command in bash
        context = {
            'event': {
                'tool': 'Bash',
                'input': {'command': 'HOTFIX: apply security patch'}
            }
        }
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'review', 'Bash', context
        )
        assert allowed
        assert 'Emergency override' in message
    
    def test_production_down_pattern_overrides(self):
        """Test that production down patterns trigger override."""
        context = {
            'event': {
                'tool': 'Bash',
                'input': {'command': 'restart server - production is down'}
            }
        }
        
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'planning', 'Bash', context
        )
        assert allowed
        assert 'Emergency override' in message
    
    def test_case_insensitive_emergency_patterns(self):
        """Test that emergency patterns are case insensitive."""
        # Test lowercase
        context = {
            'event': {
                'tool': 'Bash',
                'input': {'command': 'emergency: database corruption'}
            }
        }
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'planning', 'Bash', context
        )
        assert allowed
        
        # Test mixed case
        context = {
            'event': {
                'tool': 'Bash',
                'input': {'command': 'Security Vulnerability detected'}
            }
        }
        allowed, message, _ = WorkflowRules.evaluate_tool_use(
            'review', 'Bash', context
        )
        assert allowed
    
    # Test Step Completion Detection
    
    def test_is_step_complete_planning(self):
        """Test planning step completion detection."""
        # Not complete without progress
        is_complete, message = WorkflowRules.is_step_complete('planning', {})
        assert not is_complete
        
        # Complete when marked by post_tool_use
        is_complete, message = WorkflowRules.is_step_complete(
            'planning', {'planning_complete': True}
        )
        assert is_complete
        assert 'Planning complete' in message
    
    def test_is_step_complete_implementation(self):
        """Test implementation step completion detection."""
        # Not complete without files
        is_complete, message = WorkflowRules.is_step_complete('implementation', {})
        assert not is_complete
        
        # Complete when files modified
        is_complete, message = WorkflowRules.is_step_complete(
            'implementation', {'files_modified': ['app.py', 'test.py']}
        )
        assert is_complete
        assert '2 files modified' in message
    
    def test_is_step_complete_validation(self):
        """Test validation step completion detection."""
        # Not complete without tests
        is_complete, message = WorkflowRules.is_step_complete('validation', {})
        assert not is_complete
        
        # Complete when tests run
        is_complete, message = WorkflowRules.is_step_complete(
            'validation', {'tests_run': True}
        )
        assert is_complete
        assert 'Validation complete' in message
    
    def test_is_step_complete_review(self):
        """Test review step completion detection."""
        # Not complete without review
        is_complete, message = WorkflowRules.is_step_complete('review', {})
        assert not is_complete
        
        # Complete when review done
        is_complete, message = WorkflowRules.is_step_complete(
            'review', {'review_complete': True}
        )
        assert is_complete
        assert 'Review complete' in message
    
    def test_is_step_complete_refinement(self):
        """Test refinement step completion detection."""
        # Not complete without edits
        is_complete, message = WorkflowRules.is_step_complete('refinement', {})
        assert not is_complete
        
        # Complete when Edit used
        is_complete, message = WorkflowRules.is_step_complete(
            'refinement', {'tools_used': ['Read', 'Edit', 'Bash']}
        )
        assert is_complete
        assert 'Refinement complete' in message
        
        # Also complete with MultiEdit
        is_complete, message = WorkflowRules.is_step_complete(
            'refinement', {'tools_used': ['MultiEdit']}
        )
        assert is_complete
    
    def test_is_step_complete_integration(self):
        """Test integration step completion detection."""
        # Not complete without git operations
        is_complete, message = WorkflowRules.is_step_complete('integration', {})
        assert not is_complete
        
        # Complete with git tools
        is_complete, message = WorkflowRules.is_step_complete(
            'integration', {'tools_used': ['GitCommit', 'GitPush']}
        )
        assert is_complete
        assert 'Integration complete' in message
        
        # Also complete with Bash git commands
        is_complete, message = WorkflowRules.is_step_complete(
            'integration', {'tools_used': ['Bash'], 'git_commands_run': True}
        )
        assert is_complete
    
    # Test Compliance Scoring
    
    def test_compliance_score_perfect(self):
        """Test perfect compliance score."""
        metrics = {
            'tools_allowed': 100,
            'tools_blocked': 0,
            'emergency_overrides': 0,
            'workflow_violations': 0
        }
        score = WorkflowRules.calculate_compliance_score(metrics)
        assert score == 100.0
    
    def test_compliance_score_with_blocks(self):
        """Test compliance score with blocked tools."""
        metrics = {
            'tools_allowed': 80,
            'tools_blocked': 20,
            'emergency_overrides': 0,
            'workflow_violations': 0
        }
        score = WorkflowRules.calculate_compliance_score(metrics)
        assert score == 80.0
    
    def test_compliance_score_with_violations(self):
        """Test compliance score with workflow violations."""
        metrics = {
            'tools_allowed': 90,
            'tools_blocked': 10,
            'emergency_overrides': 0,
            'workflow_violations': 2  # -20 points
        }
        score = WorkflowRules.calculate_compliance_score(metrics)
        assert score == 70.0  # 90% - 20
    
    def test_compliance_score_with_overrides(self):
        """Test compliance score with emergency overrides."""
        metrics = {
            'tools_allowed': 95,
            'tools_blocked': 5,
            'emergency_overrides': 5,  # -10 points
            'workflow_violations': 0
        }
        score = WorkflowRules.calculate_compliance_score(metrics)
        assert score == 85.0  # 95% - 10
    
    def test_compliance_score_bounds(self):
        """Test compliance score stays within 0-100 bounds."""
        # Test lower bound
        metrics = {
            'tools_allowed': 10,
            'tools_blocked': 90,
            'emergency_overrides': 0,
            'workflow_violations': 10  # Would be -90
        }
        score = WorkflowRules.calculate_compliance_score(metrics)
        assert score == 0.0
        
        # Test upper bound (already tested in perfect score)
        metrics = {
            'tools_allowed': 100,
            'tools_blocked': 0,
            'emergency_overrides': 0,
            'workflow_violations': 0
        }
        score = WorkflowRules.calculate_compliance_score(metrics)
        assert score == 100.0
    
    def test_compliance_score_no_actions(self):
        """Test compliance score with no actions taken."""
        metrics = {
            'tools_allowed': 0,
            'tools_blocked': 0,
            'emergency_overrides': 0,
            'workflow_violations': 0
        }
        score = WorkflowRules.calculate_compliance_score(metrics)
        assert score == 100.0  # Default to perfect when no actions
    
    # Test Helper Methods
    
    def test_get_step_completion_indicators(self):
        """Test step completion indicators structure."""
        for step in ['planning', 'implementation', 'validation', 'review', 'refinement', 'integration']:
            indicators = WorkflowRules.get_step_completion_indicators(step)
            
            # Should have required keys
            assert 'required_actions' in indicators
            assert 'completion_signals' in indicators
            assert 'next_step' in indicators
            
            # Should have content
            assert len(indicators['required_actions']) > 0
            assert len(indicators['completion_signals']) > 0
            assert indicators['next_step'] in WorkflowRules.WORKFLOW_RULES
    
    def test_workflow_sequence_integrity(self):
        """Test that workflow steps form a proper cycle."""
        # Check each step leads to the next correctly
        expected_sequence = [
            ('planning', 'implementation'),
            ('implementation', 'validation'),
            ('validation', 'review'),
            ('review', 'refinement'),
            ('refinement', 'integration'),
            ('integration', 'planning')  # Cycle back
        ]
        
        for current, expected_next in expected_sequence:
            indicators = WorkflowRules.get_step_completion_indicators(current)
            assert indicators['next_step'] == expected_next
    
    def test_unknown_workflow_step(self):
        """Test handling of unknown workflow steps."""
        # Should allow by default for unknown steps
        allowed, message, suggestions = WorkflowRules.evaluate_tool_use(
            'unknown_step', 'Write', {}
        )
        assert allowed
        assert 'No rules defined' in message
        
        # Completion indicators should return empty dict
        indicators = WorkflowRules.get_step_completion_indicators('unknown_step')
        assert indicators == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])