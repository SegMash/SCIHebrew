; King's Quest VI Hebrew Patch Installer
; NSIS Script

;--------------------------------
; General Attributes

Name "King's Quest VI - תרגום עברי"
OutFile "KQ6_Hebrew_Patch_Setup.exe"
InstallDir ""
RequestExecutionLevel admin

;--------------------------------
; Version Information

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "King's Quest VI Hebrew Patch"
VIAddVersionKey "FileDescription" "Hebrew Translation Patch for King's Quest VI"
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
!define MUI_WELCOMEPAGE_TEXT "אשף זה ידריך אותך בהתקנת התרגום העברי למשחק King's Quest VI.$\r$\n$\r$\nלחץ 'הבא' כדי להמשיך."
!define MUI_DIRECTORYPAGE_TEXT_TOP "בחר את תיקיית המשחק שבה מותקן King's Quest VI."
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
  File "kq6_work\${FILE}"
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

Section "King's Quest VI Hebrew Patch" SecMain

  SetOutPath "$INSTDIR"
  SetOverwrite try

  ; Font files
  !insertmacro BackupAndInstall "0.fon"
  !insertmacro BackupAndInstall "1.fon"
  !insertmacro BackupAndInstall "4.fon"
  !insertmacro BackupAndInstall "1111.fon"
  !insertmacro BackupAndInstall "2207.fon"
  !insertmacro BackupAndInstall "3110.fon"

  ; msg files
  !insertmacro BackupAndInstall "0.msg"
  !insertmacro BackupAndInstall "21.msg"
  !insertmacro BackupAndInstall "94.msg"
  !insertmacro BackupAndInstall "95.msg"
  !insertmacro BackupAndInstall "99.msg"
  !insertmacro BackupAndInstall "100.msg"
  !insertmacro BackupAndInstall "105.msg"
  !insertmacro BackupAndInstall "130.msg"
  !insertmacro BackupAndInstall "135.msg"
  !insertmacro BackupAndInstall "140.msg"
  !insertmacro BackupAndInstall "145.msg"
  !insertmacro BackupAndInstall "150.msg"
  !insertmacro BackupAndInstall "155.msg"
  !insertmacro BackupAndInstall "160.msg"
  !insertmacro BackupAndInstall "165.msg"
  !insertmacro BackupAndInstall "180.msg"
  !insertmacro BackupAndInstall "190.msg"
  !insertmacro BackupAndInstall "194.msg"
  !insertmacro BackupAndInstall "200.msg"
  !insertmacro BackupAndInstall "205.msg"
  !insertmacro BackupAndInstall "210.msg"
  !insertmacro BackupAndInstall "220.msg"
  !insertmacro BackupAndInstall "230.msg"
  !insertmacro BackupAndInstall "240.msg"
  !insertmacro BackupAndInstall "250.msg"
  !insertmacro BackupAndInstall "260.msg"
  !insertmacro BackupAndInstall "270.msg"
  !insertmacro BackupAndInstall "280.msg"
  !insertmacro BackupAndInstall "290.msg"
  !insertmacro BackupAndInstall "300.msg"
  !insertmacro BackupAndInstall "320.msg"
  !insertmacro BackupAndInstall "340.msg"
  !insertmacro BackupAndInstall "350.msg"
  !insertmacro BackupAndInstall "370.msg"
  !insertmacro BackupAndInstall "380.msg"
  !insertmacro BackupAndInstall "390.msg"
  !insertmacro BackupAndInstall "400.msg"
  !insertmacro BackupAndInstall "410.msg"
  !insertmacro BackupAndInstall "420.msg"
  !insertmacro BackupAndInstall "440.msg"
  !insertmacro BackupAndInstall "450.msg"
  !insertmacro BackupAndInstall "451.msg"
  !insertmacro BackupAndInstall "460.msg"
  !insertmacro BackupAndInstall "470.msg"
  !insertmacro BackupAndInstall "480.msg"
  !insertmacro BackupAndInstall "490.msg"
  !insertmacro BackupAndInstall "500.msg"
  !insertmacro BackupAndInstall "510.msg"
  !insertmacro BackupAndInstall "520.msg"
  !insertmacro BackupAndInstall "540.msg"
  !insertmacro BackupAndInstall "550.msg"
  !insertmacro BackupAndInstall "560.msg"
  !insertmacro BackupAndInstall "580.msg"
  !insertmacro BackupAndInstall "600.msg"
  !insertmacro BackupAndInstall "630.msg"
  !insertmacro BackupAndInstall "640.msg"
  !insertmacro BackupAndInstall "650.msg"
  !insertmacro BackupAndInstall "660.msg"
  !insertmacro BackupAndInstall "670.msg"
  !insertmacro BackupAndInstall "671.msg"
  !insertmacro BackupAndInstall "680.msg"
  !insertmacro BackupAndInstall "690.msg"
  !insertmacro BackupAndInstall "710.msg"
  !insertmacro BackupAndInstall "720.msg"
  !insertmacro BackupAndInstall "730.msg"
  !insertmacro BackupAndInstall "740.msg"
  !insertmacro BackupAndInstall "743.msg"
  !insertmacro BackupAndInstall "750.msg"
  !insertmacro BackupAndInstall "770.msg"
  !insertmacro BackupAndInstall "780.msg"
  !insertmacro BackupAndInstall "781.msg"
  !insertmacro BackupAndInstall "790.msg"
  !insertmacro BackupAndInstall "800.msg"
  !insertmacro BackupAndInstall "810.msg"
  !insertmacro BackupAndInstall "820.msg"
  !insertmacro BackupAndInstall "840.msg"
  !insertmacro BackupAndInstall "850.msg"
  !insertmacro BackupAndInstall "860.msg"
  !insertmacro BackupAndInstall "870.msg"
  !insertmacro BackupAndInstall "880.msg"
  !insertmacro BackupAndInstall "899.msg"
  !insertmacro BackupAndInstall "907.msg"
  !insertmacro BackupAndInstall "908.msg"
  !insertmacro BackupAndInstall "916.msg"
  !insertmacro BackupAndInstall "990.msg"
  !insertmacro BackupAndInstall "994.msg"

  ; v56 files
  !insertmacro BackupAndInstall "100.v56"
  !insertmacro BackupAndInstall "132.v56"
  !insertmacro BackupAndInstall "190.v56"
  !insertmacro BackupAndInstall "462.v56"
  !insertmacro BackupAndInstall "678.v56"
  !insertmacro BackupAndInstall "713.v56"
  !insertmacro BackupAndInstall "901.v56"
  !insertmacro BackupAndInstall "947.v56"

  ; p56 files
  !insertmacro BackupAndInstall "100.p56"
  !insertmacro BackupAndInstall "130.p56"  
  !insertmacro BackupAndInstall "240.p56"

  ; hep files
  !insertmacro BackupAndInstall "190.hep"
  !insertmacro BackupAndInstall "640.hep"
  !insertmacro BackupAndInstall "690.hep"
  !insertmacro BackupAndInstall "802.hep"
  !insertmacro BackupAndInstall "820.hep"

  ; scr files
  !insertmacro BackupAndInstall "916.scr"
  !insertmacro BackupAndInstall "917.scr"

  ; AVI files
  !insertmacro BackupAndInstall "TOON.AVI"
  FileOpen $0 "$INSTDIR\hebrew_patch_installed.dat" w
  FileWrite $0 "KQ6 Hebrew Patch installed"
  FileClose $0

  ; Store installation folder
  WriteRegStr HKLM "Software\KQ6_Hebrew_Patch" "Install_Dir" "$INSTDIR"

  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall_KQ6_Hebrew_Patch.exe"

  ; Write uninstall registry keys
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ6_Hebrew_Patch" "DisplayName" "King's Quest VI - Hebrew Patch"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ6_Hebrew_Patch" "UninstallString" '"$INSTDIR\Uninstall_KQ6_Hebrew_Patch.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ6_Hebrew_Patch" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ6_Hebrew_Patch" "NoRepair" 1

SectionEnd

;--------------------------------
; Uninstaller Section

Section "Uninstall"

  ; Font files
  !insertmacro UninstallFile "0.fon"
  !insertmacro UninstallFile "1.fon"
  !insertmacro UninstallFile "4.fon"
  !insertmacro UninstallFile "1111.fon"
  !insertmacro UninstallFile "2207.fon"
  !insertmacro UninstallFile "3110.fon"

  ; msg files
  !insertmacro UninstallFile "0.msg"
  !insertmacro UninstallFile "21.msg"
  !insertmacro UninstallFile "94.msg"
  !insertmacro UninstallFile "95.msg"
  !insertmacro UninstallFile "99.msg"
  !insertmacro UninstallFile "100.msg"
  !insertmacro UninstallFile "105.msg"
  !insertmacro UninstallFile "130.msg"
  !insertmacro UninstallFile "135.msg"
  !insertmacro UninstallFile "140.msg"
  !insertmacro UninstallFile "145.msg"
  !insertmacro UninstallFile "150.msg"
  !insertmacro UninstallFile "155.msg"
  !insertmacro UninstallFile "160.msg"
  !insertmacro UninstallFile "165.msg"
  !insertmacro UninstallFile "180.msg"
  !insertmacro UninstallFile "190.msg"
  !insertmacro UninstallFile "194.msg"
  !insertmacro UninstallFile "200.msg"
  !insertmacro UninstallFile "205.msg"
  !insertmacro UninstallFile "210.msg"
  !insertmacro UninstallFile "220.msg"
  !insertmacro UninstallFile "230.msg"
  !insertmacro UninstallFile "240.msg"
  !insertmacro UninstallFile "250.msg"
  !insertmacro UninstallFile "260.msg"
  !insertmacro UninstallFile "270.msg"
  !insertmacro UninstallFile "280.msg"
  !insertmacro UninstallFile "290.msg"
  !insertmacro UninstallFile "300.msg"
  !insertmacro UninstallFile "320.msg"
  !insertmacro UninstallFile "340.msg"
  !insertmacro UninstallFile "350.msg"
  !insertmacro UninstallFile "370.msg"
  !insertmacro UninstallFile "380.msg"
  !insertmacro UninstallFile "390.msg"
  !insertmacro UninstallFile "400.msg"
  !insertmacro UninstallFile "410.msg"
  !insertmacro UninstallFile "420.msg"
  !insertmacro UninstallFile "440.msg"
  !insertmacro UninstallFile "450.msg"
  !insertmacro UninstallFile "451.msg"
  !insertmacro UninstallFile "460.msg"
  !insertmacro UninstallFile "470.msg"
  !insertmacro UninstallFile "480.msg"
  !insertmacro UninstallFile "490.msg"
  !insertmacro UninstallFile "500.msg"
  !insertmacro UninstallFile "510.msg"
  !insertmacro UninstallFile "520.msg"
  !insertmacro UninstallFile "540.msg"
  !insertmacro UninstallFile "550.msg"
  !insertmacro UninstallFile "560.msg"
  !insertmacro UninstallFile "580.msg"
  !insertmacro UninstallFile "600.msg"
  !insertmacro UninstallFile "630.msg"
  !insertmacro UninstallFile "640.msg"
  !insertmacro UninstallFile "650.msg"
  !insertmacro UninstallFile "660.msg"
  !insertmacro UninstallFile "670.msg"
  !insertmacro UninstallFile "671.msg"
  !insertmacro UninstallFile "680.msg"
  !insertmacro UninstallFile "690.msg"
  !insertmacro UninstallFile "710.msg"
  !insertmacro UninstallFile "720.msg"
  !insertmacro UninstallFile "730.msg"
  !insertmacro UninstallFile "740.msg"
  !insertmacro UninstallFile "743.msg"
  !insertmacro UninstallFile "750.msg"
  !insertmacro UninstallFile "770.msg"
  !insertmacro UninstallFile "780.msg"
  !insertmacro UninstallFile "781.msg"
  !insertmacro UninstallFile "790.msg"
  !insertmacro UninstallFile "800.msg"
  !insertmacro UninstallFile "810.msg"
  !insertmacro UninstallFile "820.msg"
  !insertmacro UninstallFile "840.msg"
  !insertmacro UninstallFile "850.msg"
  !insertmacro UninstallFile "860.msg"
  !insertmacro UninstallFile "870.msg"
  !insertmacro UninstallFile "880.msg"
  !insertmacro UninstallFile "899.msg"
  !insertmacro UninstallFile "907.msg"
  !insertmacro UninstallFile "908.msg"
  !insertmacro UninstallFile "916.msg"
  !insertmacro UninstallFile "990.msg"
  !insertmacro UninstallFile "994.msg"

  ; v56 files
  !insertmacro UninstallFile "100.v56"
  !insertmacro UninstallFile "132.v56"
  !insertmacro UninstallFile "190.v56"
  !insertmacro UninstallFile "462.v56"
  !insertmacro UninstallFile "678.v56"
  !insertmacro UninstallFile "713.v56"
  !insertmacro UninstallFile "901.v56"
  !insertmacro UninstallFile "947.v56"

  ; p56 files
  !insertmacro UninstallFile "100.p56"
  !insertmacro UninstallFile "130.p56"
  !insertmacro UninstallFile "240.p56"

  ; hep files
  !insertmacro UninstallFile "190.hep"
  !insertmacro UninstallFile "640.hep"
  !insertmacro UninstallFile "690.hep"
  !insertmacro UninstallFile "802.hep"
  !insertmacro UninstallFile "820.hep"

  ; scr files
  !insertmacro UninstallFile "916.scr"
  !insertmacro UninstallFile "917.scr"

  ; AVI files
  !insertmacro UninstallFile "TOON.AVI"
  RMDir /r "$INSTDIR\hebrew_patch_backup"

  ; Remove marker file
  Delete "$INSTDIR\hebrew_patch_installed.dat"

  ; Remove uninstaller
  Delete "$INSTDIR\Uninstall_KQ6_Hebrew_Patch.exe"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ6_Hebrew_Patch"
  DeleteRegKey HKLM "Software\KQ6_Hebrew_Patch"

SectionEnd
