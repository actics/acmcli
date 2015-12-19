import requests
from typing import List

from acm_api.acm_api import AcmApi, Problem, SubmitStatus
from .parsers import parse_languages, parse_submit_status, parse_problem, parse_problem_set, parse_submits_of


class TimusUrls:
    timus = 'http://acm.timus.ru'
    submit = 'http://acm.timus.ru/submit.aspx'
    auth = 'http://acm.timus.ru/auth.aspx'
    status = 'http://acm.timus.ru/status.aspx?count=&from={0}'
    error = 'http://acm.timus.ru/ce.aspx?id={0}'
    get_submit = 'http://acm.timus.ru/getsubmit.aspx/{0}.pas'
    problem = 'http://acm.timus.ru/problem.aspx?num={0}'
    problem_set = 'http://acm.timus.ru/problemset.aspx?page=all'
    submits_of = 'http://acm.timus.ru/status.aspx?author=me&count=1000&num={0}'


class TimusApi(AcmApi):
    def __init__(self, locale):
        self.locale = locale
        self.author_id = None
        self.session_id = None

    @property
    def _cookies(self):
        return {
            'Locale': self.locale,
            'AuthorID': self.author_id,
            'ASP.NET_SessionId': self.session_id,
        }

    def _get(self, url):
        response = requests.get(url, cookies=self._cookies)
        if self.session_id is None:
            self.session_id = response.cookies.get('ASP.NET_SessionId')
        return response

    def _post(self, url, payload):
        if self.session_id is None:
            response = self._get(TimusUrls.timus)
            self.session_id = response.cookies.get('ASP.NET_SessionId')
        return requests.post(url, payload, cookies=self._cookies, allow_redirects=False)

    def login(self, judge_id):
        payload = {
            'Action': 'login',
            'JudgeID': judge_id
        }

        response = self._post(TimusUrls.auth, payload)
        self.author_id = response.cookies.get('AuthorID')
        return self.author_id

    def get_languages(self):
        response = self._get(TimusUrls.submit)
        return parse_languages(response.content)

    def get_compilation_error(self, submit_id):
        url = TimusUrls.error.format(submit_id)
        response = self._get(url)

        # if compilation error is found, timus return a text/plain
        # else he return html page
        if response.headers['Content-Type'].startswith('text/html'):
            return ''

        return response.content

    def get_problem(self, number):
        problem_url = TimusUrls.problem.format(number)
        response = self._get(problem_url)
        return parse_problem(response.content)

    def get_submit_status(self, submit_id):
        response = self._get(TimusUrls.status.format(submit_id))
        return parse_submit_status(response.content)

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

        response = self._post(TimusUrls.submit, payload)
        if 'x-submitid' not in response.headers:
            return None

        return response.headers['x-submitid']

    def get_problem_set(self) -> List[Problem]:
        response = self._get(TimusUrls.problem_set)
        return parse_problem_set(response.content)

    def get_submits_of(self, problem_number) -> List[SubmitStatus]:
        response = self._get(TimusUrls.submits_of.format(problem_number))
        return parse_submits_of(response.content)
