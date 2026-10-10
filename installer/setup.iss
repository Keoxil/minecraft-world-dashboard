; Inno Setup script: builds MinecraftWorldDashboard-Setup.exe from the PyInstaller folder in dist_app/.
; Installs per-user (no administrator rights), adds Start menu / desktop shortcuts and an uninstaller.

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#define MyAppName "Minecraft World Dashboard"
#define MyAppExe "MinecraftWorldDashboard.exe"

[Setup]
AppId={{9B6C0C5E-6B1F-4C55-9E54-3C0D6E2B7A11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher=Keoxil
AppPublisherURL=https://github.com/Keoxil/minecraft-world-dashboard
AppSupportURL=https://github.com/Keoxil/minecraft-world-dashboard/issues
AppUpdatesURL=https://github.com/Keoxil/minecraft-world-dashboard/releases
VersionInfoCompany=Keoxil
VersionInfoDescription={#MyAppName} Setup
VersionInfoVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=MinecraftWorldDashboard-Setup
SetupIconFile=..\assets\app.ico
UninstallDisplayIcon={app}\{#MyAppExe}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"
Name: "autostart"; Description: "Start {#MyAppName} when I log in to Windows"; GroupDescription: "Options:"; Flags: unchecked

[Files]
Source: "..\dist_app\MinecraftWorldDashboard\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "MinecraftWorldDashboard"; ValueData: """{app}\{#MyAppExe}"" --minimized"; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExe}"; Description: "Open {#MyAppName} now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; the app's own data (settings, cached maps, history) lives here
Type: filesandordirs; Name: "{localappdata}\MinecraftWorldDashboard"
