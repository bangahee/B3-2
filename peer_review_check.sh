#!/bin/bash

set -e

echo "========================================"
echo "1. Python syntax check"
echo "========================================"

python -m py_compile \
    main.py \
    mini_git.py \
    models/commit.py \
    algorithms/graph.py \
    algorithms/sorting.py

echo "PASS: Python syntax is valid."
echo

echo "========================================"
echo "2. Forbidden sorting API check"
echo "========================================"

python check_constraints.py
echo

echo "========================================"
echo "3. Basic command test"
echo "========================================"

python main.py < tests/basic_commands.txt
echo

echo "========================================"
echo "4. Branch command test"
echo "========================================"

python main.py < tests/branch_commands.txt
echo

echo "========================================"
echo "5. Search command test"
echo "========================================"

python main.py < tests/search_commands.txt
echo

echo "========================================"
echo "6. Error handling test"
echo "========================================"

python main.py < tests/error_commands.txt
echo

echo "========================================"
echo "ALL AUTOMATED CHECKS PASSED"
echo "========================================"