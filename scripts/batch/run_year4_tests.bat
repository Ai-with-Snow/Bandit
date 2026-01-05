@echo off
set "PYTHONPATH=C:\Users\Goddexx Snow\Documents\Bandit"
.venv\Scripts\python.exe -m pytest tests/year4/test_year4_production.py -v --tb=short > year4_test_results.log 2>&1
type year4_test_results.log
