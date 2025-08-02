#!/bin/bash
set -euo pipefail

# AIFlow - Installation Script
# This script safely installs the command system with prerequisite checking and error handling

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source security library
source "$PROJECT_ROOT/scripts/common_security.sh" || {
    echo "Error: Failed to load security library" >&2
    exit 1
}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation tracking
INSTALL_LOG=$(secure_temp_file "claude-pm-install") || {
    echo "Error: Failed to create install log" >&2
    exit 1
}
ERRORS_FOUND=0

# Parse command line arguments
GLOBAL_INSTALL=false
PROJECT_DIR=""
SHOW_HELP=false
UNINSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --global|-g)
            GLOBAL_INSTALL=true
            shift
            ;;
        --project-dir|-p)
            if [[ -z "${2:-}" ]]; then
                echo "Error: --project-dir requires a directory path" >&2
                SHOW_HELP=true
                shift
            else
                PROJECT_DIR="$2"
                shift 2
            fi
            ;;
        --uninstall|-u)
            UNINSTALL=true
            shift
            ;;
        --help|-h)
            SHOW_HELP=true
            shift
            ;;
        *)
            echo "Error: Unknown option $1" >&2
            SHOW_HELP=true
            shift
            ;;
    esac
done

# Show help if requested or on error
if [[ "$SHOW_HELP" == "true" ]]; then
    cat << EOF
AIFlow Installation Script

Usage: ./install.sh [OPTIONS]

Options:
  --project-dir, -p DIR   Install to specific project directory (default: current directory)
  --global, -g           Install globally to ~/.claude/commands/project
  --uninstall, -u        Uninstall AIFlow (use with --global for global uninstall)
  --help, -h             Show this help message

Examples:
  # Install to current project
  ./install.sh

  # Install to specific project
  ./install.sh --project-dir /path/to/my-project

  # Install globally (affects all Claude Code sessions)
  ./install.sh --global

  # Uninstall from current project
  ./install.sh --uninstall

  # Uninstall globally
  ./install.sh --uninstall --global

By default, AIFlow installs to the current project directory, creating a .claude/
subdirectory with hooks that only affect Claude Code sessions in that project.

Global installation will affect ALL Claude Code sessions system-wide.
EOF
    exit 0
fi

# Determine installation directory
if [[ "$GLOBAL_INSTALL" == "true" ]]; then
    INSTALL_DIR="$HOME/.claude/commands/project"
    HOOKS_DIR="$HOME/.claude/hooks"
    INSTALL_TYPE="global"
else
    # Use project directory or current directory
    if [[ -n "$PROJECT_DIR" ]]; then
        # Validate that the project directory exists or can be created
        if [[ -d "$PROJECT_DIR" ]]; then
            PROJECT_TARGET="$(cd "$PROJECT_DIR" 2>/dev/null && pwd)" || {
                echo "Error: Cannot access project directory: $PROJECT_DIR" >&2
                exit 1
            }
        else
            # Try to create the directory if it doesn't exist
            mkdir -p "$PROJECT_DIR" 2>/dev/null || {
                echo "Error: Cannot create project directory: $PROJECT_DIR" >&2
                exit 1
            }
            PROJECT_TARGET="$(cd "$PROJECT_DIR" 2>/dev/null && pwd)" || {
                echo "Error: Cannot access project directory: $PROJECT_DIR" >&2
                exit 1
            }
        fi
    else
        PROJECT_TARGET="$(pwd)"
    fi
    
    # Check if target is a git repository
    if [[ ! -d "$PROJECT_TARGET/.git" ]]; then
        echo "Warning: $PROJECT_TARGET is not a git repository" >&2
        echo "AIFlow works best with git repositories. Continue anyway? (y/N)" >&2
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "Installation cancelled." >&2
            exit 1
        fi
    fi
    
    INSTALL_DIR="$PROJECT_TARGET/.claude/commands/project"
    HOOKS_DIR="$PROJECT_TARGET/.claude/hooks"
    INSTALL_TYPE="project"
fi

# Cleanup function
cleanup() {
    if [[ -n "${INSTALL_LOG:-}" ]] && [[ -f "$INSTALL_LOG" ]]; then
        echo ""
        echo "Installation log saved to: $INSTALL_LOG"
    fi
}

# Signal handler
handle_signal() {
    local signal="$1"
    print_status "warning" "Installation interrupted by signal: $signal"
    log_security_event "INTERRUPT" "Installation interrupted" "Signal: $signal"
    exit 130
}

# Set up cleanup and signal traps
setup_cleanup_trap cleanup
trap 'handle_signal INT' INT
trap 'handle_signal TERM' TERM
trap 'handle_signal HUP' HUP

echo "🚀 AIFlow - AI Software Project Management System Installer" | tee "$INSTALL_LOG"
echo "========================================================" | tee -a "$INSTALL_LOG"
echo "Installation type: $INSTALL_TYPE" | tee -a "$INSTALL_LOG"
if [[ "$INSTALL_TYPE" == "project" ]]; then
    echo "Target directory: ${PROJECT_TARGET}" | tee -a "$INSTALL_LOG"
fi
echo "" | tee -a "$INSTALL_LOG"

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✅ $message${NC}" | tee -a "$INSTALL_LOG"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}" | tee -a "$INSTALL_LOG"
            ERRORS_FOUND=1
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}" | tee -a "$INSTALL_LOG"
            ;;
        "info")
            echo -e "${BLUE}ℹ️  $message${NC}" | tee -a "$INSTALL_LOG"
            ;;
    esac
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to check Python version
check_python_version() {
    local python_cmd=""
    local required_version="3.7"
    
    # Try different Python commands
    for cmd in python3 python; do
        if command_exists "$cmd"; then
            local version=$(get_python_version "$cmd")
            if [[ $? -eq 0 ]] && version_ge "$version" "$required_version"; then
                python_cmd="$cmd"
                print_status "success" "Found Python $version at $(which $cmd)"
                echo "$cmd"
                return 0
            fi
        fi
    done
    
    print_status "error" "Python $required_version or higher is required but not found"
    print_status "info" "Please install Python from https://python.org"
    return 1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "info" "Checking prerequisites..."
    
    # Check OS
    local os=$(detect_os)
    case $os in
        "linux"|"macos")
            print_status "success" "Operating system: $os"
            ;;
        "windows")
            print_status "warning" "Windows detected - some features may require WSL"
            ;;
        *)
            print_status "error" "Unsupported operating system: $OSTYPE"
            return 1
            ;;
    esac
    
    # Check Git
    if command_exists git; then
        local git_version=$(git --version | cut -d' ' -f3)
        print_status "success" "Git $git_version found"
    else
        print_status "error" "Git is required but not found"
        print_status "info" "Please install Git from https://git-scm.com"
        return 1
    fi
    
    # Check Python
    # Capture output separately from function return
    local python_output
    python_output=$(check_python_version)
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    # Extract just the python command from the last line of output
    PYTHON_CMD=$(echo "$python_output" | tail -1)
    
    # Check Claude Code CLI
    if command_exists claude; then
        print_status "success" "Claude Code CLI found at $(which claude)"
    else
        print_status "warning" "Claude Code CLI not found - commands will not be available until installed"
        print_status "info" "Install with: npm install -g @anthropic-ai/claude-code"
    fi
    
    # Check write permissions
    if [[ -w "$HOME/.claude" ]] || [[ ! -e "$HOME/.claude" ]]; then
        print_status "success" "Write permissions verified for ~/.claude/"
    else
        print_status "error" "No write permissions for ~/.claude/"
        return 1
    fi
    
    return 0
}

# Function to create directory structure
create_directories() {
    print_status "info" "Creating directory structure..."
    
    mkdir -p "$INSTALL_DIR" || {
        print_status "error" "Failed to create $INSTALL_DIR"
        return 1
    }
    
    mkdir -p "$INSTALL_DIR/lib" || {
        print_status "error" "Failed to create $INSTALL_DIR/lib"
        return 1
    }
    
    # For project installs, create hooks directory at project level
    if [[ "$INSTALL_TYPE" == "project" ]]; then
        mkdir -p "$HOOKS_DIR" || {
            print_status "error" "Failed to create $HOOKS_DIR"
            return 1
        }
    else
        # For global installs, keep hooks with commands
        mkdir -p "$INSTALL_DIR/hooks" || {
            print_status "error" "Failed to create $INSTALL_DIR/hooks"
            return 1
        }
    fi
    
    print_status "success" "Directory structure created"
    return 0
}

# Function to install Python modules
install_python_modules() {
    print_status "info" "Installing Python modules..."
    
    # Copy only necessary source files (exclude tests)
    if [[ -d "$PROJECT_ROOT/src" ]]; then
        cp -r "$PROJECT_ROOT/src" "$INSTALL_DIR/lib/" || {
            print_status "error" "Failed to copy Python source files"
            return 1
        }
        print_status "success" "Python modules installed"
    else
        print_status "error" "Source directory not found at $PROJECT_ROOT/src"
        return 1
    fi
    
    # Copy required scripts
    for script in logged_secure_shell.py analyze_logs.sh; do
        if [[ -f "$PROJECT_ROOT/scripts/$script" ]]; then
            cp "$PROJECT_ROOT/scripts/$script" "$HOME/.claude/commands/" || {
                print_status "warning" "Failed to copy $script"
            }
            if [[ -f "$HOME/.claude/commands/$script" ]]; then
                chmod +x "$HOME/.claude/commands/$script"
            fi
        fi
    done
    
    return 0
}

# Function to install command files
install_commands() {
    print_status "info" "Installing command files..."
    
    local command_count=0
    if [[ -d "$PROJECT_ROOT/src/commands" ]]; then
        for cmd_file in "$PROJECT_ROOT/src/commands"/*.md; do
            if [[ -f "$cmd_file" ]]; then
                cp "$cmd_file" "$INSTALL_DIR/" || {
                    print_status "warning" "Failed to copy $(basename "$cmd_file")"
                    continue
                }
                ((command_count++))
            fi
        done
        print_status "success" "Installed $command_count command files"
    else
        print_status "error" "Commands directory not found"
        return 1
    fi
    
    return 0
}

# Function to install hooks
install_hooks() {
    print_status "info" "Installing hook scripts..."
    
    # Determine target hooks directory
    local target_hooks_dir
    if [[ "$INSTALL_TYPE" == "project" ]]; then
        target_hooks_dir="$HOOKS_DIR"
    else
        target_hooks_dir="$INSTALL_DIR/hooks"
    fi
    
    # Copy hook Python files
    local hook_count=0
    for hook_file in "$PROJECT_ROOT/src/hooks"/*.py; do
        if [[ -f "$hook_file" ]]; then
            cp "$hook_file" "$target_hooks_dir/" || {
                print_status "warning" "Failed to copy $(basename "$hook_file")"
                continue
            }
            ((hook_count++))
        fi
    done
    
    # Ensure hook_import_helper.py is copied
    if [[ -f "$PROJECT_ROOT/src/hooks/hook_import_helper.py" ]]; then
        cp "$PROJECT_ROOT/src/hooks/hook_import_helper.py" "$target_hooks_dir/" || {
            print_status "warning" "Failed to copy hook_import_helper.py"
        }
    fi
    
    # Copy hook configuration templates
    for config_file in "$PROJECT_ROOT/src/hooks"/*.json "$PROJECT_ROOT/src/hooks"/*.template; do
        if [[ -f "$config_file" ]]; then
            cp "$config_file" "$target_hooks_dir/" || {
                print_status "warning" "Failed to copy $(basename "$config_file")"
            }
        fi
    done
    
    print_status "success" "Installed $hook_count hook scripts"
    
    # Create hook configuration README
    create_hook_readme
    
    # For project installations, optionally create settings.json
    if [[ "$INSTALL_TYPE" == "project" ]]; then
        local settings_file="${PROJECT_TARGET}/.claude/settings.json"
        if [[ ! -f "$settings_file" ]]; then
            print_status "info" "Creating .claude/settings.json with hook configuration..."
            
            # Check if there's a template for project settings
            if [[ -f "$PROJECT_ROOT/src/hooks/project_settings.json.template" ]]; then
                cp "$PROJECT_ROOT/src/hooks/project_settings.json.template" "$settings_file" || {
                    print_status "warning" "Failed to create settings.json"
                }
            else
                # Create a basic settings.json
                cat > "$settings_file" << 'EOF'
{
  "hooks": {
    "PreToolUse": {
      "command": "python3 .claude/hooks/pre_tool_use.py",
      "timeout": 5000
    },
    "PostToolUse": {
      "command": "python3 .claude/hooks/post_tool_use.py",
      "timeout": 3000
    },
    "Stop": {
      "command": "python3 .claude/hooks/stop.py",
      "timeout": 3000
    }
  }
}
EOF
            fi
            
            if [[ -f "$settings_file" ]]; then
                print_status "success" "Created .claude/settings.json with hook configuration"
                print_status "info" "Hooks are now active for this project"
            fi
        else
            print_status "info" "Existing .claude/settings.json found - not overwriting"
            print_status "warning" "Please manually add hook configuration if needed"
        fi
    fi
    
    return 0
}

# Function to create hook configuration README
create_hook_readme() {
    local readme_path
    if [[ "$INSTALL_TYPE" == "project" ]]; then
        readme_path="$HOOKS_DIR/README.md"
    else
        readme_path="$INSTALL_DIR/hooks/README.md"
    fi
    
    if [[ "$INSTALL_TYPE" == "project" ]]; then
        # Project-level installation
        cat > "$readme_path" << 'EOF'
# Claude Code Hooks Configuration (Project-Level)

These hooks are installed for this project only. To enable automated workflow enforcement, 
create a .claude/settings.json file in this project:

```json
{
  "hooks": {
    "PreToolUse": {
      "command": "python3 .claude/hooks/pre_tool_use.py",
      "timeout": 5000
    },
    "PostToolUse": {
      "command": "python3 .claude/hooks/post_tool_use.py",
      "timeout": 3000
    },
    "Stop": {
      "command": "python3 .claude/hooks/stop.py",
      "timeout": 3000
    }
  }
}
```

The hooks enforce the 6-step workflow automatically:
1. Planning - Research and requirements only
2. Implementation - Code writing allowed
3. Validation - Testing and verification
4. Review - Code quality assessment
5. Refinement - Apply review feedback
6. Integration - Final commit and merge

Note: These hooks only affect Claude Code sessions in this project directory.
EOF
    else
        # Global installation
        cat > "$readme_path" << 'EOF'
# Claude Code Hooks Configuration (Global)

To enable automated workflow enforcement globally, add these hooks to ~/.claude/settings.json:

```json
{
  "hooks": {
    "PreToolUse": {
      "command": "python3 ${HOME}/.claude/commands/project/hooks/pre_tool_use.py",
      "timeout": 5000
    },
    "PostToolUse": {
      "command": "python3 ${HOME}/.claude/commands/project/hooks/post_tool_use.py",
      "timeout": 3000
    },
    "Stop": {
      "command": "python3 ${HOME}/.claude/commands/project/hooks/stop.py",
      "timeout": 3000
    }
  }
}
```

The hooks enforce the 6-step workflow automatically:
1. Planning - Research and requirements only
2. Implementation - Code writing allowed
3. Validation - Testing and verification
4. Review - Code quality assessment
5. Refinement - Apply review feedback
6. Integration - Final commit and merge

WARNING: These hooks will affect ALL Claude Code sessions system-wide!
To disable for specific projects, create a .claude/settings.json in that project
with empty hooks configuration.
EOF
    fi
    
    print_status "success" "Created hook configuration guide"
}

# Function to validate installation
validate_installation() {
    print_status "info" "Validating installation..."
    
    local validation_errors=0
    
    # Check directories exist
    local dirs_to_check=("$INSTALL_DIR" "$INSTALL_DIR/lib")
    
    # Add appropriate hooks directory
    if [[ "$INSTALL_TYPE" == "project" ]]; then
        dirs_to_check+=("$HOOKS_DIR")
    else
        dirs_to_check+=("$INSTALL_DIR/hooks")
    fi
    
    for dir in "${dirs_to_check[@]}"; do
        if [[ ! -d "$dir" ]]; then
            print_status "error" "Directory missing: $dir"
            ((validation_errors++))
        fi
    done
    
    # Check key files exist
    local key_files=(
        "$INSTALL_DIR/setup.md"
        "$INSTALL_DIR/start.md"
        "$INSTALL_DIR/status.md"
        "$INSTALL_DIR/lib/src/state_manager.py"
    )
    
    # Add hook file check based on installation type
    if [[ "$INSTALL_TYPE" == "project" ]]; then
        key_files+=("$HOOKS_DIR/pre_tool_use.py")
    else
        key_files+=("$INSTALL_DIR/hooks/pre_tool_use.py")
    fi
    
    for file in "${key_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_status "error" "Key file missing: $file"
            ((validation_errors++))
        fi
    done
    
    # Test Python imports safely
    # Create a temporary test script to avoid passing complex arguments
    local test_script=$(secure_temp_file "py-test")
    if [[ -z "$test_script" ]] || [[ ! -f "$test_script" ]]; then
        print_status "warning" "Could not create temp file for Python test, skipping import validation"
        # Don't count this as an error since the installation itself was successful
        return $validation_errors
    fi
    
    cat > "$test_script" << EOF
import sys
sys.path.insert(0, "$INSTALL_DIR/lib")
try:
    from src.state_manager import StateManager
    sys.exit(0)
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)
EOF
    
    # Run the test and capture output for debugging
    local test_output
    local test_exit_code
    test_output=$("$PYTHON_CMD" "$test_script" 2>&1)
    test_exit_code=$?
    
    if [[ $test_exit_code -ne 0 ]]; then
        print_status "error" "Python module import test failed"
        if [[ -n "$test_output" ]]; then
            print_status "info" "Debug output: $test_output"
        fi
        ((validation_errors++))
    else
        print_status "success" "Python module import test passed"
    fi
    rm -f "$test_script"
    
    if [[ $validation_errors -eq 0 ]]; then
        print_status "success" "Installation validation passed"
        return 0
    else
        print_status "error" "Installation validation failed with $validation_errors errors"
        return 1
    fi
}

# Function to show success message
show_success_message() {
    echo ""
    echo "============================================="
    print_status "success" "Installation completed successfully!"
    echo "============================================="
    echo ""
    echo "📦 Installed Components:"
    echo "  • Commands: $INSTALL_DIR/*.md"
    if [[ "$INSTALL_TYPE" == "project" ]]; then
        echo "  • Hooks: $HOOKS_DIR/*.py"
    else
        echo "  • Hooks: $INSTALL_DIR/hooks/*.py"
    fi
    echo "  • Python modules: $INSTALL_DIR/lib/src/"
    echo ""
    
    if [[ "$INSTALL_TYPE" == "project" ]]; then
        echo "🎯 Project-Level Installation:"
        echo "  • Hooks installed to: $HOOKS_DIR"
        echo "  • Settings file: ${PROJECT_TARGET}/.claude/settings.json"
        echo "  • This installation only affects Claude Code sessions in:"
        echo "    ${PROJECT_TARGET}"
        echo ""
        echo "🚀 Quick Start:"
        echo "1. Create .claude/settings.json in this project (see $HOOKS_DIR/README.md)"
        echo "2. Start Claude Code in this directory: claude"
        echo "3. The sprint workflow will be active only in this project"
        echo ""
        echo "To uninstall from this project:"
        echo "  rm -rf ${PROJECT_TARGET}/.claude"
    else
        echo "🎯 Global Installation:"
        echo "  • Commands available in all Claude Code sessions"
        echo "  • To enable hooks globally, update ~/.claude/settings.json"
        echo "  • WARNING: This will affect ALL Claude Code sessions!"
        echo ""
        echo "Available Commands:"
        echo "  /user:project:setup <name>     - Create new project worktree"
        echo "  /user:project:start            - Begin automated development"
        echo "  /user:project:status           - Show project progress"
        echo "  /user:project:pause [reason]   - Pause automation"
        echo "  /user:project:resume           - Resume from pause"
        echo "  /user:project:stop [reason]    - End project with summary"
        echo "  /user:project:doctor           - Validate project setup"
        echo ""
        echo "🚀 Quick Start:"
        echo "1. Start Claude Code with: claude --dangerously-skip-permissions"
        echo "2. Navigate to a git repository"
        echo "3. Run: /user:project:setup my-awesome-project"
        echo "4. cd ../my-awesome-project"
        echo "5. Customize sprint files in sprints/"
        echo "6. Run: /user:project:start"
    fi
    echo ""
    echo "📚 Documentation:"
    echo "  • Setup Guide: $PROJECT_ROOT/docs/POC_SETUP_GUIDE.md"
    echo "  • Sprint Creation: $PROJECT_ROOT/docs/SPRINT_CREATION_INSTRUCTIONS.md"
    echo "  • Hook Configuration: See README.md in hooks directory"
    echo ""
    echo "📝 Installation log saved to: $INSTALL_LOG"
}

# Function to handle installation failure
handle_failure() {
    echo ""
    echo "============================================="
    print_status "error" "Installation failed!"
    echo "============================================="
    echo ""
    echo "Please check the installation log: $INSTALL_LOG"
    echo ""
    echo "Common issues:"
    echo "  • Python 3.7+ not installed"
    echo "  • Git not installed"
    echo "  • No write permissions to ~/.claude/"
    echo ""
    echo "For manual installation instructions, see:"
    echo "  $PROJECT_ROOT/docs/POC_SETUP_GUIDE.md"
    
    exit 1
}

# Main installation flow
main() {
    # Check prerequisites
    if ! check_prerequisites; then
        handle_failure
    fi
    
    # Create directory structure
    if ! create_directories; then
        handle_failure
    fi
    
    # Install components
    if ! install_python_modules; then
        handle_failure
    fi
    
    if ! install_commands; then
        handle_failure
    fi
    
    if ! install_hooks; then
        handle_failure
    fi
    
    # Validate installation
    if ! validate_installation; then
        handle_failure
    fi
    
    # Show success message
    show_success_message
}

# Function to uninstall AIFlow
uninstall_aiflow() {
    print_status "info" "Uninstalling AIFlow..."
    
    if [[ "$INSTALL_TYPE" == "global" ]]; then
        # Global uninstall
        if [[ -d "$INSTALL_DIR" ]]; then
            rm -rf "$INSTALL_DIR" || {
                print_status "error" "Failed to remove $INSTALL_DIR"
                return 1
            }
            print_status "success" "Removed global installation from $INSTALL_DIR"
        else
            print_status "warning" "No global installation found at $INSTALL_DIR"
        fi
        
        # Check for global hooks in settings
        if [[ -f "$HOME/.claude/settings.json" ]]; then
            print_status "info" "Check ~/.claude/settings.json for any hook configurations to remove manually"
        fi
    else
        # Project uninstall
        local claude_dir="${PROJECT_TARGET}/.claude"
        if [[ -d "$claude_dir" ]]; then
            rm -rf "$claude_dir" || {
                print_status "error" "Failed to remove $claude_dir"
                return 1
            }
            print_status "success" "Removed project installation from $claude_dir"
        else
            print_status "warning" "No project installation found at $claude_dir"
        fi
    fi
    
    print_status "success" "Uninstallation complete!"
    return 0
}

# Check if uninstalling
if [[ "$UNINSTALL" == "true" ]]; then
    uninstall_aiflow
    exit $?
fi

# Run main installation
main