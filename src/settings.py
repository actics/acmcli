# coding: utf-8

import os
import locale
import configparser
import argparse


_SECTION = 'section'
_DEFAULT_SOURCE_FILE = '~/timus.code'


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('problem_number', type=int)
    parser.add_argument('-a', '--action', default='submit')
    parser.add_argument('-s', '--source-file')
    parser.add_argument('-j', '--judge-id')
    parser.add_argument('-l', '--language')
    parser.add_argument('-c', '--config')
    parser.add_argument('-v', '--version', action='version')
    parser.add_argument('--show-tags', action='store_const', const=True)
    parser.add_argument('--locale', choices=['en', 'ru'])
    return parser.parse_args()


class Config(object):
    def __init__(self):
        self.judge_id = None
        self.language = 'c'
        self.locale = None
        self.show_tags = False
        self.default_source_file = os.path.expanduser('~/timus.code')

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
        if parser.has_option(_SECTION, 'show_tags'):
            config.show_tags = parser.getboolean(_SECTION, 'show_tags')
        if parser.has_option(_SECTION, 'default_source_file'):
            config.default_source_file = parser.get(_SECTION, 'default_source_file')
        return config


class Settings(object):
    _CONFIG_NAME = '~/.config/timus.conf'

    def __init__(self):
        self.action = ''
        self.problem_number = ''
        self.judge_id = ''
        self.author_id = ''
        self.language = ''
        self.locale = ''
        self.show_tags = False
        self.source_file = ''

    def convert_locale(self):
        if self.locale is None:
            self.locale = locale.getdefaultlocale()[0]
        self.locale = 'Russian' if self.locale.lower().startswith('ru') else 'English'

    @classmethod
    def read(cls):
        args = _parse_args()
        # TODO(actics): set default config name in build
        config_name = args.config if args.config is not None else cls._CONFIG_NAME
        config = Config.read(config_name)

        settings = Settings()
        settings.action = args.action.lower()
        settings.problem_number = args.problem_number
        settings.judge_id = args.judge_id if args.judge_id is not None else config.judge_id
        settings.language = args.language if args.language is not None else config.language
        settings.locale = args.locale if args.locale is not None else config.locale
        settings.show_tags = args.show_tags if args.show_tags is not None else config.show_tags
        settings.source_file = args.source_file if args.source_file is not None else config.default_source_file
        settings.source_file = os.path.expanduser(settings.source_file)

        settings.convert_locale()

        return settings


