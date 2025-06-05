$registryPaths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
)

# "Comments": "",
# "Contact": "",
# "DisplayVersion": "14.29.30133",
# "HelpLink": "",
# "HelpTelephone": "",
# "InstallDate": "20231005",
# "InstallLocation": "",
# "InstallSource": "C:\\\\ProgramData\\\\Package Cache\\\\{EC9807DE-B577-47B1-A024-0251805ACF24}v14.29.30133\\\\packages\\\\vcRuntimeMinimum_x86\\\\",
# "ModifyPath": "MsiExec.exe /I{EC9807DE-B577-47B1-A024-0251805ACF24}",
# "Publisher": "Microsoft Corporation",
# "Readme": "",
# "Size": "",
# "EstimatedSize": 1736,
# "SystemComponent": 1,
# "UninstallString": "MsiExec.exe /I{EC9807DE-B577-47B1-A024-0251805ACF24}",
# "URLInfoAbout": "",
# "URLUpdateInfo": "",
# "VersionMajor": 14,
# "VersionMinor": 29,
# "Version": 236811701,
# "Language": 1033,
# "DisplayName": "Microsoft Visual C++ 2019 X86 Minimum Runtime - 14.29.30133",
# "PSChildName": "{EC9807DE-B577-47B1-A024-0251805ACF24}",

$arr = @()

foreach ($path in $registryPaths) {
    $arr += Get-ItemProperty -Path $path\* -ErrorAction SilentlyContinue | Where-Object {
        # Filter criteria: DisplayName must exist AND not be an empty string
        $_.DisplayName -ne $null -and $_.DisplayName -ne "" -and $_.UninstallString
    } | Select-Object -Property DisplayVersion, InstallDate, Publisher, EstimatedSize, VersionMajor, VersionMinor, DisplayName, PSChildName
}

# Create JSON
$out = $arr | ConvertTo-Json -Compress

# Write JSON
Write-Host $out
