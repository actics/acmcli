# coding: utf-8

import locale
import ConfigParser
import argparse


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('problem_number', type=int)
    parser.add_argument('-a', '--action')
    parser.add_argument('-s', '--source')
    parser.add_argument('-j', '--judge-id')
    parser.add_argument('-l', '--language')
    parser.add_argument('-c', '--config')
    parser.add_argument('-v', '--version', action='version')
    parser.add_argument('--show-tags', action='store_const', const=True)
    parser.add_argument('--locale', choices=['en', 'ru'])
    return parser.parse_args()


class Config(object):
    _SECTION = 'sect'

    class FakeSectionFp(object):
        def __init__(self, fp):
            self.fp = fp
            self.section_name = '{0}\n'.format(self._SECTION)

        def readline(self):
            if self.section_name:
                try:
                    return self.section_name
                finally:
                    self.section_name = None
            else:
                return self.fp.readline()

    def __init__(self):
        self.judge_id = None
        self.language = 'c'
        self.locale = None
        self.show_tags = False
        self.default_source_file = '~/timus.code'

    @classmethod
    def read(cls, config_name):
        parser = ConfigParser.ConfigParser()
        try:
            with open(config_name, 'r') as fp:
                parser.readfp(cls.FakeSectionFp(fp))
        except IOError:
            pass

        config = cls()
        if parser.has_option(cls._SECTION, 'judge_id'):
            config.judge_id = parser.get(cls._SECTION, 'judge_id')
        if parser.has_option(cls._SECTION, 'language'):
            config.language = parser.get(cls._SECTION, 'language').lower()
        if parser.has_option(cls._SECTION, 'locale'):
            config.locale = parser.get(cls._SECTION, 'locale').lower()
        if parser.has_option(cls._SECTION, 'show_tags'):
            config.show_tags = parser.getboolean(cls._SECTION, 'show_tags')
        if parser.has_option(cls._SECTION, 'default_source_file'):
            config.default_source_file = parser.get(cls._SECTION, 'default_source_file')
        return config


class Settings(object):
    _CONFIG_NAME = '~/.config/timus.conf'

    def __init__(self):
        self.action = None
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
        settings.source = args.source if args.source is not None else config.default_source_file

        settings.convert_locale()

        return settings


