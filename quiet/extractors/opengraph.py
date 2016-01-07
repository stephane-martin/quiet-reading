# encoding: utf-8
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
from collections import defaultdict


def extract_opengraph(soup):
    return OpenGraph(soup)


class OpenGraph(defaultdict):

    def __init__(self, whole_soup):
        super(OpenGraph, self).__init__(list)

        ogs = whole_soup.html.head.find_all(
            'meta',
            attrs={'property': re.compile(r'^og:', flags=re.U), 'content': True}
        )
        for og in ogs:
            self[og['property'][3:]].append(og['content'])

    def __getattr__(self, name):
        return self[name]

