# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import arrow
import dateutil.parser

import re

import bs4


PUBLISH_DATE_TAGS = [
    ('meta', 'name', 'DC.date.issued', 'content'),
    ('meta', 'property', 'rnews:datePublished', 'content'),
    ('meta', 'property', 'article:published_time', 'content'),
    ('name', 'OriginalPublicationDate', 'content'),
    (None,   'itemprop', 'datePublished', 'datetime'),
    ('meta', 'property', 'og:published_time', 'content'),
    ('meta', 'name', 'article_date_original', 'content'),
    ('meta', 'name', 'publication_date', 'content'),
    ('meta', 'name', 'sailthru.date', 'content'),
    ('meta', 'name', 'PublishDate', 'content'),
]

COUNTRIES_FORMAT = {
    'us': 'MDY',
    'europe': 'DMY',
    'france': 'DMY',
    'uk': 'DMY',
    'russia': 'DMY',
    'china': 'YMD',
    'africa': 'DMY',
    'australia': 'DMY'
}

DATE_REGEX = r'([\./\-_]{0,1}(19|20)\d{2})' + \
             '[\./\-_]{0,1}(' + \
             '([0-3]{0,1}[0-9][\./\-_])' + \
             '|(\w{3,5}[\./\-_]))' + \
             '([0-3]{0,1}[0-9][\./\-]{0,1})?'

DATE_REGEX = re.compile(DATE_REGEX, flags=re.U)


def extract_publishdate(whole_soup, url=None, country=None):
    assert(isinstance(whole_soup, bs4.element.Tag))

    dayfirst = True
    yearfirst = False
    if country:
        fmt = COUNTRIES_FORMAT.get(country, 'DMY')
        if fmt == 'DMY':
            dayfirst = True
            yearfirst = False
        elif fmt == "MDY":
            dayfirst = False
            yearfirst = False
        elif fmt == "YMD":
            yearfirst = True
            dayfirst = False
        else:
            dayfirst = True
            yearfirst = False

    def parse_date(date):
        try:
            return arrow.get(dateutil.parser.parse(date, dayfirst=dayfirst, yearfirst=yearfirst))
        except ValueError:
            return None

    # search in HTML common places
    for tag_name, attr_name, attr_value, attr_content in PUBLISH_DATE_TAGS:
        tag = whole_soup.find(tag_name, attrs={attr_name: attr_value, attr_content: True})
        if tag:
            d = parse_date(tag[attr_content])
            if d:
                return d

    # look at the URL
    if not url:
        return None
    date_match = DATE_REGEX.search(url)
    if date_match:
        return parse_date(date_match.group(0))
    return None
