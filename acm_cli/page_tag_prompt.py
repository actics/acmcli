import cmd
import sys
import gettext

from .acm_api import AcmApi
from .settings import Settings

_ = gettext.gettext


def tags_action(api: AcmApi, settings: Settings=None) -> None:
    tags = api.get_tags()
    max_id_length = max(len(tag.id) for tag in tags)
    format_string = _('tag  {{t.id:<{0}}} : {{t.description}}').format(max_id_length)
    for tag in tags:
        print(format_string.format(t=tag))


def pages_action(api: AcmApi, settings: Settings=None) -> None:
    pages = api.get_pages()
    max_id_length = max(len(page.id) for page in pages)
    format_string = _('page  {{p.id:<{0}}} : {{p.description}}').format(max_id_length)
    for page in pages:
        print(format_string.format(p=page))


class PageTagPrompt(cmd.Cmd):
    intro = _('Type "page ID" or "tag ID" for getting problem set. For help type "help" or "?".')
    prompt = ': '

    def __init__(self, api: AcmApi):
        super(PageTagPrompt, self).__init__()
        self.tag = None
        self.page = None
        self.api = api

    def do_pages(self, line):
        pages_action(self.api)

    def do_tags(self, line):
        tags_action(self.api)

    def do_page(self, line):
        try:
            self.page = self.api.get_page_by_id(line)
            return True
        except ValueError:
            print(_('Unknown page name "{0}"').format(line))

    def complete_page(self, text, line, begidx, endidx):
        prefix = line[begidx:]
        return [page.id for page in self.api.get_pages() if page.id.startswith(prefix)]

    def do_tag(self, line):
        try:
            self.tag = self.api.get_tag_by_id(line)
            return True
        except ValueError:
            print(_('Unknown tag name "{0}"').format(line))

    def complete_tag(self, text, line, begidx, endidx):
        prefix = line[begidx:]
        return [tag.id for tag in self.api.get_tags() if tag.id.startswith(prefix)]

    def do_help(self, line):
        print(_('Type "page ID" or "tag ID". For list of available IDs type "pages" or "tags"'))
        print(_('Also you can use auto-completion'))

    def default(self, line):
        print(_('Unknown syntax: {0}').format(line))

    def emptyline(self):
        pass

    def do_EOF(self, line):
        print()
        sys.exit(0)
