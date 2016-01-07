# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import bs4
import langid

#<meta property="og:locale" content="fr_FR" />
#<meta name="lang" content="fr">
#<meta name="DC.language" content="fr">
#<meta itemprop="inLanguage" content="en-US" />
#<meta name="http-equiv" content-language="fr">

META_TAGS = [
    ('name', 'lang', 'content'),
    ('property', 'og:locale', 'content'),
    ('name', 'DC.language', 'content'),
    ('itemprop', 'inLanguage', 'content'),
    ('name', 'http-equiv', 'content-language'),
]


def extract_language(whole_soup, summary_text=None):
    assert(isinstance(whole_soup, bs4.element.Tag))

    # first search on the <html> tag
    if 'lang' in whole_soup.html:
        return whole_soup.html['lang']

    # common places
    if whole_soup.head:
        for attr_name, attr_val, attr_content in META_TAGS:
            tag = whole_soup.head.find('meta', attrs={attr_name: attr_val, attr_content:True})
            if tag:
                return tag[attr_content]

    # nothing found... fallback on language detection
    s = summary_text if summary_text else whole_soup.text
    return langid.classify(s.text)[0]

