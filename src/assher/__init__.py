#!/usr/bin/python3
# encoding: utf8

import asyncio, asyncssh, sys, os, argparse
from time import sleep, time_ns
from aioqs import AIOQS
from asyncssh.misc import DisconnectError
from asyncssh.sftp import SFTPError
from .conf import settings


async def run_client(host, cmds,
                     downloads=[], download_dir="/tmp",
                     upload_dir="/tmp", uploads=[]):
    if settings.debug >=2: print("Running client", time_ns())
    try:
        async with await asyncio.wait_for(
            asyncssh.connect(host,
                             username=settings.username,
                             password=settings.password,
                             client_keys=settings.privkey,
                             known_hosts=None,
                             **{}),
            timeout=5) as conn:
            if uploads or downloads:
                async with await conn.start_sftp_client() as sftp:
                    try:
                        if uploads:
                            await sftp.put(uploads, "/tmp/")
                            if settings.debug:
                                print("Copied file to remote host {}".format(host), file=sys.stderr)
                        if downloads:
                            await sftp.get(downloads, "/tmp/")
                            if settings.debug:
                                print("Copied file to remote host {}".format(host), file=sys.stderr)
                    except SFTPError as e:
                        print(e, host)
            results = [await conn.run(c) for c in cmds]
            return [host]+ [(r.stdout.strip()
                             if r.exit_status == 0
                             else '')
                            for r in results]
    except asyncio.TimeoutError: pass
    except (
        OSError,
        ValueError,
        ConnectionRefusedError,
            ) as e:
        return e
    except DisconnectError as e:
        print("Disconnected {}: {}".format(host,e))
        return e
#     except Exception as e:
#         return e
    

def iter_concat(*args):
    generator = type((i for i in range(1)))
    for x in args:
        if type(x) is str: yield x
        elif type(x) in (list,tuple, generator):
            for y in x: yield y
        else: raise TypeError

    
async def main():
    hosts = iter_concat(*([ settings.HOSTS.get(hp, [])
                            for hp in settings.hosts_presets] + settings.hosts))
    cmds4exec = ( [ settings.SCRIPTS[S]
                    for S in settings.scripts if settings.get(S) ]
                  + settings.commands )
#    print("USERNAME:", settings.username); exit()
    tasks = AIOQS((run_client(host,
                              ["hostname -s"] + cmds4exec,
                              downloads=settings.downloads,
                              uploads=settings.uploads)
                   for host in hosts), limit=settings.limit)

    c=0
    sc=0
    async for t in tasks:
        res = t.result()
        if isinstance(res, Exception): pass #print(res)
        elif res is not None:
            c+=1
            if settings.output_format == "csv":
                print(*('"{}"'.format(r) for r in res), sep=";")
            else:
                print(*res)
    print('Total', c, 'results.', file=sys.stderr)
