#!/bin/bash
# Common Security Library for AI Software Project Management System
# Provides secure functions for input validation, path handling, and command execution

# Validate and sanitize a file path to prevent traversal attacks
# Usage: validate_path "/base/dir" "user/input/path"
# Returns: 0 if valid, 1 if invalid
# Outputs: Validated absolute path on stdout
validate_path() {
    local base_dir="$1"
    local user_path="$2"
    
    # Check inputs
    if [[ -z "$base_dir" ]] || [[ -z "$user_path" ]]; then
        echo "Error: validate_path requires base_dir and user_path arguments" >&2
        return 1
    fi
    
    # Resolve base directory to absolute path
    local abs_base
    abs_base=$(cd "$base_dir" 2>/dev/null && pwd)
    if [[ $? -ne 0 ]] || [[ -z "$abs_base" ]]; then
        echo "Error: Invalid base directory: $base_dir" >&2
        return 1
    fi
    
    # Resolve symlinks in base path to get real path
    if command -v realpath >/dev/null 2>&1; then
        abs_base=$(realpath "$abs_base" 2>/dev/null) || true
    elif command -v readlink >/dev/null 2>&1; then
        # Fallback for systems without realpath
        abs_base=$(cd "$abs_base" 2>/dev/null && pwd -P) || true
    fi
    
    # Handle absolute vs relative paths
    local target_path
    if [[ "$user_path" = /* ]]; then
        # Absolute path provided
        target_path="$user_path"
    else
        # Relative path - combine with base
        target_path="$abs_base/$user_path"
    fi
    
    # Normalize the path (remove .., ., //, etc) without requiring it to exist
    # This is safer than using cd for paths that don't exist yet
    local normalized_path="$target_path"
    
    # Remove trailing slashes
    normalized_path="${normalized_path%/}"
    
    # Handle . and .. manually
    local IFS='/'
    local -a path_parts=($normalized_path)
    local -a clean_parts=()
    
    for part in "${path_parts[@]}"; do
        if [[ "$part" == "" ]] && [[ ${#clean_parts[@]} -eq 0 ]]; then
            # Leading slash (absolute path)
            clean_parts+=("")
        elif [[ "$part" == "." ]] || [[ "$part" == "" ]]; then
            # Skip . and empty parts (from //)
            continue
        elif [[ "$part" == ".." ]]; then
            # Go up one level if possible
            if [[ ${#clean_parts[@]} -gt 0 ]]; then
                # Don't go above root for absolute paths
                if [[ ${#clean_parts[@]} -eq 1 ]] && [[ "${clean_parts[0]}" == "" ]]; then
                    continue  # At root, can't go up
                else
                    # Remove last element (bash 3 compatible)
                    local len=${#clean_parts[@]}
                    if [[ $len -gt 0 ]]; then
                        unset "clean_parts[$((len-1))]"
                        clean_parts=("${clean_parts[@]}")  # Reindex array
                    fi
                fi
            fi
        else
            # Normal path component
            clean_parts+=("$part")
        fi
    done
    
    # Reconstruct path
    local canonical_path
    if [[ ${#clean_parts[@]} -eq 0 ]]; then
        canonical_path="/"
    elif [[ "${clean_parts[0]}" == "" ]]; then
        # Absolute path
        canonical_path="/${clean_parts[*]:1}"
        canonical_path="${canonical_path//\/ /\/}"  # Fix spacing in path
    else
        # Relative path
        canonical_path="${clean_parts[*]}"
        canonical_path="${canonical_path// /\/}"  # Replace spaces with /
    fi
    
    # Store the original canonical path before resolution
    local output_path="$canonical_path"
    
    # If the path exists, resolve any symlinks to get the real path
    # This prevents symlink-based escapes
    if [[ -e "$canonical_path" ]]; then
        local real_path
        if command -v realpath >/dev/null 2>&1; then
            real_path=$(realpath "$canonical_path" 2>/dev/null) || real_path="$canonical_path"
        elif command -v readlink >/dev/null 2>&1; then
            # Fallback for systems without realpath
            real_path=$(cd "$(dirname "$canonical_path")" 2>/dev/null && pwd -P)/$(basename "$canonical_path")
        else
            real_path="$canonical_path"
        fi
        canonical_path="$real_path"
    fi
    
    # Ensure the resolved path is within the base directory
    if [[ "$canonical_path" != "$abs_base"* ]]; then
        echo "Error: Path traversal detected: $user_path would escape $base_dir" >&2
        return 1
    fi
    
    # Return the non-resolved path for consistency with user expectations
    echo "$output_path"
    return 0
}

# Sanitize a string for safe shell usage (removes special characters)
# Usage: sanitize_string "user input"
# Returns: Sanitized string on stdout
sanitize_string() {
    local input="$1"
    # Remove all characters except alphanumeric, dash, underscore, and dot
    # This is very restrictive but safe (no slashes allowed for commands)
    # Use tr to handle newlines and other control characters properly
    echo "$input" | tr -d '\n\r\t\0' | sed 's/[^a-zA-Z0-9._-]//g'
}

# Validate a command name (no paths, only command names)
# Usage: validate_command "ls"
# Returns: 0 if valid, 1 if invalid
validate_command() {
    local cmd="$1"
    
    # Check for empty command
    if [[ -z "$cmd" ]]; then
        echo "Error: Empty command" >&2
        return 1
    fi
    
    # Reject if contains path separators
    if [[ "$cmd" == *"/"* ]] || [[ "$cmd" == *"\\"* ]]; then
        echo "Error: Command contains path separator" >&2
        return 1
    fi
    
    # Reject if contains shell metacharacters
    if [[ "$cmd" =~ [^a-zA-Z0-9._-] ]]; then
        echo "Error: Command contains invalid characters" >&2
        return 1
    fi
    
    return 0
}

# Create a secure temporary file
# Usage: secure_temp_file "prefix"
# Returns: Path to temporary file on stdout
secure_temp_file() {
    local prefix="${1:-claude-pm}"
    
    # Sanitize prefix
    prefix=$(sanitize_string "$prefix")
    
    # Use mktemp with secure template
    local temp_file
    temp_file=$(mktemp "/tmp/${prefix}-XXXXXX") || {
        echo "Error: Failed to create temporary file" >&2
        return 1
    }
    
    # Set restrictive permissions
    chmod 600 "$temp_file"
    
    echo "$temp_file"
    return 0
}

# Create a secure temporary directory
# Usage: secure_temp_dir "prefix"
# Returns: Path to temporary directory on stdout
secure_temp_dir() {
    local prefix="${1:-claude-pm}"
    
    # Sanitize prefix
    prefix=$(sanitize_string "$prefix")
    
    # Use mktemp with secure template
    local temp_dir
    temp_dir=$(mktemp -d "/tmp/${prefix}-XXXXXX") || {
        echo "Error: Failed to create temporary directory" >&2
        return 1
    }
    
    # Set restrictive permissions
    chmod 700 "$temp_dir"
    
    echo "$temp_dir"
    return 0
}

# Safely remove a file or directory with validation
# Usage: safe_remove "/base/dir" "path/to/remove"
# Returns: 0 on success, 1 on error
safe_remove() {
    local base_dir="$1"
    local target="$2"
    
    # Validate the path first
    local validated_path
    validated_path=$(validate_path "$base_dir" "$target") || {
        echo "Error: Invalid path for removal: $target" >&2
        return 1
    }
    
    # Extra safety checks
    if [[ "$validated_path" == "/" ]] || [[ "$validated_path" == "$HOME" ]]; then
        echo "Error: Refusing to remove critical directory: $validated_path" >&2
        return 1
    fi
    
    # Check if path exists
    if [[ ! -e "$validated_path" ]]; then
        # Not an error - already removed
        return 0
    fi
    
    # Remove safely
    if [[ -d "$validated_path" ]]; then
        rm -rf "$validated_path"
    else
        rm -f "$validated_path"
    fi
    
    return $?
}

# Execute a command with validation
# Usage: safe_execute "command" "arg1" "arg2" ...
# Returns: Command exit code
safe_execute() {
    local cmd="$1"
    shift
    
    # Validate command
    if ! validate_command "$cmd"; then
        return 1
    fi
    
    # Check if command exists
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: Command not found: $cmd" >&2
        return 127
    fi
    
    # Execute with arguments (arguments are passed as-is, should be validated by caller)
    "$cmd" "$@"
    return $?
}

# Extract version from Python safely
# Usage: get_python_version "python3"
# Returns: Version string on stdout (e.g., "3.9")
get_python_version() {
    local python_cmd="$1"
    
    # Validate command first
    if ! validate_command "$python_cmd"; then
        return 1
    fi
    
    # Use a safe Python command that can't be exploited
    local version
    version=$("$python_cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
    local exit_code=$?
    
    # Validate output format (should be like "3.9")
    if [[ $exit_code -eq 0 ]] && [[ "$version" =~ ^[0-9]+\.[0-9]+$ ]]; then
        echo "$version"
        return 0
    else
        echo "Error: Failed to get Python version from $python_cmd" >&2
        return 1
    fi
}

# Compare version strings safely
# Usage: version_ge "3.9" "3.7"
# Returns: 0 if first >= second, 1 otherwise
version_ge() {
    local version1="$1"
    local version2="$2"
    
    # Validate format
    if ! [[ "$version1" =~ ^[0-9]+\.[0-9]+$ ]] || ! [[ "$version2" =~ ^[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Invalid version format" >&2
        return 2
    fi
    
    # Compare using sort -V if available
    if command -v sort >/dev/null 2>&1 && sort --version 2>&1 | grep -q GNU; then
        # Use GNU sort with version sort
        local highest
        highest=$(printf "%s\n%s" "$version1" "$version2" | sort -V | tail -n1)
        [[ "$highest" == "$version1" ]]
        return $?
    else
        # Fallback to manual comparison
        local major1="${version1%%.*}"
        local minor1="${version1#*.}"
        local major2="${version2%%.*}"
        local minor2="${version2#*.}"
        
        if [[ $major1 -gt $major2 ]]; then
            return 0
        elif [[ $major1 -eq $major2 ]] && [[ $minor1 -ge $minor2 ]]; then
            return 0
        else
            return 1
        fi
    fi
}

# Strip ANSI escape sequences from input
# Usage: strip_ansi "colored text"
# Returns: Plain text on stdout
strip_ansi() {
    local input="$1"
    # Remove ANSI escape sequences
    echo "$input" | sed 's/\x1b\[[0-9;]*m//g'
}

# Validate user input (Y/N responses)
# Usage: validate_yes_no "user_input"
# Returns: 0 for yes, 1 for no, 2 for invalid
validate_yes_no() {
    local input="$1"
    
    # Strip whitespace and convert to lowercase
    input=$(echo "$input" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')
    
    case "$input" in
        y|yes) return 0 ;;
        n|no) return 1 ;;
        *) return 2 ;;
    esac
}

# Setup signal handlers for cleanup
# Usage: setup_cleanup_trap "cleanup_function"
setup_cleanup_trap() {
    local cleanup_function="$1"
    
    if [[ -z "$cleanup_function" ]]; then
        echo "Error: No cleanup function specified" >&2
        return 1
    fi
    
    # Trap multiple signals
    trap "$cleanup_function" EXIT INT TERM HUP
    
    return 0
}

# Log security events
# Usage: log_security_event "event_type" "message" ["details"]
log_security_event() {
    local event_type="$1"
    local message="$2"
    local details="${3:-}"
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local log_entry="[$timestamp] SECURITY.$event_type: $message"
    
    if [[ -n "$details" ]]; then
        log_entry="$log_entry | Details: $details"
    fi
    
    # Log to stderr for security events
    echo "$log_entry" >&2
    
    # Also log to security log if available
    if [[ -n "$SECURITY_LOG" ]] && [[ -w "$SECURITY_LOG" ]]; then
        echo "$log_entry" >> "$SECURITY_LOG"
    fi
}

# Self-test function to verify security functions work correctly
# Usage: security_self_test
security_self_test() {
    echo "Running security library self-tests..."
    
    local tests_passed=0
    local tests_failed=0
    
    # Test validate_path
    echo -n "Testing validate_path... "
    if validate_path "/tmp" "test/../../../etc/passwd" >/dev/null 2>&1; then
        echo "FAIL: Path traversal not detected"
        ((tests_failed++))
    else
        echo "PASS"
        ((tests_passed++))
    fi
    
    # Test sanitize_string
    echo -n "Testing sanitize_string... "
    local sanitized=$(sanitize_string "test;rm -rf /")
    if [[ "$sanitized" == "testrmrf/" ]]; then
        echo "PASS"
        ((tests_passed++))
    else
        echo "FAIL: Got '$sanitized'"
        ((tests_failed++))
    fi
    
    # Test validate_command
    echo -n "Testing validate_command... "
    if validate_command "ls;rm" >/dev/null 2>&1; then
        echo "FAIL: Command injection not detected"
        ((tests_failed++))
    else
        echo "PASS"
        ((tests_passed++))
    fi
    
    # Test version comparison
    echo -n "Testing version_ge... "
    if version_ge "3.9" "3.7" && ! version_ge "3.7" "3.9"; then
        echo "PASS"
        ((tests_passed++))
    else
        echo "FAIL: Version comparison incorrect"
        ((tests_failed++))
    fi
    
    echo ""
    echo "Security self-tests complete: $tests_passed passed, $tests_failed failed"
    
    [[ $tests_failed -eq 0 ]]
    return $?
}

# Export functions if sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    export -f validate_path
    export -f sanitize_string
    export -f validate_command
    export -f secure_temp_file
    export -f secure_temp_dir
    export -f safe_remove
    export -f safe_execute
    export -f get_python_version
    export -f version_ge
    export -f strip_ansi
    export -f validate_yes_no
    export -f setup_cleanup_trap
    export -f log_security_event
    export -f security_self_test
fi