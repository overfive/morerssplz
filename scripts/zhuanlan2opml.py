# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import requests
import sys
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
baseurl = 'https://www.zhihu.com'
column_url = 'https://zhuanlan.zhihu.com'


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

    def request(self, method, url, **kwargs):
        url = urls_full(url)
        r = requests.request(method, url, headers=self.headers, **kwargs)
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


class Zhihu:

    def __init__(self, url_token, cookie):
        self.url_token = url_token
        self.req = Request()
        self.req.setCookie(cookie)

    def profile(self, include=None):
        """Get profile of this user."""
        url = '/api/v4/members/%s' % self.url_token
        params = {}
        if include:
            includes = ','.join(include) if include else ''
            params["include"] = includes
        data = self.req.get(url, params)
        return data if self.req._raw else profile(data)

    def following_columns(self, offset=0):
        """Get columns that this user followed.

        Args:
            offset: An integer.

        Returns:
            A list of columns.
        """
        url = '/api/v4/members/%s/following-columns' % self.url_token
        params = {
            'offset': offset,
            'limit': 20,
            'include': ','.join([
                'data[*].intro',
                'followers',
                'articles_count',
                'image_url',
                'is_following'
            ])
        }
        data = self.req.get(url, params)
        return data if self.req._raw else user_following_columns(data)


if __name__ == '__main__':

    zhihu_id = sys.argv[1]
    cookie = sys.argv[2]
    # print(zhihu_id)
    # print(cookie)
    with open(cookie) as f:
        user = Zhihu(zhihu_id, f.read())
    profile = user.profile(include=['following_columns_count'])
    following_columns_count = int(profile.get("following_columns_count", 0))
    columns = []
    for step in range(0, following_columns_count, 20):
        columns += user.following_columns(offset=step)
    # print(columns[0])
    outline = '<outline type="rss" text="{text} (Zhihu)" title="{title} (Zhihu)" xmlUrl="{xml_url}" htmlUrl="{html_url}"/>'
    outlines = []
    for column in columns:
        print(column)
        outlines.append(outline.format(**{
            "text": column['title'],
            "title": column['title'],
            "xml_url": "https://zhuanlan.zhihu.com/" + column["id"],
            "html_url": column["url"]
        }))

    opml = """<?xml version="1.0" encoding="UTF-8"?>
    <opml version="1.0">
        <head>
            <title>Feedly Cloud</title>
        </head>
        <body>
            <outline text="知乎专栏" title="知乎专栏">
                {outline}
            </outline>
        </body>
    </opml>

    """.format(**{"outline": '\n'.join(outlines)})

    with open('feedly.opml', 'w') as file:
        file.write(opml)
