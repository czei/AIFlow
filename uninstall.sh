#!/bin/bash
set -euo pipefail

# AI Software Project Management System - Uninstall Script
# This script safely removes the installed command system

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

# Installation paths
INSTALL_DIR="$HOME/.claude/commands/project"
SCRIPTS_DIR="$HOME/.claude/commands"
BACKUP_DIR_NAME="claude-pm-backup-$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$HOME/.claude/backups/$BACKUP_DIR_NAME"

# Cleanup function
cleanup() {
    # Nothing to clean up for uninstaller
    return 0
}

# Signal handler
handle_signal() {
    local signal="$1"
    print_status "warning" "Uninstall interrupted by signal: $signal"
    log_security_event "INTERRUPT" "Uninstall interrupted" "Signal: $signal"
    exit 130
}

# Set up cleanup and signal traps
setup_cleanup_trap cleanup
trap 'handle_signal INT' INT
trap 'handle_signal TERM' TERM
trap 'handle_signal HUP' HUP

echo "🗑️  AI Software Project Management System Uninstaller"
echo "===================================================="
echo ""

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "info")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
    esac
}

# Function to check if installation exists
check_installation() {
    if [[ ! -d "$INSTALL_DIR" ]]; then
        print_status "error" "Installation not found at $INSTALL_DIR"
        echo ""
        echo "Nothing to uninstall."
        exit 0
    fi
    
    print_status "info" "Found installation at $INSTALL_DIR"
}

# Function to prompt for confirmation
confirm_uninstall() {
    echo ""
    print_status "warning" "This will remove all Claude PM commands and configurations"
    echo ""
    echo "The following will be removed:"
    echo "  • Commands at $INSTALL_DIR"
    echo "  • Scripts at $SCRIPTS_DIR/logged_secure_shell.py"
    echo "  • Scripts at $SCRIPTS_DIR/analyze_logs.sh"
    echo ""
    
    read -p "Do you want to create a backup before uninstalling? (y/N): " backup_choice
    validate_yes_no "$backup_choice"
    if [[ $? -eq 0 ]]; then
        CREATE_BACKUP=true
    else
        CREATE_BACKUP=false
    fi
    
    echo ""
    read -p "Are you sure you want to uninstall? (y/N): " confirm
    validate_yes_no "$confirm"
    if [[ $? -ne 0 ]]; then
        print_status "info" "Uninstall cancelled"
        exit 0
    fi
}

# Function to create backup
create_backup() {
    print_status "info" "Creating backup..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR" || {
        print_status "error" "Failed to create backup directory"
        return 1
    }
    
    # Backup installation directory
    if [[ -d "$INSTALL_DIR" ]]; then
        cp -r "$INSTALL_DIR" "$BACKUP_DIR/project" || {
            print_status "warning" "Failed to backup project directory"
        }
    fi
    
    # Backup scripts
    for script in logged_secure_shell.py analyze_logs.sh; do
        if [[ -f "$SCRIPTS_DIR/$script" ]]; then
            cp "$SCRIPTS_DIR/$script" "$BACKUP_DIR/" || {
                print_status "warning" "Failed to backup $script"
            }
        fi
    done
    
    # Save installation info
    cat > "$BACKUP_DIR/installation_info.txt" << EOF
Claude PM Backup
Created: $(date)
Installation Directory: $INSTALL_DIR
Scripts Directory: $SCRIPTS_DIR

To restore:
1. Copy project/ to $INSTALL_DIR
2. Copy scripts to $SCRIPTS_DIR
EOF
    
    print_status "success" "Backup created at $BACKUP_DIR"
    return 0
}

# Function to check for active projects
check_active_projects() {
    print_status "info" "Checking for active projects..."
    
    # Look for .project-state.json files in parent directories
    local active_projects=()
    
    # Check common project locations
    for dir in "$HOME/projects" "$HOME/dev" "$HOME/workspace" "$HOME"; do
        if [[ -d "$dir" ]]; then
            while IFS= read -r -d '' state_file; do
                local project_dir=$(dirname "$state_file")
                if [[ -f "$state_file" ]]; then
                    active_projects+=("$project_dir")
                fi
            done < <(find "$dir" -maxdepth 3 -name ".project-state.json" -print0 2>/dev/null)
        fi
    done
    
    if [[ ${#active_projects[@]} -gt 0 ]]; then
        print_status "warning" "Found ${#active_projects[@]} active project(s):"
        for project in "${active_projects[@]}"; do
            echo "    • $project"
        done
        echo ""
        echo "These projects will continue to work but commands will not be available."
    else
        print_status "success" "No active projects found"
    fi
}

# Function to remove installation
remove_installation() {
    print_status "info" "Removing installation..."
    
    local removal_errors=0
    
    # Remove main installation directory
    if [[ -d "$INSTALL_DIR" ]]; then
        if safe_remove "$HOME/.claude/commands" "project"; then
            print_status "success" "Removed commands directory"
        else
            print_status "error" "Failed to remove $INSTALL_DIR"
            ((removal_errors++))
        fi
    fi
    
    # Remove scripts
    for script in logged_secure_shell.py analyze_logs.sh; do
        if [[ -f "$SCRIPTS_DIR/$script" ]]; then
            if safe_remove "$SCRIPTS_DIR" "$script"; then
                print_status "success" "Removed $script"
            else
                print_status "warning" "Failed to remove $script"
                ((removal_errors++))
            fi
        fi
    done
    
    # Clean up empty parent directory if safe
    if [[ -d "$HOME/.claude/commands" ]]; then
        # Only remove if directory is empty or only contains our backup directory
        local remaining_files=$(find "$HOME/.claude/commands" -mindepth 1 -maxdepth 1 -not -name "backups" | wc -l)
        if [[ $remaining_files -eq 0 ]]; then
            rmdir "$HOME/.claude/commands" 2>/dev/null || true
        fi
    fi
    
    if [[ $removal_errors -eq 0 ]]; then
        print_status "success" "Uninstallation completed successfully"
        return 0
    else
        print_status "warning" "Uninstallation completed with $removal_errors warning(s)"
        return 1
    fi
}

# Function to show post-uninstall message
show_completion_message() {
    echo ""
    echo "============================================="
    print_status "success" "Uninstall completed!"
    echo "============================================="
    echo ""
    
    if [[ "$CREATE_BACKUP" == true ]]; then
        echo "📦 Backup Location:"
        echo "  $BACKUP_DIR"
        echo ""
        echo "To restore the installation:"
        echo "  1. Copy files from backup to original locations"
        echo "  2. Or reinstall using install.sh"
        echo ""
    fi
    
    echo "📝 Notes:"
    echo "  • Existing projects will remain intact"
    echo "  • Git worktrees are not affected"
    echo "  • Sprint files in projects are preserved"
    echo ""
    echo "To reinstall:"
    echo "  ./install.sh"
    echo ""
    echo "Thank you for using Claude PM!"
}

# Main uninstall flow
main() {
    # Check if installation exists
    check_installation
    
    # Check for active projects
    check_active_projects
    
    # Confirm uninstall
    confirm_uninstall
    
    # Create backup if requested
    if [[ "$CREATE_BACKUP" == true ]]; then
        if ! create_backup; then
            print_status "error" "Backup failed"
            read -p "Continue with uninstall anyway? (y/N): " continue_anyway
            validate_yes_no "$continue_anyway"
            if [[ $? -ne 0 ]]; then
                print_status "info" "Uninstall cancelled"
                exit 1
            fi
        fi
    fi
    
    # Remove installation
    remove_installation
    
    # Show completion message
    show_completion_message
}

# Run main uninstall
main