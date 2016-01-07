# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from future.builtins import str as str_unicode

"""
:Name:
    kea

:Authors:
    Florian Boudin (florian com boudin at univ-nantes dot fr)
    Modified by Stephane Martin (stef dot martin at gmail dot com)

:Version:
    0.22sma

:Date:
    - 20160116

:Description:
    kea is a Tokenizer for French. The tokenization process is decomposed in two steps:

        1. A rule-based tokenization approach is employed using the punctuation
           as an indication of token boundaries.
        2. A large-coverage lexicon is used to merge over-tokenized units (e.g.
           fixed contractions such as *aujourd'hui* are considered as one token)

:History:
    - 0.22sma (16 jan 2016), modernize code a bit
    - 0.22 (13 feb. 2012), adding the compound words exceptions
    - 0.21 (21 nov. 2011), bug fixes, adding the french city lexicon
    - 0.2 (26 oct. 2011), adding a large lexicon constructed from the lefff.
    - 0.1 (20 oct. 2011), first released version.

:Usage:
    A typical usage of this module is sample:

        >>> import kea
        >>> sentence = "Le Kea est le seul perroquet alpin au monde."
        >>> keatokenizer = kea.Tokenizer()
        >>> tokens = keatokenizer.tokenize(sentence)
        ['Le', 'Kea', 'est', 'le', 'seul', 'perroquet', 'alpin', 'au', 'monde', '.']
"""

from os.path import dirname, join, abspath
import re

my_dir = abspath(dirname(__file__))


class Tokenizer(object):
    """
    The Kea Tokenizer is a rule-based Tokenizer for french
    """

    def __init__(self):
        self.resources = join(my_dir, 'resources')
        self.lexicon = set()

        self.regexp = re.compile(
            r"(?xumsi)"
            r"(?:[lcdjmnts]|qu)['’]"                    # Contraction
            r"|https?://[^\s/$.?#].[^\s]*"              # Adresses web
            r"|\d+[.,]\d+"                              # Les réels en/fr
            r"|[.-]+"                                   # Les ponctuations
            r"|\w+"                                     # Les mots pleins
            r"|[^\w\s]",
            flags=re.U
        )

        # Loads the default lexicon (path is /resources/abbrs.list).
        self.loadlist(join(self.resources, 'abbrs.list'))

        # Loads the city lexicon (path is /resources/villes.list).
        self.loadlist(join(self.resources, 'villes.list'))

    def tokenize(self, text):
        """
        Tokenize the sentence given in parameter and return a list of tokens.

        This is a two-steps process:
        1. tokenize text using punctuation marks,
        2. merge over-tokenized units using the lexicon or a regex
        """
        if not isinstance(text, str_unicode):
            text = text.decode('utf-8')

        # STEP 1 : tokenize with punctuation
        text = text.replace(u'\u2019', "'")
        tokens = self.regexp.findall(text)

        # STEP 2 : merge over-tokenized units using the lexicons

        # A temporary list used for merging tokens
        tmp_list = []
        i, j = 0, 0

        # Loop and search for mis-tokenized tokens
        while i < len(tokens):
            # The second counter indicates the ending character
            j = i
            # While the second counter does not exceed the last word
            while j <= len(tokens) and (j - i) < 10:
                candidate = ''.join([tokens[k] for k in range(i, j)])
                # Check if the candidate word must be tokenized:
                # in the dictionary or corresponds to a compound with uppercase first letters
                if candidate.lower() in self.lexicon or (re.match(r'^[A-Z]\w+-[A-Z]\w+', candidate, flags=re.U) and (j - i) < 4):
                    # Place first counter on the last word
                    i = j - 1
                    # Replace the i-th token by the candidate
                    tokens[i] = candidate
                    # Stop the candidate construction
                    break
                # Increment second counter
                j += 1
            # Add the token to the temporary list
            tmp_list.append(tokens[i])
            # Increment First counter
            i += 1
        # Return the tokenized text
        return tmp_list

    def loadlist(self, path):
        """
        Load a resource list and generate the corresponding regexp part
        """
        with open(path, 'rb') as f:
            lines = f.read().decode('utf-8').lower().splitlines()
        lines = [line.strip('\r\n ') for line in lines]
        lines = [line for line in lines if bool(line) and not line.startswith('#')]
        self.lexicon.update(lines)
