from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Dict

from .structs import Problem, SubmitStatus, SortType


class AcmApiError(Exception):
    pass


class AcmApi(metaclass=ABCMeta):
    @abstractmethod
    def login(self, judge_id: str, password: str) -> None:
        pass

    @abstractmethod
    def login_local(self, judge_id: str, password: str, auth_key: str) -> None:
        pass

    @abstractmethod
    def get_auth_key(self) -> str:
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
    def submit(self, judge_id: str, language: str, problem_num: int, source: str) -> str:
        pass

    @abstractmethod
    def get_problem_set(self, page: str = 'all', tag: str = None, sort_type: SortType = SortType.id,
                        show_ac: bool = True) -> List[Problem]:
        pass

    @abstractmethod
    def get_problem_submits(self, problem_number: int, count: int = 1000) -> List[SubmitStatus]:
        pass

    @abstractmethod
    def get_submit_source(self, submit_id: str) -> str:
        pass

    @abstractmethod
    def get_languages(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_tags(self) -> List[Tuple[str, str]]:
        pass

    @abstractmethod
    def get_pages(self) -> List[Tuple[str, str]]:
        pass
