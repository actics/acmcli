#!/usr/bin/env python3

import json
import os

import colorama

from .actions import Actions
from .acm_api import AcmApi, TimusApi
from .settings import Settings


AUTH_KEYS_FILE = os.path.expanduser('~/.local/share/acmcli/author_ids.json')


def api_auth(api: AcmApi, settings: Settings) -> None:
    if settings.judge_id is None:
        return

    auth_keys_dir = os.path.dirname(AUTH_KEYS_FILE)
    if not os.path.exists(auth_keys_dir):
        os.makedirs(auth_keys_dir)

    try:
        with open(AUTH_KEYS_FILE, 'r') as json_file:
            auth_keys = json.loads(json_file.read())
    except FileNotFoundError:
        auth_keys = {}

    if settings.judge_id not in auth_keys:
        api.login(settings.judge_id, settings.password)

        auth_keys[settings.judge_id] = api.get_auth_key()

        with open(AUTH_KEYS_FILE, 'a') as json_file:
            json_file.write(json.dumps(auth_keys))
    else:
        api.login_local(settings.judge_id, settings.password, auth_keys[settings.judge_id])


def main() -> None:
    colorama.init()

    settings = Settings.read()
    api = TimusApi(settings.locale)

    api_auth(api, settings)

    Actions.run(api, settings)
