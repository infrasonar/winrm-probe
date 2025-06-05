# Get Scheduled Task Information
$tasks = Get-ScheduledTask | Get-ScheduledTaskInfo | Select-Object -Property LastRunTime, LastTaskResult, NextRunTime, NumberOfMissedRuns, TaskName, PSComputerName

# Define the Unix Epoch start time (January 1, 1970, 00:00:00 UTC)
# Using [DateTimeOffset] for better handling of UTC and milliseconds
$unixEpoch = [DateTimeOffset](Get-Date -Year 1970 -Month 1 -Day 1 -Hour 0 -Minute 0 -Second 0 -Millisecond 0 -Kind Utc)

# Process the tasks and convert dates to Unix timestamps
# Note we divide by 10.000.000 as there are 10,000,000 nanosecond ticks in one second
$processedTasks = $tasks | Select-Object -Property @{
    Name = 'LastRunTimestampMs'
    Expression = {
        # Check if LastRunTime exists and is a valid DateTime object
        if ($_.LastRunTime -and ($_.LastRunTime -is [DateTime]) -and ($_.LastRunTime -ne [DateTime]::MinValue)) {
            # Convert to DateTimeOffset to easily get Unix milliseconds
            [DateTimeOffset]$_.LastRunTime.ToUniversalTime().Ticks / 10000000 - ([DateTimeOffset]$unixEpoch.Ticks / 10000000)
        } else {
            $null # Or 0, or an empty string, depending on your desired output for null dates
        }
    }
}, @{
    Name = 'NextRunTimestamp'
    Expression = {
        # Check if NextRunTime exists and is a valid DateTime object
        if ($_.NextRunTime -and ($_.NextRunTime -is [DateTime]) -and ($_.NextRunTime -ne [DateTime]::MinValue)) {
            # Convert to DateTimeOffset to easily get Unix milliseconds
            [DateTimeOffset]$_.NextRunTime.ToUniversalTime().Ticks / 10000000 - ([DateTimeOffset]$unixEpoch.Ticks / 10000000)
        } else {
            $null # Or 0, or an empty string
        }
    }
}

# Create JSON
$out = $processedTasks | ConvertTo-Json -Compress -Depth 5  # -Depth just in case

# Write JSON
Write-Host $out