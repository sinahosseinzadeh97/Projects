#!/bin/bash

# Run tests for the Intelligent Multi-Agent Email Automation System
# This script runs all test suites and reports results

echo "Starting tests for the Intelligent Multi-Agent Email Automation System..."
echo "========================================================================"

# Create logs directory if it doesn't exist
mkdir -p ../logs

# Function to run a test and report results
run_test() {
    test_file=$1
    test_name=$2
    
    echo ""
    echo "Running $test_name tests..."
    echo "----------------------------------------"
    
    # Run the test
    python3 $test_file 2>&1 | tee ../logs/$(basename $test_file .py)_results.log
    
    # Check if test passed
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✅ $test_name tests PASSED"
    else
        echo "❌ $test_name tests FAILED"
    fi
}

# Run system component tests
run_test "test_system.py" "System Component"

# Run API endpoint tests
run_test "test_api.py" "API Endpoint"

# Run frontend tests
run_test "test_frontend.py" "Frontend"

# Run integration tests
run_test "test_integration.py" "Integration"

echo ""
echo "========================================================================"
echo "All tests completed. See logs directory for detailed results."
echo "Summary of test results:"

# Print summary of test results
for log_file in ../logs/*_results.log; do
    test_name=$(basename $log_file _results.log)
    if grep -q "FAILED" $log_file; then
        echo "❌ $test_name: FAILED"
    else
        echo "✅ $test_name: PASSED"
    fi
done
