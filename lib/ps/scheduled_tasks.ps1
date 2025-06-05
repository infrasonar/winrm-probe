$tasks = Get-ScheduledTask | Get-ScheduledTaskInfo

# Create JSON
$out = $tasks | ConvertTo-Json -Compress

# Write JSON
Write-Host $out
