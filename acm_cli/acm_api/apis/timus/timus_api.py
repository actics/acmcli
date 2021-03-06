import urllib.parse
import os.path
from enum import Enum
from typing import List, Dict, Union

import requests
import time

from . import parsers
from ...acm_api import AcmApi, AcmApiError, Problem, SubmitStatus, SortType, Language, ProblemsPage, ProblemsTag


_MAX_SUBMIT_ATTEMPTS_TIME = 15
_QUERY_WAIT_TIME = 0.3


class TimusApiError(AcmApiError):
    # TODO(actics): find a best way to create errors
    pass


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

    def set_query(self, query_params: Dict[str, Union[str, int]]) -> str:
        return self.url + '?' + urllib.parse.urlencode(query_params)


class TimusApi(AcmApi):
    def __init__(self, locale):
        self.locale = locale
        self._password = None
        self._judge_id = None
        self._session = requests.Session()
        self._session.cookies.set('Locale', locale)
        self._cached_pages = None
        self._cached_tags = None
        self._cached_languages = None

    def login(self, judge_id: str, password: str) -> None:
        self._judge_id = judge_id
        self._password = password
        payload = {
            'Action': 'login',
            'JudgeID': judge_id
        }

        self._session.post(TimusUrls.auth, payload, allow_redirects=False)

    def login_local(self, judge_id: str, password: str, auth_key: str) -> None:
        self._judge_id = judge_id
        self._password = password
        self._session.cookies.set('AuthorID', auth_key)

    def get_auth_key(self) -> str:
        return self._session.cookies['AuthorID']

    def get_compilation_error(self, submit_id: str) -> str:
        query = {'id': submit_id}
        url = TimusUrls.error.set_query(query)
        response = self._session.get(url)

        # if compilation error is found, timus return a text/plain
        # else he return html page
        if response.headers['Content-Type'].startswith('text/html'):
            return ''

        return response.content.decode('utf-8')

    def get_problem(self, number: int) -> Problem:
        query = {'num': number}
        url = TimusUrls.problem.set_query(query)
        response = self._session.get(url)
        return parsers.parse_problem(response.content)

    def get_submit_status(self, submit_id: str) -> SubmitStatus:
        query = {'count': 1, 'from': submit_id, 'author': 'me'}
        url = TimusUrls.status.set_query(query)
        response = self._session.get(url)
        return parsers.parse_submit_status(response.content)

    def submit(self, judge_id: str, language: str, problem_num: int, source: str) -> str:
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

        start_time = time.time()
        while (time.time() - start_time) < _MAX_SUBMIT_ATTEMPTS_TIME:
            response = self._session.post(TimusUrls.submit, payload, allow_redirects=False)
            if 'x-submitid' in response.headers:
                return response.headers['x-submitid']
            time.sleep(_QUERY_WAIT_TIME)

        raise TimusApiError('Can\'t submit problem in {0} seconds. Try again later', _MAX_SUBMIT_ATTEMPTS_TIME)

    def get_problem_set(self, page: ProblemsPage=None, tag: ProblemsTag=None, sort_type: SortType = SortType.id,
                        show_ac: bool = True) -> List[Problem]:
        if page is None:
            page = ProblemsPage('all', '')
        if tag is None:
            tag = ProblemsTag('', '')
        query = {'page': page.id, 'tag': tag.id, 'sort': sort_type.name, 'skipac': not show_ac}
        url = TimusUrls.problem_set.set_query(query)
        response = self._session.get(url)
        return parsers.parse_problem_set(response.content)

    def get_problem_submits(self, problem_number: int, count: int = 1000) -> List[SubmitStatus]:
        query = {'author': 'me', 'count': count, 'num': problem_number}
        url = TimusUrls.status.set_query(query)
        response = self._session.get(url)
        return parsers.parse_problem_submits(response.content)

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

    def get_languages(self) -> List[Language]:
        if self._cached_languages is not None:
            return self._cached_languages

        response = self._session.get(TimusUrls.submit)
        self._cached_languages = parsers.parse_languages(response.content)
        return self._cached_languages

    def get_tags(self) -> List[ProblemsTag]:
        if self._cached_tags is not None:
            return self._cached_tags

        response = self._session.get(TimusUrls.problem_set)
        self._cached_tags = parsers.parse_tags(response.content)
        return self._cached_tags


    def get_pages(self) -> List[ProblemsPage]:
        if self._cached_pages is not None:
            return self._cached_pages
        response = self._session.get(TimusUrls.problem_set)
        self._cached_pages = parsers.parse_pages(response.content)
        return self._cached_pages

    def get_tag_by_id(self, tag_id: str) -> ProblemsTag:
        tag_id = tag_id.lower()
        tags = self.get_tags()
        for tag in tags:
            if tag_id == tag.id:
                return tag
        raise ValueError('Timus don\'t have tag with id {0}'.format(tag_id))

    def get_page_by_id(self, page_id: str) -> ProblemsPage:
        page_id = page_id.lower()
        pages = self.get_pages()
        for page in pages:
            if page_id == page.id:
                return page
        raise ValueError('Timus don\'t have page with id {0}'.format(page_id))
