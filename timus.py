#!/usr/bin/env python2.7
# coding: utf-8

from __future__ import print_function
import sys

from timus_api import SubmitPayload, Submitter, Problem

def main():
    settings = settings.read()

    with open(sys.argv[1]) as source_file:
        source = source_file.read()

    for number in xrange(1900, 2074):
        try:
            problem = Problem.get_problem(number)
            print(problem.title)
        except Exception as err:
            print(str(number) + '!!!!!!!!!!!!!!!!!!!!!!!')

    # submit_payload['Source'] = source

    # submit_status = Submitter.submit(submit_payload)

    # for status in submit_status:
        # print(status.verdict)

    # if status.compilation_error:
        # print(status.compilation_error)


if __name__ == '__main__':
    main()

