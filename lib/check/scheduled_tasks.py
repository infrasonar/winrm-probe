from collections import defaultdict
from libprobe.asset import Asset
from ..utils import ps_script, get_session


SCHEDULED_TASKS_PS1 = ps_script('scheduled_tasks.ps1')

# "TaskName"  # str
# "TaskPath"  # str (->name)
# "State": # str
# "LastRunTime"  # int?
# "NextRunTime"  # int?
# "LastTaskResult"  # int?
# "NumberOfMissedRuns"  # int?
# "PSComputerName"  # str?


async def check_scheduled_tasks(
        asset: Asset,
        asset_config: dict,
        config: dict) -> dict:
    sess = await get_session(asset, asset_config, config)
    items = await sess.query(SCHEDULED_TASKS_PS1)

    counter = defaultdict(int)
    for item in items:
        name = item['TaskName']
        counter[name] += 1
        item['name'] = f'{name}{counter[name]}'

    return {
        'scheduledTasks': items
    }
