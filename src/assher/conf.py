import os, sys
from argparse import ArgumentParser, Namespace
from os.path import expanduser
from getpass import getuser
#from . import settings


settings = Namespace(SCRIPTS={}, HOSTS={})

def read_settings(config_file_path):
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
            settings.__dict__.update(
                {k:v for k,v in d.items()
                 if k in settings.__dict__ and not k in ("SCRIPTS", "HOSTS")}
            )
            # Update HOSTS and SCRIPTS from config file, instead of replacement
            settings.HOSTS.update(d.get("HOSTS",{}))
            settings.SCRIPTS.update(d.get("SCRIPTS",{}))
    except Exception as e:
        print("Configuration file", config_file_path, "is wrong formated", e)

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
params.add_argument("--downdir", nargs='?', default="/tmp",
                    help="Root directory for downloading files from remote hosts. Actual files will be put in per host subdirectories of that directory.")
params.add_argument('-F', "--output-format", default="asis",
                    choices=["asis", "csv"],
                    help="Sets output format")
params.add_argument('-f', "--config-file",
                    default=expanduser("./.arss.conf"),
                    help="Path to config file to get values from.")
params.add_argument('-H', "--hosts-presets", type=str, nargs="+",
                    choices=settings.HOSTS,
                    default=[],
                    help="List of target hosts by preset name")
params.add_argument("--hosts", nargs="+", metavar='T', default=[],
                    help="List of target hosts by hostname")
params.add_argument('-i', "--privkey", metavar="PK", nargs='+',
                    default=[expanduser("~/.ssh/id_rsa")],
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
params.add_argument("--updir", nargs='?', default="/tmp",
                    help="Path on remote host to upload selected files")

params.parse_args([], settings)
if os.access(settings.config_file, os.R_OK):
    read_settings(settings.config_file)
    if settings.debug >= 3:
        print("SETTINGS:", *settings, file=sys.stderr)
        quit()
