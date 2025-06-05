from __future__ import annotations
from base64 import b64encode
from typing import Optional, Any
from winrm import Response
from winrm.protocol import Protocol
import asyncio
import json
import logging
import re
import time
import warnings
import xml.etree.ElementTree as ET


class Session:
    sessions: dict[tuple[str, str, str, int], Session] = dict()
    loop: Optional[asyncio.AbstractEventLoop] = None
    task: Optional[asyncio.Future] = None
    max_idle: float = 60.0

    def __init__(self, username: str, password: str,
                 host: str, port: int = 5986):
        self.lock = asyncio.Lock()
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.last_access = time.time()

        self.protocol: Optional[Protocol] = None
        self.shell_id: Optional[str] = None
        if self.loop is None:
            self.__class__.loop = asyncio.get_running_loop()
            self.__class__.task = asyncio.ensure_future(self.close_sessions())

    @classmethod
    async def close_sessions(cls):
        while True:
            min_threshold = time.time() - cls.max_idle
            for key, sess in cls.sessions.copy().items():
                if sess.last_access < min_threshold:
                    async with sess.lock:
                        if sess.protocol and sess.shell_id:
                            sess._close_shell()
                            del cls.sessions[key]
            for _ in range(20):
                await asyncio.sleep(0.5)

    @staticmethod
    def _decode(b: bytes) -> str:
        try:
            msg = b.decode('utf-8')
        except Exception:
            msg = b.decode('cp1252')

        return msg

    @staticmethod
    def _truncate(msg: str, n: int) -> str:
        return f'{msg[:n-3]}...' if len(msg) > n else msg

    def _strip_namespace(self, xml: bytes) -> bytes:
        """strips any namespaces from an xml string"""
        p = re.compile(b'xmlns=*[""][^""]*[""]')
        allmatches = p.finditer(xml)
        for match in allmatches:
            xml = xml.replace(match.group(), b"")
        return xml

    def _clean_error_msg(self, msg: bytes) -> bytes:
        """converts a Powershell CLIXML message to a more human readable
        string"""
        # if the msg does not start with this, return it as is
        if msg.startswith(b"#< CLIXML\r\n"):
            # for proper xml, we need to remove the CLIXML part
            # (the first line)
            msg_xml = msg[11:]
            try:
                # remove the namespaces from the xml for easier processing
                msg_xml = self._strip_namespace(msg_xml)
                root = ET.fromstring(msg_xml)
                # the S node is the error message, find all S nodes
                nodes = root.findall("./S")
                new_msg = ""
                for s in nodes:
                    # append error msg string to result, also
                    # the hex chars represent CRLF so we replace with newline
                    if s.text:
                        new_msg += s.text.replace("_x000D__x000A_", "\n")
            except Exception as e:
                # if any of the above fails, the msg was not true xml
                # print a warning and return the original string
                warnings.warn(
                    "There was a problem converting the Powershell error "
                    f"message: {e}")
            else:
                # if new_msg was populated, that's our error message
                # otherwise the original error message will be used
                if len(new_msg):
                    # remove leading and trailing whitespace while we are here
                    return new_msg.strip().encode("utf-8")

        # either failed to decode CLIXML or there was nothing to decode
        # just return the original message
        return msg

    def _query(self, script: str) -> Any:
        encoded_ps = b64encode(script.encode("utf_16_le")).decode("ascii")
        command = f"powershell -encodedcommand {encoded_ps}"
        retry = True
        while True:
            if self.protocol is None:
                self._open_shell()
                retry = False

            assert(self.protocol and self.shell_id)
            try:
                command_id = self.protocol.run_command(self.shell_id, command)
                try:
                    rs = Response(self.protocol.get_command_output(
                        self.shell_id,
                        command_id))
                finally:
                    self.protocol.cleanup_command(self.shell_id, command_id)
            except Exception as e:
                self._close_shell()
                if retry:
                    retry = False
                    logging.debug(f'error: {e} (retry...)')
                    continue
                raise
            else:
                break

        if rs.status_code:
            # if there was an error, clean it it up and make it human
            # readable
            try:
                b = self._clean_error_msg(rs.std_err)
                msg = self._truncate(self._decode(b), 60)
                assert msg  # only raise when we have a message
                raise Exception(msg)
            except Exception:
                raise Exception(f'status code: {rs.status_code} (no message)')

        try:
            data = json.loads(rs.std_out)
        except Exception:
            msg = self._truncate(self._decode(rs.std_out), 30)
            raise Exception(f'failed to parse content as JSON: {msg}')

        return data

    def _open_shell(self):
        assert self.protocol is None and self.shell_id is None
        # WinRM port 5985 is http and 5986 is https
        proto = 'http' if self.port == 5985 else 'https'

        self.protocol = Protocol(
            endpoint=f'{proto}://{self.host}:{self.port}/wsman',
            transport='ntlm',
            username=self.username,
            password=self.password,
            server_cert_validation='ignore')
        try:
            self.shell_id = self.protocol.open_shell()
        except Exception:
            self.protocol = None
            raise

    def _close_shell(self):
        assert self.protocol and self.shell_id
        try:
            self.protocol.close_shell(self.shell_id)
        finally:
            self.protocol = None
            self.shell_id = None

    async def query(self, script: str) -> Any:
        assert self.loop
        async with self.lock:
            res = await self.loop.run_in_executor(None, self._query, script)
            self.last_access = time.time()  # update on no exception
            return res

    @classmethod
    async def get(cls, username: str, password: str,
                  host: str, port: int = 5986) -> Session:
        key = (host, username, password, port)
        sess = cls.sessions.get(key)
        if sess is None:
            sess = cls.sessions[key] = cls(username, password, host, port)

        return sess
