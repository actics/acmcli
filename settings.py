# coding: utf-8

import locale
import ConfigParser

from timus_api import SubmitPayload

submit_payload = {
    'Action': 'submit',
    'SpaceID': '1',
    'JudgeID': '103946PD',
    'Language': 9,
    'ProblemNum': 1001,
    'Source': None,
    'SourceFile': ''
}

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
        self.judje_id = ''
        self.language = ''
        self.locale = ''
        self.show_tags = True
        self.default_source_file = '~/timus.code'

    @classmethod
    def read(cls, config_name):
        parser = ConfigParser.ConfigParser()
        with open(config_name, 'r') as fp:
            parser.readfp(FakeSectionFp(fp))

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


class CmdParams(object):
    def __init__(self):
        self.action = None
        self.problem_number = ''
        self.source_file = ''
        self.judje_id = ''
        self.language = ''
        self.locale = ''
        self.show_tags = None
        self.config_name = ''

    @classmethod
    def read(cls):
        params = CmdParams()
        return params


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
        self.judje_id = ''
        self.language = ''
        self.locale = ''
        self.show_tags = True
        self.source_file = ''
        self.languages = {}

    @classmethod
    def _convert_locale(cls, config_locale):
        if config_locale.lower() == 'ru':
            return 'Russian'
        elif config_locale.lower() == 'en'
            return 'English'
        else:
            lang_code = locale.getdefaultlocale()[0]
            if lang_code is not None and lang_code == 'ru_RU':
                return 'Russian'
            else:
                return 'English'

    @classmethod
    def _convert_language(cls, language, compilers):
        lang = language.lower()
        if cls._language_map.has_key(lang):
            lang = cls._language_map[lang]

        for compiler in compilers.iterkey():
            if lang in compiler.lower():
                return compilers[compiler]

        error_msg = 'Can\'t find compilers for language {0}. ' + \
            'You can use one of this names: {1}'
        names = reduce(lambda res, x: res + x + ', ', config.languages.iterkeys(), '')
        names = names[:-2]
        raise Exception(error_msg.format(config.language, names))

    @classmethod
    def read(cls):
        params = CmdParams.read()
        # TODO(actics): set default config name in build
        config_name = params.config_name if params.config_name else cls._CONFIG_NAME
        config = Config.read(config_file)

        settings = Settings()
        settings.action = params.action
        settings.problem_number = params.problem_number
        settings.languages = SubmitPayload.get_languages())
        settings.judge_id = params.judge_id if params.judge_id else config.judge_id
        settings.language = params.language if params.language else config.language
        settings.language = cls._convert_language(setting.language, settings.languages)
        settings.locale = params.locale if params.locale else config.locale
        settings.locale = cls._convert_locale(settings.locale)
        settings.show_tags = params.show_tags if params.show_tags is not None
        settings.show_tags = config.show_tags if params.show_tags is None
        settings.source_file = params.source_file if params.source_file
        settings.source_file = config.default_source_file if not params.source_file

        return settings


