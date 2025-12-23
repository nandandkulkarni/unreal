# Enable GPU Acceleration for Remote Desktop
# This script must be run as Administrator
# After running, a RESTART is required for changes to take effect

Write-Host "=============================================="
Write-Host "ENABLING GPU ACCELERATION FOR REMOTE DESKTOP"
Write-Host "=============================================="
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "Running with Administrator privileges..." -ForegroundColor Green
Write-Host ""

# Registry path for Terminal Services policies
$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services"

# Create the registry path if it doesn't exist
if (-not (Test-Path $regPath)) {
    Write-Host "Creating registry path: $regPath"
    New-Item -Path $regPath -Force | Out-Null
}

Write-Host "Applying GPU acceleration settings..."
Write-Host ""

# 1. Use WDDM graphics display driver for Remote Desktop Connections
Write-Host "  [1/4] Enabling WDDM graphics driver..."
Set-ItemProperty -Path $regPath -Name "fEnableWddmDriver" -Value 1 -Type DWord -Force

# 2. Use hardware default graphics adapter for all RDP sessions
Write-Host "  [2/4] Enabling hardware graphics adapter..."
Set-ItemProperty -Path $regPath -Name "bEnumerateHWBeforeSW" -Value 1 -Type DWord -Force

# 3. Enable H.264/AVC hardware encoding
Write-Host "  [3/4] Enabling H.264/AVC hardware encoding..."
Set-ItemProperty -Path $regPath -Name "AVCHardwareEncodePreferred" -Value 1 -Type DWord -Force

# 4. Prioritize H.264/AVC 444 Graphics mode
Write-Host "  [4/4] Enabling AVC 444 Graphics mode..."
Set-ItemProperty -Path $regPath -Name "AVC444ModePreferred" -Value 1 -Type DWord -Force

# Also set system-level keys to ensure policies take effect
$sysTsPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server"
$rdpTcpPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp"

Write-Host ""
Write-Host "Applying system Terminal Server settings..."
Set-ItemProperty -Path $sysTsPath -Name "UseWDDMGraphicsDriver" -Value 1 -Type DWord -Force
Set-ItemProperty -Path $rdpTcpPath -Name "UseDefaultGfxAdapter" -Value 1 -Type DWord -Force

Write-Host ""
Write-Host "=============================================="
Write-Host "SETTINGS APPLIED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=============================================="
Write-Host ""
Write-Host "Current registry values:"
Get-ItemProperty -Path $regPath | Select-Object fEnableWddmDriver, bEnumerateHWBeforeSW, AVCHardwareEncodePreferred, AVC444ModePreferred | Format-List
Get-ItemProperty -Path $sysTsPath | Select-Object UseWDDMGraphicsDriver | Format-List
Get-ItemProperty -Path $rdpTcpPath | Select-Object UseDefaultGfxAdapter | Format-List

Write-Host ""
Write-Host "IMPORTANT: You must RESTART the computer for changes to take effect!" -ForegroundColor Yellow
Write-Host ""

$restart = Read-Host "Would you like to restart now? (y/n)"
if ($restart -eq 'y' -or $restart -eq 'Y') {
    Write-Host "Restarting in 10 seconds... Press Ctrl+C to cancel."
    Start-Sleep -Seconds 10
    Restart-Computer -Force
} else {
    Write-Host "Please restart manually when ready."
}
