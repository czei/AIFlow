#!/usr/bin/env python3
"""
Unit tests for installer security fixes.
Tests that the security functions properly prevent command injection.
"""

import unittest
import subprocess
import tempfile
import os
import sys
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestInstallerSecurity(unittest.TestCase):
    """Test security functions in installation scripts"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.project_root = Path(__file__).parent.parent.parent
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
        
    def test_python_version_extraction_safe(self):
        """Test that Python version extraction is safe from injection"""
        # Create a test script that sources security library and tests get_python_version
        test_script = self.test_dir / "test_version.sh"
        test_script.write_text(f"""#!/bin/bash
source "{self.project_root}/scripts/common_security.sh"

# Test with safe input
version=$(get_python_version "python3")
echo "VERSION:$version"

# Test with malicious input (should fail)
malicious=$(get_python_version "python3;echo INJECTED" 2>&1 || echo "BLOCKED")
echo "MALICIOUS:$malicious"
""")
        test_script.chmod(0o755)
        
        # Run the test
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        # Check results
        self.assertIn("VERSION:3.", result.stdout)  # Should get real version
        self.assertIn("BLOCKED", result.stdout)  # Malicious input should be blocked
        self.assertNotIn("INJECTED", result.stdout)  # Injection should not execute
        
    def test_path_validation(self):
        """Test that path validation prevents traversal"""
        test_script = self.test_dir / "test_paths.sh"
        test_script.write_text(f"""#!/bin/bash
source "{self.project_root}/scripts/common_security.sh"

# Test valid path
valid=$(validate_path "/tmp" "subdir/file.txt" 2>&1)
echo "VALID:$?"

# Test path traversal
traversal=$(validate_path "/tmp" "../../../etc/passwd" 2>&1)
echo "TRAVERSAL:$?"
""")
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        self.assertIn("VALID:0", result.stdout)  # Valid path should succeed
        self.assertIn("TRAVERSAL:1", result.stdout)  # Traversal should fail
        
    def test_command_validation(self):
        """Test that command validation prevents injection"""
        test_script = self.test_dir / "test_commands.sh"
        test_script.write_text(f"""#!/bin/bash
source "{self.project_root}/scripts/common_security.sh"

# Test valid command
valid=$(validate_command "python3" 2>&1)
echo "VALID:$?"

# Test command with path
path_cmd=$(validate_command "/usr/bin/python3" 2>&1)
echo "PATH:$?"

# Test command injection
injection=$(validate_command "python3;rm -rf /" 2>&1)
echo "INJECTION:$?"
""")
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        self.assertIn("VALID:0", result.stdout)  # Valid command should succeed
        self.assertIn("PATH:1", result.stdout)  # Path in command should fail
        self.assertIn("INJECTION:1", result.stdout)  # Injection should fail
        
    def test_secure_temp_file_creation(self):
        """Test secure temporary file creation"""
        test_script = self.test_dir / "test_temp.sh"
        test_script.write_text(f"""#!/bin/bash
source "{self.project_root}/scripts/common_security.sh"

# Test creating temp file
temp_file=$(secure_temp_file "test-prefix")
if [[ -f "$temp_file" ]]; then
    echo "CREATED:YES"
    # Check permissions
    perms=$(stat -f "%Lp" "$temp_file" 2>/dev/null || stat -c "%a" "$temp_file")
    echo "PERMS:$perms"
    rm -f "$temp_file"
else
    echo "CREATED:NO"
fi

# Test with malicious prefix
malicious=$(secure_temp_file "test;rm -rf /")
if [[ -f "$malicious" ]]; then
    echo "MALICIOUS:CREATED"
    rm -f "$malicious"
else
    echo "MALICIOUS:FAILED"
fi
""")
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        self.assertIn("CREATED:YES", result.stdout)
        self.assertIn("PERMS:600", result.stdout)  # Should have secure permissions
        self.assertIn("MALICIOUS:CREATED", result.stdout)  # Should still create file safely
        
    def test_safe_remove_validation(self):
        """Test that safe_remove validates paths"""
        test_script = self.test_dir / "test_remove.sh"
        test_file = self.test_dir / "test.txt"
        test_file.write_text("test")
        
        test_script.write_text(f"""#!/bin/bash
source "{self.project_root}/scripts/common_security.sh"

# Test removing file in allowed directory
safe_remove "{self.test_dir}" "test.txt" 2>&1
if [[ -f "{test_file}" ]]; then
    echo "REMOVE:FAILED"
else
    echo "REMOVE:SUCCESS"
fi

# Test removing outside allowed directory
safe_remove "{self.test_dir}" "/etc/passwd" 2>&1
echo "OUTSIDE:$?"

# Test path traversal
safe_remove "{self.test_dir}" "../../../etc/passwd" 2>&1
echo "TRAVERSAL:$?"
""")
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        self.assertIn("REMOVE:SUCCESS", result.stdout)
        self.assertIn("OUTSIDE:1", result.stdout)  # Should fail
        self.assertIn("TRAVERSAL:1", result.stdout)  # Should fail


if __name__ == '__main__':
    unittest.main()