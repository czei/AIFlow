"""
GitOperations - Safe git worktree and branch management for the automated development system.

Provides secure git operations including worktree creation, branch management, and validation
with comprehensive error handling and rollback capabilities.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


class GitOperationError(Exception):
    """Raised when git operations fail."""
    pass


@dataclass
class GitContext:
    """Git repository context information."""
    repo_root: Path
    current_branch: str
    is_clean: bool
    has_remote: bool
    remote_url: Optional[str] = None
    uncommitted_changes: List[str] = None


@dataclass  
class WorktreeInfo:
    """Worktree information."""
    path: Path
    branch: str
    is_detached: bool
    is_locked: bool


class GitOperations:
    """
    Manages git operations with safety checks and error recovery.
    
    Provides atomic git operations for worktree management, branch operations,
    and repository validation with comprehensive error handling.
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize GitOperations for a specific repository.
        
        Args:
            repo_path: Path to git repository. Defaults to current directory.
        """
        self.repo_path = Path(repo_path or ".").resolve()
        self._validate_git_repo()
        
    def _validate_git_repo(self) -> None:
        """Validate that the path contains a git repository."""
        if not self._is_git_repo(self.repo_path):
            raise GitOperationError(f"Not a git repository: {self.repo_path}")
            
    def _is_git_repo(self, path: Path) -> bool:
        """Check if path is a git repository."""
        try:
            result = self._run_git_command(["rev-parse", "--git-dir"], cwd=path)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
            
    def _run_git_command(
        self, 
        args: List[str], 
        cwd: Optional[Path] = None,
        capture_output: bool = True,
        check: bool = False
    ) -> subprocess.CompletedProcess:
        """
        Run git command with safety checks.
        
        Args:
            args: Git command arguments
            cwd: Working directory for command
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero exit
            
        Returns:
            Completed process result
            
        Raises:
            GitOperationError: If command fails and check=True
        """
        cmd = ["git"] + args
        cwd = cwd or self.repo_path
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,  
                capture_output=capture_output,
                text=True,
                check=False  # We handle errors manually for better messages
            )
            
            if check and result.returncode != 0:
                raise GitOperationError(
                    f"Git command failed: {' '.join(cmd)}\n"
                    f"Exit code: {result.returncode}\n"
                    f"Error: {result.stderr}"
                )
                
            return result
            
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            raise GitOperationError(f"Failed to execute git command: {e}")
            
    def get_repo_context(self) -> GitContext:
        """
        Get current repository context information.
        
        Returns:
            GitContext with repository state information
        """
        # Get current branch
        result = self._run_git_command(["branch", "--show-current"], check=True)
        current_branch = result.stdout.strip()
        
        # Check if working tree is clean
        result = self._run_git_command(["status", "--porcelain"], check=True)
        uncommitted_changes = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        is_clean = len(uncommitted_changes) == 0
        
        # Check for remote
        result = self._run_git_command(["remote", "-v"])
        has_remote = result.returncode == 0 and result.stdout.strip()
        remote_url = None
        
        if has_remote:
            # Get origin URL
            result = self._run_git_command(["remote", "get-url", "origin"])
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                
        return GitContext(
            repo_root=self.repo_path,
            current_branch=current_branch,
            is_clean=is_clean,
            has_remote=has_remote,
            remote_url=remote_url,
            uncommitted_changes=uncommitted_changes if not is_clean else []
        )
        
    def validate_worktree_name(self, name: str) -> str:
        """
        Validate and sanitize worktree name.
        
        Args:
            name: Proposed worktree name
            
        Returns:
            Sanitized name safe for filesystem and git
            
        Raises:
            GitOperationError: If name is invalid
        """
        if not name or not name.strip():
            raise GitOperationError("Worktree name cannot be empty")
            
        # Remove dangerous characters and sanitize
        sanitized = "".join(c for c in name if c.isalnum() or c in "-_.")
        
        if not sanitized:
            raise GitOperationError(f"Invalid worktree name: {name}")
            
        if sanitized != name:
            raise GitOperationError(
                f"Worktree name contains invalid characters: {name}\n"
                f"Suggested name: {sanitized}"
            )
            
        return sanitized
        
    def get_worktree_path(self, name: str) -> Path:
        """
        Get path for new worktree relative to repository.
        
        Args:
            name: Worktree name
            
        Returns:
            Absolute path for worktree
        """
        # Worktrees are created as siblings to the main repository
        return self.repo_path.parent / name
        
    def worktree_exists(self, name: str) -> bool:
        """
        Check if worktree already exists.
        
        Args:
            name: Worktree name
            
        Returns:
            True if worktree exists
        """
        worktree_path = self.get_worktree_path(name)
        return worktree_path.exists()
        
    def branch_exists(self, branch_name: str) -> bool:
        """
        Check if branch exists locally.
        
        Args:
            branch_name: Branch name to check
            
        Returns:
            True if branch exists
        """
        result = self._run_git_command(["branch", "--list", branch_name])
        return result.returncode == 0 and branch_name in result.stdout
        
    def create_worktree(
        self, 
        name: str, 
        branch_name: Optional[str] = None,
        base_branch: str = "main"
    ) -> Tuple[Path, str]:
        """
        Create a new git worktree with branch.
        
        Args:
            name: Worktree name (will be sanitized)
            branch_name: Branch name. Defaults to feature/{name}
            base_branch: Base branch to branch from
            
        Returns:
            Tuple of (worktree_path, branch_name)
            
        Raises:
            GitOperationError: If creation fails
        """
        # Validate and sanitize name
        sanitized_name = self.validate_worktree_name(name)
        branch_name = branch_name or f"feature/{sanitized_name}"
        worktree_path = self.get_worktree_path(sanitized_name)
        
        # Pre-flight checks
        if self.worktree_exists(sanitized_name):
            raise GitOperationError(f"Worktree already exists: {worktree_path}")
            
        if self.branch_exists(branch_name):
            raise GitOperationError(f"Branch already exists: {branch_name}")
            
        # Check if base branch exists
        if not self.branch_exists(base_branch) and base_branch != "main":
            # Try "master" as fallback
            if self.branch_exists("master"):
                base_branch = "master"
            else:
                raise GitOperationError(f"Base branch does not exist: {base_branch}")
        
        try:
            # Create worktree with new branch
            self._run_git_command([
                "worktree", "add", 
                str(worktree_path),
                "-b", branch_name,
                base_branch
            ], check=True)
            
            # Verify creation was successful
            if not worktree_path.exists():
                raise GitOperationError(f"Worktree creation failed: {worktree_path}")
                
            # Set up remote tracking if remote exists
            context = self.get_repo_context()
            if context.has_remote:
                try:
                    self._run_git_command([
                        "branch", "--set-upstream-to=origin/" + base_branch, branch_name
                    ], cwd=worktree_path)
                except GitOperationError:
                    # Non-fatal - branch tracking setup failed
                    pass
                    
            return worktree_path, branch_name
            
        except Exception as e:
            # Cleanup on failure
            self._cleanup_failed_worktree(worktree_path, branch_name)
            raise GitOperationError(f"Failed to create worktree: {e}")
            
    def _cleanup_failed_worktree(self, worktree_path: Path, branch_name: str) -> None:
        """Clean up after failed worktree creation."""
        try:
            # Remove worktree if it exists
            if worktree_path.exists():
                self._run_git_command(["worktree", "remove", str(worktree_path), "--force"])
                
            # Delete branch if it was created
            if self.branch_exists(branch_name):
                self._run_git_command(["branch", "-D", branch_name])
                
        except Exception:
            # Cleanup failure is non-fatal but should be logged
            pass
            
    def remove_worktree(self, name: str, force: bool = False) -> None:
        """
        Remove a git worktree.
        
        Args:
            name: Worktree name
            force: Force removal even if worktree has changes
            
        Raises:
            GitOperationError: If removal fails
        """
        worktree_path = self.get_worktree_path(name)
        
        if not worktree_path.exists():
            raise GitOperationError(f"Worktree does not exist: {worktree_path}")
            
        try:
            args = ["worktree", "remove", str(worktree_path)]
            if force:
                args.append("--force")
                
            self._run_git_command(args, check=True)
            
        except GitOperationError as e:
            if "has modifications" in str(e) and not force:
                raise GitOperationError(
                    f"Worktree has uncommitted changes: {worktree_path}\n"
                    f"Use force=True to remove anyway"
                )
            raise
            
    def list_worktrees(self) -> List[WorktreeInfo]:
        """
        List all worktrees.
        
        Returns:
            List of WorktreeInfo objects
        """
        try:
            result = self._run_git_command(["worktree", "list", "--porcelain"], check=True)
            
            worktrees = []
            current_worktree = {}
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    if current_worktree:
                        worktrees.append(self._parse_worktree_info(current_worktree))
                        current_worktree = {}
                    continue
                    
                if line.startswith('worktree '):
                    current_worktree['path'] = line[9:]  # Remove 'worktree ' prefix
                elif line.startswith('branch '):
                    current_worktree['branch'] = line[7:]  # Remove 'branch ' prefix
                elif line == 'detached':
                    current_worktree['detached'] = True
                elif line == 'locked':
                    current_worktree['locked'] = True
                    
            # Handle last worktree
            if current_worktree:
                worktrees.append(self._parse_worktree_info(current_worktree))
                
            return worktrees
            
        except GitOperationError:
            return []
            
    def _parse_worktree_info(self, data: Dict[str, Any]) -> WorktreeInfo:
        """Parse worktree info from git worktree list output."""
        return WorktreeInfo(
            path=Path(data.get('path', '')),
            branch=data.get('branch', ''),
            is_detached=data.get('detached', False),
            is_locked=data.get('locked', False)
        )
        
    def get_current_commit(self, worktree_path: Optional[Path] = None) -> str:
        """
        Get current commit hash.
        
        Args:
            worktree_path: Path to worktree. Defaults to main repository.
            
        Returns:
            Current commit hash
        """
        cwd = worktree_path or self.repo_path
        result = self._run_git_command(["rev-parse", "HEAD"], cwd=cwd, check=True)
        return result.stdout.strip()
        
    def create_commit(
        self, 
        message: str, 
        worktree_path: Optional[Path] = None,
        add_all: bool = True
    ) -> str:
        """
        Create a commit in the specified worktree.
        
        Args:
            message: Commit message
            worktree_path: Path to worktree. Defaults to main repository.
            add_all: Whether to add all changes before committing
            
        Returns:
            Commit hash
            
        Raises:
            GitOperationError: If commit fails
        """
        cwd = worktree_path or self.repo_path
        
        try:
            if add_all:
                self._run_git_command(["add", "."], cwd=cwd, check=True)
                
            self._run_git_command(["commit", "-m", message], cwd=cwd, check=True)
            
            return self.get_current_commit(cwd)
            
        except GitOperationError as e:
            if "nothing to commit" in str(e):
                # Not an error - just no changes
                return self.get_current_commit(cwd)
            raise
            
    def is_worktree_clean(self, worktree_path: Path) -> bool:
        """
        Check if worktree has uncommitted changes.
        
        Args:
            worktree_path: Path to worktree
            
        Returns:
            True if worktree is clean
        """
        try:
            result = self._run_git_command(["status", "--porcelain"], cwd=worktree_path)
            return result.returncode == 0 and not result.stdout.strip()
        except GitOperationError:
            return False