#!/usr/bin/env python

# NTFY API
# specification: https://docs.ntfy.sh/subscribe/api/

# original:
# https://github.com/iacchus/python-pushover-open-client/blob/main/src/python_pushover_open_client/__init__.py

import base64
import os
import pathlib
import shlex
import shutil
import sys
import types

import requests
import websocket

from importlib.metadata import PackageNotFoundError, version  # pragma: no cover


FUNCTION = types.FunctionType

DEBUG: bool = False
#  DEBUG: bool = True

if DEBUG:
    websocket.enableTrace(True)

# from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

# if sys.version_info[:2] >= (3, 8):
#    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
#    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
# else:
#    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "ntfy-client"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

PRIORITIES = {"urgent", "high", "default", "low", "min"}
YES_NO = {"yes", "no"}
ON_OFF = {"1", "0"}

FILE_RECEIVED_MESSAGE = "You received a file: {file_name}"

default_config_dict = {
    "title": "from ntfycli.py",
    "message": "defmsg",
    "priority": "default",
    "tags": [],
    "markdown": None,
    "delay": None,
    "actions": None,
    "click": None,
    "attach": None,
    "filename": None,
    "email": None,
    "call": None,

    "cache": None,
    "firebase": None,
    "unifiedpush": None,

    "authorization": None,
    "content_type": None
    }


# FIXME:
# Group mutually exclusive options (argparse docs)
# those are:
# * X-UnifiedPush vs X-Firebase
# * Authorization Basic vs Bearer
# * Authorization Username (envvar/arg) vs Bearer auth
# * Authorization Password (envvar/arg) vs Bearer
# * Authorization Token (envvar/arg) vs Basic auth
# * X-Attach vs X-File
# * X-Markdown vs Content-Type != "text/markdown"

# FIXME: UnifiedPush vs --file sending file as message

# TODO; sanitize parameters?

# TODO: CONFIG PRIORITY
# (first in this list has greater priority)
# 
# command-line arguments (user)
# environment variables (user, file or inline)
# ~/.notify-cli.conf (user, file)
# /etc/notify-cli.conf (system, file)
# (script, hardcoded defaults)


class NTFYClient:

    hostname: str
    topic: str
    token: str

    title: str
    message: str
    priority: str
    tags: list[str]  # ", ".join(tags)
    markdown: bool
    delay: str
    actions: list[str]  # "; ".join(actions)
    click: str
    attach: str
    filename: str
    email: str
    call: str

    cache: str
    firebase: str
    unifiedpush: str

    authorization: str | tuple[str, str]
    content_type: str

    def __init__(self, hostname, topic, token, args):
        self.hostname = hostname
        self.topic = topic
        self.token = token

        self.message = args.message or sys.stdin  # FIXME
        self.args = args  # FIXME: remove this: process it yourself

        self.url_https = f"https://{hostname}/{topic}"
        self.url_wss = f"wss://{hostname}/{topic}/ws"

        self.authorization = self.make_auth_token(method="basic")
        self.headers = self.make_headers(args)

    def pub(self, message=None):
        # FIXME: message above
        file_path = pathlib.Path(self.args.file)

        if file_path.is_file():
            self.headers.update({
                "X-Title": "File received (via ntfy)",
                "X-Message": FILE_RECEIVED_MESSAGE.format(file_name=self.args.filename
                                                          or file_path.name),
                "X-tags": "gift",
                "X-Filename": self.args.filename or file_path.name
                })
        elif self.args.file and not file_path.is_file():
            print(f"Error: file '{file_path.absolute()}' not found, exiting.")
            exit(1)

        data = open(file_path.absolute(), "rb") \
                if self.args.file else self.args.message

        response = requests.post(url=self.url_https,
                                 data=data,
                                 headers=self.headers)

        return response

    def make_headers(self, args):
        all_headers = {
                #  "X-Title": args.title or DEFAULT_MESSAGE_TITLE,
                "X-Title": args.title,
                "X-Icon": args.icon or None, #ICON_IMAGE_URL,
                "X-Priority": args.priority or None,
                "X-Tags": ",".join(args.tags if args.tags else []),
                "X-Markdown": args.markdown or None,
                "X-Delay": args.delay or None,
                "X-Actions": "; ".join(args.actions if args.actions else []),
                "X-Click": args.click or None,
                "X-Attach": args.attach,
                "X-Filename": args.filename or None,
                "X-Email": args.email or None,
                "X-Call": args.call or None,
                "X-Cache": args.cache or None,
                "X-Firebase": args.firebase or None,
                "X-UnifiedPush": args.unifiedpush or None,
                "X-Poll-ID": args.poll_id or None,
                "Authorization": self.authorization,
                "Content-Type": args.content_type or None,
                }

        headers = {key: value for key, value in all_headers.items() if value}
        #  print("all_headers", all_headers, end="\n\n")
        #  print("headers", headers, end="\n\n")

        return headers

    def make_auth_token(self, method="basic"):
        if method == "basic":
            auth_string = f":{self.token}"  # str: "empty_username:token"
            auth_string_bytes = auth_string.encode("ascii")
            auth_string_base64 = base64.b64encode(auth_string_bytes).decode("utf-8")

            authorization = f"Basic {auth_string_base64}"
        elif method == "query_param":
            # FIXME: deduplicate this code with the above
            auth_string = f":{self.token}"  # str: "empty_username:token"
            auth_string_bytes = auth_string.encode("ascii")
            auth_header_basic = \
                    base64.b64encode(auth_string_bytes).decode("utf-8")
            auth_string_base64 = base64.b64encode(auth_string_bytes).decode("utf-8")

            authorization = f"Basic {auth_string_base64}"
            auth_header_query_param_key = "auth"
            auth_header_query_param_value = \
                    base64.b64encode(auth_header_basic
                                     .encode("ascii")).decode("utf-8")
            authorization = (auth_header_query_param_key,
                             auth_header_query_param_value)
        else:
            authorization = f"Bearer {self.token}"

        return authorization

