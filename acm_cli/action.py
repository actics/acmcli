from enum import Enum


class Action(Enum):
    submit = 'submit'
    problem = 'problem'
    problem_submits = 'problem-submits'
    problem_set = 'problem-set'
    submit_source = 'submit-source'
    languages = 'languages'
    tags = 'tags'
    pages = 'pages'

    def __str__(self):
        return self.value
