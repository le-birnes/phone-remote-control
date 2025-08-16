$WshShell = New-Object -comObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$Shortcut = $WshShell.CreateShortcut("$Desktop\Phone Remote Control.lnk")
$Shortcut.TargetPath = "E:\Claude\repos\phone-remote-control\Phone Remote Control.bat"
$Shortcut.Description = "Control your PC from your phone"
$Shortcut.IconLocation = "C:\Windows\System32\SHELL32.dll,13"
$Shortcut.WorkingDirectory = "E:\Claude\repos\phone-remote-control"
$Shortcut.Save()
Write-Host "Desktop shortcut created successfully!"