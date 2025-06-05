# Define the Unix Epoch start time (January 1, 1970, 00:00:00 UTC)
$unixEpoch = [DateTimeOffset](Get-Date -Year 1970 -Month 1 -Day 1 -Hour 0 -Minute 0 -Second 0 -Millisecond 0 -Kind Utc)

# Process all scheduled tasks
$allTasksData = Get-ScheduledTask | ForEach-Object {
    $task = $_ # This is the object from Get-ScheduledTask (contains State)
    $taskInfo = $task | Get-ScheduledTaskInfo -ErrorAction SilentlyContinue # Get details for this specific task

    # Initialize variables for properties that might be missing if $taskInfo is null
    $lastRunTime = $null
    $nextRunTime = $null
    $lastTaskResult = $null
    $numberOfMissedRuns = $null
    $psComputerName = $task.PSComputerName # PSComputerName is usually available on the base task object

    # Populate values from $taskInfo if it was successfully retrieved
    if ($taskInfo) {
        # Convert LastRunTime
        if ($taskInfo.LastRunTime -and ($taskInfo.LastRunTime -is [DateTime]) -and ($taskInfo.LastRunTime -ne [DateTime]::MinValue)) {
            $lastRunTime = [int64]([DateTimeOffset]$taskInfo.LastRunTime.ToUniversalTime()).ToUnixTimeSeconds()
        }

        # Convert NextRunTime
        if ($taskInfo.NextRunTime -and ($taskInfo.NextRunTime -is [DateTime]) -and ($taskInfo.NextRunTime -ne [DateTime]::MinValue)) {
            $nextRunTime = [int64]([DateTimeOffset]$taskInfo.NextRunTime.ToUniversalTime()).ToUnixTimeSeconds()
        }

        $lastTaskResult = $taskInfo.LastTaskResult
        $numberOfMissedRuns = $taskInfo.NumberOfMissedRuns
        $psComputerName = $taskInfo.PSComputerName
    }

    # Construct the custom object for JSON output
    [PSCustomObject]@{
        TaskName = $task.TaskName
        State = $task.State.ToString() # Get State from the base task object and convert enum to string
        LastRunTime = $lastRunTime
        NextRunTime = $nextRunTime
        LastTaskResult = $lastTaskResult
        NumberOfMissedRuns = $numberOfMissedRuns
        PSComputerName = $psComputerName
    }
}

# Create JSON
$out = $allTasksData | ConvertTo-Json -Compress -Depth 5

# Write JSON
Write-Host $out