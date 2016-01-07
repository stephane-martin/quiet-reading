# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import bs4

# <meta name="twitter:image" content="http://media.guim.co.uk/0_172_597_358/master/597.jpg"/>
# <meta name="thumbnail" content="https://i.guim.co.uk/img/media/0_172_597_358/master/597.jpg"/>
# <meta property="og:image" content="http://md1.libe.com/photo/robert-fico-a-bruxelles-le-7-juillet-2015.jpg>


def extract_favicon_url(whole_soup):
    # <link rel="shortcut icon" type="image/png" href="favicon.png" />
    # <link rel="icon" type="image/png" href="favicon.png" />
    pass


def extract_main_image(whole_soup):
    pass


def extract_top_image(top_node):
    pass


def extract_largest_image(whole_soup):
    pass
