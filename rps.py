import asyncio
import getpass
import argparse
from lib.session import Session


async def main(ps_script: str, username: str, password: str,
               host: str, port: int):
    sess = await Session.get(username, password, host, port)
    result = await sess.query(ps_script)
    print(result)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-s',
        '--script',
        type=str,
        required=True,
        help='Powershell script to execute')

    parser.add_argument(
        '-a',
        '--address',
        type=str,
        required=True,
        help='host name or address of remote host')

    parser.add_argument(
        '-u',
        '--username',
        type=str,
        required=True,
        help='Username')

    parser.add_argument(
        '--password',
        type=str,
        help='password (asked if not provided)')

    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=5985,
        help='port should be either 5985 (http) or 5986 (https)')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(prompt='Password: ', stream=None)

    with open(args.script, 'r') as fp:
        ps_script = fp.read()

    asyncio.run(main(
        ps_script,
        args.username,
        args.password,
        args.address,
        args.port))
