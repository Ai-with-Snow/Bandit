@echo off
set "PYTHONPATH=C:\Users\Goddexx Snow\Documents\Bandit"
.venv\Scripts\python.exe -m pytest tests/year3/test_year3_tools.py tests/year3/test_year3_reasoning.py -v --tb=short > year3_test_results.log 2>&1
type year3_test_results.log
