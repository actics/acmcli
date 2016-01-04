import os
import locale
import configparser
import argparse

from .acm_api import SortType
from .action import Action

_SECTION = 'section'
_DEFAULT_SOURCE_FILE = os.path.expanduser('~/acmcli.code')
_CONFIG_NAME = os.path.expanduser('~/.config/acmcli.conf')


def _parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action', help='sub-command help')

    parser.add_argument('-v', '--version', action='version')
    parser.add_argument('-l', '--locale', choices=['en', 'ru'])
    parser.add_argument('-c', '--config')

    submit_parser = subparsers.add_parser(Action.submit.value, help='submit solution for problem')
    submit_parser.add_argument('problem_number', type=int)
    submit_parser.add_argument('-s', '--source-file')
    submit_parser.add_argument('-j', '--judge-id')
    submit_parser.add_argument('-l', '--language')

    problem_parser = subparsers.add_parser(Action.problem.value, help='get problem info')
    problem_parser.add_argument('problem_number', type=int)
    problem_parser.add_argument('-j', '--judge-id')
    problem_parser.add_argument('--show-tags', action='store_const', const=True, help='show problem tags')

    problem_parser = subparsers.add_parser(Action.problem_submits.value, help='get list of problem submits')
    problem_parser.add_argument('problem_number', type=int)
    problem_parser.add_argument('-j', '--judge-id')
    problem_parser.add_argument('-c', '--count', type=int)

    problem_set_parser = subparsers.add_parser(Action.problem_set.value, help='get problem set')
    problem_set_parser.add_argument('-p', '--page')
    problem_set_parser.add_argument('-t', '--tag')
    problem_set_parser.add_argument('-s', '--sort', type=SortType)
    problem_set_parser.add_argument('-j', '--judge-id')
    problem_set_parser.add_argument('--show-ac', action='store_const', const=True, help='show solved problems')

    submit_source_parser = subparsers.add_parser(Action.submit_source.value, help='get submit source code')
    submit_source_parser.add_argument('submit_id', type=int)
    submit_source_parser.add_argument('-j', '--judge-id')

    subparsers.add_parser(Action.languages.value, help='get languages list')
    subparsers.add_parser(Action.tags.value, help='get tags list')
    subparsers.add_parser(Action.pages.value, help='get pages list')

    return parser.parse_args()


class Config(object):
    def __init__(self):
        self.judge_id = None
        self.language = 'c'
        self.locale = None
        self.password = None
        self.show_tags = False
        self.show_ac = True
        self.submits_count = 1000
        self.default_source_file = os.path.expanduser(_DEFAULT_SOURCE_FILE)

    @classmethod
    def read(cls, config_name):
        parser = configparser.ConfigParser()
        try:
            with open(config_name, 'r') as config_file:
                config_text = '[{0}]\n{1}'.format(_SECTION, config_file.read())
                parser.read_string(config_text)
        except FileNotFoundError:
            # FIXME(actics): print
            pass

        config = cls()
        if parser.has_option(_SECTION, 'judge_id'):
            config.judge_id = parser.get(_SECTION, 'judge_id')
        if parser.has_option(_SECTION, 'language'):
            config.language = parser.get(_SECTION, 'language').lower()
        if parser.has_option(_SECTION, 'locale'):
            config.locale = parser.get(_SECTION, 'locale').lower()
        if parser.has_option(_SECTION, 'password'):
            config.locale = parser.get(_SECTION, 'password').lower()
        if parser.has_option(_SECTION, 'show_tags'):
            config.show_tags = parser.getboolean(_SECTION, 'show_tags')
        if parser.has_option(_SECTION, 'show_ac'):
            config.show_ac = parser.getboolean(_SECTION, 'show_ac')
        if parser.has_option(_SECTION, 'submits_count'):
            config.show_ac = parser.getint(_SECTION, 'submits_count')
        if parser.has_option(_SECTION, 'default_source_file'):
            config.default_source_file = parser.get(_SECTION, 'default_source_file')
        return config


class Settings(object):
    def __init__(self):
        self.action = ''
        self.problem_number = ''
        self.judge_id = None
        self.author_id = ''
        self.language = ''
        self.locale = ''
        self.submit_id = ''
        self.password = ''
        self.show_tags = False
        self.show_ac = True
        self.sort = None
        self.tag_id = None
        self.page_id = None
        self.count = None
        self.source_file = ''

    def convert_locale(self):
        if self.locale is None:
            self.locale = locale.getdefaultlocale()[0]
        self.locale = 'Russian' if self.locale.lower().startswith('ru') else 'English'

    @classmethod
    def read(cls):
        args = _parse_args()
        # TODO(actics): set default config name in build
        config_name = args.config if args.config is not None else _CONFIG_NAME
        config = Config.read(config_name)

        settings = Settings()
        settings.action = Action(args.action)

        if settings.action == Action.submit:
            settings.problem_number = args.problem_number
            settings.judge_id = args.judge_id if args.judge_id is not None else config.judge_id
            settings.language = args.language if args.language is not None else config.language
            settings.source_file = args.source_file if args.source_file is not None else config.default_source_file
            settings.source_file = os.path.expanduser(settings.source_file)

        if settings.action == Action.problem:
            settings.problem_number = args.problem_number
            settings.judge_id = args.judge_id if args.judge_id is not None else config.judge_id
            settings.show_tags = args.show_tags if args.show_tags is not None else config.show_tags

        if settings.action == Action.problem_submits:
            settings.problem_number = args.problem_number
            settings.judge_id = args.judge_id if args.judge_id is not None else config.judge_id
            settings.count = args.count if args.count is not None else config.submits_count

        if settings.action == Action.problem_set:
            settings.page_id = args.page
            settings.tag_id = args.tag
            settings.sort = args.sort if args.sort is not None else SortType.id
            settings.judge_id = args.judge_id if args.judge_id is not None else config.judge_id
            settings.show_ac = args.show_ac if args.show_ac is not None else config.show_ac

        if settings.action == Action.submit_source:
            settings.submit_id = args.submit_id
            settings.judge_id = args.judge_id if args.judge_id is not None else config.judge_id

        settings.password = config.password
        settings.locale = args.locale if args.locale is not None else config.locale
        settings.convert_locale()

        return settings
