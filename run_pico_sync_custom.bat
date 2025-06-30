@echo off
title Pico Sync Manager
echo Starting Pico Sync Manager...
py pico_sync_manager.py
if errorlevel 1 pause
