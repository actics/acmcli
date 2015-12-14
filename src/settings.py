# coding: utf-8

import locale
import ConfigParser
import argparse

from timus_api import SubmitPayload


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
    class FakeSectionFp(object):
        def __init__(self, fp):
            self.fp = fp
            self.sechead = '[sect]\n'

        def readline(self):
            if self.sechead:
                try:
                    return self.sechead
                finally:
                    self.sechead = None
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
        with open(config_name, 'r') as fp:
            parser.readfp(cls.FakeSectionFp(fp))

        config = cls()
        if parser.has_option('sect', 'judge_id'):
            config.judge_id = parser.get('sect', 'judge_id')
        if parser.has_option('sect', 'language'):
            config.language = parser.get('sect', 'language').lower()
        if parser.has_option('sect', 'locale'):
            config.locale = parser.get('sect', 'locale').lower()
        if parser.has_option('sect', 'show_tags'):
            config.show_tags = parser.getboolean('sect', 'show_tags')
        if parser.has_option('sect', 'default_source_file'):
            config.default_source_file = parser.get('sect', 'default_source_file')
        return config


class Settings(object):
    _CONFIG_NAME = '~/.config/timus.conf'
    _language_map = {
        'c': 'gcc',
        'c++': 'g++',
        'python': 'python 2.7',
        'python2': 'python 2.7',
        'python3': 'python 3',
    }

    def __init__(self):
        self.action = None
        self.problem_number = ''
        self.judge_id = ''
        self.language = ''
        self.locale = ''
        self.show_tags = False
        self.source_file = ''
        self.languages = {}

    def _convert_locale(self):
        if self.locale is None:
            self.locale = locale.getdefaultlocale()[0]
        self.locale = 'Russian' if self.locale.lower().startswith('ru') else 'English'

    def _convert_language(self):
        lang = self.language.lower()
        if self._language_map.has_key(lang):
            lang = self._language_map[lang]

        for compiler in self.languages.iterkeys():
            if lang in compiler.lower():
                self.language = self.languages[compiler]
                return

        error_msg = 'Can\'t find compilers for language {0}. ' + \
            'You can use one of this names: {1}'
        names = reduce(lambda res, x: res + x + ', ', self.languages.iterkeys(), '')
        names = names[:-2]
        raise Exception(error_msg.format(lang, names))

    @classmethod
    def read(cls):
        args = _parse_args()
        # TODO(actics): set default config name in build
        config_name = args.config if args.config is not None else cls._CONFIG_NAME
        config = Config.read(config_name)

        settings = Settings()
        settings.action = args.action
        settings.problem_number = args.problem_number
        settings.judge_id = args.judge_id if args.judge_id is not None else config.judge_id
        settings.language = args.language if args.language is not None else config.language
        settings.locale = args.locale if args.locale is not None else config.locale
        settings.show_tags = args.show_tags if args.show_tags is not None else config.show_tags
        settings.source = args.source if args.source is not None else config.default_source_file

        settings.languages = SubmitPayload.get_languages()
        settings._convert_locale()
        settings._convert_language()
        return settings


