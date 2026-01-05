@echo off
REM Build and Package AAANKPose Plugin v2.0.0

echo ====================================
echo AAANKPose v2.0.0 - Build and Package
echo ====================================
echo.

set PLUGIN_DIR=%~dp0
set PLUGIN_FILE=%PLUGIN_DIR%AAANKPose.uplugin
set OUTPUT_DIR=%USERPROFILE%\Desktop\AAANKPose_v2.0.0_Final
set UE_ENGINE_DIR=C:\Program Files\Epic Games\UE_5.7
set UAT_BAT=%UE_ENGINE_DIR%\Engine\Build\BatchFiles\RunUAT.bat

echo Plugin: %PLUGIN_FILE%
echo Output: %OUTPUT_DIR%
echo.

REM Check if UAT exists
if not exist "%UAT_BAT%" (
    echo ERROR: Unreal Automation Tool not found!
    echo Expected: %UAT_BAT%
    pause
    exit /b 1
)

echo Building plugin with Unreal Build Tool...
echo This will take several minutes...
echo.

REM Build the plugin
"%UAT_BAT%" BuildPlugin -Plugin="%PLUGIN_FILE%" -Package="%OUTPUT_DIR%" -CreateSubFolder -TargetPlatforms=Win64

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Plugin build failed!
    pause
    exit /b 1
)

echo.
echo Cleaning up...
set PLUGIN_OUTPUT=%OUTPUT_DIR%\AAANKPose

REM Remove source code for binary distribution
if exist "%PLUGIN_OUTPUT%\Source\" (
    rmdir /s /q "%PLUGIN_OUTPUT%\Source\"
)

REM Remove intermediate files
if exist "%PLUGIN_OUTPUT%\Intermediate\" (
    rmdir /s /q "%PLUGIN_OUTPUT%\Intermediate\"
)

REM Copy documentation
copy "%PLUGIN_DIR%README.md" "%PLUGIN_OUTPUT%\" /Y >nul 2>&1

REM Create installation guide
(
echo # AAANKPose Plugin v2.0.0 - Binary Distribution
echo.
echo ## What's New:
echo - Complete PoseSearch database management API
echo - 7 Blueprint-callable functions
echo - Add/remove animations, build databases, query info
echo.
echo ## Installation:
echo 1. Copy entire folder to: YourProject\Plugins\AAANKPose\
echo 2. Enable in Edit ^> Plugins
echo 3. Restart editor
echo.
echo ## Binary Distribution - No source code included
echo.
echo Version: 2.0.0
) > "%PLUGIN_OUTPUT%\INSTALL.txt"

echo.
echo ====================================
echo SUCCESS! Plugin v2.0.0 Built
echo ====================================
echo.
echo Location: %PLUGIN_OUTPUT%
echo.
echo Contents:
echo   - Compiled DLLs ^(binary only^)
echo   - Plugin descriptor v2.0.0
echo   - Documentation
echo   - NO source code
echo.

explorer "%OUTPUT_DIR%"
pause
