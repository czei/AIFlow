"""
Unit tests for ProjectBuilder class.

Tests project structure creation, template generation, and integration
with GitOperations and StateManager.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.project_builder import ProjectBuilder, ProjectBuilderError
from src.git_operations import GitOperations


class TestProjectBuilder(unittest.TestCase):
    """Test ProjectBuilder functionality."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.worktree_path = self.test_dir / "test-project"
        self.worktree_path.mkdir()
        
        # Mock GitOperations
        self.mock_git_ops = Mock(spec=GitOperations)
        self.project_builder = ProjectBuilder(self.mock_git_ops)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_create_project_structure_success(self):
        """Test successful project structure creation."""
        with patch('src.project_builder.StateManager') as mock_state_manager:
            mock_manager_instance = Mock()
            mock_state_manager.return_value = mock_manager_instance
            
            # Should not raise exception
            self.project_builder.create_project_structure(
                self.worktree_path, 
                "test-project"
            )
            
            # Verify directories were created
            self.assertTrue((self.worktree_path / "phases").exists())
            self.assertTrue((self.worktree_path / ".claude").exists())
            self.assertTrue((self.worktree_path / "logs").exists())
            self.assertTrue((self.worktree_path / "docs").exists())
            
            # Verify StateManager was called
            mock_state_manager.assert_called_once_with(str(self.worktree_path))
            mock_manager_instance.create.assert_called_once_with("test-project", "01")
            
    def test_create_directories(self):
        """Test directory creation."""
        self.project_builder._create_directories(self.worktree_path)
        
        expected_dirs = ["phases", ".claude", "logs", "docs"]
        for dir_name in expected_dirs:
            dir_path = self.worktree_path / dir_name
            self.assertTrue(dir_path.exists())
            self.assertTrue(dir_path.is_dir())
            
    def test_create_phase_files(self):
        """Test phase file creation."""
        # Create phases directory first
        phases_dir = self.worktree_path / "phases"
        phases_dir.mkdir()
        
        self.project_builder._create_phase_files(self.worktree_path, "test-project")
        
        expected_files = [
            "01-planning.md",
            "02-architecture.md", 
            "03-implementation.md",
            "04-testing.md",
            "05-deployment.md",
            "README.md"
        ]
        
        for filename in expected_files:
            file_path = phases_dir / filename
            self.assertTrue(file_path.exists())
            self.assertTrue(file_path.is_file())
            
            # Verify file has content
            content = file_path.read_text()
            self.assertGreater(len(content), 100)  # Should have substantial content
            self.assertIn("test-project", content)  # Should contain project name
            
    def test_create_claude_config(self):
        """Test Claude configuration creation."""
        # Create .claude directory first
        claude_dir = self.worktree_path / ".claude"
        claude_dir.mkdir()
        
        self.project_builder._create_claude_config(self.worktree_path, "test-project")
        
        settings_file = claude_dir / "settings.json"
        self.assertTrue(settings_file.exists())
        
        # Verify JSON content
        settings = json.loads(settings_file.read_text())
        self.assertEqual(settings["project_name"], "test-project")
        self.assertEqual(settings["version"], "1.0.0")
        self.assertFalse(settings["automation_enabled"])
        self.assertIn("hooks", settings)
        self.assertIn("workflow", settings)
        
    def test_create_documentation(self):
        """Test documentation file creation."""
        self.project_builder._create_documentation(self.worktree_path, "test-project")
        
        expected_files = [
            "CLAUDE.md",
            "README-PHASES.md", 
            "WORKFLOW_SPECIFICATIONS.md"
        ]
        
        for filename in expected_files:
            file_path = self.worktree_path / filename
            self.assertTrue(file_path.exists())
            self.assertTrue(file_path.is_file())
            
            # Verify file has content and project name
            content = file_path.read_text()
            self.assertGreater(len(content), 500)  # Should have substantial content
            self.assertIn("test-project", content)  # Should contain project name
            
    def test_initialize_project_state(self):
        """Test project state initialization."""
        with patch('src.project_builder.StateManager') as mock_state_manager:
            mock_manager_instance = Mock()
            mock_state_manager.return_value = mock_manager_instance
            
            self.project_builder._initialize_project_state(
                self.worktree_path, 
                "test-project", 
                "01"
            )
            
            mock_state_manager.assert_called_once_with(str(self.worktree_path))
            mock_manager_instance.create.assert_called_once_with("test-project", "01")
            
    def test_initialize_project_state_custom_phase(self):
        """Test project state initialization with custom phase."""
        with patch('src.project_builder.StateManager') as mock_state_manager:
            mock_manager_instance = Mock()
            mock_state_manager.return_value = mock_manager_instance
            
            self.project_builder._initialize_project_state(
                self.worktree_path, 
                "test-project", 
                "02"
            )
            
            mock_manager_instance.create.assert_called_once_with("test-project", "02")
            
    def test_generate_planning_phase_template(self):
        """Test planning phase template generation."""
        content = self.project_builder._generate_planning_phase_template("test-project")
        
        # Verify content structure
        self.assertIn("Phase 01: Planning", content)
        self.assertIn("test-project", content)
        self.assertIn("Phase Objectives", content)
        self.assertIn("Requirements Analysis", content)
        self.assertIn("6-Step Workflow", content)
        self.assertIn("Quality Gates", content)
        self.assertIn("Success Criteria", content)
        
    def test_generate_architecture_phase_template(self):
        """Test architecture phase template generation."""
        content = self.project_builder._generate_architecture_phase_template("test-project")
        
        # Verify content structure
        self.assertIn("Phase 02: Architecture", content)
        self.assertIn("test-project", content)
        self.assertIn("System Architecture Design", content)
        self.assertIn("Technology Stack Selection", content)
        self.assertIn("API and Interface Design", content)
        
    def test_generate_implementation_phase_template(self):
        """Test implementation phase template generation."""
        content = self.project_builder._generate_implementation_phase_template("test-project")
        
        # Verify content structure
        self.assertIn("Phase 03: Implementation", content)
        self.assertIn("test-project", content)
        self.assertIn("Core Infrastructure Setup", content)
        self.assertIn("Backend Implementation", content)
        self.assertIn("Frontend Implementation", content)
        
    def test_generate_testing_phase_template(self):
        """Test testing phase template generation."""
        content = self.project_builder._generate_testing_phase_template("test-project")
        
        # Verify content structure
        self.assertIn("Phase 04: Testing", content)
        self.assertIn("test-project", content)
        self.assertIn("Test Infrastructure", content)
        self.assertIn("Comprehensive Testing", content)
        self.assertIn("Quality Assurance", content)
        
    def test_generate_deployment_phase_template(self):
        """Test deployment phase template generation."""
        content = self.project_builder._generate_deployment_phase_template("test-project")
        
        # Verify content structure
        self.assertIn("Phase 05: Deployment", content)
        self.assertIn("test-project", content)
        self.assertIn("Production Environment Setup", content)
        self.assertIn("Deployment Pipeline", content)
        self.assertIn("Go-Live and Handover", content)
        
    def test_generate_phases_readme(self):
        """Test phases README generation."""
        content = self.project_builder._generate_phases_readme("test-project")
        
        # Verify content structure
        self.assertIn("Phases Directory", content)
        self.assertIn("test-project", content)
        self.assertIn("Phase Overview", content)
        self.assertIn("Workflow Methodology", content)
        self.assertIn("Quality Gates", content)
        
    def test_generate_claude_md_template(self):
        """Test CLAUDE.md template generation."""
        content = self.project_builder._generate_claude_md_template("test-project")
        
        # Verify content structure
        self.assertIn("test-project", content)
        self.assertIn("Phase-Driven Development", content)
        self.assertIn("Project Context", content)
        self.assertIn("Development Workflow", content)
        self.assertIn("Quality Gates", content)
        self.assertIn("Automation Commands", content)
        
    def test_generate_project_readme(self):
        """Test project README generation."""
        content = self.project_builder._generate_project_readme("test-project")
        
        # Verify content structure
        self.assertIn("test-project", content)
        self.assertIn("Project Overview", content)
        self.assertIn("Development Methodology", content)
        self.assertIn("6-Step Universal Workflow", content)
        self.assertIn("Quality Gates", content)
        
    def test_generate_workflow_specifications(self):
        """Test workflow specifications generation."""
        content = self.project_builder._generate_workflow_specifications("test-project")
        
        # Verify content structure
        self.assertIn("Workflow Specifications", content)
        self.assertIn("test-project", content)
        self.assertIn("Universal 6-Step Workflow", content)
        self.assertIn("Step 1: Planning", content)
        self.assertIn("Quality Gates System", content)
        self.assertIn("Automation Specifications", content)
        
    def test_create_project_structure_failure(self):
        """Test project structure creation failure handling."""
        with patch('src.project_builder.StateManager') as mock_state_manager:
            # Make StateManager initialization fail
            mock_state_manager.side_effect = Exception("State manager error")
            
            with self.assertRaises(ProjectBuilderError) as context:
                self.project_builder.create_project_structure(
                    self.worktree_path, 
                    "test-project"
                )
                
            self.assertIn("Failed to create project structure", str(context.exception))
            
    def test_all_templates_contain_project_name(self):
        """Test that all generated templates contain the project name."""
        project_name = "unique-test-project-name"
        
        # Test all template generation methods
        template_methods = [
            '_generate_planning_phase_template',
            '_generate_architecture_phase_template',
            '_generate_implementation_phase_template', 
            '_generate_testing_phase_template',
            '_generate_deployment_phase_template',
            '_generate_phases_readme',
            '_generate_claude_md_template',
            '_generate_project_readme',
            '_generate_workflow_specifications'
        ]
        
        for method_name in template_methods:
            method = getattr(self.project_builder, method_name)
            content = method(project_name)
            
            self.assertIn(project_name, content, 
                         f"Template {method_name} missing project name")
            
    def test_phase_templates_have_required_sections(self):
        """Test that phase templates have required sections."""
        project_name = "test-project"
        
        required_sections = [
            "Phase Objectives",
            "Prerequisites", 
            "Quality Gates",
            "Success Criteria",
            "6-Step Workflow"
        ]
        
        phase_methods = [
            '_generate_planning_phase_template',
            '_generate_architecture_phase_template',
            '_generate_implementation_phase_template',
            '_generate_testing_phase_template',
            '_generate_deployment_phase_template'
        ]
        
        for method_name in phase_methods:
            method = getattr(self.project_builder, method_name)
            content = method(project_name)
            
            for section in required_sections:
                self.assertIn(section, content, 
                             f"Template {method_name} missing section: {section}")
                             
    def test_claude_config_has_required_fields(self):
        """Test that Claude configuration has all required fields."""
        claude_dir = self.worktree_path / ".claude"
        claude_dir.mkdir()
        
        self.project_builder._create_claude_config(self.worktree_path, "test-project")
        
        settings_file = claude_dir / "settings.json"
        settings = json.loads(settings_file.read_text())
        
        required_fields = [
            "version",
            "project_name", 
            "automation_enabled",
            "hooks",
            "workflow",
            "settings"
        ]
        
        for field in required_fields:
            self.assertIn(field, settings, f"Missing field: {field}")
            
        # Verify nested structure
        self.assertIn("steps", settings["workflow"])
        self.assertIn("quality_gates", settings["workflow"])
        self.assertIn("pre_tool_use", settings["hooks"])
        self.assertIn("post_tool_use", settings["hooks"])
        self.assertIn("stop", settings["hooks"])


if __name__ == '__main__':
    unittest.main()