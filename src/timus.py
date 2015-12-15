#!/usr/bin/env python2.7
# coding: utf-8

from __future__ import print_function
import time
import os
import os.path
import json

from settings import Settings
from timus_api import TimusApi


MAX_SUBMIT_ATTEMPTS_TIME = 15
AUTHOR_ID_STORAGE_FILE = '~/.local/share/timus/author_ids.json'
language_map = {
    'c': 'gcc',
    'c++': 'g++',
    'python': 'python 2.7',
    'python2': 'python 2.7',
    'python3': 'python 3',
}


def set_api_author_id(api, judge_id):
    author_ids_dir = os.path.dirname(AUTHOR_ID_STORAGE_FILE)
    if not os.path.exists(author_ids_dir):
        os.makedirs(author_ids_dir)

    with open(AUTHOR_ID_STORAGE_FILE, 'r') as json_file:
        try:
            author_ids = json.loads(json_file.readall())
        except ValueError:
            author_ids = {}

    if not author_ids.has_key(judge_id):
        author_ids[judge_id] = api.login(judge_id)

        with open(AUTHOR_ID_STORAGE_FILE, 'w') as json_file:
            json_file.write(json.dumps(author_ids))

    api.author_id = author_ids[judge_id]


def convert_language(language, languages):
    lang = language.lower()
    if language_map.has_key(lang):
        lang = language_map[lang]

    for compiler in languages.iterkeys():
        if lang in compiler.lower():
            return languages[compiler]
    return None

error_msg = 'Can\'t find compilers for language {0}. ' + \
        'You can use one of this names: {1}'


def submit(api, settings):
    languages = api.get_languages()
    lang = convert_language(settings.language, languages)

    start_time = time.time()
    while (time.time() - start_time) < MAX_SUBMIT_ATTEMPTS_TIME:
        status_id = api.submit(settings.judge_id, lang, settings.problem_number, settings.source)
        if status_id is not None:
            return status_id
        print('Wait...')
        time.sleep(0.5)
    return None


def process_submit_status(api, status_id):
    status = api.get_submit_status(status_id)
    print(status.verdict)
    while status.in_process:
        status = api.get_submit_status(status_id)
        print(status.verdict)


def main():
    settings = Settings.read()
    api = TimusApi(settings.locale)

    if settings.judge_id is not None:
        set_api_author_id(api, settings.judge_id)

    if settings.action is None:
        status_id = submit(api, settings)
        process_submit_status(api, status_id)
    elif settings.action == 'problem':
        problem = api.get_problem(settings.problem_number)
        print(problem.title)
    elif settings.action == 'languages':
        languages = api.get_languages().keys()
        languages.sort()
        for language in languages:
            print(language)


if __name__ == '__main__':
    main()
