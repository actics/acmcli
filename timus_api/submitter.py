# coding: utf-8

import time

import requests
import lxml.html


class SubmitStatus(object):
    _status_url_pattern = 'http://acm.timus.ru/status.aspx?count=&from={0}'
    _error_url_pattern = 'http://acm.timus.ru/ce.aspx?id={0}'

    _processing_verdicts = ['Compiling', 'Running', 'Waiting']
    _accepted_verdict = 'Accepted'
    _wrong_answer_verdict = 'Wrong answer'
    _compilation_error_verdict = 'Compilation error'

    def __init__(self, submit_id, author_id, session_id):
        self._author_id = author_id
        self._session_id = session_id
        self._compilation_error = None

        self.submit_id = submit_id
        self.verdict = ''
        self.language = ''
        self.problem = ''
        self.test = ''
        self.runtime = ''
        self.memory = ''

    def _get_compilation_error(self):
        url = self._error_url_pattern.format(self.submit_id)
        cookies = {'ASP.NET_SessionId': self._session_id}
        response = requests.get(url, cookies=cookies)
        self._compilation_error = response.content

        # if compilation error is found, timus return a text/plain
        # else he return html page
        if response.headers['Content-Type'].startswith('text/html'):
            self._compilation_error = ''

    def __iter__(self):
        while True:
            self.update()
            yield self
            if self.completed:
                break

    def update(self):
        current_status_url = self._status_url_pattern.format(self.submit_id)
        response = requests.get(current_status_url)

        html_tree = lxml.html.fromstring(response.content)
        status_element = html_tree.find_class('even')[0]
        verdict_element = status_element.find_class('verdict_rj')
        if verdict_element == list():
            verdict_element = status_element.find_class('verdict_wt')
        if verdict_element == list():
            verdict_element = status_element.find_class('verdict_ac')

        self.verdict = verdict_element[0].text_content()
        self.language = status_element.find_class('language')[0].text_content()
        self.problem = status_element.find_class('problem')[0].text_content()
        self.test = status_element.find_class('test')[0].text_content()
        self.runtime = status_element.find_class('runtime')[0].text_content()
        self.memory = status_element.find_class('memory')[0].text_content()

    @property
    def proccess(self):
        return self.verdict in self._processing_verdicts

    @property
    def completed(self):
        return self.verdict and not self.proccess

    @property
    def accepted(self):
        return self.verdict == self._accepted_verdict

    @property
    def wrong_answer(self):
        return self.verdict == self._wrong_answer_verdict

    @property
    def compilation_error(self):
        if self.verdict != self._compilation_error_verdict:
            return ''
        if self._compilation_error is None:
            self._get_compilation_error()
        return self._compilation_error


class Submitter(object):
    MAX_SUBMIT_ATTEMPTS_TIME = 15

    _submit_url = 'http://acm.timus.ru/submit.aspx'

    @classmethod
    def try_submit(cls, payload):
        response = requests.post(cls._submit_url, payload, allow_redirects=False)
        if 'x-submitid' not in response.headers:
            return None

        submit_id = response.headers['x-submitid']
        author_id = response.cookies.get('AuthorID')
        session_id = response.cookies.get('ASP.NET_SessionId')
        return SubmitStatus(submit_id, author_id, session_id)

    @classmethod
    def submit(cls, payload):
        '''The break between submissions must be at least 10 seconds
        if we spend more than once at 10 seconds, Timus return a submit
        page with error string
        '''
        start_time = time.time()
        while (time.time() - start_time) < cls.MAX_SUBMIT_ATTEMPTS_TIME:
            status = cls.try_submit(payload)
            if status is not None:
                return status
        return None


class SubmitPayload(object):
    _submit_url = 'http://acm.timus.ru/submit.aspx'

    @classmethod
    def get_languages(cls):
        # TODO(actics): release warning if language list is updated
        response = requests.get(cls._submit_url)
        html_tree = lxml.html.fromstring(response.content)
        select_tag = html_tree.xpath('//select')[0]
        option_tags = select_tag.xpath('./option')

        languages = dict()
        for tag in option_tags:
            languages[tag.text] = tag.attrib['value']

        return languages

    def __init__(self):
        action = 'submit'
        space_id = '1'
        judge_id = ''
        language = 0
        problem_num = 0
        source = ''

    @property
    def dict(self):
        return {
            'Action': self.action,
            'SpaceID': self.space_id,
            'JudgeID': self.judge_id,
            'Language': self.language,
            'ProblemNum': self.problem_num,
            'Source': self.source,
        }



