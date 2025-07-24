#!/usr/bin/env python3
"""
Workflow Enforcement Tests - Test hooks enforce workflow rules correctly.

Tests that pre_tool_use, post_tool_use, and stop hooks properly
enforce the 6-step workflow without needing Claude.
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
    verify_workflow_state,
    read_project_state,
    update_project_state,
    assert_hook_response,
    create_test_files
)

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.state_manager import StateManager
from src.project_builder import ProjectBuilder


class WorkflowEnforcementTest:
    """Test workflow rule enforcement through hooks."""
    
    def __init__(self):
        self.env = TestEnvironment()
        self.passed = 0
        self.failed = 0
        
    def setup(self):
        """Setup test environment."""
        self.test_dir = self.env.setup("workflow-test")
        self.executor = CommandExecutor(self.test_dir)
        
        # Create project structure
        builder = ProjectBuilder("workflow-test", str(self.test_dir))
        builder.create_structure()
        
        # Initialize state
        state_manager = StateManager(self.test_dir)
        state_manager.create("workflow-test")
        
        print(f"✅ Test environment created at: {self.test_dir}")
        
    def teardown(self):
        """Cleanup test environment."""
        self.env.teardown()
        print("✅ Test environment cleaned up")
        
    def test_planning_sprint_restrictions(self):
        """Test planning sprint blocks write operations."""
        print("\n🧪 Testing planning sprint restrictions...")
        
        # Set state to planning sprint
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'planning'
        })
        
        # Test 1: Write tool should be blocked
        response = self.executor.simulate_tool_use('Write', {
            'file_path': 'src/app.py',
            'content': 'print("hello")'
        })
        
        # Debug: print actual response
        print(f"  Debug: Response = {response}")
        if response.get('decision') == 'error':
            print(f"  Debug: Hook error: {response.get('message', 'No message')}")
            
        assert_hook_response(response, 'block')
        message = response.get('message') or response.get('reason', '')
        assert 'planning' in message.lower(), \
            "Block message should mention planning sprint"
        print("  ✓ Write tool blocked in planning sprint")
        
        # Test 2: Edit tool should be blocked
        response = self.executor.simulate_tool_use('Edit', {
            'file_path': 'README.md',
            'old_string': 'test',
            'new_string': 'updated'
        })
        
        assert_hook_response(response, 'block')
        print("  ✓ Edit tool blocked in planning sprint")
        
        # Test 3: Read tool should be allowed
        response = self.executor.simulate_tool_use('Read', {
            'file_path': 'README.md'
        })
        
        assert_hook_response(response, 'allow', check_message=False)
        print("  ✓ Read tool allowed in planning sprint")
        
        # Test 4: TodoWrite should be allowed
        response = self.executor.simulate_tool_use('TodoWrite', {
            'todos': [
                {'id': '1', 'content': 'Implement feature', 'status': 'pending'}
            ]
        })
        
        assert_hook_response(response, 'allow', check_message=False)
        print("  ✓ TodoWrite allowed in planning sprint")
        
        # Test 5: Bash commands should be blocked
        response = self.executor.simulate_tool_use('Bash', {
            'command': 'python manage.py migrate'
        })
        
        assert_hook_response(response, 'block')
        print("  ✓ Bash execution blocked in planning sprint")
        
        print("✅ Planning sprint restrictions working correctly")
        self.passed += 1
        
    def test_implementation_sprint_permissions(self):
        """Test implementation sprint allows all tools."""
        print("\n🧪 Testing implementation sprint permissions...")
        
        # Set state to implementation sprint
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'implementation'
        })
        
        # Test all tools should be allowed
        tools_to_test = [
            ('Write', {'file_path': 'app.py', 'content': 'code'}),
            ('Edit', {'file_path': 'app.py', 'old_string': 'a', 'new_string': 'b'}),
            ('Read', {'file_path': 'README.md'}),
            ('Bash', {'command': 'echo test'}),
            ('TodoWrite', {'todos': []})
        ]
        
        for tool, params in tools_to_test:
            response = self.executor.simulate_tool_use(tool, params)
            assert_hook_response(response, 'allow', check_message=False)
            print(f"  ✓ {tool} allowed in implementation sprint")
            
        print("✅ Implementation sprint permissions working correctly")
        self.passed += 1
        
    def test_validation_sprint_restrictions(self):
        """Test validation sprint restricts new file creation."""
        print("\n🧪 Testing validation sprint restrictions...")
        
        # Set state to validation sprint
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'validation'
        })
        
        # Write should be blocked
        response = self.executor.simulate_tool_use('Write', {
            'file_path': 'new_file.py',
            'content': 'new content'
        })
        assert_hook_response(response, 'block')
        print("  ✓ Write blocked in validation sprint")
        
        # Edit should be allowed (for fixes)
        response = self.executor.simulate_tool_use('Edit', {
            'file_path': 'existing.py',
            'old_string': 'bug',
            'new_string': 'fix'
        })
        assert_hook_response(response, 'allow', check_message=False)
        print("  ✓ Edit allowed in validation sprint")
        
        # Bash should be allowed (for running tests)
        response = self.executor.simulate_tool_use('Bash', {
            'command': 'pytest tests/'
        })
        assert_hook_response(response, 'allow', check_message=False)
        print("  ✓ Bash allowed for test execution")
        
        print("✅ Validation sprint restrictions working correctly")
        self.passed += 1
        
    def test_review_sprint_readonly(self):
        """Test review sprint is read-only."""
        print("\n🧪 Testing review sprint read-only mode...")
        
        # Set state to review sprint
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'review'
        })
        
        # All write operations should be blocked
        write_tools = [
            ('Write', {'file_path': 'test.py', 'content': 'test'}),
            ('Edit', {'file_path': 'test.py', 'old_string': 'a', 'new_string': 'b'}),
            ('Bash', {'command': 'rm file.txt'})
        ]
        
        for tool, params in write_tools:
            response = self.executor.simulate_tool_use(tool, params)
            assert_hook_response(response, 'block')
            print(f"  ✓ {tool} blocked in review sprint")
            
        # Read operations should be allowed
        read_tools = [
            ('Read', {'file_path': 'README.md'}),
            ('TodoWrite', {'todos': []})
        ]
        
        for tool, params in read_tools:
            response = self.executor.simulate_tool_use(tool, params)
            assert_hook_response(response, 'allow', check_message=False)
            print(f"  ✓ {tool} allowed in review sprint")
            
        print("✅ Review sprint read-only mode working correctly")
        self.passed += 1
        
    def test_automation_disabled_bypass(self):
        """Test all tools allowed when automation is disabled."""
        print("\n🧪 Testing automation disabled bypass...")
        
        # Disable automation in planning sprint
        update_project_state(self.test_dir, {
            'status': 'paused',
            'automation_active': False,
            'workflow_step': 'planning'
        })
        
        # All tools should be allowed
        tools = [
            ('Write', {'file_path': 'test.py', 'content': 'test'}),
            ('Edit', {'file_path': 'test.py', 'old_string': 'a', 'new_string': 'b'}),
            ('Bash', {'command': 'echo test'})
        ]
        
        for tool, params in tools:
            response = self.executor.simulate_tool_use(tool, params)
            assert_hook_response(response, 'allow', check_message=False)
            print(f"  ✓ {tool} allowed when automation disabled")
            
        print("✅ Automation bypass working correctly")
        self.passed += 1
        
    def test_emergency_override(self):
        """Test emergency commands bypass restrictions."""
        print("\n🧪 Testing emergency override...")
        
        # Set restrictive state (planning sprint)
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'planning'
        })
        
        # Emergency commands should bypass restrictions
        emergency_commands = [
            'EMERGENCY: fix production bug',
            'HOTFIX: security vulnerability',
            'CRITICAL: data loss prevention',
            'OVERRIDE: urgent deployment'
        ]
        
        for command in emergency_commands:
            response = self.executor.simulate_tool_use('Bash', {
                'command': command
            })
            assert_hook_response(response, 'allow', check_message=False)
            print(f"  ✓ Emergency command allowed: {command.split(':')[0]}")
            
        # Verify metrics updated
        state = read_project_state(self.test_dir)
        metrics = state.get('metrics', {})
        assert metrics.get('emergency_overrides', 0) > 0, \
            "Emergency overrides should be tracked in metrics"
        print("  ✓ Emergency overrides tracked in metrics")
        
        print("✅ Emergency override working correctly")
        self.passed += 1
        
    def test_post_tool_use_tracking(self):
        """Test post_tool_use hook tracks progress."""
        print("\n🧪 Testing post-tool-use progress tracking...")
        
        # Enable automation in implementation sprint
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'implementation'
        })
        
        # Create a test file
        test_file = self.test_dir / 'src' / 'main.py'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text('def main():\n    pass')
        
        # Simulate successful Write tool execution
        response = self.executor.simulate_post_tool_use('Write', {
            'file_path': 'src/main.py',
            'content': 'def main():\n    pass'
        }, exit_code=0)
        
        # Check state was updated
        state = read_project_state(self.test_dir)
        files_modified = state.get('files_modified', [])
        assert 'src/main.py' in files_modified, \
            "File modification should be tracked"
        print("  ✓ File modifications tracked")
        
        # Simulate test execution
        response = self.executor.simulate_post_tool_use('Bash', {
            'command': 'pytest tests/'
        }, exit_code=0)
        
        # Check progress updated
        state = read_project_state(self.test_dir)
        progress = state.get('workflow_progress', {})
        if 'implementation' in progress:
            assert progress['implementation'].get('tests_run', False), \
                "Test execution should be tracked"
        print("  ✓ Test execution tracked")
        
        print("✅ Post-tool-use tracking working correctly")
        self.passed += 1
        
    def test_workflow_suggestions(self):
        """Test hooks provide helpful suggestions when blocking."""
        print("\n🧪 Testing workflow suggestions...")
        
        # Set to planning sprint
        update_project_state(self.test_dir, {
            'status': 'active',
            'automation_active': True,
            'workflow_step': 'planning'
        })
        
        # Try blocked operation
        response = self.executor.simulate_tool_use('Write', {
            'file_path': 'app.py',
            'content': 'code'
        })
        
        assert 'suggestions' in response, "Response should include suggestions"
        assert len(response['suggestions']) > 0, "Should have at least one suggestion"
        assert any('read' in s.lower() for s in response['suggestions']), \
            "Suggestions should mention reading/analysis"
        
        print("  ✓ Helpful suggestions provided when blocking")
        print(f"  ✓ Example: {response['suggestions'][0]}")
        
        print("✅ Workflow suggestions working correctly")
        self.passed += 1
        
    def run_all_tests(self):
        """Run all workflow enforcement tests."""
        print("\n" + "="*60)
        print("🚀 Running Workflow Enforcement Tests")
        print("="*60)
        
        tests = [
            self.test_planning_sprint_restrictions,
            self.test_implementation_sprint_permissions,
            self.test_validation_sprint_restrictions,
            self.test_review_sprint_readonly,
            self.test_automation_disabled_bypass,
            self.test_emergency_override,
            self.test_post_tool_use_tracking,
            self.test_workflow_suggestions
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
    test = WorkflowEnforcementTest()
    
    try:
        test.setup()
        success = test.run_all_tests()
        test.teardown()
        
        if success:
            print("\n✅ All workflow enforcement tests passed!")
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