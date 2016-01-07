# vim: set fileencoding=utf-8 :

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import cgi

# noinspection PyPackageRequirements
import readability.readability
import bs4
import spooky
import requests
from future.moves.urllib.parse import urljoin


class Article(object):
    def __init__(self, url=b'', id=b'', etag=b'', last_modified=b'', summary='', title='', text=''):
        self.url = url
        self.etag = etag
        self.last_modified = last_modified
        self.summary = summary
        self.title = title
        self.text = text
        if id:
            self.id = id
        else:
            self.id = b'%x' % spooky.hash128(url) if url else id

    @classmethod
    def factory(cls, url=b'', h=b'', etag=b'', last_modified=b'', summary='', title='', text=''):
        return cls(url=url, h=h, etag=etag, last_modified=last_modified, summary=summary, title=title, text=text)

    def __copy__(self):
        return self.factory(
            url=self.url, h=self.id, etag=self.etag, last_modified=self.last_modified, summary=self.summary,
            title=self.title, text=self.title
        )

    def __hash__(self):
        return hash((self.url, self.id, self.etag, self.last_modified, self.text, self.title))

    @classmethod
    def from_redis(cls, id, redis_conn):
        if (not redis_conn) or (not id):
            return None
        if not redis_conn.exists(id):
            return None
        l = redis_conn.hmget(id, ['url', 'etag', 'last_modified', 'summary', 'title', 'text'])
        return cls(
            url=l[0], etag=l[1], last_modified=l[2], summary=l[3].decode('utf-8'), title=l[4].decode('utf-8'),
            text=l[5].decode('utf-8')
        )

    @classmethod
    def fetch(cls, url=b'', id=b'', redis_conn=None):
        article_from_redis = cls.from_redis(id, redis_conn)
        article = article_from_redis if article_from_redis else cls(url=url, id=id)

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
            article._complete_from_response(resp)
        else:
            raise requests.RequestException("unexpected status code: {}".format(resp.status_code))
        return article

    def _complete_from_response(self, resp):
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
        fix_summary_soup(summary_soup)

        self.summary = summary_soup.find('div', id='quiet-reading-main-content').prettify()
        self.text = summary_soup.text.strip('\r\n ')

    def to_redis(self, redis_conn=None):
        if not redis_conn:
            return
        redis_conn.hmset(self.id, {
            'url': self.url,
            'etag': self.etag,
            'last_modified': self.last_modified,
            'summary': self.summary,
            'title': self.title,
            'text': self.text
        })
        return self


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


def fix_summary_soup(summary_soup):
    # for lemonde.fr, correct figcaption so that image captions are displayed correctly
    for tag in summary_soup.find_all('figcaption', class_="legende", attrs={"data-caption": True}):
        tag.string = tag['data-caption']
    return summary_soup
