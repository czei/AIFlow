#!/bin/bash
# Log analysis tools for sprint-driven development debugging
set -euo pipefail

PROJECT_DIR=${1:-.}
LOGS_DIR="$PROJECT_DIR/.logs"

# Signal handler
handle_signal() {
    echo ""
    echo "Analysis interrupted by signal"
    exit 130
}

# Set up signal traps
trap 'handle_signal' INT TERM HUP

# Check if logs directory exists
if [ ! -d "$LOGS_DIR" ]; then
    echo "❌ Logs directory not found: $LOGS_DIR"
    echo "Run some automation first to generate logs."
    exit 1
fi

echo "📊 Sprint-Driven Development Log Analysis"
echo "========================================"
echo "Project: $PROJECT_DIR"
echo "Logs: $LOGS_DIR"
echo

# Function to safely execute jq with error handling
safe_jq() {
    if command -v jq >/dev/null 2>&1; then
        jq "$@"
    else
        echo "⚠️  jq not available - showing raw JSON"
        cat
    fi
}

# Recent Activity Summary
echo "🕒 RECENT ACTIVITY (Last 20 events)"
echo "-----------------------------------"
if [ -f "$LOGS_DIR/automation.log" ]; then
    tail -20 "$LOGS_DIR/automation.log" | safe_jq -r '[.timestamp, .level, .event, .details.command // "N/A"] | @csv' | \
    sed 's/"//g' | column -t -s','
else
    echo "No automation.log found"
fi
echo

# Error Summary
echo "❌ ERROR SUMMARY"
echo "----------------"
if [ -f "$LOGS_DIR/errors.log" ]; then
    echo "Recent errors:"
    tail -10 "$LOGS_DIR/errors.log" | safe_jq -r '[.timestamp, .event, .details.error_message // .details.reason // "See details"] | @csv' | \
    sed 's/"//g' | column -t -s','
    
    echo
    echo "Error counts by type:"
    safe_jq -r '.event' "$LOGS_DIR/errors.log" 2>/dev/null | sort | uniq -c | sort -nr
else
    echo "No errors.log found"
fi
echo

# Command Execution Summary
echo "🔧 COMMAND EXECUTION SUMMARY"
echo "----------------------------"
if [ -f "$LOGS_DIR/commands.log" ]; then
    echo "Recent command executions:"
    tail -10 "$LOGS_DIR/commands.log" | safe_jq -r '[.timestamp, .details.command, .details.exit_code, .details.duration_ms] | @csv' | \
    sed 's/"//g' | column -t -s','
    
    echo
    echo "Command success rate:"
    total_commands=$(wc -l < "$LOGS_DIR/commands.log" 2>/dev/null || echo "0")
    failed_commands=$(safe_jq 'select(.details.exit_code != 0)' "$LOGS_DIR/commands.log" 2>/dev/null | wc -l)
    if [ "$total_commands" -gt 0 ]; then
        # Calculate success rate using bash arithmetic (integer only)
        if [ "$total_commands" -gt 0 ]; then
            success_rate=$(( (total_commands - failed_commands) * 100 / total_commands ))
        else
            success_rate="N/A"
        fi
        echo "Total commands: $total_commands"
        echo "Failed commands: $failed_commands" 
        echo "Success rate: $success_rate%"
    else
        echo "No command data available"
    fi
else
    echo "No commands.log found"
fi
echo

# Workflow Progress
echo "⚡ WORKFLOW PROGRESS"
echo "-------------------"
if [ -f "$LOGS_DIR/workflow.log" ]; then
    echo "Recent workflow events:"
    tail -10 "$LOGS_DIR/workflow.log" | safe_jq -r '[.timestamp, .workflow_step, .event, .sprint] | @csv' | \
    sed 's/"//g' | column -t -s','
else
    echo "No workflow.log found"
fi
echo

# Performance Metrics
echo "🚀 PERFORMANCE METRICS"
echo "----------------------"
if [ -f "$LOGS_DIR/performance.log" ]; then
    echo "Slowest operations (>5 seconds):"
    safe_jq 'select(.details.duration_ms > 5000)' "$LOGS_DIR/performance.log" 2>/dev/null | \
    safe_jq -r '[.details.command, .details.duration_ms] | @csv' | \
    sed 's/"//g' | sort -t',' -k2 -nr | head -5 | column -t -s','
    
    echo
    echo "Average command execution time:"
    avg_time=$(safe_jq -r '.details.duration_ms' "$LOGS_DIR/performance.log" 2>/dev/null | \
               awk '{sum+=$1; count++} END {if(count>0) printf "%.1f", sum/count; else print "N/A"}')
    echo "${avg_time}ms"
else
    echo "No performance.log found"
fi
echo

# Quality Gates
echo "✅ QUALITY GATES"
echo "---------------"
if [ -f "$LOGS_DIR/quality-gates.log" ]; then
    echo "Recent quality gate evaluations:"
    tail -10 "$LOGS_DIR/quality-gates.log" | safe_jq -r '[.timestamp, .event, .details.validation_result // "N/A", .details.command // "N/A"] | @csv' | \
    sed 's/"//g' | column -t -s','
    
    echo
    echo "Quality gate success rate:"
    total_gates=$(wc -l < "$LOGS_DIR/quality-gates.log" 2>/dev/null || echo "0")
    passed_gates=$(safe_jq 'select(.details.validation_result == "ALLOWED")' "$LOGS_DIR/quality-gates.log" 2>/dev/null | wc -l)
    if [ "$total_gates" -gt 0 ]; then
        # Calculate gate success rate using bash arithmetic
        gate_success_rate=$(( passed_gates * 100 / total_gates ))
        echo "Total evaluations: $total_gates"
        echo "Passed: $passed_gates"
        echo "Success rate: $gate_success_rate%"
    else
        echo "No quality gate data available"
    fi
else
    echo "No quality-gates.log found"
fi
echo

# Correlation ID Analysis
echo "🔗 CORRELATION ANALYSIS"
echo "----------------------"
if [ -f "$LOGS_DIR/automation.log" ]; then
    echo "Recent correlation IDs (for detailed tracing):"
    tail -5 "$LOGS_DIR/automation.log" | safe_jq -r '.correlation_id' | sort -u | head -3
    
    echo
    echo "To trace a specific session, use:"
    echo "grep 'correlation-id-here' $LOGS_DIR/*.log | jq ."
else
    echo "No automation.log found"
fi
echo

echo "📋 LOG FILES SUMMARY"
echo "-------------------"
for log_file in "$LOGS_DIR"/*.log; do
    if [ -f "$log_file" ]; then
        filename=$(basename "$log_file")
        size=$(ls -lh "$log_file" | awk '{print $5}')
        lines=$(wc -l < "$log_file")
        echo "$filename: $lines lines, $size"
    fi
done

echo
echo "🔍 DETAILED ANALYSIS COMMANDS"
echo "-----------------------------"
echo "Real-time monitoring:"
echo "  tail -f $LOGS_DIR/automation.log | jq ."
echo "  tail -f $LOGS_DIR/errors.log | jq ."
echo
echo "Specific analysis:"
echo "  # Find all failed commands:"
echo "  jq 'select(.details.exit_code != 0)' $LOGS_DIR/commands.log"
echo
echo "  # Performance analysis:"
echo "  jq 'select(.details.duration_ms > 1000)' $LOGS_DIR/performance.log"
echo
echo "  # Trace specific correlation ID:"
echo "  grep 'your-correlation-id' $LOGS_DIR/*.log | jq ."

echo
echo "✨ Analysis complete. Use the commands above for deeper investigation."
