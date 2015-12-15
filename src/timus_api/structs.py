# coding: utf-8

class SubmitStatus(object):
    _processing_verdicts = ['Compiling', 'Running', 'Waiting']
    _accepted_verdict = 'Accepted'
    _wrong_answer_verdict = 'Wrong answer'
    _compilation_error_verdict = 'Compilation error'

    def __init__(self):
        self.submit_id = ''
        self.verdict = ''
        self.language = ''
        self.problem = ''
        self.test = ''
        self.runtime = ''
        self.memory = ''

    @property
    def in_process(self):
        return self.verdict in self._processing_verdicts

    @property
    def completed(self):
        return self.verdict and not self.process

    @property
    def accepted(self):
        return self.verdict == self._accepted_verdict

    @property
    def wrong_answer(self):
        return self.verdict == self._wrong_answer_verdict

    @property
    def compilation_error(self):
        return self.verdict == self._compilation_error_verdict


class Problem(object):
    def __init__(self):
        self.number = 0
        self.title = ''
        self.time_limit = ''
        self.memory_limit = ''
        self.text = ''
        self.sample_input = []
        self.sample_output = []
        self.author = ''
        self.source = ''
        self.tags = []
        self.difficulty = 0
        self.is_accepted = False
        self.discussion_count = 0
        self.submission_count = 0
        self.accepted_submission_count = 0
        self.rating_length = 0
