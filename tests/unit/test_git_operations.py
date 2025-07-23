"""
Unit tests for GitOperations class.

Tests git worktree and branch operations with mocking to avoid real git operations
during testing while still validating the logic and error handling.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

from src.git_operations import GitOperations, GitOperationError, GitContext, WorktreeInfo


class TestGitOperations(unittest.TestCase):
    """Test GitOperations functionality with mocked git commands."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Mock successful git repository detection
        self.git_patcher = patch('src.git_operations.GitOperations._run_git_command')
        self.mock_git = self.git_patcher.start()
        
        # Default mock: repository is valid
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ".git"
        mock_result.stderr = ""
        self.mock_git.return_value = mock_result
        
    def tearDown(self):
        """Clean up test environment."""
        self.git_patcher.stop()
        shutil.rmtree(self.test_dir)
        
    def test_init_valid_repository(self):
        """Test initializing GitOperations with valid repository."""
        git_ops = GitOperations(str(self.test_dir))
        self.assertEqual(git_ops.repo_path, self.test_dir.resolve())
        
    def test_init_invalid_repository(self):
        """Test initializing GitOperations with invalid repository."""
        # Mock git command failure
        mock_result = Mock()
        mock_result.returncode = 1
        self.mock_git.return_value = mock_result
        
        with self.assertRaises(GitOperationError) as context:
            GitOperations(str(self.test_dir))
            
        self.assertIn("Not a git repository", str(context.exception))
        
    def test_get_repo_context(self):
        """Test getting repository context information."""
        git_ops = GitOperations(str(self.test_dir))
        
        # Mock git command responses
        def mock_git_side_effect(args, **kwargs):
            mock_result = Mock()
            mock_result.returncode = 0
            
            if args == ["branch", "--show-current"]:
                mock_result.stdout = "main\n"
            elif args == ["status", "--porcelain"]:
                mock_result.stdout = ""  # Clean working tree
            elif args == ["remote", "-v"]:
                mock_result.stdout = "origin\tgit@github.com:user/repo.git (fetch)\n"
            elif args == ["remote", "get-url", "origin"]:
                mock_result.stdout = "git@github.com:user/repo.git\n"
            else:
                mock_result.stdout = ""
                
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        context = git_ops.get_repo_context()
        
        self.assertEqual(context.current_branch, "main")
        self.assertTrue(context.is_clean)
        self.assertTrue(context.has_remote)
        self.assertEqual(context.remote_url, "git@github.com:user/repo.git")
        self.assertEqual(context.uncommitted_changes, [])
        
    def test_get_repo_context_dirty_working_tree(self):
        """Test getting repository context with uncommitted changes."""
        git_ops = GitOperations(str(self.test_dir))
        
        def mock_git_side_effect(args, **kwargs):
            mock_result = Mock()
            mock_result.returncode = 0
            
            if args == ["branch", "--show-current"]:
                mock_result.stdout = "feature-branch\n"
            elif args == ["status", "--porcelain"]:
                mock_result.stdout = " M file1.py\n?? file2.py\n"  # Modified and untracked
            elif args == ["remote", "-v"]:
                mock_result.stdout = ""  # No remote
            else:
                mock_result.stdout = ""
                
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        context = git_ops.get_repo_context()
        
        self.assertEqual(context.current_branch, "feature-branch")
        self.assertFalse(context.is_clean)
        self.assertFalse(context.has_remote)
        self.assertIsNone(context.remote_url)
        self.assertEqual(context.uncommitted_changes, ["M file1.py", "?? file2.py"])
        
    def test_validate_worktree_name_valid(self):
        """Test validating valid worktree names."""
        git_ops = GitOperations(str(self.test_dir))
        
        valid_names = ["my-project", "test_feature", "feature.123", "simple"]
        for name in valid_names:
            result = git_ops.validate_worktree_name(name)
            self.assertEqual(result, name)
            
    def test_validate_worktree_name_invalid(self):
        """Test validating invalid worktree names."""
        git_ops = GitOperations(str(self.test_dir))
        
        invalid_names = ["", "  ", "name with spaces", "name/with/slashes", "name@with#symbols"]
        for name in invalid_names:
            with self.assertRaises(GitOperationError):
                git_ops.validate_worktree_name(name)
                
    def test_get_worktree_path(self):
        """Test getting worktree path."""
        git_ops = GitOperations(str(self.test_dir))
        
        expected_path = self.test_dir.resolve().parent / "my-project"
        result = git_ops.get_worktree_path("my-project")
        
        self.assertEqual(result, expected_path)
        
    def test_worktree_exists(self):
        """Test checking if worktree exists."""
        git_ops = GitOperations(str(self.test_dir))
        
        # Create a directory to simulate existing worktree
        worktree_path = self.test_dir.resolve().parent / "existing-worktree"
        worktree_path.mkdir()
        
        try:
            self.assertTrue(git_ops.worktree_exists("existing-worktree"))
            self.assertFalse(git_ops.worktree_exists("non-existent"))
        finally:
            worktree_path.rmdir()
            
    def test_branch_exists(self):
        """Test checking if branch exists."""
        git_ops = GitOperations(str(self.test_dir))
        
        def mock_git_side_effect(args, **kwargs):
            mock_result = Mock()
            if args == ["branch", "--list", "existing-branch"]:
                mock_result.returncode = 0
                mock_result.stdout = "  existing-branch\n"
            elif args == ["branch", "--list", "non-existent"]:
                mock_result.returncode = 0
                mock_result.stdout = ""
            else:
                mock_result.returncode = 0
                mock_result.stdout = ""
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        self.assertTrue(git_ops.branch_exists("existing-branch"))
        self.assertFalse(git_ops.branch_exists("non-existent"))
        
    def test_create_worktree_success(self):
        """Test successful worktree creation."""
        git_ops = GitOperations(str(self.test_dir))
        
        # Mock successful operations
        def mock_git_side_effect(args, **kwargs):
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        # Mock worktree path creation
        worktree_path = self.test_dir.resolve().parent / "test-project"
        with patch('pathlib.Path.exists') as mock_exists:
            # First call (pre-check): False, Second call (post-creation): True
            mock_exists.side_effect = [False, True]
            
            path, branch = git_ops.create_worktree("test-project")
            
            self.assertEqual(path, worktree_path)
            self.assertEqual(branch, "feature/test-project")
            
    def test_create_worktree_already_exists(self):
        """Test worktree creation when worktree already exists."""
        git_ops = GitOperations(str(self.test_dir))
        
        # Create directory to simulate existing worktree
        worktree_path = self.test_dir.resolve().parent / "existing"
        worktree_path.mkdir()
        
        try:
            with self.assertRaises(GitOperationError) as context:
                git_ops.create_worktree("existing")
                
            self.assertIn("already exists", str(context.exception))
        finally:
            worktree_path.rmdir()
            
    def test_create_worktree_branch_exists(self):
        """Test worktree creation when branch already exists."""
        git_ops = GitOperations(str(self.test_dir))
        
        def mock_git_side_effect(args, **kwargs):
            mock_result = Mock()
            if args == ["branch", "--list", "feature/test-project"]:
                mock_result.returncode = 0
                mock_result.stdout = "  feature/test-project\n"
            else:
                mock_result.returncode = 0
                mock_result.stdout = ""
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        with patch('pathlib.Path.exists', return_value=False):
            with self.assertRaises(GitOperationError) as context:
                git_ops.create_worktree("test-project")
                
            self.assertIn("Branch already exists", str(context.exception))
            
    def test_create_worktree_git_command_fails(self):
        """Test worktree creation when git command fails."""
        git_ops = GitOperations(str(self.test_dir))
        
        call_count = 0
        def mock_git_side_effect(args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            mock_result = Mock()
            # First few calls succeed (validation checks)
            if call_count <= 3:
                mock_result.returncode = 0
                mock_result.stdout = ""
            # Worktree add command fails
            elif "worktree" in args and "add" in args:
                mock_result.returncode = 1
                mock_result.stderr = "fatal: worktree add failed"
                if kwargs.get('check'):
                    raise GitOperationError("Git command failed")
            else:
                mock_result.returncode = 0
                mock_result.stdout = ""
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        with patch('pathlib.Path.exists', return_value=False):
            with self.assertRaises(GitOperationError) as context:
                git_ops.create_worktree("test-project")
                
            self.assertIn("Failed to create worktree", str(context.exception))
            
    def test_remove_worktree_success(self):
        """Test successful worktree removal."""
        git_ops = GitOperations(str(self.test_dir))
        
        # Create directory to simulate existing worktree
        worktree_path = self.test_dir.resolve().parent / "test-worktree"
        worktree_path.mkdir()
        
        try:
            def mock_git_side_effect(args, **kwargs):
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = ""
                return mock_result
                
            self.mock_git.side_effect = mock_git_side_effect
            
            # Should not raise exception
            git_ops.remove_worktree("test-worktree")
            
        finally:
            if worktree_path.exists():
                worktree_path.rmdir()
                
    def test_remove_worktree_not_exists(self):
        """Test removing non-existent worktree."""
        git_ops = GitOperations(str(self.test_dir))
        
        with self.assertRaises(GitOperationError) as context:
            git_ops.remove_worktree("non-existent")
            
        self.assertIn("does not exist", str(context.exception))
        
    def test_remove_worktree_has_changes(self):
        """Test removing worktree with uncommitted changes."""
        git_ops = GitOperations(str(self.test_dir))
        
        # Create directory to simulate existing worktree
        worktree_path = self.test_dir.resolve().parent / "dirty-worktree"
        worktree_path.mkdir()
        
        try:
            def mock_git_side_effect(args, **kwargs):
                mock_result = Mock()
                if "worktree" in args and "remove" in args and "--force" not in args:
                    mock_result.returncode = 1
                    mock_result.stderr = "fatal: worktree has modifications"
                    if kwargs.get('check'):
                        raise GitOperationError("Git command failed: worktree has modifications")
                else:
                    mock_result.returncode = 0
                    mock_result.stdout = ""
                return mock_result
                
            self.mock_git.side_effect = mock_git_side_effect
            
            with self.assertRaises(GitOperationError) as context:
                git_ops.remove_worktree("dirty-worktree")
                
            self.assertIn("has uncommitted changes", str(context.exception))
            
        finally:
            if worktree_path.exists():
                worktree_path.rmdir()
                
    def test_list_worktrees(self):
        """Test listing worktrees."""
        git_ops = GitOperations(str(self.test_dir))
        
        def mock_git_side_effect(args, **kwargs):
            mock_result = Mock()
            if args == ["worktree", "list", "--porcelain"]:
                mock_result.returncode = 0
                mock_result.stdout = (
                    "worktree /path/to/main\n"
                    "branch refs/heads/main\n"
                    "\n"
                    "worktree /path/to/feature\n"
                    "branch refs/heads/feature\n"
                    "\n"
                    "worktree /path/to/detached\n"
                    "detached\n"
                    "\n"
                )
            else:
                mock_result.returncode = 0
                mock_result.stdout = ""
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        worktrees = git_ops.list_worktrees()
        
        self.assertEqual(len(worktrees), 3)
        self.assertEqual(str(worktrees[0].path), "/path/to/main")
        self.assertEqual(worktrees[0].branch, "refs/heads/main")
        self.assertFalse(worktrees[0].is_detached)
        
        self.assertEqual(str(worktrees[1].path), "/path/to/feature")
        self.assertEqual(worktrees[1].branch, "refs/heads/feature")
        
        self.assertEqual(str(worktrees[2].path), "/path/to/detached")
        self.assertTrue(worktrees[2].is_detached)
        
    def test_get_current_commit(self):
        """Test getting current commit hash."""
        git_ops = GitOperations(str(self.test_dir))
        
        def mock_git_side_effect(args, **kwargs):
            mock_result = Mock()
            if args == ["rev-parse", "HEAD"]:
                mock_result.returncode = 0
                mock_result.stdout = "abc123def456\n"
            else:
                mock_result.returncode = 0
                mock_result.stdout = ""
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        commit_hash = git_ops.get_current_commit()
        self.assertEqual(commit_hash, "abc123def456")
        
    def test_create_commit_success(self):
        """Test successful commit creation."""
        git_ops = GitOperations(str(self.test_dir))
        
        def mock_git_side_effect(args, **kwargs):
            mock_result = Mock()
            if args == ["rev-parse", "HEAD"]:
                mock_result.returncode = 0
                mock_result.stdout = "new123commit456\n"
            else:
                mock_result.returncode = 0
                mock_result.stdout = ""
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        commit_hash = git_ops.create_commit("Test commit message")
        self.assertEqual(commit_hash, "new123commit456")
        
    def test_create_commit_nothing_to_commit(self):
        """Test commit creation when nothing to commit."""
        git_ops = GitOperations(str(self.test_dir))
        
        call_count = 0
        def mock_git_side_effect(args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            mock_result = Mock()
            if args == ["add", "."]:
                mock_result.returncode = 0
                mock_result.stdout = ""
            elif args == ["commit", "-m", "Test commit"]:
                mock_result.returncode = 1
                mock_result.stderr = "nothing to commit, working tree clean"
                if kwargs.get('check'):
                    raise GitOperationError("Git command failed: nothing to commit")
            elif args == ["rev-parse", "HEAD"]:
                mock_result.returncode = 0
                mock_result.stdout = "existing123commit456\n"
            else:
                mock_result.returncode = 0
                mock_result.stdout = ""
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        # Should return existing commit hash, not raise exception
        commit_hash = git_ops.create_commit("Test commit")
        self.assertEqual(commit_hash, "existing123commit456")
        
    def test_is_worktree_clean(self):
        """Test checking if worktree is clean."""
        git_ops = GitOperations(str(self.test_dir))
        worktree_path = Path("/path/to/worktree")
        
        def mock_git_side_effect(args, **kwargs):
            mock_result = Mock()
            if args == ["status", "--porcelain"]:
                if kwargs.get('cwd') == worktree_path:
                    mock_result.returncode = 0
                    mock_result.stdout = ""  # Clean
                else:
                    mock_result.returncode = 0
                    mock_result.stdout = " M file.py"  # Dirty
            else:
                mock_result.returncode = 0
                mock_result.stdout = ""
            return mock_result
            
        self.mock_git.side_effect = mock_git_side_effect
        
        self.assertTrue(git_ops.is_worktree_clean(worktree_path))
        self.assertFalse(git_ops.is_worktree_clean(Path("/other/path")))


if __name__ == '__main__':
    unittest.main()