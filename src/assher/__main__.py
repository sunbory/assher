#!/bin/env python3
#encoding: utf8

import os, sys, asyncio
from getpass import getuser, getpass
from argparse import ArgumentParser, Namespace
from . import Assher


settings = Namespace(SCRIPTS={}, HOSTS={})
params = ArgumentParser(description="Run commands through list of hosts and collect results asynchronously")
params.add_argument('-S', "--scripts", nargs='+',
                    choices=settings.SCRIPTS,
                    default=[],
                    help="Command by preset name to execute on remote host")
params.add_argument('-c', "--commands", metavar="CMD", nargs='+', default=[],
                    help="Command to execute on remote host")
params.add_argument('-D', "--debug", action="count", default=0,
                    help="Debug level")
params.add_argument('-d', "--downloads", nargs='+', metavar="DL", default=[],
                    help="List of absolute paths to download from remote hosts.")
params.add_argument("--download-dir", nargs='?', default="/tmp",
                    help="Root directory for downloading files from remote hosts. Actual files will be put in per host subdirectories of that directory.")
params.add_argument('-F', "--output-format", default="asis",
                    choices=["asis", "csv"],
                    help="Sets output format")
params.add_argument('-f', "--config-file",
                    default="assher.conf",
                    help="Path to config file to get values from.")
params.add_argument('-H', "--hosts-presets", type=str, nargs="+",
                    choices=settings.HOSTS,
                    default=[],
                    help="List of target hosts by preset name")
params.add_argument("--hosts", nargs="+", metavar='T', default=[],
                    help="List of target hosts by hostname")
params.add_argument('-i', "--privkey", metavar="PK", nargs='+',
                    default=[os.path.expanduser("~/.ssh/id_rsa")],
                    help="Path to SSH private key to use for connetions. It is possible to set several keys.")
params.add_argument('-L', "--limit", type=int, default=10, metavar='N',
                    help="Sets number of workers. Missing option or 0 means unlimited. BUT UNLIMITED EXECUTION NOT YET SUPPORTED, IT HANGS!")
params.add_argument('-p', "--proxy", nargs="+",
                    help="List of routers to proxy connections through.")
params.add_argument('-P', "--password", nargs='?',
                    help="Password for remote ssh connections. If special value \"-\" used, password will be prompted from stdandard input.")
params.add_argument('-U', "--username", nargs='?', default=getuser(),
                    help="Username to use for login to remote hosts. By defautl username of calling user.")
params.add_argument('-u', "--uploads", nargs='+', metavar="UL", default=[],
                    help="List of files to upload.")
params.add_argument("--upload-dir", nargs='?', default="/tmp",
                    help="Path on remote host to upload selected files")

# Set defaults
params.parse_args([],settings)


def iter_concat(*args):
    generator = type((i for i in range(1)))
    for x in args:
        if type(x) is str: yield x
        elif type(x) in (list,tuple, generator):
            for y in x: yield y
        else: raise TypeError


def read_conf_file(config_file_path, ns):
    gns = {
        "__builtins__":{k:v for k,v in __builtins__.items()
                        if k not in ("compile",
                                     "open",
                                     "exec",
                                     "eval",
                                     "quit",
                                     "exit")}
        }
    try:
        with open(config_file_path, 'r') as cf:
            d=eval("{{{}}}".format(cf.read().strip()), gns)
            print(*d)
            ns.__dict__.update(
                {k:v for k,v in d.items()
                 if k in settings.__dict__ and not k in ("SCRIPTS", "HOSTS")}
            )
            # Update HOSTS and SCRIPTS from config file, instead of replacement
            ns.HOSTS.update(d.get("HOSTS",{}))
            ns.SCRIPTS.update(d.get("SCRIPTS",{}))
    except Exception as e:
        print("Configuration file", config_file_path, "is wrong formated", e)


async def main():
    cmdline_arguments = params.parse_args()
    # Updating settings from command line making it prefered over config file
    if os.access(cmdline_arguments.config_file, os.R_OK):
        read_conf_file(arguments.config_file, settings)
    elif cmdline_arguments.config_file != settings.config_file:
        print("No such file or directory:", cmdline_arguments.config_file,
              file=sys.stderr)
        exit(1)

    settings.__dict__.update({k:v for k,v in cmdline_arguments.__dict__.items()
                              if not params.get_default(k) == v})
    
    if settings.downloads or settings.uploads or settings.proxy:
        print('Some of used options not implemented yet!', file=sys.stderr)
        exit()
    
    try:
        if settings.password == '-': settings.password = getpass("Password: ")
    except (EOFError, KeyboardInterrupt):
        print()
        exit(1)
    
    assher = Assher(
        hosts=iter_concat(*(
            [ settings.HOSTS.get(hp, [])
              for hp in settings.hosts_presets]
            + settings.hosts)),
        username=settings.username,
        password=settings.password,
        privkeys=settings.privkey,
        commands=([ settings.SCRIPTS[S]
                    for S in settings.scripts if settings.get(S) ]
                  + settings.commands),
        download_dir=settings.download_dir,
        downloads=settings.downloads,
        upload_dir=settings.upload_dir,
        uploads=settings.uploads,
        limit=50)

    c=0
    async for t in assher:
        res = t.result()
        if isinstance(res, Exception): pass
        elif res is not None:
            c+=1
            if settings.output_format == "csv":
                print(*('"{}"'.format(r) for r in res), sep=";")
            else:
                print(*res)
    print('Total', c, 'results.', file=sys.stderr)


asyncio.get_event_loop().run_until_complete(main())
