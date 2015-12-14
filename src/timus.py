#!/usr/bin/env python2.7
# coding: utf-8

from __future__ import print_function
import sys

from settings import Settings
from timus_api import SubmitPayload, Submitter, Problem


def get_problem(settings):
    problem = Problem.get_problem(settings.problem_number

def main():
    settings = Settings.read()

    get_problem(setings.problem_number)
    return
    with open(sys.argv[1]) as source_file:
        source = source_file.read()

    submit_payload['Source'] = source

    submit_status = Submitter.submit(submit_payload)

    for status in submit_status:
        print(status.verdict)

    if status.compilation_error:
        print(status.compilation_error)


if __name__ == '__main__':
    main()

