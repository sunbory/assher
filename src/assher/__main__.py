#!/bin/env python3
# encoding: utf8

import os, sys
from getpass import getpass
from . import *
from .conf import params, settings

params.parse_args(namespace=settings)
if settings.downloads or settings.uploads or settings.proxy:
    print('Some of used options not implemented yet!', file=sys.stderr)
    exit()
    
try:
    if settings.password == '-': settings.password = getpass("Password: ")
except (EOFError, KeyboardInterrupt):
    print()
    exit(1)
    
if settings.debug >= 3:
    for i in settings._get_args():
        print(i)
    for i in settings._get_kwargs():
        print(i[0]+':\t', *i[1:])
    sys.exit(0)
asyncio.get_event_loop().run_until_complete(main())
