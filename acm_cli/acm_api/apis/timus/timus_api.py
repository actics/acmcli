import urllib.parse
from enum import Enum
from typing import List, Dict, Tuple

import requests

from . import parsers
from ...acm_api import AcmApi, Problem, SubmitStatus, SortType


class TimusUrls(Enum):
    timus = 'http://acm.timus.ru'
    submit = 'http://acm.timus.ru/submit.aspx'
    auth = 'http://acm.timus.ru/auth.aspx'
    status = 'http://acm.timus.ru/status.aspx'
    error = 'http://acm.timus.ru/ce.aspx'
    get_submit = 'http://acm.timus.ru/getsubmit.aspx'
    problem = 'http://acm.timus.ru/problem.aspx'
    problem_set = 'http://acm.timus.ru/problemset.aspx'

    def __init__(self, url):
        self.url = url

    def __str__(self):
        return self.url

    def set_query(self, query_params: Dict[str, str]) -> str:
        return self.url + '?' + urllib.parse.urlencode(query_params)


class TimusApi(AcmApi):
    def __init__(self, locale):
        self.locale = locale
        self._password = None
        self._judge_id = None
        self._session = requests.Session()
        self._session.cookies.set('Locale', locale)

    def login(self, judge_id, password):
        self._judge_id = judge_id
        self._password = password
        payload = {
            'Action': 'login',
            'JudgeID': judge_id
        }

        self._session.post(TimusUrls.auth, payload, allow_redirects=False)

    def login_local(self, judge_id, password, auth_key):
        self._judge_id = judge_id
        self._password = password
        self._session.cookies.set('AuthorID', auth_key)

    def get_auth_key(self) -> str:
        return self._session.cookies['AuthorID']

    def get_languages(self):
        response = self._session.get(TimusUrls.submit)
        return parsers.parse_languages(response.content)

    def get_compilation_error(self, submit_id):
        query = {'id': submit_id}
        url = TimusUrls.error.set_query(query)
        response = self._session.get(url)

        # if compilation error is found, timus return a text/plain
        # else he return html page
        if response.headers['Content-Type'].startswith('text/html'):
            return ''

        return response.content.decode('utf-8')

    def get_problem(self, number):
        query = {'num': number}
        url = TimusUrls.problem.set_query(query)
        response = self._session.get(url)
        return parsers.parse_problem(response.content)

    def get_submit_status(self, submit_id):
        query = {'count': 1, 'from': submit_id, 'author': 'me'}
        url = TimusUrls.status.set_query(query)
        response = self._session.get(url)
        return parsers.parse_submit_status(response.content)

    def submit(self, judge_id, language, problem_num, source):
        # The break between submissions must be at least 10 seconds
        # if we spend more than once at 10 seconds, Timus return a submit
        # page with error string
        payload = {
            'Action': 'submit',
            'SpaceID': 1,
            'JudgeID': judge_id,
            'Language': language,
            'ProblemNum': problem_num,
            'Source': source,
        }

        response = self._session.post(TimusUrls.submit, payload, allow_redirects=False)
        if 'x-submitid' not in response.headers:
            return None

        return response.headers['x-submitid']

    def get_problem_set(self, page: str = 'all', tag: str = None, sort_type: SortType = SortType.id,
                        show_ac: bool = True) -> List[Problem]:
        query = {'page': page, 'sort': sort_type.name, 'skipac': not show_ac, 'tag': tag}
        url = TimusUrls.problem_set.set_query(query)
        response = self._session.get(url)
        return parsers.parse_problem_set(response.content)

    def get_submit_source(self, submit_id: str) -> str:
        status = self.get_submit_status(submit_id)
        payload = {
            'Action': 'getsubmit',
            'JudgeID': self._judge_id,
            'Password': self._password
        }
        url = TimusUrls.get_submit.value + '/' + status.source_file
        response = self._session.post(url, payload)

        # if source code is found, timus return a text/plain
        # else he return html page
        if response.headers['Content-Type'].startswith('text/html'):
            # TODO(actics): raise exception
            return ''

        return response.content.decode('utf-8')

    def get_tags(self) -> List[Tuple[str, str]]:
        response = self._session.get(TimusUrls.problem_set)
        return parsers.parse_tags(response.content)

    def get_pages(self) -> List[Tuple[str, str]]:
        response = self._session.get(TimusUrls.problem_set)
        return parsers.parse_pages(response.content)

    def get_problem_submits(self, problem_number: int, count: int = 1000) -> List[SubmitStatus]:
        query = {'author': 'me', 'count': count, 'num': problem_number}
        url = TimusUrls.status.set_query(query)
        response = self._session.get(url)
        return parsers.parse_problem_submits(response.content)
