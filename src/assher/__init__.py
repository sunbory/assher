#!/usr/bin/python3
# encoding: utf8

__version__ = "0.7.5"
import asyncio, asyncssh
from aioqs import AIOQS

    
class Assher(object):
    """A_SSHer
    This class represents job for (asynchronously) run commands and exchange files on group of remote hosts by SSH.
"""
    __tasks__ = None

    def __init__(self, hosts=[],
                 port=22,
                 username=None,
                 password=None,
                 privkeys=[],
                 commands=[],
                 upload_dir="/tmp",
                 uploads=[],
                 downloads=[],
                 download_dir="/tmp",
                 limit=50,
                 timeout=5,
                 debug=0):
        self.username = username
        self.password = password
        self.hosts = hosts
        self.port = port
        self.privkeys = privkeys
        self.commands = commands
        self.upload_dir = upload_dir
        self.uploads = uploads
        self.download_dir = download_dir
        self.downloads = downloads
        self.limit = limit
        self.timeout = timeout
        self.debug = debug

    async def run_client(self, host):
        results = []
        conparams = {
            "host": host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
        }
        conparams.update(host_url_parse(host))
        host = conparams.pop("host")

        try:
            async with await asyncio.wait_for(
                    asyncssh.connect(host,
                                     client_keys=self.privkeys,
                                     known_hosts=None,
                                     **conparams),
                    timeout=self.timeout) as conn:
                if self.uploads:
                    async with await conn.start_sftp_client()  as sftp:
                        if self.uploads:
                            try:
                                results.append(await sftp.put(uploads, "/tmp/"))
                            except asyncssh.sftp.SFTPError as e:
                                results.append(e)
                                
                results.extend([await conn.run(cmd) for cmd in self.commands])
                        
                if self.downloads:
                    async with await conn.start_sftp_client()  as sftp:
                        if self.downloads:
                            try:
                                results.append(
                                    await sftp.get(downloads, "/tmp/")
                                )
                            except asyncssh.sftp.SFTPError as e:
                                results.append(e)
                            
                return [host] + [(r.stdout.strip()
                                 if r.exit_status == 0
                                 else '')
                                for r in results]
            
        except (asyncio.TimeoutError,
                OSError,
                ValueError,
                ConnectionRefusedError,
                asyncssh.misc.DisconnectError) as e:
            return e


    async def __aenter__(self):
        return self


    async def __aexit__(self):
        self.__tasks__.__aexit__()


    def __aiter__(self):
        self.__tasks__ = AIOQS(
            (self.run_client(host) for host in self.hosts), # Tasks generator
            limit=self.limit
        ).__aiter__()
        return self


    async def __anext__(self):
        return await self.__tasks__.__anext__()


def host_url_parse(host_url):
    d = {}
    if "@" not in host_url and ":" in host_url:
        d["host"] = host_url
        return d

    url_parts = host_url.split("@")
    if len(url_parts) == 2:
        us, hs = url_parts
        if us:
            u = us.split(":")
            d["username"] = u.pop(0)
            if u:
                d["password"] = ':'.join(u)
    else: hs = url_parts[0]
    h = hs.split(':')
    d["host"] = h.pop(0)
    if h: d["port"] = int(h.pop(0))
    return d
