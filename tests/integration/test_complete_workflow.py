#!/usr/bin/env python3
"""
Complete Workflow Test - Test full 6-step workflow from start to finish.

Simulates a complete development cycle through all workflow steps,
verifying that the system works end-to-end.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from command_executor import CommandExecutor
from test_utilities import (
    TestEnvironment,
    read_project_state,
    update_project_state,
    create_test_files
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.state_manager import StateManager
from src.project_builder import ProjectBuilder


class CompleteWorkflowTest:
    """Test complete 6-step workflow execution."""
    
    def __init__(self):
        self.env = TestEnvironment()
        self.passed = 0
        self.failed = 0
        
    def setup(self):
        """Setup test environment."""
        self.test_dir = self.env.setup("complete-workflow")
        self.executor = CommandExecutor(self.test_dir)
        
        # Create project
        builder = ProjectBuilder("calculator-app", str(self.test_dir))
        builder.create_structure()
        
        state_manager = StateManager(self.test_dir)
        state_manager.create("calculator-app")
        
        # Start project
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'planning',
            'current_sprint': '01'  # Ensure current_sprint is set
        })
        
        print(f"✅ Test environment created at: {self.test_dir}")
        
    def teardown(self):
        """Cleanup test environment."""
        self.env.teardown()
        print("✅ Test environment cleaned up")
        
    def simulate_planning_sprint(self):
        """Simulate planning sprint activities."""
        print("\n📋 Sprint 1: Planning")
        
        # Simulate reading existing code
        response = self.executor.simulate_tool_use('Read', {
            'file_path': 'README.md'
        })
        assert response['decision'] == 'allow', "Read should be allowed in planning"
        print("  ✓ Read existing documentation")
        
        # Simulate creating todo list
        response = self.executor.simulate_tool_use('TodoWrite', {
            'todos': [
                {'id': '1', 'content': 'Create Calculator class', 'status': 'pending'},
                {'id': '2', 'content': 'Implement add method', 'status': 'pending'},
                {'id': '3', 'content': 'Implement subtract method', 'status': 'pending'},
                {'id': '4', 'content': 'Write unit tests', 'status': 'pending'}
            ]
        })
        assert response['decision'] == 'allow', "TodoWrite should be allowed"
        print("  ✓ Created implementation todo list")
        
        # Update progress
        update_project_state(self.test_dir, {
            'workflow_progress': {
                'planning': {
                    'planning_complete': True,
                    'tools_used': ['Read', 'TodoWrite']
                }
            }
        })
        
        # Advance workflow
        self.executor.simulate_stop_hook("Planning complete")
        
        # Verify advancement
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'implementation', \
            "Should advance to implementation"
        print("  ✓ Advanced to implementation sprint")
        
    def simulate_implementation_sprint(self):
        """Simulate implementation sprint activities."""
        print("\n💻 Sprint 2: Implementation")
        
        # Create Calculator class
        response = self.executor.simulate_tool_use('Write', {
            'file_path': 'src/calculator.py',
            'content': '''class Calculator:
    """Simple calculator implementation."""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
        
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b
'''
        })
        assert response['decision'] == 'allow', "Write should be allowed"
        
        # Actually create the file for testing
        calc_file = self.test_dir / 'src' / 'calculator.py'
        calc_file.parent.mkdir(parents=True, exist_ok=True)
        # Use the content we defined above, not from response
        calc_content = '''class Calculator:
    """Simple calculator implementation."""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
        
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b
'''
        calc_file.write_text(calc_content)
        print("  ✓ Created Calculator class")
        
        # Create tests
        response = self.executor.simulate_tool_use('Write', {
            'file_path': 'tests/test_calculator.py',
            'content': '''import sys
sys.path.append('../src')
from calculator import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0

def test_subtract():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
    assert calc.subtract(0, 5) == -5
'''
        })
        
        # Create test file
        test_file = self.test_dir / 'tests' / 'test_calculator.py'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        # Use the content we defined above, not from response
        test_content = '''import sys
sys.path.append('../src')
from calculator import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0

def test_subtract():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
    assert calc.subtract(0, 5) == -5
'''
        test_file.write_text(test_content)
        print("  ✓ Created unit tests")
        
        # Track progress
        self.executor.simulate_post_tool_use('Write', {
            'file_path': 'src/calculator.py'
        }, exit_code=0)
        
        self.executor.simulate_post_tool_use('Write', {
            'file_path': 'tests/test_calculator.py'
        }, exit_code=0)
        
        # Update progress
        update_project_state(self.test_dir, {
            'workflow_progress': {
                'implementation': {
                    'files_modified': ['src/calculator.py', 'tests/test_calculator.py'],
                    'tools_used': ['Write']
                }
            }
        })
        
        # Advance workflow
        self.executor.simulate_stop_hook("Implementation complete")
        
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'validation', "Should advance to validation"
        print("  ✓ Advanced to validation sprint")
        
    def simulate_validation_sprint(self):
        """Simulate validation sprint activities."""
        print("\n🧪 Sprint 3: Validation")
        
        # Run tests
        response = self.executor.simulate_tool_use('Bash', {
            'command': 'cd tests && python -m pytest test_calculator.py -v'
        })
        assert response['decision'] == 'allow', "Bash should be allowed for tests"
        print("  ✓ Executed unit tests")
        
        # Track test execution
        self.executor.simulate_post_tool_use('Bash', {
            'command': 'pytest'
        }, exit_code=0)
        
        # Update progress
        update_project_state(self.test_dir, {
            'workflow_progress': {
                'validation': {
                    'tests_run': True,
                    'test_results': 'All tests passed',
                    'tools_used': ['Bash']
                }
            },
            'acceptance_criteria_passed': ['existing_tests']
        })
        
        # Advance workflow
        self.executor.simulate_stop_hook("Validation complete")
        
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'review', "Should advance to review"
        print("  ✓ Tests passed, advanced to review")
        
    def simulate_review_sprint(self):
        """Simulate review sprint activities."""
        print("\n👀 Sprint 4: Review")
        
        # Read code for review
        response = self.executor.simulate_tool_use('Read', {
            'file_path': 'src/calculator.py'
        })
        assert response['decision'] == 'allow', "Read allowed in review"
        print("  ✓ Reviewed Calculator implementation")
        
        # Create review notes
        response = self.executor.simulate_tool_use('TodoWrite', {
            'todos': [
                {'id': 'r1', 'content': 'Add error handling for division by zero', 
                 'status': 'pending'},
                {'id': 'r2', 'content': 'Add type validation for inputs', 
                 'status': 'pending'}
            ]
        })
        print("  ✓ Created review feedback")
        
        # Update progress
        update_project_state(self.test_dir, {
            'workflow_progress': {
                'review': {
                    'review_complete': True,
                    'issues_found': ['Missing error handling', 'No input validation'],
                    'tools_used': ['Read', 'TodoWrite']
                }
            }
        })
        
        # Advance workflow
        self.executor.simulate_stop_hook("Review complete")
        
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'refinement', "Should advance to refinement"
        print("  ✓ Advanced to refinement sprint")
        
    def simulate_refinement_sprint(self):
        """Simulate refinement sprint activities."""
        print("\n🔧 Sprint 5: Refinement")
        
        # Apply review feedback
        response = self.executor.simulate_tool_use('Edit', {
            'file_path': 'src/calculator.py',
            'old_string': '    def add(self, a: float, b: float) -> float:\n        """Add two numbers."""\n        return a + b',
            'new_string': '''    def add(self, a: float, b: float) -> float:
        """Add two numbers with validation."""
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Arguments must be numbers")
        return a + b'''
        })
        assert response['decision'] == 'allow', "Edit allowed in refinement"
        print("  ✓ Added input validation")
        
        # Run tests again
        response = self.executor.simulate_tool_use('Bash', {
            'command': 'cd tests && python -m pytest test_calculator.py'
        })
        print("  ✓ Re-ran tests after refinements")
        
        # Update progress
        update_project_state(self.test_dir, {
            'workflow_progress': {
                'refinement': {
                    'refinements_applied': True,
                    'tools_used': ['Edit', 'Bash'],
                    'files_refined': ['src/calculator.py']
                }
            }
        })
        
        # Advance workflow
        self.executor.simulate_stop_hook("Refinements complete")
        
        state = read_project_state(self.test_dir)
        assert state['workflow_step'] == 'integration', "Should advance to integration"
        print("  ✓ Advanced to integration sprint")
        
    def simulate_integration_sprint(self):
        """Simulate integration sprint activities."""
        print("\n🔀 Sprint 6: Integration")
        
        # Final test run
        response = self.executor.simulate_tool_use('Bash', {
            'command': 'python -m pytest tests/ --tb=short'
        })
        assert response['decision'] == 'allow', "Bash allowed for final tests"
        print("  ✓ Ran final test suite")
        
        # Simulate git operations (normally blocked in real integration)
        print("  ✓ Would commit changes (simulated)")
        
        # Update progress
        update_project_state(self.test_dir, {
            'workflow_progress': {
                'integration': {
                    'final_tests_run': True,
                    'tools_used': ['Bash'],
                    'ready_to_commit': True,
                    'git_commands_run': True  # This triggers integration completion
                }
            },
            'acceptance_criteria_passed': [
                'existing_tests', 'compilation', 'review', 'integration'
            ]
        })
        
        # Complete sprint
        self.executor.simulate_stop_hook("Integration complete, ready to merge")
        
        state = read_project_state(self.test_dir)
        assert '01' in state.get('completed_sprints', []), \
            "Sprint 01 should be marked complete"
        assert state['workflow_step'] == 'planning', \
            "Should cycle back to planning for next sprint"
        print("  ✓ Sprint 01 completed successfully")
        print("  ✓ Ready for next sprint")
        
    def test_complete_workflow(self):
        """Run complete 6-step workflow test."""
        print("\n🚀 Testing Complete 6-Step Workflow")
        print("="*50)
        
        try:
            # Run all sprints in sequence
            self.simulate_planning_sprint()
            self.simulate_implementation_sprint()
            self.simulate_validation_sprint()
            self.simulate_review_sprint()
            self.simulate_refinement_sprint()
            self.simulate_integration_sprint()
            
            # Verify final state
            state = read_project_state(self.test_dir)
            
            # Check metrics
            assert len(state.get('files_modified', [])) > 0, \
                "Should have modified files"
            assert len(state.get('acceptance_criteria_passed', [])) >= 3, \
                "Should have passed quality gates"
            assert state.get('automation_cycles', 0) > 0, \
                "Should have automation cycles"
            
            print("\n✅ Complete workflow test passed!")
            print(f"  - Modified {len(state.get('files_modified', []))} files")
            print(f"  - Passed {len(state.get('acceptance_criteria_passed', []))} quality gates")
            print(f"  - Completed sprint: {state.get('completed_sprints', [])}")
            
            self.passed += 1
            
        except Exception as e:
            print(f"\n❌ Workflow test failed: {e}")
            import traceback
            traceback.print_exc()
            self.failed += 1
            
    def test_workflow_metrics(self):
        """Test that workflow metrics are tracked correctly."""
        print("\n📊 Testing Workflow Metrics")
        
        # Run a simplified workflow
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'planning',
            'metrics': {
                'tools_allowed': 0,
                'tools_blocked': 0,
                'emergency_overrides': 0
            }
        })
        
        # Track some tool usage
        response1 = self.executor.simulate_tool_use('Write', {
            'file_path': 'test.py',
            'content': 'print("test")'
        })  # Should be blocked in planning sprint
        print(f"  Write response: {response1}")
        
        response2 = self.executor.simulate_tool_use('Read', {'file_path': 'README.md'})  # Allowed
        print(f"  Read response: {response2}")
        
        response3 = self.executor.simulate_tool_use('Bash', {'command': 'EMERGENCY: fix'})  # Override
        print(f"  Bash response: {response3}")
        
        # Check metrics updated
        state = read_project_state(self.test_dir)
        metrics = state.get('metrics', {})
        print(f"  Current metrics: {metrics}")
        
        assert metrics.get('tools_blocked', 0) > 0, "Should track blocked tools"
        assert metrics.get('tools_allowed', 0) > 0, "Should track allowed tools"
        assert metrics.get('emergency_overrides', 0) > 0, "Should track overrides"
        
        print("  ✓ Tool usage metrics tracked")
        print(f"  ✓ Blocked: {metrics.get('tools_blocked', 0)}")
        print(f"  ✓ Allowed: {metrics.get('tools_allowed', 0)}")
        print(f"  ✓ Overrides: {metrics.get('emergency_overrides', 0)}")
        
        print("✅ Metrics tracking test passed")
        self.passed += 1
        
    def run_all_tests(self):
        """Run all complete workflow tests."""
        print("\n" + "="*60)
        print("🚀 Running Complete Workflow Tests")
        print("="*60)
        
        tests = [
            self.test_complete_workflow,
            self.test_workflow_metrics
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test failed: {test.__name__}")
                print(f"   Error: {e}")
                self.failed += 1
                
        print("\n" + "="*60)
        print(f"📊 Test Results: {self.passed} passed, {self.failed} failed")
        print("="*60)
        
        return self.failed == 0


def main():
    """Main test runner."""
    test = CompleteWorkflowTest()
    
    try:
        test.setup()
        success = test.run_all_tests()
        test.teardown()
        
        if success:
            print("\n✅ All complete workflow tests passed!")
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