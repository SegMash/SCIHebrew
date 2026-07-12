; King's Quest I - Orchestral Score Patch Installer
; NSIS Script
;
; This patch adds "THE ORCHESTRAL SCORE by Nissim Khalifa" to
; King's Quest I (SCI0 / 1990 remake). It replaces the original
; in-game music with a newly composed orchestral score, delivered
; as MP3 tracks played through the sciAudio extension.

;--------------------------------
; General Attributes

Name "King's Quest I - Orchestral Score"
OutFile "KQ1_Orchestral_Score_Setup.exe"
InstallDir ""
RequestExecutionLevel admin

;--------------------------------
; Version Information

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "King's Quest I Orchestral Score Patch"
VIAddVersionKey "FileDescription" "Orchestral Score by Nissim Khalifa for King's Quest I"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0.0"
VIAddVersionKey "LegalCopyright" "Nissim Khalifa"

;--------------------------------
; Modern UI

!include "MUI2.nsh"

;--------------------------------
; MUI Settings

!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Custom English text explaining the patch
!define MUI_WELCOMEPAGE_TITLE "King's Quest I - Orchestral Score by Nissim Khalifa"
!define MUI_WELCOMEPAGE_TEXT "This setup installs THE ORCHESTRAL SCORE by Nissim Khalifa for King's Quest I.$\r$\n$\r$\nThe patch replaces the original in-game music with a newly composed orchestral score delivered as high-quality MP3 tracks (played through the sciAudio extension).$\r$\n$\r$\nIt does NOT alter the game's text, graphics or gameplay - only the soundtrack.$\r$\n$\r$\nClick 'Next' to continue."
!define MUI_DIRECTORYPAGE_TEXT_TOP "Select the folder where King's Quest I is installed.$\r$\n$\r$\nThe installer will verify that this is a valid King's Quest I directory before proceeding."
!define MUI_FINISHPAGE_TITLE "Installation Complete"
!define MUI_FINISHPAGE_TEXT "The Orchestral Score by Nissim Khalifa has been installed successfully.$\r$\n$\r$\nLaunch King's Quest I to enjoy the new soundtrack.$\r$\n$\r$\nClick 'Finish' to close this wizard."

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

!insertmacro MUI_LANGUAGE "English"

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

  ; Check if file size is exactly 5,790 bytes (KQ1 SCI0 resource.map)
  IntCmp $1 5790 valid_dir invalid_dir invalid_dir

  valid_dir:
    Return

  invalid_dir:
    Abort
FunctionEnd

;--------------------------------
; Installer Sections

Section "King's Quest I Orchestral Score" SecMain

  SetOutPath "$INSTDIR"

  ; Set overwrite on to replace existing files
  SetOverwrite try

  ; Vocab files
  File "games_assets\kq1\bin_audio_only\vocab.996"
  File "games_assets\kq1\bin_audio_only\vocab.997"
  
  ; View files
  File "games_assets\kq1\bin_audio_only\view.913"

  ; Script files (patched to trigger sciAudio playback)
  File "games_assets\kq1\bin_audio_only\script.001"
  File "games_assets\kq1\bin_audio_only\script.003"
  File "games_assets\kq1\bin_audio_only\script.009"
  File "games_assets\kq1\bin_audio_only\script.010"
  File "games_assets\kq1\bin_audio_only\script.011"
  File "games_assets\kq1\bin_audio_only\script.013"
  File "games_assets\kq1\bin_audio_only\script.017"
  File "games_assets\kq1\bin_audio_only\script.021"
  File "games_assets\kq1\bin_audio_only\script.022"
  File "games_assets\kq1\bin_audio_only\script.025"
  File "games_assets\kq1\bin_audio_only\script.039"
  File "games_assets\kq1\bin_audio_only\script.040"
  File "games_assets\kq1\bin_audio_only\script.041"
  File "games_assets\kq1\bin_audio_only\script.049"
  File "games_assets\kq1\bin_audio_only\script.050"
  File "games_assets\kq1\bin_audio_only\script.051"
  File "games_assets\kq1\bin_audio_only\script.052"
  File "games_assets\kq1\bin_audio_only\script.053"
  File "games_assets\kq1\bin_audio_only\script.058"
  File "games_assets\kq1\bin_audio_only\script.063"
  File "games_assets\kq1\bin_audio_only\script.065"
  File "games_assets\kq1\bin_audio_only\script.066"
  File "games_assets\kq1\bin_audio_only\script.067"
  File "games_assets\kq1\bin_audio_only\script.068"
  File "games_assets\kq1\bin_audio_only\script.069"
  File "games_assets\kq1\bin_audio_only\script.070"
  File "games_assets\kq1\bin_audio_only\script.071"
  File "games_assets\kq1\bin_audio_only\script.073"
  File "games_assets\kq1\bin_audio_only\script.074"
  File "games_assets\kq1\bin_audio_only\script.075"
  File "games_assets\kq1\bin_audio_only\script.076"
  File "games_assets\kq1\bin_audio_only\script.077"
  File "games_assets\kq1\bin_audio_only\script.079"
  File "games_assets\kq1\bin_audio_only\script.080"
  File "games_assets\kq1\bin_audio_only\script.084"
  File "games_assets\kq1\bin_audio_only\script.085"
  File "games_assets\kq1\bin_audio_only\script.086"
  File "games_assets\kq1\bin_audio_only\script.087"
  File "games_assets\kq1\bin_audio_only\script.095"
  File "games_assets\kq1\bin_audio_only\script.200"
  File "games_assets\kq1\bin_audio_only\script.603"
  File "games_assets\kq1\bin_audio_only\script.605"
  File "games_assets\kq1\bin_audio_only\script.606"
  File "games_assets\kq1\bin_audio_only\script.608"
  File "games_assets\kq1\bin_audio_only\script.609"
  File "games_assets\kq1\bin_audio_only\script.610"
  File "games_assets\kq1\bin_audio_only\script.612"
  File "games_assets\kq1\bin_audio_only\script.613"
  File "games_assets\kq1\bin_audio_only\script.779"
  File "games_assets\kq1\bin_audio_only\script.782"
  File "games_assets\kq1\bin_audio_only\script.800"
  File "games_assets\kq1\bin_audio_only\script.803"
  File "games_assets\kq1\bin_audio_only\script.804"
  File "games_assets\kq1\bin_audio_only\script.994"
  

  ; Orchestral score MP3 tracks (sciAudio subdirectory)
  SetOutPath "$INSTDIR\sciAudio"
  File "games_assets\kq1\bin_audio_only\sciAudio\badGuess.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\beanGrow.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\cave.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\climb.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\condor.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\condorComing.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\credits.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\death.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\death2.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\death3.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\dwarf.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\endClimb.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\enterCastleWithTreasures.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\exitFromWater.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\fairy.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\fairyShort.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\giant.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\goat.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\goodGuess.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\intro.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\leprechauns42.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\leprechauns47.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\leprechauns48.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\longLive.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\longLiveTheEnd.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\mainTitle.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\mirror.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\moat.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\oak.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\orge.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\orgeDwarfWolf.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\rat.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\ratPart2.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\snoringPart1.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\snoringPart2.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\sorcerer.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\tiredGiant.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\treasures.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\troll.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\trollAndGoat.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\underwater.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\witch.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\witchInForest.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\witchKilling.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\woodcutter.mp3"
  File "games_assets\kq1\bin_audio_only\sciAudio\woodcutterGiveBowl.mp3"

  ; Reset output path for uninstaller / registry writes
  SetOutPath "$INSTDIR"

  ; Store installation folder
  WriteRegStr HKLM "Software\KQ1_Orchestral_Score" "Install_Dir" "$INSTDIR"

  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall_Orchestral_Score.exe"

  ; Write uninstall registry keys
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ1_Orchestral_Score" "DisplayName" "King's Quest I - Orchestral Score by Nissim Khalifa"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ1_Orchestral_Score" "UninstallString" '"$INSTDIR\Uninstall_Orchestral_Score.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ1_Orchestral_Score" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ1_Orchestral_Score" "NoRepair" 1

SectionEnd

;--------------------------------
; Uninstaller Section

Section "Uninstall"

  ; Remove vocab files
  Delete "$INSTDIR\vocab.996"
  Delete "$INSTDIR\vocab.997"

  ; Remove view files
  Delete "$INSTDIR\view.913"
  
  ; Remove script files
  Delete "$INSTDIR\script.001"
  Delete "$INSTDIR\script.003"
  Delete "$INSTDIR\script.009"
  Delete "$INSTDIR\script.010"
  Delete "$INSTDIR\script.011"
  Delete "$INSTDIR\script.013"
  Delete "$INSTDIR\script.017"
  Delete "$INSTDIR\script.021"
  Delete "$INSTDIR\script.022"
  Delete "$INSTDIR\script.025"
  Delete "$INSTDIR\script.039"
  Delete "$INSTDIR\script.040"
  Delete "$INSTDIR\script.041"
  Delete "$INSTDIR\script.049"
  Delete "$INSTDIR\script.050"
  Delete "$INSTDIR\script.051"
  Delete "$INSTDIR\script.052"
  Delete "$INSTDIR\script.053"
  Delete "$INSTDIR\script.058"
  Delete "$INSTDIR\script.063"
  Delete "$INSTDIR\script.065"
  Delete "$INSTDIR\script.066"
  Delete "$INSTDIR\script.067"
  Delete "$INSTDIR\script.068"
  Delete "$INSTDIR\script.069"
  Delete "$INSTDIR\script.070"
  Delete "$INSTDIR\script.071"
  Delete "$INSTDIR\script.073"
  Delete "$INSTDIR\script.074"
  Delete "$INSTDIR\script.075"
  Delete "$INSTDIR\script.076"
  Delete "$INSTDIR\script.077"
  Delete "$INSTDIR\script.079"
  Delete "$INSTDIR\script.080"
  Delete "$INSTDIR\script.084"
  Delete "$INSTDIR\script.085"
  Delete "$INSTDIR\script.086"
  Delete "$INSTDIR\script.087"
  Delete "$INSTDIR\script.095"
  Delete "$INSTDIR\script.200"
  Delete "$INSTDIR\script.603"
  Delete "$INSTDIR\script.605"
  Delete "$INSTDIR\script.606"
  Delete "$INSTDIR\script.608"
  Delete "$INSTDIR\script.609"
  Delete "$INSTDIR\script.610"
  Delete "$INSTDIR\script.612"
  Delete "$INSTDIR\script.613"
  Delete "$INSTDIR\script.779"
  Delete "$INSTDIR\script.782"
  Delete "$INSTDIR\script.800"
  Delete "$INSTDIR\script.803"
  Delete "$INSTDIR\script.804"
  Delete "$INSTDIR\script.994"


  ; Remove MP3 tracks
  Delete "$INSTDIR\sciAudio\badGuess.mp3"
  Delete "$INSTDIR\sciAudio\beanGrow.mp3"
  Delete "$INSTDIR\sciAudio\cave.mp3"
  Delete "$INSTDIR\sciAudio\climb.mp3"
  Delete "$INSTDIR\sciAudio\condor.mp3"
  Delete "$INSTDIR\sciAudio\condorComing.mp3"
  Delete "$INSTDIR\sciAudio\credits.mp3"
  Delete "$INSTDIR\sciAudio\death.mp3"
  Delete "$INSTDIR\sciAudio\death2.mp3"
  Delete "$INSTDIR\sciAudio\death3.mp3"
  Delete "$INSTDIR\sciAudio\dwarf.mp3"
  Delete "$INSTDIR\sciAudio\endClimb.mp3"
  Delete "$INSTDIR\sciAudio\enterCastleWithTreasures.mp3"
  Delete "$INSTDIR\sciAudio\exitFromWater.mp3"
  Delete "$INSTDIR\sciAudio\fairy.mp3"
  Delete "$INSTDIR\sciAudio\fairyShort.mp3"
  Delete "$INSTDIR\sciAudio\giant.mp3"
  Delete "$INSTDIR\sciAudio\goat.mp3"
  Delete "$INSTDIR\sciAudio\goodGuess.mp3"
  Delete "$INSTDIR\sciAudio\intro.mp3"
  Delete "$INSTDIR\sciAudio\leprechauns42.mp3"
  Delete "$INSTDIR\sciAudio\leprechauns47.mp3"
  Delete "$INSTDIR\sciAudio\leprechauns48.mp3"
  Delete "$INSTDIR\sciAudio\longLive.mp3"
  Delete "$INSTDIR\sciAudio\longLiveTheEnd.mp3"
  Delete "$INSTDIR\sciAudio\mainTitle.mp3"
  Delete "$INSTDIR\sciAudio\mirror.mp3"
  Delete "$INSTDIR\sciAudio\moat.mp3"
  Delete "$INSTDIR\sciAudio\oak.mp3"
  Delete "$INSTDIR\sciAudio\orge.mp3"
  Delete "$INSTDIR\sciAudio\orgeDwarfWolf.mp3"
  Delete "$INSTDIR\sciAudio\rat.mp3"
  Delete "$INSTDIR\sciAudio\ratPart2.mp3"
  Delete "$INSTDIR\sciAudio\snoringPart1.mp3"
  Delete "$INSTDIR\sciAudio\snoringPart2.mp3"
  Delete "$INSTDIR\sciAudio\sorcerer.mp3"
  Delete "$INSTDIR\sciAudio\tiredGiant.mp3"
  Delete "$INSTDIR\sciAudio\treasures.mp3"
  Delete "$INSTDIR\sciAudio\troll.mp3"
  Delete "$INSTDIR\sciAudio\trollAndGoat.mp3"
  Delete "$INSTDIR\sciAudio\underwater.mp3"
  Delete "$INSTDIR\sciAudio\witch.mp3"
  Delete "$INSTDIR\sciAudio\witchInForest.mp3"
  Delete "$INSTDIR\sciAudio\witchKilling.mp3"
  Delete "$INSTDIR\sciAudio\woodcutter.mp3"
  Delete "$INSTDIR\sciAudio\woodcutterGiveBowl.mp3"


  ; Remove sciAudio folder if empty
  RMDir "$INSTDIR\sciAudio"

  ; Remove uninstaller
  Delete "$INSTDIR\Uninstall_Orchestral_Score.exe"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KQ1_Orchestral_Score"
  DeleteRegKey HKLM "Software\KQ1_Orchestral_Score"

SectionEnd
