# AAANKPose Plugin v3 Distribution Packager
# Creates a clean distribution package on Desktop

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  AAANKPose Plugin v3 Packager" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Paths
$SourceBinaries = "$env:USERPROFILE\Desktop\AAANKPose_v2.0.0_Final\Binaries"
$PluginSource = "C:\UnrealProjects\ThirdPerson5\Plugins\AAANKPose"
$Destination = "$env:USERPROFILE\Desktop\AAANKPose_v3"

# Remove old v3 if exists
if (Test-Path $Destination) {
    Write-Host "Removing old v3 distribution..." -ForegroundColor Yellow
    Remove-Item $Destination -Recurse -Force
}

# Create directory structure
Write-Host "Creating directory structure..." -ForegroundColor Green
New-Item -ItemType Directory -Path "$Destination\Binaries\Win64" -Force | Out-Null
New-Item -ItemType Directory -Path "$Destination\Resources" -Force | Out-Null
New-Item -ItemType Directory -Path "$Destination\Config" -Force | Out-Null

# Copy compiled binaries
Write-Host "Copying compiled binaries..." -ForegroundColor Green
if (Test-Path "$SourceBinaries\Win64\UnrealEditor-AAANKPose.dll") {
    Copy-Item "$SourceBinaries\Win64\*.dll" "$Destination\Binaries\Win64\" -Force
    Copy-Item "$SourceBinaries\Win64\*.modules" "$Destination\Binaries\Win64\" -Force -ErrorAction SilentlyContinue
    Write-Host "  ? DLL: $(Get-Item "$SourceBinaries\Win64\UnrealEditor-AAANKPose.dll" | Select-Object -ExpandProperty Length) bytes" -ForegroundColor Gray
} else {
    Write-Host "  ? WARNING: No compiled DLL found!" -ForegroundColor Red
}

# Copy plugin descriptor
Write-Host "Copying plugin descriptor..." -ForegroundColor Green
Copy-Item "$PluginSource\AAANKPose.uplugin" "$Destination\" -Force

# Copy resources
Write-Host "Copying resources..." -ForegroundColor Green
if (Test-Path "$PluginSource\Resources") {
    Copy-Item "$PluginSource\Resources\*" "$Destination\Resources\" -Force -Recurse
}

# Copy config
Write-Host "Copying config..." -ForegroundColor Green
if (Test-Path "$PluginSource\Config") {
    Copy-Item "$PluginSource\Config\*" "$Destination\Config\" -Force -Recurse
}

# Copy documentation
Write-Host "Copying documentation..." -ForegroundColor Green
if (Test-Path "$PluginSource\README.md") {
    Copy-Item "$PluginSource\README.md" "$Destination\" -Force
}

# Create INSTALL.md
Write-Host "Creating installation guide..." -ForegroundColor Green
@"
# AAANKPose Plugin v2.0.0 - Distribution v3

## Installation

1. **Copy plugin to your project:**
   ``````
   Copy: AAANKPose_v3 folder
   To:   YourProject\Plugins\AAANKPose\
   ``````

2. **Enable required plugins:**
   - Open Unreal Editor
   - Edit ? Plugins
   - Enable "PoseSearch"
   - Enable "AAANKPose"
   - Restart editor

## Features (7 Functions)

**Runtime-Safe:**
- GetHelloWorld() - Test function
- GetAnimationCount() - Query database
- GetDatabaseInfo() - Get details

**Editor-Only:**
- AddAnimationToDatabase() - Add single animation
- AddAnimationsToDatabase() - Batch add
- BuildDatabase() - Rebuild index
- ClearDatabase() - Remove all animations

## Python API Example

``````python
import unreal

# Load assets
db = unreal.load_asset("/Game/MyDatabase")
anim = unreal.load_asset("/Game/Animations/MyAnim")

# Add animation (Editor only)
unreal.AAANKPoseBlueprintLibrary.add_animation_to_database(db, anim)

# Build database (Editor only)
unreal.AAANKPoseBlueprintLibrary.build_database(db)

# Get info (works everywhere)
info = unreal.AAANKPoseBlueprintLibrary.get_database_info(db)
print(info)
``````

## Requirements

- Unreal Engine 5.7
- Windows x64
- PoseSearch plugin enabled

## Version

- Plugin: 2.0.0
- Distribution: v3
- Build: January 2026
"@ | Out-File "$Destination\INSTALL.md" -Encoding UTF8

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  Package Created Successfully!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Location: $Destination" -ForegroundColor Cyan
Write-Host ""
Write-Host "Contents:" -ForegroundColor Yellow
Get-ChildItem $Destination -Recurse | ForEach-Object {
    $indent = "  " * (($_.FullName.Replace($Destination, "").Split("\").Count) - 2)
    if ($_.PSIsContainer) {
        Write-Host "$indent?? $($_.Name)/" -ForegroundColor Cyan
    } else {
        $size = if ($_.Length -gt 1KB) { "{0:N1} KB" -f ($_.Length / 1KB) } else { "$($_.Length) bytes" }
        Write-Host "$indent?? $($_.Name) ($size)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Ready for distribution!" -ForegroundColor Green
Write-Host ""

# Open folder
Start-Process explorer.exe $Destination
