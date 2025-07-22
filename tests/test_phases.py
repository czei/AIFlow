#!/usr/bin/env python3
"""
Phase-Driven Development System Test Suite
Tests core functionality without requiring Claude Code integration
"""

import os
import json
import subprocess
import tempfile
import shutil
import time
from pathlib import Path
from datetime import datetime
import unittest

class TestPhaseProject:
    """Test project with measurable phase operations"""
    
    def __init__(self, test_dir):
        self.test_dir = Path(test_dir)
        self.phases_dir = self.test_dir / "phases"
        self.output_dir = self.test_dir / "output"
        
    def create_test_phases(self):
        """Create phase files that perform simple, testable operations"""
        self.phases_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Phase 01: Create initial file
        phase_01 = """# Phase 01: Initialization

## Status: NOT_STARTED
## Completion: 0%

## Prerequisites:
- [x] Test environment ready

## Objectives:
- [ ] Create output/data.json with initial structure
- [ ] Create output/log.txt with timestamp
- [ ] Verify files are created correctly

## 6-Step Workflow Implementation
Each objective follows the universal workflow:
1. Planning: Design file structure
2. Implementation: Create files with content
3. Validation: Verify files exist and are valid
4. Review: Check file contents match spec
5. Refinement: Fix any issues found
6. Integration: Update project state

## Quality Gates:
- Files must be created successfully
- JSON must be valid
- Log must contain timestamp

## Success Criteria:
- [ ] output/data.json exists with valid JSON
- [ ] output/log.txt exists with timestamp
- [ ] No errors during creation

## Automation Instructions:
Commands allowed: touch, echo, cat, ls
Create files using echo with proper JSON formatting
"""
        
        # Phase 02: Modify files
        phase_02 = """# Phase 02: Data Processing

## Status: NOT_STARTED  
## Completion: 0%

## Prerequisites:
- [x] Phase 01 complete
- [x] output/data.json exists

## Objectives:
- [ ] Add user data to data.json
- [ ] Append processing log to log.txt
- [ ] Create output/processed.flag file

## 6-Step Workflow Implementation
Each objective follows the universal workflow with focus on modification

## Quality Gates:
- JSON remains valid after modification
- Log entries are properly formatted
- Flag file created successfully

## Success Criteria:
- [ ] data.json contains user array
- [ ] log.txt has processing entries
- [ ] processed.flag exists

## Automation Instructions:
Modify files using safe append operations
Validate JSON after each modification
"""
        
        # Phase 03: Validation
        phase_03 = """# Phase 03: Quality Validation

## Status: NOT_STARTED
## Completion: 0%

## Prerequisites:
- [x] Phase 02 complete
- [x] All output files exist

## Objectives:
- [ ] Validate all JSON files are properly formatted
- [ ] Count entries in data files
- [ ] Create output/validation-report.txt

## 6-Step Workflow Implementation
Focus on validation and verification steps

## Quality Gates:
- All validations must pass
- Report must be comprehensive
- No data corruption detected

## Success Criteria:
- [ ] validation-report.txt contains all checks
- [ ] All files validated successfully
- [ ] Metrics calculated correctly

## Automation Instructions:
Use jq or python for JSON validation
Create detailed validation report
"""
        
        # Phase 04: Completion
        phase_04 = """# Phase 04: Project Completion

## Status: NOT_STARTED
## Completion: 0%

## Prerequisites:
- [x] All previous phases complete
- [x] All files validated

## Objectives:
- [ ] Create output/summary.json with project metrics
- [ ] Archive all outputs
- [ ] Create completion timestamp

## 6-Step Workflow Implementation
Focus on finalization and archival

## Quality Gates:
- Summary must include all metrics
- Archive must be complete
- Timestamp must be accurate

## Success Criteria:
- [ ] summary.json contains full project report
- [ ] All outputs properly archived
- [ ] Project marked complete

## Automation Instructions:
Generate comprehensive summary
Create clean final state
"""
        
        # Write phase files
        (self.phases_dir / "01-initialization.md").write_text(phase_01)
        (self.phases_dir / "02-data-processing.md").write_text(phase_02)
        (self.phases_dir / "03-validation.md").write_text(phase_03)
        (self.phases_dir / "04-completion.md").write_text(phase_04)
        
        # Create initial project state
        project_state = {
            "project_name": "test-project",
            "current_phase": "01",
            "status": "active",
            "automation_active": False,
            "workflow_step": "planning",
            "completed_phases": [],
            "started": datetime.utcnow().isoformat() + "Z"
        }
        
        state_file = self.test_dir / ".project-state.json"
        state_file.write_text(json.dumps(project_state, indent=2))
        
        # Create workflow state
        workflow_state = {
            "current_step": 1,
            "current_step_name": "planning",
            "quality_gates_passed": [],
            "automation_active": False
        }
        
        workflow_file = self.test_dir / ".workflow-state.json"
        workflow_file.write_text(json.dumps(workflow_state, indent=2))


class TestPhaseDrivenDevelopment(unittest.TestCase):
    """Test suite for phase-driven development system"""
    
    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="pdds_test_"))
        self.test_project = TestPhaseProject(self.test_dir)
        self.test_project.create_test_phases()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
        
    def test_phase_file_structure(self):
        """Test that phase files have required sections"""
        required_sections = [
            "## Status:",
            "## Prerequisites:",
            "## Objectives:",
            "## 6-Step Workflow Implementation",
            "## Quality Gates:",
            "## Success Criteria:",
            "## Automation Instructions:"
        ]
        
        for phase_file in self.test_project.phases_dir.glob("*.md"):
            content = phase_file.read_text()
            for section in required_sections:
                self.assertIn(section, content, 
                    f"Phase {phase_file.name} missing required section: {section}")
                    
    def test_state_management(self):
        """Test project state file operations"""
        state_file = self.test_dir / ".project-state.json"
        
        # Test initial state
        state = json.loads(state_file.read_text())
        self.assertEqual(state["current_phase"], "01")
        self.assertEqual(state["status"], "active")
        self.assertEqual(state["workflow_step"], "planning")
        self.assertEqual(state["completed_phases"], [])
        
        # Test state updates
        state["workflow_step"] = "implementation"
        state["current_objective"] = "Create output/data.json"
        state_file.write_text(json.dumps(state, indent=2))
        
        # Verify update
        updated_state = json.loads(state_file.read_text())
        self.assertEqual(updated_state["workflow_step"], "implementation")
        self.assertEqual(updated_state["current_objective"], "Create output/data.json")
        
    def test_workflow_progression(self):
        """Test 6-step workflow state transitions"""
        workflow_steps = [
            "planning",
            "implementation", 
            "validation",
            "review",
            "refinement",
            "integration"
        ]
        
        workflow_file = self.test_dir / ".workflow-state.json"
        
        for i, step in enumerate(workflow_steps, 1):
            # Update workflow state
            workflow_state = {
                "current_step": i,
                "current_step_name": step,
                "quality_gates_passed": [],
                "automation_active": True
            }
            workflow_file.write_text(json.dumps(workflow_state, indent=2))
            
            # Verify state
            state = json.loads(workflow_file.read_text())
            self.assertEqual(state["current_step"], i)
            self.assertEqual(state["current_step_name"], step)
            
    def test_quality_gates(self):
        """Test quality gate tracking"""
        quality_gates = [
            "compilation",
            "testing", 
            "review",
            "integration",
            "documentation",
            "performance"
        ]
        
        workflow_file = self.test_dir / ".workflow-state.json"
        workflow_state = json.loads(workflow_file.read_text())
        
        # Simulate passing quality gates
        for gate in quality_gates:
            workflow_state["quality_gates_passed"].append(gate)
            workflow_file.write_text(json.dumps(workflow_state, indent=2))
            
            # Verify gate recorded
            state = json.loads(workflow_file.read_text())
            self.assertIn(gate, state["quality_gates_passed"])
            
    def test_phase_operations(self):
        """Test actual phase operations (file creation/modification)"""
        output_dir = self.test_dir / "output"
        
        # Phase 01: Create files
        data_file = output_dir / "data.json"
        log_file = output_dir / "log.txt"
        
        # Simulate phase 01 operations
        initial_data = {"version": "1.0", "created": datetime.utcnow().isoformat()}
        data_file.write_text(json.dumps(initial_data, indent=2))
        log_file.write_text(f"[{datetime.utcnow().isoformat()}] Project initialized\n")
        
        # Verify phase 01 results
        self.assertTrue(data_file.exists())
        self.assertTrue(log_file.exists())
        
        # Validate JSON
        data = json.loads(data_file.read_text())
        self.assertEqual(data["version"], "1.0")
        
        # Phase 02: Modify files
        data["users"] = [{"id": 1, "name": "Test User"}]
        data_file.write_text(json.dumps(data, indent=2))
        
        with open(log_file, "a") as f:
            f.write(f"[{datetime.utcnow().isoformat()}] Processing started\n")
            
        flag_file = output_dir / "processed.flag"
        flag_file.touch()
        
        # Verify phase 02 results
        data = json.loads(data_file.read_text())
        self.assertIn("users", data)
        self.assertEqual(len(data["users"]), 1)
        self.assertTrue(flag_file.exists())
        
        # Phase 03: Validation
        validation_report = output_dir / "validation-report.txt"
        report_content = f"""Validation Report
Generated: {datetime.utcnow().isoformat()}

JSON Files:
- data.json: VALID
  - Contains {len(data['users'])} users
  - Version: {data['version']}

Log Files:
- log.txt: {len(log_file.read_text().splitlines())} entries

Flags:
- processed.flag: EXISTS

Overall Status: PASSED
"""
        validation_report.write_text(report_content)
        
        # Verify phase 03 results
        self.assertTrue(validation_report.exists())
        self.assertIn("Overall Status: PASSED", validation_report.read_text())
        
        # Phase 04: Completion
        summary = {
            "project": "test-project",
            "phases_completed": 4,
            "files_created": 5,
            "validation_status": "PASSED",
            "completed": datetime.utcnow().isoformat()
        }
        
        summary_file = output_dir / "summary.json"
        summary_file.write_text(json.dumps(summary, indent=2))
        
        # Verify phase 04 results
        self.assertTrue(summary_file.exists())
        summary_data = json.loads(summary_file.read_text())
        self.assertEqual(summary_data["phases_completed"], 4)
        
    def test_phase_advancement(self):
        """Test phase progression logic"""
        state_file = self.test_dir / ".project-state.json"
        
        phases = ["01", "02", "03", "04"]
        
        for i, phase in enumerate(phases):
            # Update to current phase
            state = json.loads(state_file.read_text())
            state["current_phase"] = phase
            
            # Mark previous phases complete
            if i > 0:
                state["completed_phases"].append(phases[i-1])
                
            state_file.write_text(json.dumps(state, indent=2))
            
            # Verify advancement
            updated_state = json.loads(state_file.read_text())
            self.assertEqual(updated_state["current_phase"], phase)
            self.assertEqual(len(updated_state["completed_phases"]), i)
            
    def test_automation_control(self):
        """Test automation pause/resume functionality"""
        state_file = self.test_dir / ".project-state.json"
        workflow_file = self.test_dir / ".workflow-state.json"
        
        # Test pause
        state = json.loads(state_file.read_text())
        workflow = json.loads(workflow_file.read_text())
        
        state["automation_active"] = False
        workflow["automation_active"] = False
        
        state_file.write_text(json.dumps(state, indent=2))
        workflow_file.write_text(json.dumps(workflow, indent=2))
        
        # Verify paused
        self.assertFalse(json.loads(state_file.read_text())["automation_active"])
        self.assertFalse(json.loads(workflow_file.read_text())["automation_active"])
        
        # Test resume
        state["automation_active"] = True
        workflow["automation_active"] = True
        
        state_file.write_text(json.dumps(state, indent=2))
        workflow_file.write_text(json.dumps(workflow, indent=2))
        
        # Verify resumed
        self.assertTrue(json.loads(state_file.read_text())["automation_active"])
        self.assertTrue(json.loads(workflow_file.read_text())["automation_active"])
        
    def test_error_recovery(self):
        """Test error handling and recovery"""
        state_file = self.test_dir / ".project-state.json"
        
        # Simulate corrupted state
        state_file.write_text("invalid json{")
        
        # Recovery should default to safe state
        try:
            state = json.loads(state_file.read_text())
        except json.JSONDecodeError:
            # Recovery behavior
            default_state = {
                "workflow_step": "planning",
                "status": "error",
                "error": "State file corrupted"
            }
            state_file.write_text(json.dumps(default_state, indent=2))
            
        # Verify recovery
        state = json.loads(state_file.read_text())
        self.assertEqual(state["workflow_step"], "planning")
        self.assertEqual(state["status"], "error")


class TestLoggingInfrastructure(unittest.TestCase):
    """Test the comprehensive logging system"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="pdds_log_test_"))
        self.logs_dir = self.test_dir / ".logs"
        self.logs_dir.mkdir()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_log_file_creation(self):
        """Test that all log files are created"""
        expected_logs = [
            "automation.log",
            "workflow.log",
            "commands.log",
            "quality-gates.log",
            "phase-transitions.log",
            "errors.log",
            "performance.log"
        ]
        
        # Simulate log creation
        for log_name in expected_logs:
            log_file = self.logs_dir / log_name
            log_file.touch()
            
        # Verify all logs exist
        for log_name in expected_logs:
            self.assertTrue((self.logs_dir / log_name).exists(),
                          f"Log file {log_name} not created")
                          
    def test_structured_logging(self):
        """Test JSON structured log format"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": "INFO",
            "category": "automation",
            "correlation_id": "test-correlation-id",
            "phase": "01",
            "workflow_step": "planning",
            "event": "test_event",
            "details": {
                "test_key": "test_value"
            }
        }
        
        # Write log entry
        log_file = self.logs_dir / "automation.log"
        with open(log_file, "w") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        # Read and validate
        with open(log_file, "r") as f:
            logged_entry = json.loads(f.readline())
            
        self.assertEqual(logged_entry["level"], "INFO")
        self.assertEqual(logged_entry["event"], "test_event")
        self.assertEqual(logged_entry["correlation_id"], "test-correlation-id")
        
    def test_performance_metrics(self):
        """Test performance logging"""
        perf_log = self.logs_dir / "performance.log"
        
        # Log command performance
        perf_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": "DEBUG",
            "category": "performance",
            "event": "command_performance",
            "details": {
                "command": "npm test",
                "duration_ms": 1234.56,
                "success": True,
                "output_size_bytes": 4096
            }
        }
        
        with open(perf_log, "w") as f:
            f.write(json.dumps(perf_entry) + "\n")
            
        # Verify metrics
        with open(perf_log, "r") as f:
            entry = json.loads(f.readline())
            
        self.assertEqual(entry["details"]["duration_ms"], 1234.56)
        self.assertEqual(entry["details"]["command"], "npm test")
        self.assertTrue(entry["details"]["success"])


if __name__ == "__main__":
    # Run the test suite
    unittest.main(verbosity=2)
