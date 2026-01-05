@echo off
REM Run all Bandit curriculum tests Years 1-12 with real-time output
REM Created: 2025-12-06

echo ============================================
echo  BANDIT 12-YEAR CURRICULUM TEST SUITE
echo  Running Years 1-12 with live output
echo ============================================
echo.

cd /d "C:\Users\Goddexx Snow\Documents\Bandit"

echo [Year 1] Gemini API Fundamentals
echo ----------------------------------------
.venv\Scripts\python.exe -m pytest tests/year1/ -v -s --tb=short
echo.

echo [Year 2] Multimodal Capabilities
echo ----------------------------------------
.venv\Scripts\python.exe -m pytest tests/year2/ -v -s --tb=short
echo.

echo [Year 3] Advanced Features ^& Tools
echo ----------------------------------------
.venv\Scripts\python.exe -m pytest tests/year3/ -v -s --tb=short
echo.

echo [Year 4] Production Systems
echo ----------------------------------------
.venv\Scripts\python.exe -m pytest tests/year4/ -v -s --tb=short
echo.

echo [Year 5] Advanced Agent Architectures
echo ----------------------------------------
.venv\Scripts\python.exe -m pytest tests/year5/ -v -s --tb=short
echo.

echo [Year 6] Master's Thesis
echo ----------------------------------------
.venv\Scripts\python.exe -m pytest tests/year6/ -v -s --tb=short
echo.

echo [Years 7-8] PhD Qualifying Exams
echo ----------------------------------------
.venv\Scripts\python.exe -m pytest tests/year7_8/ -v -s --tb=short
echo.

echo [Years 9-10] Dissertation Research
echo ----------------------------------------
.venv\Scripts\python.exe -m pytest tests/year9_10/ -v -s --tb=short
echo.

echo [Year 11] Publication ^& Defense Prep
echo ----------------------------------------
.venv\Scripts\python.exe -m pytest tests/year11/ -v -s --tb=short
echo.

echo [Year 12] PhD Defense
echo ----------------------------------------
.venv\Scripts\python.exe -m pytest tests/year12/ -v -s --tb=short
echo.

echo ============================================
echo  ALL YEARS COMPLETE
echo ============================================
pause
