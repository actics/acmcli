#!/usr/bin/env python3
# coding=utf-8

import gettext
import json
import os
import time
from typing import List

import colorama

from settings import Settings
from acm_api import AcmApi, TimusApi, SubmitStatus
from simple_progressbar import SimpleProgressBar


_ = gettext.gettext
_n = gettext.ngettext
double_sep = str(os.linesep + os.linesep)

MAX_SUBMIT_ATTEMPTS_TIME = 15
QUERY_WAIT_TIME = 0.3
AUTHOR_ID_STORAGE_FILE = os.path.expanduser('~/.local/share/acmcli/author_ids.json')
language_map = {
    'c': 'gcc',
    'c++': 'g++',
    'python': 'python 2.7',
    'python2': 'python 2.7',
    'python3': 'python 3',
}


def set_api_author_id(api: AcmApi, judge_id: str) -> None:
    author_ids_dir = os.path.dirname(AUTHOR_ID_STORAGE_FILE)
    if not os.path.exists(author_ids_dir):
        os.makedirs(author_ids_dir)

    try:
        with open(AUTHOR_ID_STORAGE_FILE, 'r') as json_file:
                author_ids = json.loads(json_file.read())
    except FileNotFoundError:
        author_ids = {}

    if judge_id not in author_ids:
        author_ids[judge_id] = api.login(judge_id)

        with open(AUTHOR_ID_STORAGE_FILE, 'w') as json_file:
            json_file.write(json.dumps(author_ids))

    api.author_id = author_ids[judge_id]


def convert_language(language: str, languages: List[str]) -> str:
    lang = language.lower()
    if lang in language_map:
        lang = language_map[lang]

    for compiler in languages:
        if lang in compiler.lower():
            return languages[compiler]
    return None

error_msg = 'Can\'t find compilers for language {0}. ' + \
        'You can use one of this names: {1}'


def submit_action(api: AcmApi, settings: Settings) -> None:
    bar = SimpleProgressBar()

    try:
        with open(settings.source_file, 'r') as source_file:
            source = source_file.read()
    except FileNotFoundError:
        # FIXME(actics): print
        raise

    bar.update(_('Please wait. Your submit in process...'))
    status_id = submit(api, source, settings)

    if status_id is None:
        bar.update(_('Submit failed. Try again later.'))
        return

    process_submit_status(api, bar, status_id)


def submit(api: AcmApi, source: str, settings: Settings) -> SubmitStatus:
    languages = api.get_languages()
    lang = convert_language(settings.language, languages)

    start_time = time.time()
    while (time.time() - start_time) < MAX_SUBMIT_ATTEMPTS_TIME:
        status_id = api.submit(settings.judge_id, lang, settings.problem_number, source)
        if status_id is not None:
            return status_id
        time.sleep(QUERY_WAIT_TIME)

    return None


def process_submit_status(api: AcmApi, bar: SimpleProgressBar, status_id: str) -> None:
    status = api.get_submit_status(status_id)

    bar.clear()
    print(_('Submit of problem "{s.problem}" on language {s.language}. Submit id: {s.submit_id}').format(s=status))

    bar.update_status(status)
    while status.in_process:
        status = api.get_submit_status(status_id)
        bar.update_status(status)
        if status.in_process:
            time.sleep(QUERY_WAIT_TIME)
    print()
    if status.compilation_error:
        error = api.get_compilation_error(status_id)
        print()
        print(_('Compilation error log:'), end=double_sep)
        print(error.decode('utf-8'))


def problem_action(api: AcmApi, settings: Settings) -> None:
    problem = api.get_problem(settings.problem_number)
    accepted = ''
    if problem.is_accepted is not None:
        accepted = '[✔] ' if problem.is_accepted else '[-] '
    print('{ac}{p.title}'.format(p=problem, ac=accepted), end=double_sep)
    print(_('Time limit: {p.time_limit}, Memory limit: {p.memory_limit}').format(p=problem))
    if problem.author:
        print(_('Author: {p.author}').format(p=problem), end='')
    if problem.source:
        print(_('Source: {p.source}').format(p=problem), end='')
    if problem.author or problem.source:
        print()
    if settings.show_tags:
        print(_('Tags: {0}').format(', '.join(problem.tags)))
    print(_('Difficulty: {p.difficulty}').format(p=problem), end=double_sep)
    print(problem.text, end=double_sep)
    print(_('### Input'), end=double_sep)
    print(problem.input, end=double_sep)
    print(_('### Output'), end=double_sep)
    print(problem.output, end=double_sep)
    print(_n('### Sample', '### Samples', len(problem.sample_input)), end=double_sep)
    for sample_input, sample_output in zip(problem.sample_inputs, problem.sample_outputs):
        print(_('-----> Input <---------------------------------------------------------'))
        print(sample_input)
        print(_('-----> Output <--------------------------------------------------------'))
        print(sample_output)


def language_action(api: AcmApi, settings: Settings) -> None:
    languages = api.get_languages()
    for language in sorted(languages):
        print(language)


def main() -> None:
    colorama.init()
    settings = Settings.read()
    api = TimusApi(settings.locale)

    if settings.judge_id is not None:
        set_api_author_id(api, settings.judge_id)

    if settings.action == 'submit':
        submit_action(api, settings)
    elif settings.action == 'problem':
        problem_action(api, settings)
    elif settings.action == 'languages':
        language_action(api, settings)


if __name__ == '__main__':
    main()
