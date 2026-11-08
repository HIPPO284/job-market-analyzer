Unicode true

!include "MUI2.nsh"

Name "Job Market Analyzer"
OutFile "${__FILEDIR__}\..\JobMarketAnalyzer-Setup.exe"

InstallDir "$LOCALAPPDATA\Programs\JobMarketAnalyzer"
RequestExecutionLevel user

!define MUI_ICON "${__FILEDIR__}\hippo.ico"
!define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\JobMarketAnalyzer"

!insertmacro MUI_PAGE_LICENSE "${__FILEDIR__}\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!define MUI_FINISHPAGE_RUN "$INSTDIR\JobMarketAnalyzer.exe"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetShellVarContext current
    SetOutPath "$INSTDIR"

    File "${__FILEDIR__}\..\release\JobMarketAnalyzer.exe"
    File "${__FILEDIR__}\..\release\README.md"
    File "${__FILEDIR__}\..\release\LICENSE"
    File "${__FILEDIR__}\..\release\ARTWORK_LICENSE.txt"
    File "${__FILEDIR__}\..\release\THIRD_PARTY_NOTICES.txt"
    File "${__FILEDIR__}\..\release\PYTHON_LICENSE.txt"
    File /r "${__FILEDIR__}\..\release\third_party_licenses"

    WriteUninstaller "$INSTDIR\Uninstall.exe"

    CreateShortcut "$DESKTOP\Job Market Analyzer.lnk" "$INSTDIR\JobMarketAnalyzer.exe"

    CreateDirectory "$SMPROGRAMS\Job Market Analyzer"
    CreateShortcut "$SMPROGRAMS\Job Market Analyzer\Job Market Analyzer.lnk" "$INSTDIR\JobMarketAnalyzer.exe"
    CreateShortcut "$SMPROGRAMS\Job Market Analyzer\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

    WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayName" "Job Market Analyzer"
    WriteRegStr HKCU "${UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\JobMarketAnalyzer.exe"
    WriteRegStr HKCU "${UNINSTALL_KEY}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegDWORD HKCU "${UNINSTALL_KEY}" "NoModify" 1
    WriteRegDWORD HKCU "${UNINSTALL_KEY}" "NoRepair" 1
SectionEnd


Section "Uninstall"
    SetShellVarContext current

    Delete "$DESKTOP\Job Market Analyzer.lnk"

    Delete "$SMPROGRAMS\Job Market Analyzer\Job Market Analyzer.lnk"
    Delete "$SMPROGRAMS\Job Market Analyzer\Uninstall.lnk"
    RMDir "$SMPROGRAMS\Job Market Analyzer"

    Delete "$INSTDIR\JobMarketAnalyzer.exe"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\LICENSE"
    Delete "$INSTDIR\ARTWORK_LICENSE.txt"
    Delete "$INSTDIR\THIRD_PARTY_NOTICES.txt"
    Delete "$INSTDIR\PYTHON_LICENSE.txt"

    RMDir /r "$INSTDIR\third_party_licenses"

    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"

    DeleteRegKey HKCU "${UNINSTALL_KEY}"
SectionEnd






















