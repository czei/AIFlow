"""
Setup Command - Create new project worktree and structure.

Orchestrates GitOperations, ProjectBuilder, and StateManager to create
a complete sprint-based project setup with error handling and rollback.
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

from ..git_operations import GitOperations, GitOperationError
from ..project_builder import ProjectBuilder, ProjectBuilderError
from ..state_manager import StateManager, StateValidationError


class SetupCommandError(Exception):
    """Raised when setup command fails."""
    pass


class SetupCommand:
    """
    Implements project setup functionality.
    
    Creates git worktree, project structure, and initial state with
    comprehensive error handling and rollback capabilities.
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize setup command.
        
        Args:
            repo_path: Path to git repository. Defaults to current directory.
        """
        try:
            self.git_ops = GitOperations(repo_path)
            self.project_builder = ProjectBuilder(self.git_ops)
        except GitOperationError as e:
            raise SetupCommandError(f"Git repository initialization failed: {e}")
            
    def execute(
        self, 
        project_name: str,
        base_branch: str = "main",
        initial_sprint: str = "01"
    ) -> Tuple[Path, str]:
        """
        Execute project setup.
        
        Args:
            project_name: Name of the project/worktree
            base_branch: Base branch to branch from
            initial_sprint: Starting sprint identifier
            
        Returns:
            Tuple of (worktree_path, branch_name)
            
        Raises:
            SetupCommandError: If setup fails
        """
        print(f"🚀 Setting up project: {project_name}")
        
        try:
            # Step 1: Validate repository state
            print("📋 Validating git repository...")
            self._validate_repository_state()
            
            # Step 2: Create worktree and branch
            print(f"🌿 Creating worktree and branch...")
            worktree_path, branch_name = self._create_worktree(
                project_name, base_branch
            )
            
            try:
                # Step 3: Create project structure
                print("📁 Creating project structure...")
                self._create_project_structure(
                    worktree_path, project_name, initial_sprint
                )
                
                # Step 4: Create initial commit
                print("📝 Creating initial commit...")
                self._create_initial_commit(worktree_path, project_name)
                
                # Step 5: Display success information
                self._display_success_info(worktree_path, branch_name, project_name)
                
                return worktree_path, branch_name
                
            except Exception as e:
                # Rollback worktree on project structure failure
                print(f"❌ Project setup failed: {e}")
                print("🔄 Rolling back changes...")
                self._rollback_worktree(project_name)
                raise
                
        except GitOperationError as e:
            raise SetupCommandError(f"Git operation failed: {e}")
        except (ProjectBuilderError, StateValidationError) as e:
            raise SetupCommandError(f"Project creation failed: {e}")
        except Exception as e:
            raise SetupCommandError(f"Unexpected error during setup: {e}")
            
    def _validate_repository_state(self) -> None:
        """Validate repository is in good state for project creation."""
        try:
            context = self.git_ops.get_repo_context()
            
            # Check if we have uncommitted changes (warning, not error)
            if not context.is_clean:
                print("⚠️  Warning: Repository has uncommitted changes:")
                for change in context.uncommitted_changes[:5]:  # Show first 5
                    print(f"   {change}")
                if len(context.uncommitted_changes) > 5:
                    print(f"   ... and {len(context.uncommitted_changes) - 5} more")
                print("   This won't affect worktree creation, but consider committing first.")
                
            print(f"✅ Repository validated (branch: {context.current_branch})")
            
        except GitOperationError as e:
            raise SetupCommandError(f"Repository validation failed: {e}")
            
    def _create_worktree(
        self, 
        project_name: str, 
        base_branch: str
    ) -> Tuple[Path, str]:
        """Create git worktree with new branch."""
        try:
            # Validate project name
            sanitized_name = self.git_ops.validate_worktree_name(project_name)
            if sanitized_name != project_name:
                print(f"📝 Project name sanitized: {project_name} → {sanitized_name}")
                project_name = sanitized_name
                
            # Check for existing worktree
            if self.git_ops.worktree_exists(project_name):
                raise SetupCommandError(
                    f"Worktree already exists: {self.git_ops.get_worktree_path(project_name)}"
                )
                
            # Create worktree and branch
            worktree_path, branch_name = self.git_ops.create_worktree(
                project_name, base_branch=base_branch
            )
            
            print(f"✅ Created worktree: {worktree_path}")
            print(f"✅ Created branch: {branch_name}")
            
            return worktree_path, branch_name
            
        except GitOperationError as e:
            raise SetupCommandError(f"Worktree creation failed: {e}")
            
    def _create_project_structure(
        self, 
        worktree_path: Path, 
        project_name: str,
        initial_sprint: str
    ) -> None:
        """Create complete project structure."""
        try:
            self.project_builder.create_project_structure(
                worktree_path, project_name, initial_sprint
            )
            
            print("✅ Created project directories")
            print("✅ Generated sprint templates")
            print("✅ Created Claude configuration")
            print("✅ Generated documentation")
            print("✅ Initialized project state")
            
        except (ProjectBuilderError, StateValidationError) as e:
            raise SetupCommandError(f"Project structure creation failed: {e}")
            
    def _create_initial_commit(self, worktree_path: Path, project_name: str) -> None:
        """Create initial commit with project structure."""
        try:
            commit_msg = f"Initial setup: {project_name} project structure\n\n" \
                        f"- Created sprint-based development structure\n" \
                        f"- Generated sprint templates and documentation\n" \
                        f"- Initialized project state and configuration\n" \
                        f"- Ready for sprint customization and development"
                        
            commit_hash = self.git_ops.create_commit(
                commit_msg, worktree_path, add_all=True
            )
            
            print(f"✅ Created initial commit: {commit_hash[:8]}")
            
        except GitOperationError as e:
            raise SetupCommandError(f"Initial commit failed: {e}")
            
    def _rollback_worktree(self, project_name: str) -> None:
        """Rollback worktree creation on failure."""
        try:
            if self.git_ops.worktree_exists(project_name):
                self.git_ops.remove_worktree(project_name, force=True)
                print(f"🔄 Removed worktree: {project_name}")
        except Exception as e:
            print(f"⚠️  Warning: Failed to cleanup worktree: {e}")
            print("   You may need to manually remove the worktree directory")
            
    def _display_success_info(
        self, 
        worktree_path: Path, 
        branch_name: str, 
        project_name: str
    ) -> None:
        """Display success information and next steps."""
        print(f"\n🎉 Project setup completed successfully!")
        print(f"")
        print(f"📍 Project Location:")
        print(f"   Worktree: {worktree_path}")
        print(f"   Branch: {branch_name}")
        print(f"")
        print(f"📂 Created Structure:")
        print(f"   ├── sprints/              # Sprint definitions (customize these!)")
        print(f"   ├── .claude/            # Claude Code configuration")
        print(f"   ├── docs/               # Project documentation")
        print(f"   ├── logs/               # Development logs")
        print(f"   ├── CLAUDE.md           # Project context for Claude")
        print(f"   ├── README-SPRINTS.md    # Phase documentation")
        print(f"   ├── WORKFLOW_SPECIFICATIONS.md  # Detailed methodology")
        print(f"   └── .project-state.json # Project state tracking")
        print(f"")
        print(f"🔧 Next Steps:")
        print(f"   1. cd {worktree_path}")
        print(f"   2. Customize sprint files in sprints/ directory")
        print(f"   3. Edit CLAUDE.md with project-specific context")
        print(f"   4. Run: /user:project:doctor to validate setup")
        print(f"   5. Run: /user:project:start to begin automated development")
        print(f"")
        print(f"💡 Important:")
        print(f"   - Sprint files contain templates - customize them for your project")
        print(f"   - Each sprint has detailed user stories and acceptance criteria")
        print(f"   - Review WORKFLOW_SPECIFICATIONS.md for methodology details")
        print(f"   - Project uses git worktree isolation for safety")
        print(f"")
        print(f"🚀 Ready for sprint-based development!")


def main():
    """Command-line interface for setup command."""
    if len(sys.argv) < 2:
        print("Usage: python -m src.commands.setup <project-name> [base-branch]")
        print("")
        print("Arguments:")
        print("  project-name    Name for the project and worktree")
        print("  base-branch     Base branch to branch from (default: main)")
        print("")
        print("Example:")
        print("  python -m src.commands.setup my-awesome-feature")
        print("  python -m src.commands.setup api-refactor main")
        sys.exit(1)
        
    project_name = sys.argv[1]
    base_branch = sys.argv[2] if len(sys.argv) > 2 else "main"
    
    try:
        setup_cmd = SetupCommand()
        setup_cmd.execute(project_name, base_branch)
        
    except SetupCommandError as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()