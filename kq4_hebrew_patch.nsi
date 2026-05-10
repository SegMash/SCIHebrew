; King's Quest IV Hebrew Patch Installer
; NSIS Script

;--------------------------------
; General Attributes

Name "King's Quest IV - תרגום עברי"
OutFile "KQ4_Hebrew_Patch_Setup.exe"
InstallDir ""
RequestExecutionLevel admin

;--------------------------------
; Version Information

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "King's Quest IV Hebrew Patch"
VIAddVersionKey "FileDescription" "Hebrew Translation Patch for King's Quest IV"
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
!define MUI_WELCOMEPAGE_TEXT "אשף זה ידריך אותך בהתקנת התרגום העברי למשחק King's Quest IV.$\r$\n$\r$\nלחץ 'הבא' כדי להמשיך."
!define MUI_DIRECTORYPAGE_TEXT_TOP "בחר את תיקיית המשחק שבה מותקן King's Quest IV."
!define MUI_FINISHPAGE_TITLE "ההתקנה הושלמה בהצלחה"
!define MUI_FINISHPAGE_TEXT "התרגום העברי הותקן בהצלחה.$\r$\n$\r$\nלחץ 'סיום' כדי לסגור אשף זה."

;--------------------------------
; Pages

!insertmacro MUI_PAGE_WELCOME
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
; Validation Function

Function .onVerifyInstDir
  ; Check if resource.map exists
  IfFileExists "$INSTDIR\resource.map" 0 invalid_dir
  
  ; Get file size of resource.map
  ClearErrors
  FileOpen $0 "$INSTDIR\resource.map" r
  FileSeek $0 0 END $1
  FileClose $0
  
  ; Check if file size is exactly 7,476 bytes
  IntCmp $1 7476 valid_dir invalid_dir invalid_dir
  
  valid_dir:
    ; Directory is valid
    Return
  
  invalid_dir:
    ; Directory is invalid - abort
    Abort
FunctionEnd

;--------------------------------
; Installer Sections

Section "King's Quest IV Hebrew Patch" SecMain

  SetOutPath "$INSTDIR"
  
  ; Set overwrite on to replace existing files
  SetOverwrite try
  
  ; Copy all files from games_assets/kq4/bin directory
  File "games_assets\kq4\bin\font.000"
  File "games_assets\kq4\bin\font.001"
  File "games_assets\kq4\bin\font.004"
  File "games_assets\kq4\bin\font.999"
  File "games_assets\kq4\bin\kq_ref_Card.pdf"
  File "games_assets\kq4\bin\pic.096"
  File "games_assets\kq4\bin\vocab.000"
  
  ; Copy all script files
  File "games_assets\kq4\bin\script.000"
  File "games_assets\kq4\bin\script.015"
  File "games_assets\kq4\bin\script.027"
  File "games_assets\kq4\bin\script.036"
  File "games_assets\kq4\bin\script.042"
  File "games_assets\kq4\bin\script.043"
  File "games_assets\kq4\bin\script.045"
  File "games_assets\kq4\bin\script.048"
  File "games_assets\kq4\bin\script.051"
  File "games_assets\kq4\bin\script.053"
  File "games_assets\kq4\bin\script.057"
  File "games_assets\kq4\bin\script.066"
  File "games_assets\kq4\bin\script.068"
  File "games_assets\kq4\bin\script.069"
  File "games_assets\kq4\bin\script.070"
  File "games_assets\kq4\bin\script.071"
  File "games_assets\kq4\bin\script.077"
  File "games_assets\kq4\bin\script.078"
  File "games_assets\kq4\bin\script.081"
  File "games_assets\kq4\bin\script.082"
  File "games_assets\kq4\bin\script.084"
  File "games_assets\kq4\bin\script.086"
  File "games_assets\kq4\bin\script.089"
  File "games_assets\kq4\bin\script.120"
  File "games_assets\kq4\bin\script.221"
  File "games_assets\kq4\bin\script.222"
  File "games_assets\kq4\bin\script.255"
  File "games_assets\kq4\bin\script.507"
  File "games_assets\kq4\bin\script.517"
  File "games_assets\kq4\bin\script.518"
  File "games_assets\kq4\bin\script.519"
  File "games_assets\kq4\bin\script.690"
  File "games_assets\kq4\bin\script.694"
  File "games_assets\kq4\bin\script.699"
  File "games_assets\kq4\bin\script.701"
  File "games_assets\kq4\bin\script.985"
  File "games_assets\kq4\bin\script.987"
  File "games_assets\kq4\bin\script.988"
  File "games_assets\kq4\bin\script.989"
  File "games_assets\kq4\bin\script.990"
  File "games_assets\kq4\bin\script.991"
  File "games_assets\kq4\bin\script.992"
  File "games_assets\kq4\bin\script.994"
  File "games_assets\kq4\bin\script.995"
  File "games_assets\kq4\bin\script.996"
  File "games_assets\kq4\bin\script.997"
  File "games_assets\kq4\bin\script.998"
  File "games_assets\kq4\bin\script.999"
  
  ; Copy all text files
  File "games_assets\kq4\bin\text.000"
  File "games_assets\kq4\bin\text.001"
  File "games_assets\kq4\bin\text.002"
  File "games_assets\kq4\bin\text.003"
  File "games_assets\kq4\bin\text.004"
  File "games_assets\kq4\bin\text.005"
  File "games_assets\kq4\bin\text.006"
  File "games_assets\kq4\bin\text.007"
  File "games_assets\kq4\bin\text.008"
  File "games_assets\kq4\bin\text.009"
  File "games_assets\kq4\bin\text.010"
  File "games_assets\kq4\bin\text.011"
  File "games_assets\kq4\bin\text.012"
  File "games_assets\kq4\bin\text.013"
  File "games_assets\kq4\bin\text.014"
  File "games_assets\kq4\bin\text.015"
  File "games_assets\kq4\bin\text.016"
  File "games_assets\kq4\bin\text.017"
  File "games_assets\kq4\bin\text.018"
  File "games_assets\kq4\bin\text.019"
  File "games_assets\kq4\bin\text.020"
  File "games_assets\kq4\bin\text.021"
  File "games_assets\kq4\bin\text.022"
  File "games_assets\kq4\bin\text.023"
  File "games_assets\kq4\bin\text.024"
  File "games_assets\kq4\bin\text.025"
  File "games_assets\kq4\bin\text.026"
  File "games_assets\kq4\bin\text.027"
  File "games_assets\kq4\bin\text.028"
  File "games_assets\kq4\bin\text.029"
  File "games_assets\kq4\bin\text.030"
  File "games_assets\kq4\bin\text.031"
  File "games_assets\kq4\bin\text.032"
  File "games_assets\kq4\bin\text.033"
  File "games_assets\kq4\bin\text.034"
  File "games_assets\kq4\bin\text.035"
  File "games_assets\kq4\bin\text.036"
  File "games_assets\kq4\bin\text.037"
  File "games_assets\kq4\bin\text.038"
  File "games_assets\kq4\bin\text.039"
  File "games_assets\kq4\bin\text.040"
  File "games_assets\kq4\bin\text.041"
  File "games_assets\kq4\bin\text.042"
  File "games_assets\kq4\bin\text.043"
  File "games_assets\kq4\bin\text.044"
  File "games_assets\kq4\bin\text.045"
  File "games_assets\kq4\bin\text.046"
  File "games_assets\kq4\bin\text.047"
  File "games_assets\kq4\bin\text.048"
  File "games_assets\kq4\bin\text.049"
  File "games_assets\kq4\bin\text.050"
  File "games_assets\kq4\bin\text.051"
  File "games_assets\kq4\bin\text.053"
  File "games_assets\kq4\bin\text.054"
  File "games_assets\kq4\bin\text.055"
  File "games_assets\kq4\bin\text.056"
  File "games_assets\kq4\bin\text.057"
  File "games_assets\kq4\bin\text.058"
  File "games_assets\kq4\bin\text.059"
  File "games_assets\kq4\bin\text.060"
  File "games_assets\kq4\bin\text.061"
  File "games_assets\kq4\bin\text.062"
  File "games_assets\kq4\bin\text.063"
  File "games_assets\kq4\bin\text.064"
  File "games_assets\kq4\bin\text.065"
  File "games_assets\kq4\bin\text.066"
  File "games_assets\kq4\bin\text.067"
  File "games_assets\kq4\bin\text.068"
  File "games_assets\kq4\bin\text.069"
  File "games_assets\kq4\bin\text.070"
  File "games_assets\kq4\bin\text.071"
  File "games_assets\kq4\bin\text.073"
  File "games_assets\kq4\bin\text.076"
  File "games_assets\kq4\bin\text.077"
  File "games_assets\kq4\bin\text.078"
  File "games_assets\kq4\bin\text.079"
  File "games_assets\kq4\bin\text.080"
  File "games_assets\kq4\bin\text.081"
  File "games_assets\kq4\bin\text.082"
  File "games_assets\kq4\bin\text.083"
  File "games_assets\kq4\bin\text.084"
  File "games_assets\kq4\bin\text.085"
  File "games_assets\kq4\bin\text.086"
  File "games_assets\kq4\bin\text.087"
  File "games_assets\kq4\bin\text.088"
  File "games_assets\kq4\bin\text.089"
  File "games_assets\kq4\bin\text.090"
  File "games_assets\kq4\bin\text.091"
  File "games_assets\kq4\bin\text.092"
  File "games_assets\kq4\bin\text.093"
  File "games_assets\kq4\bin\text.094"
  File "games_assets\kq4\bin\text.095"
  File "games_assets\kq4\bin\text.120"
  File "games_assets\kq4\bin\text.221"
  File "games_assets\kq4\bin\text.222"
  File "games_assets\kq4\bin\text.255"
  File "games_assets\kq4\bin\text.301"
  File "games_assets\kq4\bin\text.302"
  File "games_assets\kq4\bin\text.305"
  File "games_assets\kq4\bin\text.306"
  File "games_assets\kq4\bin\text.307"
  File "games_assets\kq4\bin\text.333"
  File "games_assets\kq4\bin\text.503"
  File "games_assets\kq4\bin\text.504"
  File "games_assets\kq4\bin\text.505"
  File "games_assets\kq4\bin\text.506"
  File "games_assets\kq4\bin\text.507"
  File "games_assets\kq4\bin\text.508"
  File "games_assets\kq4\bin\text.509"
  File "games_assets\kq4\bin\text.510"
  File "games_assets\kq4\bin\text.511"
  File "games_assets\kq4\bin\text.512"
  File "games_assets\kq4\bin\text.513"
  File "games_assets\kq4\bin\text.514"
  File "games_assets\kq4\bin\text.516"
  File "games_assets\kq4\bin\text.517"
  File "games_assets\kq4\bin\text.518"
  File "games_assets\kq4\bin\text.519"
  File "games_assets\kq4\bin\text.600"
  File "games_assets\kq4\bin\text.602"
  File "games_assets\kq4\bin\text.603"
  File "games_assets\kq4\bin\text.604"
  File "games_assets\kq4\bin\text.605"
  File "games_assets\kq4\bin\text.654"
  File "games_assets\kq4\bin\text.690"
  File "games_assets\kq4\bin\text.692"
  File "games_assets\kq4\bin\text.694"
  File "games_assets\kq4\bin\text.697"
  File "games_assets\kq4\bin\text.699"
  File "games_assets\kq4\bin\text.700"
  File "games_assets\kq4\bin\text.701"
  File "games_assets\kq4\bin\text.800"
  File "games_assets\kq4\bin\text.801"
  File "games_assets\kq4\bin\text.989"
  File "games_assets\kq4\bin\text.990"
  File "games_assets\kq4\bin\text.991"
  File "games_assets\kq4\bin\text.992"
  File "games_assets\kq4\bin\text.993"
  File "games_assets\kq4\bin\text.994"
  File "games_assets\kq4\bin\text.995"
  File "games_assets\kq4\bin\text.996"
  File "games_assets\kq4\bin\text.997"
  File "games_assets\kq4\bin\text.998"
  File "games_assets\kq4\bin\text.999"
  
  ; Store installation folder
  WriteRegStr HKLM "Software\KQ4_Hebrew_Patch" "Install_Dir" "$INSTDIR"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall_Hebrew_Patch.exe"
  
  ; Write uninstall registry keys
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ4_Hebrew_Patch" "DisplayName" "King's Quest IV - Hebrew Patch"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ4_Hebrew_Patch" "UninstallString" '"$INSTDIR\Uninstall_Hebrew_Patch.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ4_Hebrew_Patch" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ4_Hebrew_Patch" "NoRepair" 1

SectionEnd

;--------------------------------
; Uninstaller Section

Section "Uninstall"

  ; Remove files
  Delete "$INSTDIR\font.000"
  Delete "$INSTDIR\font.001"
  Delete "$INSTDIR\font.004"
  Delete "$INSTDIR\font.999"
  Delete "$INSTDIR\kq_ref_Card.pdf"
  Delete "$INSTDIR\pic.096"
  Delete "$INSTDIR\vocab.000"
  
  ; Remove script files
  Delete "$INSTDIR\script.000"
  Delete "$INSTDIR\script.015"
  Delete "$INSTDIR\script.027"
  Delete "$INSTDIR\script.036"
  Delete "$INSTDIR\script.042"
  Delete "$INSTDIR\script.043"
  Delete "$INSTDIR\script.045"
  Delete "$INSTDIR\script.048"
  Delete "$INSTDIR\script.051"
  Delete "$INSTDIR\script.053"
  Delete "$INSTDIR\script.057"
  Delete "$INSTDIR\script.066"
  Delete "$INSTDIR\script.068"
  Delete "$INSTDIR\script.069"
  Delete "$INSTDIR\script.070"
  Delete "$INSTDIR\script.071"
  Delete "$INSTDIR\script.077"
  Delete "$INSTDIR\script.078"
  Delete "$INSTDIR\script.081"
  Delete "$INSTDIR\script.082"
  Delete "$INSTDIR\script.084"
  Delete "$INSTDIR\script.086"
  Delete "$INSTDIR\script.089"
  Delete "$INSTDIR\script.120"
  Delete "$INSTDIR\script.221"
  Delete "$INSTDIR\script.222"
  Delete "$INSTDIR\script.255"
  Delete "$INSTDIR\script.507"
  Delete "$INSTDIR\script.517"
  Delete "$INSTDIR\script.518"
  Delete "$INSTDIR\script.519"
  Delete "$INSTDIR\script.690"
  Delete "$INSTDIR\script.694"
  Delete "$INSTDIR\script.699"
  Delete "$INSTDIR\script.701"
  Delete "$INSTDIR\script.985"
  Delete "$INSTDIR\script.987"
  Delete "$INSTDIR\script.988"
  Delete "$INSTDIR\script.989"
  Delete "$INSTDIR\script.990"
  Delete "$INSTDIR\script.991"
  Delete "$INSTDIR\script.992"
  Delete "$INSTDIR\script.994"
  Delete "$INSTDIR\script.995"
  Delete "$INSTDIR\script.996"
  Delete "$INSTDIR\script.997"
  Delete "$INSTDIR\script.998"
  Delete "$INSTDIR\script.999"
  
  ; Remove text files
  Delete "$INSTDIR\text.000"
  Delete "$INSTDIR\text.001"
  Delete "$INSTDIR\text.002"
  Delete "$INSTDIR\text.003"
  Delete "$INSTDIR\text.004"
  Delete "$INSTDIR\text.005"
  Delete "$INSTDIR\text.006"
  Delete "$INSTDIR\text.007"
  Delete "$INSTDIR\text.008"
  Delete "$INSTDIR\text.009"
  Delete "$INSTDIR\text.010"
  Delete "$INSTDIR\text.011"
  Delete "$INSTDIR\text.012"
  Delete "$INSTDIR\text.013"
  Delete "$INSTDIR\text.014"
  Delete "$INSTDIR\text.015"
  Delete "$INSTDIR\text.016"
  Delete "$INSTDIR\text.017"
  Delete "$INSTDIR\text.018"
  Delete "$INSTDIR\text.019"
  Delete "$INSTDIR\text.020"
  Delete "$INSTDIR\text.021"
  Delete "$INSTDIR\text.022"
  Delete "$INSTDIR\text.023"
  Delete "$INSTDIR\text.024"
  Delete "$INSTDIR\text.025"
  Delete "$INSTDIR\text.026"
  Delete "$INSTDIR\text.027"
  Delete "$INSTDIR\text.028"
  Delete "$INSTDIR\text.029"
  Delete "$INSTDIR\text.030"
  Delete "$INSTDIR\text.031"
  Delete "$INSTDIR\text.032"
  Delete "$INSTDIR\text.033"
  Delete "$INSTDIR\text.034"
  Delete "$INSTDIR\text.035"
  Delete "$INSTDIR\text.036"
  Delete "$INSTDIR\text.037"
  Delete "$INSTDIR\text.038"
  Delete "$INSTDIR\text.039"
  Delete "$INSTDIR\text.040"
  Delete "$INSTDIR\text.041"
  Delete "$INSTDIR\text.042"
  Delete "$INSTDIR\text.043"
  Delete "$INSTDIR\text.044"
  Delete "$INSTDIR\text.045"
  Delete "$INSTDIR\text.046"
  Delete "$INSTDIR\text.047"
  Delete "$INSTDIR\text.048"
  Delete "$INSTDIR\text.049"
  Delete "$INSTDIR\text.050"
  Delete "$INSTDIR\text.051"
  Delete "$INSTDIR\text.053"
  Delete "$INSTDIR\text.054"
  Delete "$INSTDIR\text.055"
  Delete "$INSTDIR\text.056"
  Delete "$INSTDIR\text.057"
  Delete "$INSTDIR\text.058"
  Delete "$INSTDIR\text.059"
  Delete "$INSTDIR\text.060"
  Delete "$INSTDIR\text.061"
  Delete "$INSTDIR\text.062"
  Delete "$INSTDIR\text.063"
  Delete "$INSTDIR\text.064"
  Delete "$INSTDIR\text.065"
  Delete "$INSTDIR\text.066"
  Delete "$INSTDIR\text.067"
  Delete "$INSTDIR\text.068"
  Delete "$INSTDIR\text.069"
  Delete "$INSTDIR\text.070"
  Delete "$INSTDIR\text.071"
  Delete "$INSTDIR\text.073"
  Delete "$INSTDIR\text.076"
  Delete "$INSTDIR\text.077"
  Delete "$INSTDIR\text.078"
  Delete "$INSTDIR\text.079"
  Delete "$INSTDIR\text.080"
  Delete "$INSTDIR\text.081"
  Delete "$INSTDIR\text.082"
  Delete "$INSTDIR\text.083"
  Delete "$INSTDIR\text.084"
  Delete "$INSTDIR\text.085"
  Delete "$INSTDIR\text.086"
  Delete "$INSTDIR\text.087"
  Delete "$INSTDIR\text.088"
  Delete "$INSTDIR\text.089"
  Delete "$INSTDIR\text.090"
  Delete "$INSTDIR\text.091"
  Delete "$INSTDIR\text.092"
  Delete "$INSTDIR\text.093"
  Delete "$INSTDIR\text.094"
  Delete "$INSTDIR\text.095"
  Delete "$INSTDIR\text.120"
  Delete "$INSTDIR\text.221"
  Delete "$INSTDIR\text.222"
  Delete "$INSTDIR\text.255"
  Delete "$INSTDIR\text.301"
  Delete "$INSTDIR\text.302"
  Delete "$INSTDIR\text.305"
  Delete "$INSTDIR\text.306"
  Delete "$INSTDIR\text.307"
  Delete "$INSTDIR\text.333"
  Delete "$INSTDIR\text.503"
  Delete "$INSTDIR\text.504"
  Delete "$INSTDIR\text.505"
  Delete "$INSTDIR\text.506"
  Delete "$INSTDIR\text.507"
  Delete "$INSTDIR\text.508"
  Delete "$INSTDIR\text.509"
  Delete "$INSTDIR\text.510"
  Delete "$INSTDIR\text.511"
  Delete "$INSTDIR\text.512"
  Delete "$INSTDIR\text.513"
  Delete "$INSTDIR\text.514"
  Delete "$INSTDIR\text.516"
  Delete "$INSTDIR\text.517"
  Delete "$INSTDIR\text.518"
  Delete "$INSTDIR\text.519"
  Delete "$INSTDIR\text.600"
  Delete "$INSTDIR\text.602"
  Delete "$INSTDIR\text.603"
  Delete "$INSTDIR\text.604"
  Delete "$INSTDIR\text.605"
  Delete "$INSTDIR\text.654"
  Delete "$INSTDIR\text.690"
  Delete "$INSTDIR\text.692"
  Delete "$INSTDIR\text.694"
  Delete "$INSTDIR\text.697"
  Delete "$INSTDIR\text.699"
  Delete "$INSTDIR\text.700"
  Delete "$INSTDIR\text.701"
  Delete "$INSTDIR\text.800"
  Delete "$INSTDIR\text.801"
  Delete "$INSTDIR\text.989"
  Delete "$INSTDIR\text.990"
  Delete "$INSTDIR\text.991"
  Delete "$INSTDIR\text.992"
  Delete "$INSTDIR\text.993"
  Delete "$INSTDIR\text.994"
  Delete "$INSTDIR\text.995"
  Delete "$INSTDIR\text.996"
  Delete "$INSTDIR\text.997"
  Delete "$INSTDIR\text.998"
  Delete "$INSTDIR\text.999"
  
  ; Remove uninstaller
  Delete "$INSTDIR\Uninstall_Hebrew_Patch.exe"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ4_Hebrew_Patch"
  DeleteRegKey HKLM "Software\KQ4_Hebrew_Patch"

SectionEnd


