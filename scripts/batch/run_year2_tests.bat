@echo off
.venv\Scripts\python.exe -m pytest tests/year2/test_year2_multimodal.py -v --tb=short > year2_test_results.log 2>&1
type year2_test_results.log
