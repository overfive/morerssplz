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
# python jianshu2opml.py <jianshu_ID> </path/to/cookie>

user_agent = (
    'Mozilla/5.0 (Windows NT 10.0; WOW64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/55.0.2883.87 Safari/537.36'
)
baseurl = 'https://www.jianshu.com'
column_url = 'https://www.jianshu.com'


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

def get_column_source_type(source_type):
    l_source_type = source_type.lower()
    if l_source_type == 'user':
        return "作者"
    elif l_source_type == "collection":
        return "专题"
    else:
        # notebook
        return "文集"

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
        # if 'z_c0' not in c:
        #     raise Exception('Invalid cookie: '
        #                     'no authorization (z_c0) in cookie')
        # if '_xsrf' not in c:
        #     raise Exception('Invalid cookie: no _xsrf in cookie')
        self.headers['Cookie'] = cookie.strip()
        self.headers['Accept'] = 'application/json'

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


class Jianshu:

    def __init__(self, cookie):
        self.req = Request()
        self.req.setCookie(cookie)

    def get_following_subscriptions(self, page=0):
        """Get subscriptions of Users/Collections/Notebooks that this user followed.

        Args:
            offset: An integer.

        Returns:
            A list of columns.
        """
        url = '/subscriptions?types[]=user&types[]=collection&types[]=notebook&only_push_enabled=false&page={}'.format(page)
        data = self.req.get(url, params=None)
        return data
    
    def get_all_following_subscriptions(self):
        all_subs = []
        subs = self.get_following_subscriptions(page=0)
        total_pages = subs["total_pages"]
        all_subs = subs["subscriptions"]
        if total_pages > 1:
            for page in range(1, total_pages):
                subs = self.get_following_subscriptions(page=page)
                all_subs += subs["subscriptions"]
        return all_subs

    def get_subscription_detail(self, sub_id):
        url = '/subscriptions/{}'.format(sub_id)
        data = self.req.get(url, params=None)
        return data

    
if __name__ == '__main__':

    cookie = sys.argv[1]
    # print(zhihu_id)
    # print(cookie)
    with open(cookie) as f:
        jianshu_user = Jianshu(f.read())
    columns = jianshu_user.get_all_following_subscriptions()
    # print(columns[0])
    outline = '<outline type="rss" text="简书 • {source_type} • {text}" title="简书 • {source_type} • {title}" xmlUrl="{xml_url}" htmlUrl="{html_url}"/>'
    outlines = []
    for column in columns:
        print(column)
        l_source_type = column["source_type"].lower()
        detail = jianshu_user.get_subscription_detail(column["id"])
        if l_source_type in ["user", "collection"]:
            column_id = detail["source"]["slug"]
        elif l_source_type == "notebook":
            column_id = detail["source_id"]
        else:
            raise Exception("no idea")

        outlines.append(outline.format(**{
            "source_type": get_column_source_type(column["source_type"]),
            "text": column['name'],
            "title": column['name'],
            "xml_url": "http://jianshu.milkythinking.com/feeds/{}/{}".format(l_source_type+"s", column_id),
            "html_url": "http://www.jianshu.com/{}/{}".format(
                "nb" if l_source_type.startswith("notebook") else l_source_type[0],
                column_id
                )
        }))

    opml = """<?xml version="1.0" encoding="UTF-8"?>
    <opml version="1.0">
        <head>
            <title>Feedly Cloud</title>
        </head>
        <body>
            <outline text="简书" title="简书">
                {outline}
            </outline>
        </body>
    </opml>

    """.format(**{"outline": '\n'.join(outlines)})

    with open('feedly.opml', 'w') as file:
        file.write(opml)
