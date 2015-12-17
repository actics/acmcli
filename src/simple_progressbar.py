# coding=utf-8

import sys
import gettext

from colorama import Fore, Style

_ = gettext.gettext


class SimpleProgressBar(object):
    def __init__(self, delim=' <> '):
        self.prev_print_len = 0
        self.delim = delim

    def update(self, text, text_len=None):
        self.clear()
        print(text, end='')
        sys.stdout.flush()

        self.prev_print_len = text_len if text_len is not None else len(text)

    def clear(self):
        space = ' ' * self.prev_print_len
        print('\r{0}\r'.format(space), end='')
        self.prev_print_len = 0

    def coloring_verdict(self, status, verdict):
        if status.in_process:
            return Fore.YELLOW + verdict + Style.RESET_ALL
        elif status.accepted:
            return Fore.GREEN + verdict + Style.RESET_ALL
        else:
            return Fore.RED + verdict + Style.RESET_ALL

    def get_status_string(self, status):
        verdict_pattern = '[{s.verdict:^11}]'
        time_pattern = _('time:{s.runtime:^7}s')
        memory_pattern = _('memory:{s.memory:^9}KB')
        test_pattern = _('test:{s.test:^4}')
        info_pattern = _('info: {s.info}')

        verdict = verdict_pattern.format(s=status)
        string = self.coloring_verdict(status, verdict)

        if status.runtime and status.memory:
            string += self.delim
            string += time_pattern.format(s=status)
            string += self.delim
            string += memory_pattern.format(s=status)

        if status.test:
            string += self.delim
            string += test_pattern.format(s=status)

        if status.info:
            string += self.delim
            string += info_pattern.format(s=status)

        return string

    def update_status(self, status):
        string = self.get_status_string(status)
        self.update(string, len(string) - len(Fore.RED + Style.RESET_ALL))
