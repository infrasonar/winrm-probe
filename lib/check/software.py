import logging
from libprobe.asset import Asset
from libprobe.exceptions import CheckException, NoCountException
from ..utils import ps_script, get_session



# "Comments": "",
# "Contact": "",
# "DisplayVersion": "14.29.30133",
# "HelpLink": "",
# "HelpTelephone": "",
# "InstallDate": "20231005",
# "InstallLocation": "",
# "InstallSource": "C:\\\\ProgramData\\\\Package Cache\\\\{EC9807DE-B577-47B1-A024-0251805ACF24}v14.29.30133\\\\packages\\\\vcRuntimeMinimum_x86\\\\",
# "ModifyPath": "MsiExec.exe /I{EC9807DE-B577-47B1-A024-0251805ACF24}",
# "Publisher": "Microsoft Corporation",
# "Readme": "",
# "Size": "",
# "EstimatedSize": 1736,
# "SystemComponent": 1,
# "UninstallString": "MsiExec.exe /I{EC9807DE-B577-47B1-A024-0251805ACF24}",
# "URLInfoAbout": "",
# "URLUpdateInfo": "",
# "VersionMajor": 14,
# "VersionMinor": 29,
# "Version": 236811701,
# "Language": 1033,
# "DisplayName": "Microsoft Visual C++ 2019 X86 Minimum Runtime - 14.29.30133",
# "PSChildName": "{EC9807DE-B577-47B1-A024-0251805ACF24}",

SOFTWARE_PS1 = ps_script('software.ps1')


async def check_software(
        asset: Asset,
        asset_config: dict,
        config: dict) -> dict:
    sess = await get_session(asset, asset_config, config)
    res = await sess.query(SOFTWARE_PS1)

    return res
