import getpass
import gettext
import os
import sys
import time
from typing import List, Dict, Callable, Tuple

from .page_tag_prompt import PageTagPrompt, pages_action, tags_action
from .acm_api import AcmApi, SubmitStatus, Language, ProblemsPage, ProblemsTag
from .action import Action
from .settings import Settings
from .simple_progressbar import SimpleProgressBar

_ = gettext.gettext
_n = gettext.ngettext
double_sep = str(os.linesep + os.linesep)

QUERY_WAIT_TIME = 0.3

language_map = {
    'c': 'c11',
    'c++': 'c++14',
    'python': 'python 3',
    'python2': 'python 2.7',
    'python3': 'python 3',
}


class Actions(object):
    @classmethod
    def _get_actions_map(cls) -> Dict[Action, Callable[[AcmApi, Settings], None]]:
        return {
            Action.submit: submit_action,
            Action.problem: problem_action,
            Action.problem_submits: problem_submits_action,
            Action.problem_set: problem_set_action,
            Action.submit_source: submit_source_action,
            Action.languages: languages_action,
            Action.tags: tags_action,
            Action.pages: pages_action,
        }

    @classmethod
    def run(cls, api: AcmApi, settings: Settings) -> None:
        action_map = cls._get_actions_map()
        action_map[settings.action](api, settings)


def _convert_language(language: str, languages: List[Language]) -> str:
    # TODO(actics): move to api
    language = language.lower()
    if language in language_map:
        language = language_map[language]

    for compiler in languages:
        if language in compiler.description.lower():
            return compiler.id
    return None


def _get_status_string(status: SubmitStatus, delimiter: str= ' @ ') -> str:
    verdict_pattern = '[{s.verdict:^11}]'
    time_pattern = _('time:{s.runtime:^7}s')
    memory_pattern = _('memory:{s.memory:^9}KB')
    test_pattern = _('test:{s.test:^4}')
    info_pattern = _('info: {s.info}')

    verdict = verdict_pattern.format(s=status)
    string = verdict
    # if status.in_process:
    #    string = Fore.YELLOW + verdict + Style.RESET_ALL
    # elif status.accepted:
    #    string = Fore.GREEN + verdict + Style.RESET_ALL
    # else:
    #    string = Fore.RED + verdict + Style.RESET_ALL

    if status.runtime and status.memory:
        string += delimiter
        string += time_pattern.format(s=status)
        string += delimiter
        string += memory_pattern.format(s=status)

    if status.test:
        string += delimiter
        string += test_pattern.format(s=status)

    if status.info:
        string += delimiter
        string += info_pattern.format(s=status)

    return string


def _process_submit_status(api: AcmApi, bar: SimpleProgressBar, status_id: str) -> None:
    status = api.get_submit_status(status_id)
    status_str = _get_status_string(status)

    bar.clear()
    print(_('Submit of problem "{s.problem}" on language {s.language}. Submit id: {s.submit_id}').format(s=status))

    bar.update(status_str)
    while status.in_process:
        status = api.get_submit_status(status_id)
        status_str = _get_status_string(status)
        bar.update(status_str)
        if status.in_process:
            time.sleep(QUERY_WAIT_TIME)
    print()
    if status.compilation_error:
        error = api.get_compilation_error(status_id)
        print()
        print(_('Compilation error log:'), end=double_sep)
        print(error)


def submit_action(api: AcmApi, settings: Settings) -> None:
    bar = SimpleProgressBar()

    try:
        with open(settings.source_file, 'r') as source_file:
            source = source_file.read()
    except FileNotFoundError:
        # FIXME(actics): print
        raise

    languages = api.get_languages()
    lang = _convert_language(settings.language, languages)

    bar.update(_('Please wait. Your submit in process...'))
    try:
        status_id = api.submit(settings.judge_id, lang, settings.problem_number, source)
    except AcmApi:
        bar.update(_('Submit failed. Try again later.'))
        return

    _process_submit_status(api, bar, status_id)


def problem_action(api: AcmApi, settings: Settings) -> None:
    problem = api.get_problem(settings.problem_number)
    accepted = ''
    if problem.is_accepted is not None:
        accepted = '[✔] ' if problem.is_accepted else '[-] '
    print('{ac}{p.number}. {p.title}'.format(p=problem, ac=accepted), end=double_sep)
    print(_('Time limit: {p.time_limit}, Memory limit: {p.memory_limit}').format(p=problem))
    print(_('Source: '), end='')
    if problem.author and problem.source:
        print(_('{p.author} @ {p.source}').format(p=problem))
    elif problem.author:
        print(_('{p.author}').format(p=problem))
    elif problem.source:
        print(_('{p.source}').format(p=problem))
    if settings.show_tags:
        print(_('Tags: {0}').format(', '.join(problem.tags)))
    print(_('Difficulty: {p.difficulty}').format(p=problem), end=double_sep)
    print(problem.text, end=double_sep)
    print(_('### Input'), end=double_sep)
    print(problem.input, end=double_sep)
    print(_('### Output'), end=double_sep)
    print(problem.output, end=double_sep)
    print(_n('### Sample', '### Samples', len(problem.sample_inputs)), end=double_sep)
    for sample_input, sample_output in zip(problem.sample_inputs, problem.sample_outputs):
        print(_('-----> Input <----------------------------------------------------------------'))
        print(sample_input)
        print(_('-----> Output <---------------------------------------------------------------'))
        print(sample_output)


def problem_submits_action(api: AcmApi, settings: Settings) -> None:
    submits = api.get_problem_submits(settings.problem_number, settings.count)
    for submit in submits:
        print(_get_status_string(submit))


def _get_page_tag(api: AcmApi, settings: Settings) -> Tuple[ProblemsPage, ProblemsTag]:
    if settings.page_id is None and settings.tag_id is None:
        prompt = PageTagPrompt(api)
        try:
            prompt.cmdloop()
        except KeyboardInterrupt:
            print()
            sys.exit(0)
        return prompt.page, prompt.tag

    page, tag = None, None
    if settings.page_id is not None:
        try:
            page = api.get_page_by_id(settings.page_id)
        except ValueError:
            print(_('Unknown page name "{0}"').format(settings.page_id))
            sys.exit(1)
    if settings.tag_id is not None:
        try:
            tag = api.get_tag_by_id(settings.tag_id)
        except ValueError:
            print(_('Unknown tag name "{0}"').format(settings.tag_id))
            sys.exit(1)
    return page, tag


def problem_set_action(api: AcmApi, settings: Settings) -> None:
    page, tag = _get_page_tag(api, settings)

    problems = api.get_problem_set(page, tag, settings.sort, settings.show_ac)
    max_title_len = max([len(p.title) for p in problems]) + 2
    title_pattern = '{{p.title:<{0}}}'.format(max_title_len)
    for problem in problems:
        title = title_pattern.format(p=problem)
        accepted = ''
        if problem.is_accepted is not None:
            accepted = '✔' if problem.is_accepted else '-'
        difficulty = _('difficulty: {p.difficulty:<6}').format(p=problem)
        authors = _('authors: {p.rating_length}').format(p=problem)
        print('[{0:^3}] {1}. {2} {3} {4}'.format(accepted, problem.number, title, difficulty, authors))


def submit_source_action(api: AcmApi, settings: Settings) -> None:
    if settings.password is None:
        settings.password = getpass.getpass()
    api._password = settings.password
    source = api.get_submit_source(settings.submit_id)
    print(source)


def languages_action(api: AcmApi, settings: Settings=None) -> None:
    languages = api.get_languages()
    for language in languages:
        print(_('language {l.id}: {l.description}').format(l=language))
