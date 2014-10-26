#!/usr/bin/env python2.7
# coding: utf-8

from __future__ import print_function
import sys
import time
import httplib
import lxml.html

import requests
import progress_bar

WAIT_TIME = 0.3
MAX_SUBMIT_ATTEMPTS = 5
SUBMIT_ATTEMPT_WAIT_TIME = 3

submit_url = 'http://acm.timus.ru/submit.aspx'
status_url = 'http://acm.timus.ru/status.aspx'
error_url = 'http://acm.timus.ru/ce.aspx'

languages = {
    'Visual C 2010': 9,
    'Visual C++ 2010': 10,
    'Visual C# 2010': 11,
    'Go 1.3': 14,
    'VB.NET 2010': 15,
    'Ruby 1.9': 18,
    'Haskell 7.6': 19,
    'GCC 4.9': 25,
    'G++ 4.9': 26,
    'GCC 4.9 C11': 27,
    'G++ 4.9 C++11': 28,
    'Clang 3.5 C++14': 30,
    'FreePascal 2.6': 31,
    'Java 1.8': 32,
    'Scala 2.11': 33,
    'Python 2.7': 34,
    'Python 3.4': 35
}

submit_payload = {
    'Action': 'submit',
    'SpaceID': '1',
    'JudgeID': '103946PD',
    'Language': languages['Visual C# 2010'],
    'ProblemNum': 1001,
    'Source': None,
    'SourceFile': ''
}

class color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    
    @staticmethod
    def process(text):
        return color.YELLOW + text + color.END

    @staticmethod
    def ok(text):
        return color.GREEN + text + color.END

    @staticmethod
    def fail(text):
        return color.RED + text + color.END



def submit(payload):
    response = requests.post(submit_url, payload, allow_redirects=False)
    if response.status_code != httplib.FOUND:
        return None

    submit_status = dict()
    submit_status['author_id']  = response.cookies.get('AuthorID')
    submit_status['session_id'] = response.cookies.get('ASP.NET_SessionId')
    submit_status['submit_id'] =  response.headers['x-submitid']

    return submit_status


def get_status(submit_id):
    response = requests.get(status_url + '?count=1&from={0}'.format(submit_id))
    raw_html = response.content
    html_tree = lxml.html.fromstring(raw_html)
    status_element = html_tree.find_class('even')[0]

    verdict_element = status_element.find_class('verdict_rj')
    if verdict_element == list():
        verdict_element = status_element.find_class('verdict_wt')
    if verdict_element == list():
        verdict_element = status_element.find_class('verdict_ac')

    status = dict()

    status['verdict'] = verdict_element[0].text_content()
    status['language'] = status_element.find_class('language')[0].text_content()
    status['problem'] = status_element.find_class('problem')[0].text_content()
    status['test'] = status_element.find_class('test')[0].text_content()
    status['runtime'] = status_element.find_class('runtime')[0].text_content()
    status['memory'] = status_element.find_class('memory')[0].text_content()

    if status['verdict'] in processing_verdicts:
        status['status'] = 'process'
    elif status['verdict'] == accepted_verdict:
        status['status'] = 'ok'
    else:
        status['status'] = 'fail'

    return status

def get_compilation_error(submit_id, session_id):
    url = error_url + '?id=' + submit_id
    response = requests.get(url, cookies={'ASP.NET_SessionId': session_id})
    return response.content

processing_verdicts = ['Compiling', 'Running', 'Waiting']
accepted_verdict = 'Accepted'

def try_submit(submit_payload):
    submit_attempts = 0
    while submit_attempts < MAX_SUBMIT_ATTEMPTS:
        submit_status = submit(submit_payload)
        submit_attempts += 1
        if submit_status is not None:
            return submit_status
        time.sleep(SUBMIT_ATTEMPT_WAIT_TIME)
    return None

def process_verdict(progress, submit_id):
    while True:
        start_time = time.time()

        status = get_status(submit_id)
        progress.update(status)

        sleep_time = WAIT_TIME - (time.time() - start_time)
        if (sleep_time < 0):
            sleep_time = 0
        time.sleep(sleep_time)

        if status['verdict'] not in processing_verdicts:
            return status['verdict']


def main():
    with open(sys.argv[1]) as source_file:
        source = source_file.read()

    submit_payload['Source'] = source

    progress = progress_bar.ProgressBar()

    wait_status = {'status': 'wait'}
    progress.update(wait_status)

    submit_status = try_submit(submit_payload)
    if submit_status is None:
        submit_fail_status = {'status': 'submit_fail'}
        progress.update(submit_fail_status)
        return

    end_verdict = process_verdict(progress, submit_status['submit_id'])

    print()

    if end_verdict == 'Compilation error':
        print(get_compilation_error(submit_status['submit_id'], submit_status['session_id']))


if __name__ == '__main__':
    main()

