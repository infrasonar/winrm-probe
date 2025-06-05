# Get Scheduled Task Information
$tasks = Get-ScheduledTask | Get-ScheduledTaskInfo | Select-Object -Property LastRunTime, NextRunTime, LastTaskResult, NumberOfMissedRuns, TaskName, PSComputerName

# Get the current UTC date and time as a DateTimeOffset
$nowUtc = [DateTimeOffset]::UtcNow

# Calculate ticks from 0001-01-01 to now in seconds
$secondsSinceYear1 = $nowUtc.Ticks / 10000000

# Process the tasks and convert dates to Unix timestamps
# Note we divide by 10.000.000 as there are 10,000,000 nanosecond ticks in one second
$processedTasks = $tasks | Select-Object -Property @{
    Name = 'LastRunTime'
    Expression = {
        # Check if LastRunTime exists and is a valid DateTime object
        if ($_.LastRunTime -and ($_.LastRunTime -is [DateTime]) -and ($_.LastRunTime -ne [DateTime]::MinValue)) {
            # Convert to DateTimeOffset to easily get Unix milliseconds
            [int64](([DateTimeOffset]$_.LastRunTime.ToUniversalTime()).Ticks / 10000000 - $secondsSinceYear1)
        } else {
            $null # Or 0, or an empty string, depending on your desired output for null dates
        }
    }
}, @{
    Name = 'NextRunTime'
    Expression = {
        # Check if NextRunTime exists and is a valid DateTime object
        if ($_.NextRunTime -and ($_.NextRunTime -is [DateTime]) -and ($_.NextRunTime -ne [DateTime]::MinValue)) {
            # Convert to DateTimeOffset, then calculate Unix seconds
            [int64](([DateTimeOffset]$_.NextRunTime.ToUniversalTime()).Ticks / 10000000 - $secondsSinceYear1)
        } else {
            $null # Or 0, or an empty string
        }
    }
}, LastTaskResult, NumberOfMissedRuns, TaskName, PSComputerName

# Create JSON
$out = $processedTasks | ConvertTo-Json -Compress -Depth 5  # -Depth just in case

# Write JSON
Write-Host $out