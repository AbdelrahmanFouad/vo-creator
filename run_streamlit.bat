@echo off
title VO Creator Streamlit — لوغز وحقيقة
cd /d "%~dp0"
echo ========================================================
echo   VO Creator Streamlit -- لوغز وحقيقة (@لغزوحقيقه)
echo   Starting Streamlit App on http://localhost:8501 ...
echo ========================================================
set STREAMLIT_SERVER_HEADLESS=true
& "D:\SCRIPTS\bulk youtube\venv_build\Scripts\python.exe" -m streamlit run app.py --server.port 8501 --server.headless true
pause
