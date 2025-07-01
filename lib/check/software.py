from libprobe.asset import Asset
from ..utils import ps_script, get_session


SOFTWARE_PS1 = ps_script('software.ps1')

# "DisplayVersion" # str
# "InstallDate" # str?
# "Publisher": # str?
# "EstimatedSize": # int? (in KB -> *1024)
# "VersionMajor": # int?
# "VersionMinor": # int?
# "DisplayName": # str
# "PSChildName": # -> name


async def check_software(
        asset: Asset,
        asset_config: dict,
        config: dict) -> dict:
    sess = await get_session(asset, asset_config, config)
    items = await sess.query(SOFTWARE_PS1)

    for item in items:
        item['name'] = item.pop('PSChildName')

        if item['EstimatedSize']:
            item['EstimatedSize'] *= 1024

    return {
        'installed': items
    }
