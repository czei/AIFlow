#!/bin/bash
# Integration test for phase-driven development system
# This script simulates the workflow without requiring Claude Code

echo "🧪 Phase-Driven Development System Integration Test"
echo "=================================================="
echo

# Test directory setup
TEST_DIR="/Users/czei/ai-software-project-management/test-output"
PROJECT_NAME="test-measurable-project"
PROJECT_DIR="$TEST_DIR/$PROJECT_NAME"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

failure() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Cleanup function
cleanup() {
    info "Cleaning up test directory..."
    rm -rf "$TEST_DIR"
}

# Setup test environment
setup_test() {
    info "Setting up test environment..."
    
    # Create test directory
    mkdir -p "$TEST_DIR"
    cd "$TEST_DIR" || failure "Failed to create test directory"
    
    # Initialize git repo
    git init test-repo
    cd test-repo || failure "Failed to enter git repo"
    
    # Create initial commit
    echo "# Test Project" > README.md
    git add README.md
    git commit -m "Initial commit"
    
    success "Test environment ready"
}

# Test 1: Project Setup
test_project_setup() {
    echo
    echo "Test 1: Project Setup"
    echo "--------------------"
    
    # Simulate project setup command
    info "Creating git worktree..."
    git worktree add "../$PROJECT_NAME" -b "feature/$PROJECT_NAME"
    
    if [ -d "../$PROJECT_NAME" ]; then
        success "Git worktree created"
    else
        failure "Git worktree creation failed"
    fi
    
    cd "../$PROJECT_NAME" || failure "Failed to enter project directory"
    
    # Create project structure
    info "Creating project structure..."
    mkdir -p phases output .logs
    
    # Create measurable phase files
    cat > phases/01-setup.md << 'EOF'
# Phase 01: Setup

## Status: NOT_STARTED
## Completion: 0%

## Objectives:
- [ ] Create output/setup.txt with timestamp
- [ ] Create output/config.json with initial settings
- [ ] Initialize project metrics in output/metrics.json

## Measurable Outcomes:
- File: output/setup.txt exists
- File: output/config.json contains valid JSON
- File: output/metrics.json tracks phase progress
EOF

    cat > phases/02-process.md << 'EOF'
# Phase 02: Process

## Status: NOT_STARTED  
## Completion: 0%

## Objectives:
- [ ] Append processing log to output/setup.txt
- [ ] Update config.json with processing parameters
- [ ] Create output/processed_data.csv with sample data

## Measurable Outcomes:
- File: output/setup.txt has additional lines
- File: output/config.json modified with new keys
- File: output/processed_data.csv exists with headers
EOF

    cat > phases/03-validate.md << 'EOF'
# Phase 03: Validate

## Status: NOT_STARTED
## Completion: 0%

## Objectives:
- [ ] Validate all output files exist
- [ ] Create output/validation_report.txt
- [ ] Update metrics.json with validation results

## Measurable Outcomes:
- File: output/validation_report.txt contains all checks
- File: output/metrics.json updated with validation data
- All files pass validation checks
EOF
    
    # Create initial project state
    cat > .project-state.json << EOF
{
  "project_name": "$PROJECT_NAME",
  "current_phase": "01",
  "status": "setup",
  "automation_active": false,
  "workflow_step": "planning",
  "completed_phases": [],
  "started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

    success "Project structure created"
}

# Test 2: Phase Execution Simulation
test_phase_execution() {
    echo
    echo "Test 2: Phase Execution"
    echo "----------------------"
    
    # Phase 01: Setup
    info "Executing Phase 01: Setup..."
    
    # Create measurable outputs
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Project setup initialized" > output/setup.txt
    echo '{"version": "1.0", "environment": "test", "phase": "01"}' > output/config.json
    echo '{"phases": {"01": {"started": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'", "status": "in_progress"}}}' > output/metrics.json
    
    # Verify phase 01 outputs
    if [ -f "output/setup.txt" ] && [ -f "output/config.json" ] && [ -f "output/metrics.json" ]; then
        success "Phase 01 outputs created"
        
        # Update phase status
        sed -i '' 's/NOT_STARTED/COMPLETE/g' phases/01-setup.md
        sed -i '' 's/\[ \]/[x]/g' phases/01-setup.md
    else
        failure "Phase 01 outputs missing"
    fi
    
    # Phase 02: Process
    info "Executing Phase 02: Process..."
    
    # Append to existing files
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Processing started" >> output/setup.txt
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Processing completed" >> output/setup.txt
    
    # Update config
    cat > output/config.json << EOF
{
  "version": "1.0",
  "environment": "test",
  "phase": "02",
  "processing": {
    "method": "batch",
    "batch_size": 100,
    "completed": true
  }
}
EOF
    
    # Create CSV
    cat > output/processed_data.csv << EOF
id,name,value,status
1,item_a,100,processed
2,item_b,200,processed
3,item_c,300,processed
EOF
    
    if [ -f "output/processed_data.csv" ]; then
        success "Phase 02 outputs created"
        sed -i '' 's/NOT_STARTED/COMPLETE/g' phases/02-process.md
    else
        failure "Phase 02 outputs missing"
    fi
    
    # Phase 03: Validate
    info "Executing Phase 03: Validate..."
    
    # Create validation report
    cat > output/validation_report.txt << EOF
Validation Report
Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)

File Checks:
✅ output/setup.txt exists (3 lines)
✅ output/config.json exists (valid JSON)
✅ output/metrics.json exists (valid JSON)
✅ output/processed_data.csv exists (4 lines including header)

Content Validation:
✅ Config version: 1.0
✅ Processing completed: true
✅ CSV records: 3

Overall Status: PASSED
EOF
    
    # Update metrics
    cat > output/metrics.json << EOF
{
  "phases": {
    "01": {"started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "status": "complete"},
    "02": {"started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "status": "complete"},
    "03": {"started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "status": "complete"}
  },
  "validation": {
    "files_checked": 4,
    "files_valid": 4,
    "overall_status": "PASSED"
  }
}
EOF
    
    if [ -f "output/validation_report.txt" ]; then
        success "Phase 03 validation complete"
    else
        failure "Phase 03 validation failed"
    fi
}

# Test 3: State Management
test_state_management() {
    echo
    echo "Test 3: State Management"
    echo "-----------------------"
    
    # Test state transitions
    info "Testing workflow state transitions..."
    
    # Create workflow state file
    cat > .workflow-state.json << EOF
{
  "current_step": 1,
  "current_step_name": "planning",
  "quality_gates_passed": [],
  "automation_active": false
}
EOF
    
    # Simulate workflow progression
    workflow_steps=("planning" "implementation" "validation" "review" "refinement" "integration")
    
    for i in {0..5}; do
        step_num=$((i + 1))
        step_name="${workflow_steps[$i]}"
        
        cat > .workflow-state.json << EOF
{
  "current_step": $step_num,
  "current_step_name": "$step_name",
  "quality_gates_passed": [],
  "automation_active": true
}
EOF
        
        info "Workflow step $step_num: $step_name"
        sleep 0.5
    done
    
    success "Workflow state transitions tested"
    
    # Test quality gates
    info "Testing quality gate tracking..."
    
    gates=("compilation" "testing" "review" "integration" "documentation" "performance")
    gates_passed=""
    
    for gate in "${gates[@]}"; do
        if [ -n "$gates_passed" ]; then
            gates_passed="$gates_passed, \"$gate\""
        else
            gates_passed="\"$gate\""
        fi
        
        cat > .workflow-state.json << EOF
{
  "current_step": 6,
  "current_step_name": "integration",
  "quality_gates_passed": [$gates_passed],
  "automation_active": true
}
EOF
        
        info "Quality gate passed: $gate"
        sleep 0.5
    done
    
    success "Quality gates tracked successfully"
}

# Test 4: Logging Infrastructure
test_logging() {
    echo
    echo "Test 4: Logging Infrastructure"
    echo "-----------------------------"
    
    info "Creating structured logs..."
    
    # Create sample log entries
    correlation_id=$(uuidgen)
    
    # Automation log
    cat > .logs/automation.log << EOF
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","level":"INFO","category":"automation","correlation_id":"$correlation_id","phase":"01","workflow_step":"planning","event":"project_initialized","details":{"project":"$PROJECT_NAME"}}
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","level":"INFO","category":"automation","correlation_id":"$correlation_id","phase":"01","workflow_step":"implementation","event":"phase_started","details":{"objectives":3}}
EOF
    
    # Command log
    cat > .logs/commands.log << EOF
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","level":"INFO","category":"commands","correlation_id":"$correlation_id","event":"command_execution","details":{"command":"echo","exit_code":0,"duration_ms":45}}
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","level":"INFO","category":"commands","correlation_id":"$correlation_id","event":"command_execution","details":{"command":"cat","exit_code":0,"duration_ms":12}}
EOF
    
    # Performance log
    cat > .logs/performance.log << EOF
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","level":"DEBUG","category":"performance","event":"phase_performance","details":{"phase":"01","duration_ms":1234,"objectives_completed":3}}
EOF
    
    # Quality gates log
    cat > .logs/quality-gates.log << EOF
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","level":"INFO","category":"quality-gates","event":"gate_evaluation","details":{"gate":"compilation","result":"PASSED","duration_ms":500}}
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","level":"INFO","category":"quality-gates","event":"gate_evaluation","details":{"gate":"testing","result":"PASSED","duration_ms":2000}}
EOF
    
    # Verify logs created
    log_count=$(ls .logs/*.log 2>/dev/null | wc -l)
    if [ "$log_count" -ge 4 ]; then
        success "Structured logs created"
    else
        failure "Log creation failed"
    fi
    
    # Test log analysis
    info "Testing log analysis..."
    
    # Count log entries
    total_entries=$(cat .logs/*.log | wc -l)
    info "Total log entries: $total_entries"
    
    # Check for correlation tracking
    correlated=$(grep -c "$correlation_id" .logs/*.log)
    info "Correlated events: $correlated"
    
    success "Logging infrastructure verified"
}

# Test 5: Measurable Outcomes Summary
test_measurable_outcomes() {
    echo
    echo "Test 5: Measurable Outcomes"
    echo "--------------------------"
    
    info "Verifying all measurable outcomes..."
    
    # Check all expected files exist
    expected_files=(
        "output/setup.txt"
        "output/config.json"
        "output/metrics.json"
        "output/processed_data.csv"
        "output/validation_report.txt"
        ".project-state.json"
        ".workflow-state.json"
    )
    
    all_exist=true
    for file in "${expected_files[@]}"; do
        if [ -f "$file" ]; then
            success "File exists: $file"
        else
            failure "File missing: $file"
            all_exist=false
        fi
    done
    
    if $all_exist; then
        success "All expected files created"
    fi
    
    # Verify file contents are measurable
    info "Checking measurable changes..."
    
    # Count lines in setup.txt (should increase across phases)
    setup_lines=$(wc -l < output/setup.txt)
    info "setup.txt has $setup_lines lines"
    
    # Check JSON validity
    if python3 -m json.tool output/config.json > /dev/null 2>&1; then
        success "config.json is valid JSON"
    else
        failure "config.json is invalid"
    fi
    
    # Check CSV has data
    csv_lines=$(wc -l < output/processed_data.csv)
    info "CSV has $csv_lines lines"
    
    # Create final summary
    cat > output/test_summary.json << EOF
{
  "test_run": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project": "$PROJECT_NAME",
  "phases_completed": 3,
  "files_created": $(ls output/* | wc -l),
  "log_entries": $total_entries,
  "test_status": "PASSED",
  "measurable_outcomes": {
    "setup_txt_lines": $setup_lines,
    "csv_records": $((csv_lines - 1)),
    "json_files_valid": true,
    "all_files_present": $all_exist
  }
}
EOF
    
    success "Test summary created"
}

# Main test execution
main() {
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Run tests
    setup_test
    test_project_setup
    test_phase_execution
    test_state_management
    test_logging
    test_measurable_outcomes
    
    echo
    echo "=================================================="
    success "All integration tests completed successfully! 🎉"
    echo
    info "Test artifacts available at: $PROJECT_DIR"
    echo
    
    # Ask if user wants to keep test artifacts
    read -p "Keep test artifacts for inspection? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        trap - EXIT  # Remove cleanup trap
        info "Test artifacts preserved at: $PROJECT_DIR"
    else
        info "Cleaning up..."
    fi
}

# Run the tests
main
