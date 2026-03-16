; King's Quest V Hebrew Patch Installer
; NSIS Script

;--------------------------------
; General Attributes

Name "King's Quest V - תרגום עברי"
OutFile "KQ5_Hebrew_Patch_Setup.exe"
InstallDir ""
RequestExecutionLevel admin

;--------------------------------
; Version Information

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "King's Quest V Hebrew Patch"
VIAddVersionKey "FileDescription" "Hebrew Translation Patch for King's Quest V"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0.0"
VIAddVersionKey "LegalCopyright" "Hebrew Translation Team"

;--------------------------------
; Modern UI

!include "MUI2.nsh"

;--------------------------------
; MUI Settings

!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Custom Hebrew text
!define MUI_WELCOMEPAGE_TITLE "ברוכים הבאים להתקנת התרגום העברי"
!define MUI_WELCOMEPAGE_TEXT "אשף זה ידריך אותך בהתקנת התרגום העברי למשחק King's Quest V.$\r$\n$\r$\nלחץ 'הבא' כדי להמשיך."
!define MUI_DIRECTORYPAGE_TEXT_TOP "בחר את תיקיית המשחק שבה מותקן King's Quest V."
!define MUI_FINISHPAGE_TITLE "ההתקנה הושלמה בהצלחה"
!define MUI_FINISHPAGE_TEXT "התרגום העברי הותקן בהצלחה.$\r$\n$\r$\nלחץ 'סיום' כדי לסגור אשף זה."

;--------------------------------
; Pages

!insertmacro MUI_PAGE_WELCOME
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE CheckAlreadyInstalled
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "Hebrew"

;--------------------------------
; Macros
;
; BackupAndInstall FILE:
;   If the file already exists in $INSTDIR, back it up to hebrew_patch_backup\
;   before overwriting it. Uses relative jumps to avoid duplicate label issues.
;
; UninstallFile FILE:
;   If a backup exists, restore it (revert to original).
;   If no backup exists, the file was new — delete it.

!macro BackupAndInstall FILE
  IfFileExists "$INSTDIR\${FILE}" 0 +3
    CreateDirectory "$INSTDIR\hebrew_patch_backup"
    CopyFiles /SILENT "$INSTDIR\${FILE}" "$INSTDIR\hebrew_patch_backup\${FILE}"
  File "kq5_work\${FILE}"
!macroend

!macro UninstallFile FILE
  IfFileExists "$INSTDIR\hebrew_patch_backup\${FILE}" 0 +3
    CopyFiles /SILENT "$INSTDIR\hebrew_patch_backup\${FILE}" "$INSTDIR\${FILE}"
    Goto +2
  Delete "$INSTDIR\${FILE}"
!macroend

;--------------------------------
; Directory-leave callback — prevent re-installation in the same folder

Function CheckAlreadyInstalled
  IfFileExists "$INSTDIR\hebrew_patch_installed.dat" 0 dir_ok
    MessageBox MB_OK|MB_ICONEXCLAMATION "התרגום העברי כבר מותקן בתיקייה זו.$\r$\nיש להסיר אותו תחילה לפני התקנה מחדש."
    Abort
  dir_ok:
FunctionEnd

;--------------------------------
; Validation Function

Function .onVerifyInstDir
  IfFileExists "$INSTDIR\resource.map" valid_dir
  IfFileExists "$INSTDIR\RESOURCE.MAP" valid_dir
  Abort
  valid_dir:
    Return
FunctionEnd

;--------------------------------
; Installer Section

Section "King's Quest V Hebrew Patch" SecMain

  SetOutPath "$INSTDIR"
  SetOverwrite try
  ; Source files
  !insertmacro BackupAndInstall "0.SCR"
  !insertmacro BackupAndInstall "119.SCR"
  !insertmacro BackupAndInstall "255.scr"
  !insertmacro BackupAndInstall "300.scr"
  !insertmacro BackupAndInstall "604.scr"
  !insertmacro BackupAndInstall "673.scr"
  !insertmacro BackupAndInstall "753.scr"
  !insertmacro BackupAndInstall "756.scr"
  !insertmacro BackupAndInstall "763.scr"
  !insertmacro BackupAndInstall "928.scr"

  ; Font files
  !insertmacro BackupAndInstall "0.fon"
  !insertmacro BackupAndInstall "1.fon"
  !insertmacro BackupAndInstall "4.fon"
  !insertmacro BackupAndInstall "8.fon"
  !insertmacro BackupAndInstall "9.fon"
  !insertmacro BackupAndInstall "69.fon"

  ; v56 files
  !insertmacro BackupAndInstall "934.v56"
  !insertmacro BackupAndInstall "946.v56"

  ; p56 files
  !insertmacro BackupAndInstall "107.p56"

  ; TEX files (uppercase extension)
  !insertmacro BackupAndInstall "0.TEX"
  !insertmacro BackupAndInstall "119.TEX"
  !insertmacro BackupAndInstall "610.TEX"

  ; tex files (lowercase extension)
  !insertmacro BackupAndInstall "29.tex"
  !insertmacro BackupAndInstall "63.tex"
  !insertmacro BackupAndInstall "89.tex"
  !insertmacro BackupAndInstall "113.tex"
  !insertmacro BackupAndInstall "123.tex"
  !insertmacro BackupAndInstall "216.tex"
  !insertmacro BackupAndInstall "220.tex"
  !insertmacro BackupAndInstall "300.tex"
  !insertmacro BackupAndInstall "301.tex"
  !insertmacro BackupAndInstall "330.tex"
  !insertmacro BackupAndInstall "331.tex"
  !insertmacro BackupAndInstall "340.tex"
  !insertmacro BackupAndInstall "341.tex"
  !insertmacro BackupAndInstall "350.tex"
  !insertmacro BackupAndInstall "351.tex"
  !insertmacro BackupAndInstall "370.tex"
  !insertmacro BackupAndInstall "371.tex"
  !insertmacro BackupAndInstall "390.tex"
  !insertmacro BackupAndInstall "391.tex"
  !insertmacro BackupAndInstall "600.tex"
  !insertmacro BackupAndInstall "601.tex"
  !insertmacro BackupAndInstall "602.tex"
  !insertmacro BackupAndInstall "650.tex"
  !insertmacro BackupAndInstall "659.tex"
  !insertmacro BackupAndInstall "663.tex"
  !insertmacro BackupAndInstall "664.tex"
  !insertmacro BackupAndInstall "673.tex"
  !insertmacro BackupAndInstall "749.tex"
  !insertmacro BackupAndInstall "754.tex"
  !insertmacro BackupAndInstall "755.tex"
  !insertmacro BackupAndInstall "756.tex"
  !insertmacro BackupAndInstall "763.tex"
  !insertmacro BackupAndInstall "889.tex"
  !insertmacro BackupAndInstall "950.tex"

  ; Write marker file so re-installation into this directory is blocked
  FileOpen $0 "$INSTDIR\hebrew_patch_installed.dat" w
  FileWrite $0 "KQ5 Hebrew Patch installed"
  FileClose $0

  ; Store installation folder
  WriteRegStr HKLM "Software\KQ5_Hebrew_Patch" "Install_Dir" "$INSTDIR"

  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall_KQ5_Hebrew_Patch.exe"

  ; Write uninstall registry keys
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ5_Hebrew_Patch" "DisplayName" "King's Quest V - Hebrew Patch"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ5_Hebrew_Patch" "UninstallString" '"$INSTDIR\Uninstall_KQ5_Hebrew_Patch.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ5_Hebrew_Patch" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ5_Hebrew_Patch" "NoRepair" 1

SectionEnd

;--------------------------------
; Uninstaller Section

Section "Uninstall"
  ; Source files
  !insertmacro UninstallFile "0.SCR"
  !insertmacro UninstallFile "119.SCR"
  !insertmacro UninstallFile "255.scr"
  !insertmacro UninstallFile "300.scr"
  !insertmacro UninstallFile "604.scr"
  !insertmacro UninstallFile "673.scr"
  !insertmacro UninstallFile "753.scr"
  !insertmacro UninstallFile "756.scr"
  !insertmacro UninstallFile "763.scr"
  !insertmacro UninstallFile "928.scr"

  ; Font files
  !insertmacro UninstallFile "0.fon"
  !insertmacro UninstallFile "1.fon"
  !insertmacro UninstallFile "4.fon"
  !insertmacro UninstallFile "8.fon"
  !insertmacro UninstallFile "9.fon"
  !insertmacro UninstallFile "69.fon"

  ; v56 files
  !insertmacro UninstallFile "934.v56"
  !insertmacro UninstallFile "946.v56"

  ; p56 files
  !insertmacro UninstallFile "107.p56"

  ; TEX files (uppercase extension)
  !insertmacro UninstallFile "0.TEX"
  !insertmacro UninstallFile "119.TEX"
  !insertmacro UninstallFile "610.TEX"

  ; tex files (lowercase extension)
  !insertmacro UninstallFile "29.tex"
  !insertmacro UninstallFile "63.tex"
  !insertmacro UninstallFile "89.tex"
  !insertmacro UninstallFile "113.tex"
  !insertmacro UninstallFile "123.tex"
  !insertmacro UninstallFile "216.tex"
  !insertmacro UninstallFile "220.tex"
  !insertmacro UninstallFile "300.tex"
  !insertmacro UninstallFile "301.tex"
  !insertmacro UninstallFile "330.tex"
  !insertmacro UninstallFile "331.tex"
  !insertmacro UninstallFile "340.tex"
  !insertmacro UninstallFile "341.tex"
  !insertmacro UninstallFile "350.tex"
  !insertmacro UninstallFile "351.tex"
  !insertmacro UninstallFile "370.tex"
  !insertmacro UninstallFile "371.tex"
  !insertmacro UninstallFile "390.tex"
  !insertmacro UninstallFile "391.tex"
  !insertmacro UninstallFile "600.tex"
  !insertmacro UninstallFile "601.tex"
  !insertmacro UninstallFile "602.tex"
  !insertmacro UninstallFile "650.tex"
  !insertmacro UninstallFile "659.tex"
  !insertmacro UninstallFile "663.tex"
  !insertmacro UninstallFile "664.tex"
  !insertmacro UninstallFile "673.tex"
  !insertmacro UninstallFile "749.tex"
  !insertmacro UninstallFile "754.tex"
  !insertmacro UninstallFile "755.tex"
  !insertmacro UninstallFile "756.tex"
  !insertmacro UninstallFile "763.tex"
  !insertmacro UninstallFile "889.tex"
  !insertmacro UninstallFile "950.tex"

  ; Remove backup directory and all remaining files
  RMDir /r "$INSTDIR\hebrew_patch_backup"

  ; Remove marker file
  Delete "$INSTDIR\hebrew_patch_installed.dat"

  ; Remove uninstaller
  Delete "$INSTDIR\Uninstall_KQ5_Hebrew_Patch.exe"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ5_Hebrew_Patch"
  DeleteRegKey HKLM "Software\KQ5_Hebrew_Patch"

SectionEnd
