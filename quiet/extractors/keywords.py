# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import bs4
from future.moves.urllib.parse import urlparse
from itertools import chain, imap

METAS = [
    ('name', 'keywords'),
    ('name', 'news_keywords'),
    ('property', 'article:tag'),
]


def extract_keywords(whole_soup):
    assert(isinstance(whole_soup, bs4.element.Tag))
    keywords = {
        t.strip().lower()
        for attr_name, attr_val in METAS
        for tag in whole_soup.find_all('meta', attrs={attr_name: attr_val, 'content': True})
        for t in tag['content'].split(',')
    }
    return keywords


def extract_rel_tags(whole_soup):
    assert(isinstance(whole_soup, bs4.element.Tag))

    list_of_a_tags = whole_soup.find_all('a', rel='tag', href=True)
    list_of_text_tags = [tag.text.strip('\r\n ') for tag in list_of_a_tags]
    list_of_text_tags = [tag for tag in list_of_text_tags if tag]

    list_of_link_tags = whole_soup.find_all('link', rel='tag', href=True)
    iter_of_html_tags = chain(list_of_a_tags, list_of_link_tags)
    iter_of_urls = imap(
        lambda html_tag: html_tag['href'],
        iter_of_html_tags
    )
    iter_of_tags = chain(
        imap(
            lambda url: urlparse(url).path.strip('/').rsplit('/', 1)[-1],
            iter_of_urls
        ),
        list_of_text_tags
    )
    return set(iter_of_tags)


def extract_keywords_nlp(summary_text):
    pass


# <!--Tag FIGARO_EditorialTag-->
# <meta property='av:tag' content="Irak"/>
# <meta property='av:tag:type' content="EditorialTag"/>
# <meta property='av:tag' content="Mossoul"/>
# <meta property='av:tag:type' content="EditorialTag"/>
# <meta property='av:tag' content="État islamique"/>
# <meta property='av:tag:type' content="EditorialTag"/>
