@echo off
.venv\Scripts\python.exe -m pytest tests/year1/test_year1_fundamentals.py -v --tb=short > year1_test_results.log 2>&1
type year1_test_results.log
