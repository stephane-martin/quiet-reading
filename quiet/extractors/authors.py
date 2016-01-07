# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
from itertools import groupby, product, chain, imap
from copy import copy

import bs4

# todo:
# <!--Tag FIGARO_Author-->
# <meta property='av:tag' content="Eugénie Bastié"/>
# <meta property='av:tag:type' content="Author"/>

AUTHOR_ATTRS = ['name', 'rel', 'itemprop', 'class', 'id', 'property']
AUTHOR_VALS = ['author', 'byline', 'article:author', 'article:author_name']

BLACKLIST = {
    'Lefigaro Fr'
}


def extract_authors(whole_soup):
    """
    Extracts the list of authors for the given HTML document

    Parameters
    ----------
    whole_soup: bs4.element.Tag

    Returns
    -------
    authors: list
    """
    assert(isinstance(whole_soup, bs4.BeautifulSoup))
    soup = copy(whole_soup)
    [tag.insert_after(soup.new_tag("br")) for tag in soup.find_all('div')]
    [tag.insert_after(soup.new_tag("br")) for tag in soup.find_all('p')]
    [tag.insert_after(soup.new_tag("br")) for tag in soup.find_all('ul')]
    [tag.insert_after(soup.new_tag("br")) for tag in soup.find_all('li')]
    [tag.replace_with('') for tag in soup.find_all(class_='fig-auteur-metas')]
    [tag.replace_with('') for tag in soup.find_all(class_='fig-auteur-description')]
    [br_tag.replace_with('\n') for br_tag in soup.find_all('br')]

    def parse_byline(search_str):
        """
        Takes a candidate line of html or text and extracts out the names

        Parameters
        ----------
        search_str: str
            a line of html or text
        """
        # print("search", search_str)
        digits_re = re.compile('\d', flags=re.U)

        # (helps discriminate...)
        search_str = search_str.strip('\r\n ').replace('\n', '\n\n')
        # Remove "by" statement
        search_str = re.sub(r'[bB][yY][:\s]|[fF]rom[:\s]', '', search_str, flags=re.U)

        # Remove parts inside parenthesis
        search_str = re.sub(r'\([^\)]+\)', '', search_str, flags=re.U)

        # Chunk the line by non alphanumeric tokens (few name exceptions)
        # >>> re.split("[^\w\'\-]", "Lucas Ou, Dean O'Brian and Ronald")
        # ['Lucas', 'Ou', '', 'Dean', "O'Brian", 'and', 'Ronald']
        name_tokens = re.split(r"[^\w\'\-]", search_str, flags=re.U)
        name_tokens = [tok.strip() for tok in name_tokens if not digits_re.search(tok)]

        l = [list(v) for k, v in groupby(name_tokens, key=lambda x: bool(x != 'and' and x)) if k]
        l = [" ".join(grp) for grp in l if 2 <= len(grp) <= 3]
        return l

    iter_of_tags = chain.from_iterable(
        [soup.find_all(attrs={attr: val}) for attr, val in product(AUTHOR_ATTRS, AUTHOR_VALS)]
    )
    iter_of_lines = imap(
        lambda t: t.get('content', '') if t.name == 'meta' else t.text,
        iter_of_tags
    )
    iter_of_authors = chain.from_iterable(
        imap(parse_byline, iter_of_lines)
    )
    authors = {
        ' '.join([word.capitalize() for word in s.lower().split(' ')])
        for s in iter_of_authors
        if s
    }
    return list(authors.difference(BLACKLIST))
