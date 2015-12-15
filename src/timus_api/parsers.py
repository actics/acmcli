# coding: utf-8

import lxml.html
from html2text import html2text

from .structs import SubmitStatus, Problem


def parse_submit_status(html):
    tree = lxml.html.fromstring(html)

    status_element = tree.find_class('even')[0]
    verdict_element = status_element.find_class('verdict_rj')
    if len(verdict_element) == 0:
        verdict_element = status_element.find_class('verdict_wt')
    if len(verdict_element) == 0:
        verdict_element = status_element.find_class('verdict_ac')

    status = SubmitStatus()
    status.verdict = verdict_element[0].text_content()
    status.submit_id = status_element.find_class('id')[0].text_content()
    status.language = status_element.find_class('language')[0].text_content()
    status.problem = status_element.find_class('problem')[0].text_content()
    status.test = status_element.find_class('test')[0].text_content()
    status.runtime = status_element.find_class('runtime')[0].text_content()
    status.memory = status_element.find_class('memory')[0].text_content()
    return status


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
    problem.discussion_count = get_number(links[2].text)
    links = links[4:] if len(links) == 7 else links[3:]
    problem.submission_count = get_number(links[0].text)
    problem.accepted_submission_count = get_number(links[1].text)
    problem.rating_length = get_number(links[2].text)


def _set_text_and_samples(tree, problem):
    text = tree.get_element_by_id('problem_text')
    source = text.find_class('problem_source')[0]
    source.getparent().remove(source)
    samples = text.find_class('sample')
    if len(samples) == 1:
        sample = samples[0]
        sample_h3 = text.find_class('problem_subtitle')
        sample_texts = [u'Sample', u'Пример', u'Samples', u'Примеры']
        sample_h3 = next(x for x in sample_h3 if x.text in sample_texts)
        sample.getparent().remove(sample)
        sample_h3.getparent().remove(sample_h3)
        intables = sample.find_class('intable')
        problem.sample_input = [x.text for x in intables[0::2]]
        problem.sample_output = [x.text for x in intables[1::2]]
    problem.text = html2text(lxml.html.tostring(text).decode('utf-8'))
