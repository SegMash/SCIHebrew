; King's Quest VII Hebrew Patch Installer
; NSIS Script

;--------------------------------
; General Attributes

Name "King's Quest VII - תרגום עברי"
OutFile "KQ7_Hebrew_Patch_Setup.exe"
InstallDir ""
RequestExecutionLevel admin

;--------------------------------
; Version Information

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "King's Quest VII Hebrew Patch"
VIAddVersionKey "FileDescription" "Hebrew Translation Patch for King's Quest VII"
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
!define MUI_WELCOMEPAGE_TEXT "אשף זה ידריך אותך בהתקנת התרגום העברי למשחק King's Quest VII.$\r$\n$\r$\nלחץ 'הבא' כדי להמשיך."
!define MUI_COMPONENTSPAGE_TEXT_TOP "ניתן לבחור האם להחיל גם את תיקון התנועה המהירה (Fast Move)."
!define MUI_DIRECTORYPAGE_TEXT_TOP "בחר את תיקיית המשחק שבה מותקן King's Quest VII."
!define MUI_FINISHPAGE_TITLE "ההתקנה הושלמה בהצלחה"
!define MUI_FINISHPAGE_TEXT "התרגום העברי הותקן בהצלחה.$\r$\n$\r$\nלחץ 'סיום' כדי לסגור אשף זה."

;--------------------------------
; Pages

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
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

!macro BackupAndInstallTo FILE DEST SOURCE_ROOT
  CreateDirectory "$INSTDIR\${DEST}"
  IfFileExists "$INSTDIR\${DEST}\${FILE}" 0 +3
    CreateDirectory "$INSTDIR\${DEST}\hebrew_patch_backup"
    CopyFiles /SILENT "$INSTDIR\${DEST}\${FILE}" "$INSTDIR\${DEST}\hebrew_patch_backup\${FILE}"
  SetOutPath "$INSTDIR\${DEST}"
  File "${SOURCE_ROOT}\${FILE}"
!macroend

!macro BackupAndInstallRoot FILE SOURCE_ROOT
  IfFileExists "$INSTDIR\${FILE}" 0 +3
    CreateDirectory "$INSTDIR\hebrew_patch_backup"
    CopyFiles /SILENT "$INSTDIR\${FILE}" "$INSTDIR\hebrew_patch_backup\${FILE}"
  SetOutPath "$INSTDIR"
  File "${SOURCE_ROOT}\${FILE}"
!macroend

!macro UninstallFileFrom FILE DEST
  IfFileExists "$INSTDIR\${DEST}\hebrew_patch_backup\${FILE}" 0 +3
    CopyFiles /SILENT "$INSTDIR\${DEST}\hebrew_patch_backup\${FILE}" "$INSTDIR\${DEST}\${FILE}"
    Goto +2
  Delete "$INSTDIR\${DEST}\${FILE}"
!macroend

!macro UninstallRootFile FILE
  IfFileExists "$INSTDIR\hebrew_patch_backup\${FILE}" 0 +3
    CopyFiles /SILENT "$INSTDIR\hebrew_patch_backup\${FILE}" "$INSTDIR\${FILE}"
    Goto +2
  Delete "$INSTDIR\${FILE}"
!macroend

;--------------------------------
; Directory-leave callback — prevent re-installation in the same folder

Function CheckAlreadyInstalled
  IfFileExists "$INSTDIR\hebrew_patch_installed_kq7.dat" 0 dir_ok
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
; Main Installer Section

Section "King's Quest VII Hebrew Patch" SecMain
  SectionIn RO

  SetOverwrite try

  ; Main KQ7 patch files -> <game folder>\PATCHES
  !insertmacro BackupAndInstallTo "0.fon" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "0.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "0.scr" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "20.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "23.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "24.hep" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "24.scr" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "25.hep" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "25.scr" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "30.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "35.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "100.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "150.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "800.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "920.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "930.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "940.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "960.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "971.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "972.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "980.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "981.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "982.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "983.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "984.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "985.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "993.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "1000.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "1050.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "1100.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "1200.p56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "1250.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "1410.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "1450.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "1460.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "1500.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "1600.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2000.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2050.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2100.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2110.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2200.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2300.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2350.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2450.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2500.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2550.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2550.p56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2551.p56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "2600.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "3050.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "3100.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "3150.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "3200.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "3250.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "3300.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "400.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "401.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "402.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "403.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "404.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "405.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "10007.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4000.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4001.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4050.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4100.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4107.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4110.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4200.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4211.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4250.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4300.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4350.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4400.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4450.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4500.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4550.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4600.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4650.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "4700.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5000.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5050.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5100.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5150.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5200.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5210.p56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5211.p56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5212.p56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5250.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5300.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "5400.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "6000.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "6060.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "6100.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "6150.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "6250.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "6300.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "6350.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "64990.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "64994.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "6550.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "7000.msg" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "9850.v56" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "91.txt" "PATCHES" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "911.txt" "PATCHES" "games_assets\kq7"

  ; RBT files -> <game folder>\AVI
  !insertmacro BackupAndInstallTo "91.RBT" "AVI" "games_assets\kq7"
  !insertmacro BackupAndInstallTo "911.RBT" "AVI" "games_assets\kq7"

  ; Hebrew guide PDF -> <game folder>
  IfFileExists "$INSTDIR\KQ7_Hebrew_Guide.pdf" 0 +3
    CreateDirectory "$INSTDIR\hebrew_patch_backup"
    CopyFiles /SILENT "$INSTDIR\KQ7_Hebrew_Guide.pdf" "$INSTDIR\hebrew_patch_backup\KQ7_Hebrew_Guide.pdf"
  SetOutPath "$INSTDIR"
  File /oname=KQ7_Hebrew_Guide.pdf "games_assets\kq7\*.pdf"

  ; Copy fastMove files into PATCHES\fastMove (for optional later use)
  CreateDirectory "$INSTDIR\PATCHES\fastMove"
  SetOutPath "$INSTDIR\PATCHES\fastMove"
  File "games_assets\kq7\fastMove\64998.HEP"
  File "games_assets\kq7\fastMove\64998.SCR"

  ; Marker + uninstall metadata
  FileOpen $0 "$INSTDIR\hebrew_patch_installed_kq7.dat" w
  FileWrite $0 "KQ7 Hebrew Patch installed"
  FileClose $0

  WriteRegStr HKLM "Software\KQ7_Hebrew_Patch" "Install_Dir" "$INSTDIR"
  WriteUninstaller "$INSTDIR\Uninstall_KQ7_Hebrew_Patch.exe"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ7_Hebrew_Patch" "DisplayName" "King's Quest VII - Hebrew Patch"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ7_Hebrew_Patch" "UninstallString" '"$INSTDIR\Uninstall_KQ7_Hebrew_Patch.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ7_Hebrew_Patch" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ7_Hebrew_Patch" "NoRepair" 1

SectionEnd

Section /o "Fast Move (copy fastMove files into PATCHES)" SecFastMove
  SetOverwrite try
  !insertmacro BackupAndInstallTo "64998.HEP" "PATCHES" "games_assets\kq7\fastMove"
  !insertmacro BackupAndInstallTo "64998.SCR" "PATCHES" "games_assets\kq7\fastMove"
SectionEnd

;--------------------------------
; Uninstaller Section

Section "Uninstall"

  ; Main KQ7 patch files from PATCHES
  !insertmacro UninstallFileFrom "0.fon" "PATCHES"
  !insertmacro UninstallFileFrom "0.msg" "PATCHES"
  !insertmacro UninstallFileFrom "0.scr" "PATCHES"
  !insertmacro UninstallFileFrom "20.msg" "PATCHES"
  !insertmacro UninstallFileFrom "23.msg" "PATCHES"
  !insertmacro UninstallFileFrom "24.hep" "PATCHES"
  !insertmacro UninstallFileFrom "24.scr" "PATCHES"
  !insertmacro UninstallFileFrom "25.hep" "PATCHES"
  !insertmacro UninstallFileFrom "25.scr" "PATCHES"
  !insertmacro UninstallFileFrom "30.msg" "PATCHES"
  !insertmacro UninstallFileFrom "35.msg" "PATCHES"
  !insertmacro UninstallFileFrom "100.msg" "PATCHES"
  !insertmacro UninstallFileFrom "150.msg" "PATCHES"
  !insertmacro UninstallFileFrom "800.msg" "PATCHES"
  !insertmacro UninstallFileFrom "920.v56" "PATCHES"
  !insertmacro UninstallFileFrom "930.v56" "PATCHES"
  !insertmacro UninstallFileFrom "940.v56" "PATCHES"
  !insertmacro UninstallFileFrom "960.msg" "PATCHES"
  !insertmacro UninstallFileFrom "971.v56" "PATCHES"
  !insertmacro UninstallFileFrom "972.v56" "PATCHES"
  !insertmacro UninstallFileFrom "980.v56" "PATCHES"
  !insertmacro UninstallFileFrom "981.v56" "PATCHES"
  !insertmacro UninstallFileFrom "982.v56" "PATCHES"
  !insertmacro UninstallFileFrom "983.v56" "PATCHES"
  !insertmacro UninstallFileFrom "984.v56" "PATCHES"
  !insertmacro UninstallFileFrom "985.v56" "PATCHES"
  !insertmacro UninstallFileFrom "993.v56" "PATCHES"
  !insertmacro UninstallFileFrom "1000.msg" "PATCHES"
  !insertmacro UninstallFileFrom "1050.msg" "PATCHES"
  !insertmacro UninstallFileFrom "1100.msg" "PATCHES"
  !insertmacro UninstallFileFrom "1200.p56" "PATCHES"
  !insertmacro UninstallFileFrom "1250.msg" "PATCHES"
  !insertmacro UninstallFileFrom "1410.msg" "PATCHES"
  !insertmacro UninstallFileFrom "1450.msg" "PATCHES"
  !insertmacro UninstallFileFrom "1460.msg" "PATCHES"
  !insertmacro UninstallFileFrom "1500.msg" "PATCHES"
  !insertmacro UninstallFileFrom "1600.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2000.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2050.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2100.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2110.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2200.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2300.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2350.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2450.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2500.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2550.msg" "PATCHES"
  !insertmacro UninstallFileFrom "2550.p56" "PATCHES"
  !insertmacro UninstallFileFrom "2551.p56" "PATCHES"
  !insertmacro UninstallFileFrom "2600.msg" "PATCHES"
  !insertmacro UninstallFileFrom "3050.msg" "PATCHES"
  !insertmacro UninstallFileFrom "3100.msg" "PATCHES"
  !insertmacro UninstallFileFrom "3150.msg" "PATCHES"
  !insertmacro UninstallFileFrom "3200.msg" "PATCHES"
  !insertmacro UninstallFileFrom "3250.msg" "PATCHES"
  !insertmacro UninstallFileFrom "3300.msg" "PATCHES"
  !insertmacro UninstallFileFrom "400.v56" "PATCHES"
  !insertmacro UninstallFileFrom "401.v56" "PATCHES"
  !insertmacro UninstallFileFrom "402.v56" "PATCHES"
  !insertmacro UninstallFileFrom "403.v56" "PATCHES"
  !insertmacro UninstallFileFrom "404.v56" "PATCHES"
  !insertmacro UninstallFileFrom "405.v56" "PATCHES"
  !insertmacro UninstallFileFrom "10007.v56" "PATCHES"
  !insertmacro UninstallFileFrom "4000.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4001.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4050.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4100.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4107.v56" "PATCHES"
  !insertmacro UninstallFileFrom "4110.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4200.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4211.v56" "PATCHES"
  !insertmacro UninstallFileFrom "4250.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4300.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4350.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4400.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4450.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4500.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4550.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4600.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4650.msg" "PATCHES"
  !insertmacro UninstallFileFrom "4700.msg" "PATCHES"
  !insertmacro UninstallFileFrom "5000.msg" "PATCHES"
  !insertmacro UninstallFileFrom "5050.msg" "PATCHES"
  !insertmacro UninstallFileFrom "5100.msg" "PATCHES"
  !insertmacro UninstallFileFrom "5150.msg" "PATCHES"
  !insertmacro UninstallFileFrom "5200.msg" "PATCHES"
  !insertmacro UninstallFileFrom "5210.p56" "PATCHES"
  !insertmacro UninstallFileFrom "5211.p56" "PATCHES"
  !insertmacro UninstallFileFrom "5212.p56" "PATCHES"
  !insertmacro UninstallFileFrom "5250.msg" "PATCHES"
  !insertmacro UninstallFileFrom "5300.msg" "PATCHES"
  !insertmacro UninstallFileFrom "5400.msg" "PATCHES"
  !insertmacro UninstallFileFrom "6000.msg" "PATCHES"
  !insertmacro UninstallFileFrom "6060.msg" "PATCHES"
  !insertmacro UninstallFileFrom "6100.msg" "PATCHES"
  !insertmacro UninstallFileFrom "6150.msg" "PATCHES"
  !insertmacro UninstallFileFrom "6250.msg" "PATCHES"
  !insertmacro UninstallFileFrom "6300.msg" "PATCHES"
  !insertmacro UninstallFileFrom "6350.msg" "PATCHES"
  !insertmacro UninstallFileFrom "64990.msg" "PATCHES"
  !insertmacro UninstallFileFrom "64994.msg" "PATCHES"
  !insertmacro UninstallFileFrom "6550.msg" "PATCHES"
  !insertmacro UninstallFileFrom "7000.msg" "PATCHES"
  !insertmacro UninstallFileFrom "9850.v56" "PATCHES"
  !insertmacro UninstallFileFrom "91.txt" "PATCHES"
  !insertmacro UninstallFileFrom "911.txt" "PATCHES"

  ; Optional fast move files from PATCHES
  !insertmacro UninstallFileFrom "64998.HEP" "PATCHES"
  !insertmacro UninstallFileFrom "64998.SCR" "PATCHES"

  ; RBT files from AVI
  !insertmacro UninstallFileFrom "91.RBT" "AVI"
  !insertmacro UninstallFileFrom "911.RBT" "AVI"

  ; PDF from game root
  !insertmacro UninstallRootFile "KQ7_Hebrew_Guide.pdf"

  ; Remove copied fastMove helper folder and backups
  Delete "$INSTDIR\PATCHES\fastMove\64998.HEP"
  Delete "$INSTDIR\PATCHES\fastMove\64998.SCR"
  RMDir "$INSTDIR\PATCHES\fastMove"
  RMDir /r "$INSTDIR\PATCHES\hebrew_patch_backup"
  RMDir /r "$INSTDIR\AVI\hebrew_patch_backup"
  RMDir /r "$INSTDIR\hebrew_patch_backup"

  Delete "$INSTDIR\hebrew_patch_installed_kq7.dat"
  Delete "$INSTDIR\Uninstall_KQ7_Hebrew_Patch.exe"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ7_Hebrew_Patch"
  DeleteRegKey HKLM "Software\KQ7_Hebrew_Patch"

SectionEnd
