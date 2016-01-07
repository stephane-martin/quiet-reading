# encoding: utf-8
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from copy import copy
from itertools import chain, ifilter
import os
import string

TTABLE = {ord(c): None for c in string.punctuation}

my_dir = os.path.abspath(os.path.dirname(__file__))


class StopWords(object):
    _cached_stop_words = {}

    def __init__(self, language):
        if language not in self._cached_stop_words:
            path = os.path.join(my_dir, 'stopwords', 'stopwords-%s.txt' % language)
            with open(path) as f:
                content = f.read()
            stpwds = [stpwd.strip('\r\n ') for stpwd in content.decode('utf-8').splitlines()]
            self._cached_stop_words[language] = [stpwd for stpwd in stpwds if bool(stpwd) and not stpwd.startswith('#')]
        self.STOP_WORDS = self._cached_stop_words[language]

    def get_stopword_count(self, content):
        content = content.strip()
        if not content:
            return 0
        words = list(ifilter(
            lambda word: word in self.STOP_WORDS,
            content.translate(TTABLE).lower().split(' ')
        ))
        return len(words)


def calculate_best_node(soup, language):
    soup = copy(soup)
    stopwords = StopWords(language)

    top_node = None
    starting_boost = float(1.0)
    cnt = 0
    i = 0
    parent_nodes = []

    nodes_iter = chain(soup.find_all('p'), soup.find_all('pre'), soup.find_all('td'))
    nodes_with_text = list(
        ifilter(
            lambda n: stopwords.get_stopword_count(n.text) > 2 and not is_highlink_density(n),
            nodes_iter
        )
    )

    nodes_number = len(nodes_with_text)
    negative_scoring = 0
    bottom_negativescore_nodes = float(nodes_number) * 0.25

    for node in nodes_with_text:
        boost_score = float(0)
        # boost
        if is_boostable(node, stopwords):
            if cnt >= 0:
                boost_score = float((1.0 / starting_boost) * 50)
                starting_boost += 1
        # nodes_number
        if nodes_number > 15:
            if (nodes_number - i) <= bottom_negativescore_nodes:
                booster = float(bottom_negativescore_nodes - (nodes_number - i))
                boost_score = float(-pow(booster, float(2)))
                negscore = abs(boost_score) + negative_scoring
                if negscore > 40:
                    boost_score = float(5)

        upscore = int(stopwords.get_stopword_count(node.text) + boost_score)

        parent_node = node.parent
        update_score(parent_node, upscore)
        update_node_count(parent_node, 1)

        if parent_node not in parent_nodes:
            parent_nodes.append(parent_node)

        # Parent of parent node
        parent_parent_node = parent_node.parent
        if parent_parent_node is not None:
            update_node_count(parent_parent_node, 1)
            update_score(parent_parent_node, upscore / 2)
            if parent_parent_node not in parent_nodes:
                parent_nodes.append(parent_parent_node)
        cnt += 1
        i += 1

    top_node_score = 0
    for e in parent_nodes:
        score = get_score(e)

        if score > top_node_score:
            top_node = e
            top_node_score = score

        if top_node is None:
            top_node = e
    return top_node


def is_highlink_density(e):
    """
    Checks the density of links within a node, if there is a high
    link to text ratio, then the text is less likely to be relevant
    """
    links = e.find_all('a')
    if not links:
        return False

    words = e.text.split(' ')
    words_number = float(len(words))

    linktext = ''.join([link.text for link in links])
    linkwords = linktext.split(' ')
    numberoflinkwords = float(len(linkwords))
    numberoflinks = float(len(links))
    linkdivisor = float(numberoflinkwords / words_number)
    score = float(linkdivisor * numberoflinks)
    if score >= 1.0:
        return True
    return False


def get_score(node):
    """
    Returns the gravityScore as an integer from this node
    """
    return float(node['gravityScore']) if 'gravityScore' in node else 0.0


def is_nodescore_threshold_met(node, e):
    top_node_score = get_score(node)
    current_nodescore = get_score(e)
    thresholdscore = float(top_node_score * .08)

    return current_nodescore >= thresholdscore or e.name == 'td'


def is_table_and_no_para_exist(e):
    for p in e.find_all('p'):
        if len(p.txt) < 25:
            p.replace_with('')

    return (not e.find_all('p')) and (e.name != 'td')


def update_node_count(node, add_to_count):
    """
    Stores how many decent nodes are under a parent node
    """
    current_score = 0 if 'gravityNodes' not in node else int(node['gravityNodes'])
    node['gravityNodes'] = str(current_score + add_to_count)


def update_score(node, addToScore):
    """
    Adds a score to the gravityScore Attribute we put on divs
    we'll get the current score then add the score we're passing
    in to the current.
    """
    current_score = 0 if 'gravityScore' not in node else float(node['gravityScore'])
    node['gravityScore'] = str(current_score + addToScore)


def is_boostable(node, stopwords):
    """Alot of times the first paragraph might be the caption under an image
    so we'll want to make sure if we're going to boost a parent node that
    it should be connected to other paragraphs, at least for the first n
    paragraphs so we'll want to make sure that the next sibling is a
    paragraph and has at least some substantial weight to it.
    """
    steps_away = 0
    minimum_stopword_count = 5
    max_stepsaway_from_node = 3

    for current_node in node.previous_siblings:
        if current_node.name == 'p':
            if steps_away >= max_stepsaway_from_node:
                return False
            if stopwords.get_stopword_count(current_node.text) > minimum_stopword_count:
                return True
            steps_away += 1
    return False


def get_siblings_score(top_node, stopwords):
    """We could have long articles that have tons of paragraphs
    so if we tried to calculate the base score against
    the total text score of those paragraphs it would be unfair.
    So we need to normalize the score based on the average scoring
    of the paragraphs within the top node.
    For example if our total score of 10 paragraphs was 1000
    but each had an average value of 100 then 100 should be our base.
    """
    base = 100000
    paragraphs_number = 0
    paragraphs_score = 0

    for node in top_node.find_all('p'):
        stp_count = stopwords.get_stopword_count(node.text)
        if stp_count > 2 and not is_highlink_density(node):
            paragraphs_number += 1
            paragraphs_score += stp_count

    if paragraphs_number > 0:
        base = paragraphs_score / paragraphs_number

    return base
