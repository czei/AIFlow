#!/usr/bin/env python3
"""
Workflow Progression Tests - Test automatic workflow advancement.

Tests that the Stop hook properly advances workflow steps based on
progress indicators and completion criteria.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from command_executor import CommandExecutor
from test_utilities import (
    TestEnvironment,
    read_project_state,
    update_project_state,
    wait_for_state_change
)

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from state_manager import StateManager
from project_builder import ProjectBuilder


class WorkflowProgressionTest:
    """Test automatic workflow step advancement."""
    
    def __init__(self):
        self.env = TestEnvironment()
        self.passed = 0
        self.failed = 0
        
    def setup(self):
        """Setup test environment."""
        self.test_dir = self.env.setup("progression-test")
        self.executor = CommandExecutor(self.test_dir)
        
        # Create project
        builder = ProjectBuilder("progression-test", str(self.test_dir))
        builder.create_structure()
        
        state_manager = StateManager(self.test_dir)
        state_manager.create("progression-test")
        
        print(f"✅ Test environment created at: {self.test_dir}")
        
    def teardown(self):
        """Cleanup test environment."""
        self.env.teardown()
        print("✅ Test environment cleaned up")
        
    def test_planning_to_implementation(self):
        """Test advancement from planning to implementation."""
        print("\n🧪 Testing planning → implementation advancement...")
        
        # Setup planning sprint with completion indicators
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'planning',
            'workflow_progress': {
                'planning': {
                    'planning_complete': True,
                    'tools_used': ['TodoWrite', 'Read', 'Grep']
                }
            }
        })
        
        # Run Stop hook
        response = self.executor.simulate_stop_hook("Planning sprint complete")
        
        # Verify workflow advanced
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'implementation', \
            f"Expected workflow_step 'implementation' but got '{state['workflow_step']}'"
        
        print("  ✓ Workflow advanced from planning to implementation")
        print("  ✓ Stop hook detected planning completion")
        
        print("✅ Planning advancement test passed")
        self.passed += 1
        
    def test_implementation_to_validation(self):
        """Test advancement from implementation to validation."""
        print("\n🧪 Testing implementation → validation advancement...")
        
        # Setup implementation sprint with progress
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'implementation',
            'workflow_progress': {
                'implementation': {
                    'files_modified': ['src/main.py', 'src/utils.py'],
                    'tests_created': ['tests/test_main.py'],
                    'tools_used': ['Write', 'Edit']
                }
            }
        })
        
        # Run Stop hook
        response = self.executor.simulate_stop_hook("Implementation complete")
        
        # Verify advancement
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'validation', \
            f"Expected 'validation' but got '{state['workflow_step']}'"
        
        print("  ✓ Workflow advanced from implementation to validation")
        print("  ✓ Files modified tracked for advancement")
        
        print("✅ Implementation advancement test passed")
        self.passed += 1
        
    def test_validation_to_review(self):
        """Test advancement from validation to review."""
        print("\n🧪 Testing validation → review advancement...")
        
        # Setup validation sprint with test execution
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'validation',
            'workflow_progress': {
                'validation': {
                    'tests_run': True,
                    'test_results': 'All tests passed',
                    'tools_used': ['Bash']
                }
            }
        })
        
        # Run Stop hook
        response = self.executor.simulate_stop_hook("Tests completed")
        
        # Verify advancement
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'review', \
            f"Expected 'review' but got '{state['workflow_step']}'"
        
        print("  ✓ Workflow advanced from validation to review")
        print("  ✓ Test execution tracked for advancement")
        
        print("✅ Validation advancement test passed")
        self.passed += 1
        
    def test_review_to_refinement(self):
        """Test advancement from review to refinement."""
        print("\n🧪 Testing review → refinement advancement...")
        
        # Setup review sprint with completion
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'review',
            'workflow_progress': {
                'review': {
                    'review_complete': True,
                    'issues_found': ['Performance optimization needed'],
                    'tools_used': ['Read', 'TodoWrite']
                }
            }
        })
        
        # Run Stop hook
        response = self.executor.simulate_stop_hook("Review complete")
        
        # Verify advancement
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'refinement', \
            f"Expected 'refinement' but got '{state['workflow_step']}'"
        
        print("  ✓ Workflow advanced from review to refinement")
        print("  ✓ Review completion tracked")
        
        print("✅ Review advancement test passed")
        self.passed += 1
        
    def test_refinement_to_integration(self):
        """Test advancement from refinement to integration."""
        print("\n🧪 Testing refinement → integration advancement...")
        
        # Setup refinement sprint with edits
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'refinement',
            'workflow_progress': {
                'refinement': {
                    'refinements_applied': True,
                    'tools_used': ['Edit', 'MultiEdit'],
                    'files_refined': ['src/main.py']
                }
            }
        })
        
        # Run Stop hook
        response = self.executor.simulate_stop_hook("Refinements complete")
        
        # Verify advancement
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'integration', \
            f"Expected 'integration' but got '{state['workflow_step']}'"
        
        print("  ✓ Workflow advanced from refinement to integration")
        print("  ✓ Edit operations tracked for advancement")
        
        print("✅ Refinement advancement test passed")
        self.passed += 1
        
    def test_integration_completion(self):
        """Test integration sprint completion."""
        print("\n🧪 Testing integration sprint completion...")
        
        # Setup integration sprint with git operations
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'integration',
            'current_sprint': '01',
            'workflow_progress': {
                'integration': {
                    'git_commands_run': True,
                    'tools_used': ['Bash'],
                    'committed': True
                }
            }
        })
        
        # Run Stop hook
        response = self.executor.simulate_stop_hook("Integration complete")
        
        # Verify sprint completion
        state = read_project_state(self.test_dir)
        assert '01' in state.get('completed_sprints', []), \
            "Sprint should be marked as completed"
        assert state['workflow_step'] == 'planning', \
            "Should cycle back to planning for next sprint"
        
        print("  ✓ Sprint marked as completed")
        print("  ✓ Workflow cycled back to planning")
        
        print("✅ Integration completion test passed")
        self.passed += 1
        
    def test_incomplete_step_blocking(self):
        """Test that incomplete steps don't advance."""
        print("\n🧪 Testing incomplete step blocking...")
        
        # Setup planning without completion indicators
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'planning',
            'workflow_progress': {
                'planning': {
                    'planning_complete': False,
                    'tools_used': ['Read']  # No TodoWrite
                }
            }
        })
        
        # Run Stop hook
        response = self.executor.simulate_stop_hook("Still working...")
        
        # Verify no advancement
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'planning', \
            "Workflow should not advance without completion indicators"
        
        print("  ✓ Incomplete step blocked from advancing")
        print("  ✓ Completion criteria enforced")
        
        print("✅ Incomplete blocking test passed")
        self.passed += 1
        
    def test_progress_preservation(self):
        """Test that progress is preserved across steps."""
        print("\n🧪 Testing progress preservation...")
        
        # Setup with existing progress
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'planning',
            'files_modified': ['existing.py'],
            'acceptance_criteria_passed': ['compilation'],
            'workflow_progress': {
                'planning': {
                    'planning_complete': True
                }
            }
        })
        
        # Advance workflow
        response = self.executor.simulate_stop_hook("Planning done")
        
        # Verify progress preserved
        state = read_project_state(self.test_dir)
        assert 'existing.py' in state.get('files_modified', []), \
            "Files modified should be preserved"
        assert 'compilation' in state.get('acceptance_criteria_passed', []), \
            "Quality gates should be preserved"
        
        print("  ✓ Files modified preserved across steps")
        print("  ✓ Quality gates preserved")
        
        print("✅ Progress preservation test passed")
        self.passed += 1
        
    def test_manual_sprint_transition(self):
        """Test manual sprint transitions."""
        print("\n🧪 Testing manual sprint transitions...")
        
        # Use StateManager directly for sprint transition
        state_manager = StateManager(self.test_dir)
        
        # Start in sprint 01
        update_project_state(self.test_dir, {
            'current_sprint': '01',
            'completed_sprints': []
        })
        
        # Transition to sprint 02
        updated_state = state_manager.transition_sprint('02')
        
        assert updated_state['current_sprint'] == '02', \
            "Sprint should transition to 02"
        assert '01' in updated_state['completed_sprints'], \
            "Sprint 01 should be marked completed"
        assert updated_state['workflow_step'] == 'planning', \
            "Should reset to planning for new sprint"
        
        print("  ✓ Manual sprint transition successful")
        print("  ✓ Previous sprint marked completed")
        print("  ✓ Workflow reset for new sprint")
        
        print("✅ Manual transition test passed")
        self.passed += 1
        
    def run_all_tests(self):
        """Run all workflow progression tests."""
        print("\n" + "="*60)
        print("🚀 Running Workflow Progression Tests")
        print("="*60)
        
        tests = [
            self.test_planning_to_implementation,
            self.test_implementation_to_validation,
            self.test_validation_to_review,
            self.test_review_to_refinement,
            self.test_refinement_to_integration,
            self.test_integration_completion,
            self.test_incomplete_step_blocking,
            self.test_progress_preservation,
            self.test_manual_sprint_transition
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test failed: {test.__name__}")
                print(f"   Error: {e}")
                import traceback
                traceback.print_exc()
                self.failed += 1
                
        print("\n" + "="*60)
        print(f"📊 Test Results: {self.passed} passed, {self.failed} failed")
        print("="*60)
        
        return self.failed == 0


def main():
    """Main test runner."""
    test = WorkflowProgressionTest()
    
    try:
        test.setup()
        success = test.run_all_tests()
        test.teardown()
        
        if success:
            print("\n✅ All workflow progression tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        test.teardown()
        sys.exit(2)


if __name__ == '__main__':
    main()