$registryPaths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
)

$arr = @()

foreach ($path in $registryPaths) {
    $arr += Get-ItemProperty -Path $path\* -ErrorAction SilentlyContinue | Where-Object {
        # Filter criteria: DisplayName must exist AND not be an empty string
        $_.DisplayName -ne $null -and $_.DisplayName -ne "" -and $_.UninstallString
    } | Select-Object -Property Publisher, DisplayName
}

$out = $arr | ConvertTo-Json -Compress

# Write JSON
Write-Host $out
