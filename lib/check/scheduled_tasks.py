from collections import defaultdict
from libprobe.asset import Asset
from ..utils import ps_script, get_session


SCHEDULED_TASKS_PS1 = ps_script('scheduled_tasks.ps1')

# "name"  # str
# "TaskName"  # str
# "State": # str
# "LastRunTime"  # int?
# "NextRunTime"  # int?
# "LastTaskResult"  # int?
# "LastTaskResultStr"  # str?
# "NumberOfMissedRuns"  # int?
# "PSComputerName"  # str?

# Define a function to translate LastTaskResult integers to strings
def result_to_string(i: int, loopkup: dict[int, str] = {
            0: "Success",
            1: "Incorrect Function/Unknown Function",
            2: "File Not Found",
            10: "Environment Incorrect",
            # Common HRESULTs from Task Scheduler
            # (often seen in decimal due to PowerShell's type conversion)
            267008: "Task Ready",
            267009: "Task Running",
            267010: "Task Disabled",
            267011: "Task Not Yet Run",
            267012: "No More Runs Scheduled",
            267014: "Task Terminated by User",
            # Common System Error Codes (also seen in HRESULT for,
            2147942402: "File Not Found",  # Often seen when executable is missing
            2147942405: "Access Denied",
            # Often if "Run only when user logged on" is enabled and user is not logged
            2147943408: "Service Not Available",
            2147944064: "Operator/Admin Refused Request",
            # Also sometimes seen for general app error
            2147943647: "Application Failed to Initialize / Generic Failure",
            3221225786: "Application Terminated (Ctrl+C)",  # Graceful termination
            3221225810: "Application Failed to Initialize",
        }) -> str:
    return loopkup.get(i, f"Unknown Result ({hex(i)})")


async def check_scheduled_tasks(
        asset: Asset,
        asset_config: dict,
        config: dict) -> dict:
    sess = await get_session(asset, asset_config, config)
    items = await sess.query(SCHEDULED_TASKS_PS1)

    counter = defaultdict(int)
    for item in items:
        name = item['TaskName']
        rc = item['LastTaskResult']
        counter[name] += 1
        item['name'] = f'{name}{counter[name]}'
        if rc is None:
            item.pop('LastTaskResult')
        else:
            item['LastTaskResultStr'] = result_to_string(rc)

        # remove properties which are null often to reduce size
        for key in ('LastRunTime', 'NextRunTime', 'PSComputerName'):
            if item[key] is None:
                item.pop(key)

    return {
        'scheduledTasks': items
    }
