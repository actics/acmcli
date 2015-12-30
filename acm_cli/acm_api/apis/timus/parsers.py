import urllib.parse
from functools import reduce
from typing import List, Tuple

import lxml.html
from html2text import html2text

from ...acm_api import SubmitStatus, Problem


def parse_submit_status(html):
    status_element = lxml.html.fromstring(html).find_class('even')[0]
    return _parse_submit_status_element(status_element)


def parse_languages(html):
        tree = lxml.html.fromstring(html)
        select_tag = tree.xpath('//select')[0]
        option_tags = select_tag.xpath('./option')

        languages = dict()
        for tag in option_tags:
            languages[tag.text] = tag.attrib['value']
        return languages


def parse_problem(html):
    tree = lxml.html.fromstring(html)

    problem = Problem()
    _set_number_and_title(tree, problem)
    _set_limits(tree, problem)
    _set_author_and_source(tree, problem)
    _set_tags(tree, problem)
    _set_links(tree, problem)
    _set_text_and_samples(tree, problem)

    return problem


def parse_problem_set(html: str) -> List[Problem]:
    tree = lxml.html.fromstring(html)
    problems = list()
    contents = tree.find_class('content')[1:]
    for content in contents:
        content = list(content.iterchildren())
        problem = Problem()
        if content[0].xpath('.//img[@src="images/ok.gif"]'):
            problem.is_accepted = True
        elif content[0].xpath('.//img[@src="images/minus.gif"]'):
            problem.is_accepted = False
        problem.number = content[1].text_content()
        problem.title = content[2].text_content()
        problem.source = content[3].text_content()
        problem.rating_length = content[4].text_content()
        problem.difficulty = content[5].text_content()
        problems.append(problem)
    return problems


def parse_problem_submits(html: str) -> List[SubmitStatus]:
    tree = lxml.html.fromstring(html)
    evens = tree.find_class('even')
    odds = tree.find_class('odd')
    status_elements = reduce(list.__add__, [list(x) for x in zip(evens, odds)], [])
    if len(evens) > len(odds):
        status_elements.append(evens[-1])

    return [_parse_submit_status_element(element) for element in status_elements]


def parse_tags(html: str) -> List[Tuple[str, str]]:
    tree = lxml.html.fromstring(html)
    ps = tree.xpath('//p')[2:]
    tags = list()
    for element in ps[0].xpath('.//a') + ps[1].xpath('.//a'):
        description = element.text
        name = urllib.parse.parse_qs(urllib.parse.urlparse(element.attrib['href']).query)['tag'][0]
        tags.append((name, description))
    return tags

def parse_pages(html: str) -> List[Tuple[str, str]]:
    tree = lxml.html.fromstring(html)
    ps = tree.xpath('//p')
    pages = list()
    pages_elements = [ps[0].xpath('.//a')[0]] + ps[1].xpath('.//a')[0::2]
    for element in pages_elements:
        description = element.text
        name = urllib.parse.parse_qs(urllib.parse.urlparse(element.attrib['href']).query)['page'][0]
        pages.append((name, description))
    return pages


def _parse_submit_status_element(status_element):
    get_info = lambda name: status_element.find_class(name)[0].text_content()

    status = SubmitStatus()
    status.submit_id = get_info('id')
    status.date = get_info('date')
    status.author = get_info('coder')
    status.problem = get_info('problem')
    status.language = get_info('language')
    status.test = get_info('test')
    status.runtime = get_info('runtime')
    status.memory = get_info('memory')

    status.set_verdict(_parse_verdict(status_element))
    status.memory = ' '.join(status.memory.split()[:-1])

    return status


def _parse_verdict(element):
    verdict = element.find_class('verdict_rj')
    if len(verdict) == 0:
        verdict = element.find_class('verdict_wt')
    if len(verdict) == 0:
        verdict = element.find_class('verdict_ac')
    return verdict[0].text_content()


def _set_number_and_title(tree, problem):
    title = tree.find_class('problem_title')[0].text
    dot_position = title.find('.')
    problem.number = int(title[:dot_position])
    problem.title = title[dot_position+1:].strip()


def _set_limits(tree, problem):
    limits = tree.find_class('problem_limits')[0]
    limits = [x for x in limits.itertext()]
    problem.time_limit = limits[0].split(':')[1].strip()
    problem.memory_limit = limits[1].split(':')[1].strip()


def _set_author_and_source(tree, problem):
    source = tree.find_class('problem_source')[0]
    source = [x for x in source.itertext()]
    if len(source) == 0:
        pass
    elif len(source) == 4:
        problem.author = source[1].strip()
        problem.source = source[3].strip()
    elif len(source) == 2:
        source_name = source[0].strip()
        if source_name in [u'Problem Author:', u'Автор задачи:']:
            problem.author = source[1].strip()
        elif source_name in [u'Problem Source:', u'Источник задачи:']:
            problem.source = source[1].strip()
        else:
            # FIXME(actics)
            raise Exception()


def _set_tags(tree, problem):
    tags_div = tree.find_class('problem_tags_toggle')[0].getparent()
    tags = tags_div.xpath('./a[@href]')
    problem.tags = [x.text for x in tags]


def _set_links(tree, problem):
    get_number = lambda x: int(x[:-1].split('(')[-1])
    links = tree.find_class('problem_links')[0]
    problem.difficulty = int(links.xpath('./span')[0].text.split()[1])
    problem.is_accepted = len(links.find_class('myac')) == 1
    links = links.xpath('a[@href]')
    if not problem.is_accepted:
        problem.is_accepted = False if len(links) == 7 else None
    problem.discussion_count = get_number(links[2].text)
    links = links[4:] if len(links) == 7 else links[3:]
    problem.submission_count = get_number(links[0].text)
    problem.accepted_submission_count = get_number(links[1].text)
    problem.rating_length = get_number(links[2].text)


def _set_text_and_samples(tree, problem):
    text = tree.get_element_by_id('problem_text')
    source = text.find_class('problem_source')[0]
    source.getparent().remove(source)
    input_next = False
    output_next = False
    for div in text.iterchildren():
        if div.text in ['Input', 'Исходные данные']:
            input_next = True
        elif div.text in ['Output', 'Результат']:
            output_next = True
        elif input_next:
            input_next = False
            problem.input = html2text(lxml.html.tostring(div).decode('utf-8')).strip()
        elif output_next:
            output_next = False
            problem.output = html2text(lxml.html.tostring(div).decode('utf-8')).strip()
        else:
            continue
        div.getparent().remove(div)
    samples = text.find_class('sample')
    if len(samples) == 1:
        sample = samples[0]
        sample_h3 = text.find_class('problem_subtitle')
        sample_texts = [u'Sample', u'Пример', u'Samples', u'Примеры']
        sample_h3 = next(x for x in sample_h3 if x.text in sample_texts)
        sample.getparent().remove(sample)
        sample_h3.getparent().remove(sample_h3)
        intables = sample.find_class('intable')
        problem.sample_inputs = [x.text.rstrip() for x in intables[0::2]]
        problem.sample_outputs = [x.text.rstrip() for x in intables[1::2]]
    problem.text = html2text(lxml.html.tostring(text).decode('utf-8')).strip()
