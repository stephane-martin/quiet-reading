# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import bs4


def extract_canonical_url(whole_soup, url=None):
    assert(isinstance(whole_soup, bs4.BeautifulSoup))
    head = whole_soup.head

    tag = head.find('link', attrs={'rel': 'canonical', 'href': True})
    if tag:
        return tag['href']

    tag = head.find('meta', attrs={'name': 'twitter:url', 'content': True})
    if tag:
        return tag['content']

    return url


def extract_short_url(whole_soup, url=None):
    assert(isinstance(whole_soup, bs4.BeautifulSoup))
    head = whole_soup.head

    tag = head.find('link', attrs={'rel': 'shorturl', 'href': True})
    if tag:
        return tag['href']

    tag = head.find('link', attrs={'rel': 'shortlink', 'href': True})
    if tag:
        return tag['href']

    return url


def extract_description(whole_soup):
    assert(isinstance(whole_soup, bs4.BeautifulSoup))
    head = whole_soup.head

    tag = head.find('meta', attrs={'name': 'description', 'content': True})
    if tag:
        return tag['content']

    tag = head.find('meta', attrs={'name': 'twitter:description', 'content': True})
    if tag:
        return tag['content']
    return ''


# <meta name="DC.publisher" content="Le Monde">

# <link rel="canonical" href="http://www.theguardian.com/world/2016/jan/05/journalist-ruqia-hassan-killed-isis-raqqa-syria"/>
# <link rel="shorturl" href="http://arstechnica.com/?p=799263" />
# <meta name="twitter:url" content="http://www.lemonde.fr/societe/article/2016/01/05/projet-de-reforme-penale-une-nouvelle-mise-a-l-ecart-de-la-justice_4841872_3224.html">

# <meta name="description" content="Activists confirm 30-year-old was killed in September after being accused by Islamic State of spying for rival Syrian groups"/>
# <meta name="twitter:description" content="Le nouveau projet de loi confirme un élargissement des pouvoirs de police, des parquets et des préfets aux dépens des juges d’instruction.">



