@echo off
echo Starting TTS Server...
echo Please ensure you have activated your conda environment first if not using a system python.
echo Usage: conda activate qwen3-tts && run_tts_server.bat
echo.
python tts_server.py
pause
