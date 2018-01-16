# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import feedparser
import os
import re
import requests
import urlparse
import urllib2
from pyquery import PyQuery as pq
from http import cookies


# requests
# pyquery

# 将用户关注的专栏转为 opml
# 使用
# python zhuanlan2opml.py <zhihu ID> </path/to/cookie>

user_agent = (
    'Mozilla/5.0 (Windows NT 10.0; WOW64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/55.0.2883.87 Safari/537.36'
)
baseurl = 'https://api.medium.com'
column_url = 'https://api.medium.com'


def urls_full(url):
    if not url:
        return ''
    if url.startswith(baseurl):
        return url
    if url.startswith(column_url):
        return url
    if url[0] != '/':
        url = '/' + url
    return baseurl + url


def urls_user(url_token, user_type):
    if user_type == 'organization':
        user_type = 'org'
    return '%s/%s/%s' % (baseurl, user_type, url_token)


def urls_column(column_id):
    return '%s/%s' % (column_url, column_id)


def profile(data):
    data['url'] = urls_user(data['url_token'], data['user_type'])
    return data


def user_following_columns(data):
    data = data['data']
    for obj in data:
        author = obj['author']
        obj['url'] = urls_column(obj['id'])
        author['url'] = urls_user(author['url_token'], author['user_type'])
    return data


class Request(object):
    """This class is just a wrapper for requests package."""

    def __init__(self):
        """Initialize a request instance.

        `_raw` is a flag to show whether or not return the raw response body.
        This is only available for zhihu v4 api that returns a JSON format
        response body.
        """
        self.headers = {
            'Cookie': '',
            'Authorization': '',
            'Referer': baseurl,
            'User-Agent': user_agent
        }
        self._xsrf = ''
        self._raw = False

    def setCookie(self, cookie):
        c = cookies.SimpleCookie()
        c.load(cookie)
        if 'z_c0' not in c:
            raise Exception('Invalid cookie: '
                            'no authorization (z_c0) in cookie')
        if '_xsrf' not in c:
            raise Exception('Invalid cookie: no _xsrf in cookie')
        self.headers['Cookie'] = cookie.strip()
        self.headers['Authorization'] = 'Bearer %s' % c['z_c0'].value
        self._xsrf = c['_xsrf'].value
    
    def setHeaders(self, headers=None):
        if headers:
            self.headers.update(headers)

    def request(self, method, url, **kwargs):
        url = urls_full(url)
        if "medium.com" in url:
            proxies = {
                'http': 'http://127.0.0.1:18123',
                'https': 'http://127.0.0.1:18123',
            }
        print(self.headers)
        r = requests.request(method, url, headers=self.headers, proxies=proxies, **kwargs)
        content_type = r.headers['content-type']
        if 'application/json' in content_type:
            return r.json()
        else:
            return pq(r.text)

    def get(self, url, params=None):
        return self.request('GET', url, params=params)

    def post(self, url, data=None, json=None):
        return self.request('POST', url, data=data, json=json)

    def delete(self, url):
        return self.request('DELETE', url)


class Medium:

    def __init__(self, access_token):
        self.req = Request()
        self.req.setHeaders({
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
            })
        self.user_id = None
        self.username = None

    def profile(self):
        """Get profile of this user."""
        url = '/v1/me'
        params = None
        data = self.req.get(url, params)
        print(data)
        return data

    def publications(self):
        """Get publications that this user followed.

        Returns:
            A list of columns.
        """
        if not self.user_id:
            data = self.profile()
            self.user_id = data["data"]["id"]
        url = '/v1/users/{}/publications'.format(self.user_id)
        params = None
        data = self.req.get(url, params)
        return data

    def followings(self):
        path = os.path.dirname(__file__)
        with open(os.path.join(path, "following.html")) as f:
            html = f.read()
        regex = re.compile(r'https:\/\/medium.com\/@[a-zA-Z0-9]*', re.I)
        results = regex.findall(str(html))
        followings = list(set(results))
        len_medium = len("https://medium.com/")
        fs = []
        proxy = urllib2.ProxyHandler( {"http":"http://127.0.0.1:18123", "https":"http://127.0.0.1:18123"} )
        for following in followings:
            print(following)
            d = feedparser.parse(following[:len_medium] + "feed/" + following[len_medium:], handlers=[proxy])
            title = d.get("feed", {}).get("title", "")
            if not title:
                print("FAILED ==> {}".format(following))
                continue
            if "Stories by " in title:
                title = title[len("Stories by "):]
            if " on Medium" in title:
                title = title[:-len(" on Medium")]
            fs.append({
                "name": title,
                "url": following
            })
        return fs

if __name__ == '__main__':

    access_token = sys.argv[1]
    # print(zhihu_id)
    # print(cookie)
    with open(access_token) as f:
        user = Medium(f.read())
    
    followings = user.followings()
    columns = user.publications()["data"]
    columns += followings
    # print(columns[0])
    outline = '<outline type="rss" text="{text} - Medium" title="{title} - Medium" xmlUrl="{xml_url}" htmlUrl="{html_url}"/>'
    outlines = []
    len_medium = len("https://medium.com/")
    for column in columns:
        print(column)
        if column["url"].startswith("https://medium.com/"):
            xml_url = column["url"][:len_medium] + "feed/" + column["url"][len_medium:]
        else:
            xml_url = urlparse.urljoin(column["url"], "feed")
        outlines.append(outline.format(**{
            "text": column['name'],
            "title": column['name'],
            "xml_url": xml_url,
            "html_url": column["url"]
        }))

    opml = """<?xml version="1.0" encoding="UTF-8"?>
    <opml version="1.0">
        <head>
            <title>Feedly Cloud</title>
        </head>
        <body>
            <outline text="Medium" title="Medium">
                {outline}
            </outline>
        </body>
    </opml>

    """.format(**{"outline": '\n'.join(outlines)})

    with open('feedly.opml', 'w') as file:
        file.write(opml)
