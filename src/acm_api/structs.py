class SubmitStatus(object):
    _processing_verdicts = ['Compiling', 'Running', 'Waiting']
    _running_verdict = 'Running'
    _accepted_verdict = 'Accepted'
    _failed_verdict = 'Failed'
    _compilation_error_info = 'Compilation error'

    def __init__(self) -> None:
        self.submit_id = ''
        self.date = ''
        self.author = ''
        self.problem = ''
        self.language = ''
        self.verdict = ''
        self.test = ''
        self.runtime = ''
        self.memory = ''
        self.info = ''

    def set_verdict(self, verdict: str) -> None:
        self.verdict = verdict
        if not self.in_process and not self.accepted:
            self.verdict = self._failed_verdict
            self.info = verdict

    @property
    def in_process(self) -> bool:
        return self.verdict in self._processing_verdicts

    @property
    def running(self) -> bool:
        return self.verdict == self._running_verdict

    @property
    def accepted(self) -> bool:
        return self.verdict == self._accepted_verdict

    @property
    def failed(self) -> bool:
        return self.verdict == self._failed_verdict

    @property
    def compilation_error(self) -> bool:
        return self.info == self._compilation_error_info


class Problem(object):
    def __init__(self):
        self.number = 0
        self.title = ''
        self.time_limit = ''
        self.memory_limit = ''
        self.text = ''
        self.input = ''
        self.output = ''
        self.sample_inputs = []
        self.sample_outputs = []
        self.author = ''
        self.source = ''
        self.tags = []
        self.difficulty = 0
        self.is_accepted = None
        self.discussion_count = 0
        self.submission_count = 0
        self.accepted_submission_count = 0
        self.rating_length = 0
