from libprobe.asset import Asset
from ..utils import ps_script, get_session


SCHEDULED_TASKS_PS1 = ps_script('scheduled_tasks.ps1')

# "LastRunTime": "/Date(1746375193000)/",
# "LastTaskResult": 0,
# "NextRunTime": null,
# "NumberOfMissedRuns": 0,
# "TaskName": "OobeDiscovery",
# "TaskPath": "\\Microsoft\\Windows\\WwanSvc\\",
# "PSComputerName": null


async def check_scheduled_tasks(
        asset: Asset,
        asset_config: dict,
        config: dict) -> dict:
    sess = await get_session(asset, asset_config, config)
    items = await sess.query(SCHEDULED_TASKS_PS1)

    for item in items:
        pass

    return {
        'scheduledTasks': items
    }
