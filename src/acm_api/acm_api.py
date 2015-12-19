from abc import ABCMeta, abstractmethod
from typing import List

from .structs import Problem, SubmitStatus


class AcmApi(metaclass=ABCMeta):
    @abstractmethod
    def login(self, judge_id: str) -> None:
        pass

    @abstractmethod
    def get_languages(self) -> List[str]:
        pass

    @abstractmethod
    def get_compilation_error(self, submit_id: str) -> str:
        pass

    @abstractmethod
    def get_problem(self, number: int) -> Problem:
        pass

    @abstractmethod
    def get_submit_status(self, submit_id: str) -> SubmitStatus:
        pass

    @abstractmethod
    def submit(self, judge_id: str, language: int, problem_num: int, source: str) -> SubmitStatus:
        pass

    @abstractmethod
    def get_problem_set(self) -> List[Problem]:
        pass

    @abstractmethod
    def get_submits_of(self) -> List[SubmitStatus]:
        pass