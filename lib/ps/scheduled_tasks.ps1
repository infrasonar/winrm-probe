# Define the Unix Epoch start time (January 1, 1970, 00:00:00 UTC)
$unixEpoch = [DateTimeOffset](Get-Date -Year 1970 -Month 1 -Day 1 -Hour 0 -Minute 0 -Second 0 -Millisecond 0 -Kind Utc)

# Define a function to translate LastTaskResult integers to strings
function Convert-LastTaskResultToString {
    param (
        [int]$ResultCode
    )

    switch ($ResultCode) {
        0 { "Success" }
        1 { "Incorrect Function/Unknown Function" }
        2 { "File Not Found" }
        10 { "Environment Incorrect" }

        # Common HRESULTs from Task Scheduler (often seen in decimal due to PowerShell's type conversion)
        267008 { "Task Ready" }
        267009 { "Task Running" }
        267010 { "Task Disabled" }
        267011 { "Task Not Yet Run" }
        267012 { "No More Runs Scheduled" }
        267014 { "Task Terminated by User" }

        # Common System Error Codes (also seen in HRESULT form)
        2147942402 { "File Not Found" } # Often seen when executable is missing
        2147942405 { "Access Denied" }
        2147943408 { "Service Not Available" } # Often if "Run only when user logged on" is enabled and user is not logged on
        2147944064 { "Operator/Admin Refused Request" }
        2147943647 { "Application Failed to Initialize / Generic Failure" } # Also sometimes seen for general app errors
        3221225786 { "Application Terminated (Ctrl+C)" } # Graceful termination
        3221225810 { "Application Failed to Initialize" }

        # Default case for unknown codes
        Default { "Unknown Result ($ResultCode / 0x{0:X})" -f $ResultCode }
    }
}

# Process all scheduled tasks
$allTasksData = Get-ScheduledTask | ForEach-Object {
    $task = $_ # This is the object from Get-ScheduledTask (contains State)
    $taskInfo = $task | Get-ScheduledTaskInfo -ErrorAction SilentlyContinue # Get details for this specific task

    # Initialize variables for properties that might be missing if $taskInfo is null
    $lastRunTime = $null
    $nextRunTime = $null
    $lastTaskResult = $null
    $lastTaskResultStr = $null
    $numberOfMissedRuns = $null
    $psComputerName = $task.PSComputerName  # PSComputerName is usually available on the base task object

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
        $lastTaskResultStr = Convert-LastTaskResultToString -ResultCode $taskInfo.LastTaskResult # Convert to string
        $numberOfMissedRuns = $taskInfo.NumberOfMissedRuns
        $psComputerName = $taskInfo.PSComputerName  # Execution of the task (with -ComputerName RemotePC as example)
    }

    # Construct the custom object for JSON output
    [PSCustomObject]@{
        TaskName = $task.TaskName
        State = $task.State.ToString() # Get State from the base task object and convert enum to string
        LastRunTime = $lastRunTime
        NextRunTime = $nextRunTime
        LastTaskResult = $lastTaskResult
        LastTaskResultStr = $lastTaskResultStr
        NumberOfMissedRuns = $numberOfMissedRuns
        PSComputerName = $psComputerName
    }
}

# Create JSON
$out = $allTasksData | ConvertTo-Json -Compress -Depth 5

# Write JSON
Write-Host $out