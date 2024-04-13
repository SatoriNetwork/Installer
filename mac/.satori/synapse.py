
# must include and compile all the packages requied by the internal script
import typing as t
import os
import json
import hashlib
import traceback
import asyncio
import socket
import requests  # ==2.31.0
import aiohttp  # ==3.8.4

# # standard library imports -
# # in case our future script needs to utilize more functionality without
# # recompiling which necesitates the need for re-download and reinstall.
import argparse
# import asyncio
import collections
import contextlib
import copy
import ctypes
import datetime as dt
import dataclasses
import email.mime.multipart
import email.mime.text
import enum
import encodings
import functools
# import hashlib
import http.client
import http.server
import importlib
import itertools
# import json
import logging
import math
import multiprocessing
import multiprocessing.pool
# import os
import pathlib
import pickle
import queue
import random
import re
import select
import signal
# import socket
import sqlite3
import subprocess
import sys
import threading
import timeit
import uuid
import urllib
import urllib.error
import urllib.parse
import urllib.request
import xml


def generateHash(inputStr: str) -> str:
    '''
    Generates a SHA-256 hash for the given string.
    hashlib requires bytes-like object.
    '''
    return hashlib.sha256(inputStr.encode('utf-8')).hexdigest()


def runSynapse(installDir: str):
    p2pScript = os.path.join(installDir, 'scripts', 'p2p.py')
    if not os.path.isfile(p2pScript):
        print(f'File not found: {p2pScript}')
        return
    with open(p2pScript, 'r') as file:
        script = file.read()
    r = requests.get('https://satorinet.io/verify/scripthash')
    if r.status_code == 200:
        hashes = r.json()
        if generateHash(script) in hashes:
            try:
                namespace = {}
                exec(script, namespace)
            except Exception as e:
                print(f'An error occurred while executing the code: {e}')
                traceback.print_exc()
    else:
        print('Satori Network unreachable, check internet connection and restart. '
              'Proceeding without p2p functionality.')
