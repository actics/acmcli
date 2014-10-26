#!/usr/bin/env python2.7
# coding: utf-8

from __future__ import print_function
import sys
import re


class TerminalController:
    # Cursor movement:
    BOL = ''             #: Move the cursor to the beginning of the line
    UP = ''              #: Move the cursor up one line
    DOWN = ''            #: Move the cursor down one line
    LEFT = ''            #: Move the cursor left one char
    RIGHT = ''           #: Move the cursor right one char

    # Deletion:
    CLEAR_SCREEN = ''    #: Clear the screen and move to home position
    CLEAR_EOL = ''       #: Clear to the end of the line.
    CLEAR_BOL = ''       #: Clear to the beginning of the line.
    CLEAR_EOS = ''       #: Clear to the end of the screen

    # Output modes:
    BOLD = ''            #: Turn on bold mode
    BLINK = ''           #: Turn on blink mode
    DIM = ''             #: Turn on half-bright mode
    REVERSE = ''         #: Turn on reverse-video mode
    NORMAL = ''          #: Turn off all modes

    # Cursor display:
    HIDE_CURSOR = ''     #: Make the cursor invisible
    SHOW_CURSOR = ''     #: Make the cursor visible

    # Terminal size:
    COLS = None          #: Width of the terminal (None for unknown)
    LINES = None         #: Height of the terminal (None for unknown)

    # Foreground colors:
    BLACK = BLUE = GREEN = CYAN = RED = MAGENTA = YELLOW = WHITE = ''
    
    # Background colors:
    BG_BLACK = BG_BLUE = BG_GREEN = BG_CYAN = ''
    BG_RED = BG_MAGENTA = BG_YELLOW = BG_WHITE = ''
    
    _STRING_CAPABILITIES = """
    BOL=cr UP=cuu1 DOWN=cud1 LEFT=cub1 RIGHT=cuf1
    CLEAR_SCREEN=clear CLEAR_EOL=el CLEAR_BOL=el1 CLEAR_EOS=ed BOLD=bold
    BLINK=blink DIM=dim REVERSE=rev UNDERLINE=smul NORMAL=sgr0
    HIDE_CURSOR=cinvis SHOW_CURSOR=cnorm""".split()
    _COLORS = """BLACK BLUE GREEN CYAN RED MAGENTA YELLOW WHITE""".split()
    _ANSICOLORS = "BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE".split()

    def __init__(self, term_stream=sys.stdout):
        # Curses isn't available on all platforms
        try: 
            import curses
        except: 
            return

        # If the stream isn't a tty, then assume it has no capabilities.
        if not term_stream.isatty(): 
            return

        # Check the terminal type.  If we fail, then assume that the
        # terminal has no capabilities.
        try: 
            curses.setupterm()
        except: 
            return

        # Look up numeric capabilities.
        self.COLS = curses.tigetnum('cols')
        self.LINES = curses.tigetnum('lines')
        
        # Look up string capabilities.
        for capability in self._STRING_CAPABILITIES:
            (attrib, cap_name) = capability.split('=')
            setattr(self, attrib, self._tigetstr(cap_name) or '')

        # Colors
        set_fg = self._tigetstr('setf')
        if set_fg:
            for i, color in enumerate(self._COLORS):
                setattr(self, color, curses.tparm(set_fg, i) or '')

        set_fg_ansi = self._tigetstr('setaf')
        if set_fg_ansi:
            for i, color in enumerate(self._ANSICOLORS):
                setattr(self, color, curses.tparm(set_fg_ansi, i) or '')

        set_bg = self._tigetstr('setb')
        if set_bg:
            for i, color in enumerate(self._COLORS):
                setattr(self, 'BG_'+color, curses.tparm(set_bg, i) or '')

        set_bg_ansi = self._tigetstr('setab')
        if set_bg_ansi:
            for i, color in enumerate(self._ANSICOLORS):
                setattr(self, 'BG_'+color, curses.tparm(set_bg_ansi, i) or '')

    def _tigetstr(self, cap_name):
        import curses
        cap = curses.tigetstr(cap_name) or ''
        return re.sub(r'\$<\d+>[/*]?', '', cap)

    def render(self, template):
        return re.sub(r'\$\$|\${\w+}', self._render_sub, template)

    def _render_sub(self, match):
        s = match.group()
        if s == '$$': 
            return s
        else: 
            return getattr(self, s[2:-1])

class ProgressBar:
    header = '${BOLD}${CYAN}Status of problem {0}, Language {1}${NORMAL}'
    verdicts = {
        'ok':      "${BOLD}${GREEN}{0}${NORMAL}",
        'fail':    "${BOLD}${RED}{0}${NORMAL}",
        'process': "${BOLD}${YELLOW}{0}${NORMAL}",
    }

    status_lines = {
        'runtime': 'Runtime:      {0}',
        'memory':  'Memory usage: {0}',
        'test':    'Test:         {0}',
    }
        
    def __init__(self):
        self.term = TerminalController()
        self.header = self.term.render(self.header)
        self.prev_lines_count = 0
        for key, value in self.verdicts.iteritems():
            self.verdicts[key] = self.term.render(value)

    def __create_string_list(self, status):
        lines = list()
        if status['status'] == 'wait':
            return ['Please wait. Your submit in process.']
        if status['status'] == 'submit_fail':
            return ['Submit failed. Try again later.']

        header = self.header.format(status['problem'], status['language'])
        verdict = 'Status:       ' + self.verdicts[status['status']].format(status['verdict'])
        lines.append(header)
        lines.append(verdict)

        for key, value in self.status_lines.iteritems():
            if status[key]:
                lines.append(value.format(status[key]))

        return lines

    def update(self, status):
        lines = self.__create_string_list(status)

        print(self.term.BOL, end='')
        for i in xrange(self.prev_lines_count):
            print(self.term.UP + self.term.CLEAR_EOL, end='')

        for line in lines:
            print(line)

        self.prev_lines_count = len(lines)

