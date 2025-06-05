import os
from libprobe.asset import Asset
from libprobe.exceptions import CheckException
from .session import Session


def ps_script(fn: str) -> str:
    fn = os.path.join(os.path.dirname(__file__), 'ps', fn)
    with open(fn, 'r') as fp:
        content = fp.read()

    return content


async def get_session(
        asset: Asset,
        asset_config: dict,
        config: dict) -> Session:
    address = config.get('address')
    if not address:
        address = asset.name

    port = config.get('port', 5861)
    if port not in (5985, 5986):
        raise CheckException(
            'port should be either 5985 (http) or 5986 (https)')

    username = asset_config.get('username')
    if not username:
        raise CheckException(
            'missing `username` in appliance asset configuration')
    password = asset_config.get('password')
    if not password:
        raise CheckException(
            'missing `password` in appliance asset configuration')

    sess = await Session.get(
        username=username,
        password=password,
        host=address,
        port=port)

    return sess
