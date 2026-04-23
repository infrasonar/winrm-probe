from libprobe.asset import Asset
from libprobe.check import Check
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


class CheckSoftware(Check):
    key = 'software'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        sess = await get_session(asset, local_config, config)
        items = await sess.query(SOFTWARE_PS1)

        for item in items:
            item['name'] = item.pop('PSChildName')

            if item['EstimatedSize']:
                item['EstimatedSize'] *= 1024

        return {
            'installed': items
        }
