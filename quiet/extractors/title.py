# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re

import bs4
from future.moves.urllib.parse import urlparse


def ireplace(old, repl, text):
    return re.sub(re.escape(old), lambda m: repl, text, flags=re.I | re.U)


def extract_title(whole_soup, opengraph=None, url=None):
    assert(isinstance(whole_soup, bs4.element.Tag))

    def clean_title(t):
        # remove the website name from the title (eg Le Monde.fr)
        if opengraph:
            for site_name in opengraph.site_name:
                t = t.replace(site_name, '')
        # remove the domain name from the title (eg www.lemonde.fr)
        if url:
            t = ireplace(urlparse(url).netloc, '', t)
        return t.strip(' \'"\r\n|-_«»:')

    assert(isinstance(whole_soup, bs4.element.Tag))
    title = ''

    # rely on opengraph in case we have the data
    if opengraph:
        if opengraph.title:
            return clean_title(opengraph.title[0])

    if whole_soup.head is not None:
        # <meta name="twitter:title" content="blabla">
        twitter_meta = whole_soup.head.find('meta', attrs={'name': 'twitter:title', 'content': True})
        if twitter_meta:
            return clean_title(twitter_meta['content'])
        # <meta name="headline" content="blabla">
        headline = whole_soup.head.find('meta', attrs={'name': 'headline', 'content': True})
        if headline:
            return clean_title(headline['content'])

    # otherwise use the title tag
    if whole_soup.head is not None:
        if whole_soup.head.title is not None:
            return clean_title(whole_soup.head.title.text)

    return title
