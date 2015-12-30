import sys

from colorama import Fore, Style


class SimpleProgressBar(object):
    def __init__(self):
        self.prev_print_len = 0

    def update(self, text, text_len=None):
        self.clear()
        print(text, end='')
        sys.stdout.flush()

        self.prev_print_len = text_len if text_len is not None else len(text)

    def clear(self):
        space = ' ' * self.prev_print_len
        print('\r{0}\r'.format(space), end='')
        self.prev_print_len = 0

    def update_status(self, string):
        self.update(string, len(string) - len(Fore.RED + Style.RESET_ALL))
