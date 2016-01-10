# vim: set fileencoding=utf-8 :

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import cgi
import json

# noinspection PyPackageRequirements
import readability.readability
import bs4
import spooky
import requests
from future.moves.urllib.parse import urljoin
from future.builtins import str as str_unicode


def make_utf8(x):
    return x.encode('utf-8') if isinstance(x, str_unicode) else x


class Article(object):

    def __init__(self, url=b'', id='', etag=b'', last_modified=b'', summary='', title='', text=''):
        url = make_utf8(url)
        self.url = url
        self.etag = etag
        self.last_modified = last_modified
        self.summary = summary
        self.title = title
        self.text = text
        if id:
            self.id = id
        else:
            self.id = '%x' % spooky.hash128(url) if url else id

    def to_json(self):
        return json.dumps({
            'url': self.url,
            'etag': self.etag,
            'last_modified': self.last_modified,
            'summary': self.summary,
            'title': self.title,
            'text': self.text
        })

    @classmethod
    def from_json(cls, json_text):
        d = json.loads(json_text)
        return cls(
            url=d['url'], etag=d['etag'], last_modified=d['last_modified'], summary=d['summary'],
            title=d['title'], text=d['text']
        )

    @classmethod
    def factory(cls, url=b'', id='', etag=b'', last_modified=b'', summary='', title='', text=''):
        return cls(url=url, id=id, etag=etag, last_modified=last_modified, summary=summary, title=title, text=text)

    def __copy__(self):
        return self.factory(
            url=self.url, id=self.id, etag=self.etag, last_modified=self.last_modified, summary=self.summary,
            title=self.title, text=self.title
        )

    def __hash__(self):
        return hash((self.url, self.id, self.etag, self.last_modified, self.text, self.title))

    @classmethod
    def from_cache(cls, id, article_cache):
        if (not article_cache) or (not id):
            return None
        a = article_cache.get(id)
        return None if a is None else cls.from_json(a)

    def to_cache(self, article_cache):
        if not article_cache:
            return
        article_cache.set(self.id, self.to_json())
        return self

    @classmethod
    def fetch(cls, url=b'', id='', article_cache=None, image_store=None):
        article_from_cache = cls.from_cache(id, article_cache)
        article = article_from_cache if article_from_cache else cls(url=url, id=id)

        if not article.url:
            raise requests.RequestException("No URL provided, or unknown ID")

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0'}
        if article.etag:
            headers['If-None-Match'] = article.etag
        if article.last_modified:
            headers['If-Modified-Since'] = article.last_modified
        resp = requests.get(article.url, headers=headers)
        resp.raise_for_status()

        if resp.status_code == 304:
            # not modified
            pass
        elif resp.status_code == 200:
            content_type = resp.headers.get('content-type')
            if not content_type:
                raise requests.RequestException("content_type header is not set")
            if 'text/html' not in content_type:
                raise requests.RequestException("content_type is not text/html")
            article._complete_from_response(resp, image_store)
        else:
            raise requests.RequestException("unexpected status code: {}".format(resp.status_code))
        return article

    def _complete_from_response(self, resp, image_store):
        assert(isinstance(resp, requests.Response))
        self.etag = resp.headers.get('ETag', b'')
        self.last_modified = resp.headers.get('Last-Modified', b'')
        # in case encoding is not defined in the response headers
        content_type, params = cgi.parse_header(resp.headers.get('content-type'))
        if 'charset' not in params:
            resp.encoding = resp.apparent_encoding
        t = resp.text

        whole_article_soup = bs4.BeautifulSoup(t, 'lxml')
        clean_soup(whole_article_soup)

        readability_obj = readability.readability.Document(t)
        self.title = readability_obj.short_title()
        summary_soup = bs4.BeautifulSoup(
            "<div id='quiet-reading-main-content'>" + readability_obj.summary(True) + "</div>", 'lxml'
        )
        clean_soup(summary_soup)
        fix_summary_soup(summary_soup, image_store)

        self.summary = summary_soup.find('div', id='quiet-reading-main-content').prettify()
        self.text = summary_soup.text.strip('\r\n ')




def clean_soup(soup, url=None):
    # delete video and objects
    for tag_name in ['iframe', 'embed', 'object', 'video']:
        for tag in soup.find_all(tag_name):
            tag.replace_with('\n')

    if url:
        # make links absolute
        base_tag = soup.find('base', href=True)
        base_url = urljoin(url, base_tag['href']) if base_tag else url
        for tag in soup.find_all('a', href=True):
            tag['href'] = urljoin(base_url, tag['href'])
        for tag in soup.find_all('link', href=True):
            tag['href'] = urljoin(base_url, tag['href'])

    return soup


def fix_summary_soup(summary_soup, image_store):
    # if the original article has mentioned a main image, and if its not present in the summary, add it
    if image_store:
        # download images and replace image links
        img_tags = summary_soup.find_all('img', src=True)
        old_urls = [tag['src'] for tag in img_tags]
        assoc_old_url_new_url = image_store.add_many(old_urls)
        assoc_tag_new_url = [(tag, assoc_old_url_new_url[tag['src']]) for tag in img_tags]
        [tag.attrs.__setitem__('src', new_url) for (tag, new_url) in assoc_tag_new_url if new_url]

    # for lemonde.fr, correct figcaption so that image captions are displayed correctly
    for tag in summary_soup.find_all('figcaption', class_="legende", attrs={"data-caption": True}):
        tag.string = tag['data-caption']
    return summary_soup
