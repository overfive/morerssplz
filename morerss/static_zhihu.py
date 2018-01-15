import json
import re

from tornado.httpclient import AsyncHTTPClient
from lxml.html import fromstring, tostring

from . import base
from .base import BaseHandler
from .zhihu_stream import tidy_content, re_zhihu_img

httpclient = AsyncHTTPClient()

page_template = '''\
<!DOCTYPE html>
<meta charset="utf-8" />
<meta name="referrer" value="no-referrer" />
<title>{title} - {author}</title>
<style type="text/css">
body {{ max-width: 700px; margin: auto; }}
</style>
<h2>{title}</h2>
<h3>作者: {author}</h3>
{body}
<hr/>
<footer><a href="https://zhuanlan.zhihu.com/p/{id}">原文链接</a></footer>
'''

class StaticZhihuHandler(BaseHandler):
  async def get(self, id):
    pic = self.get_argument('pic', None)
    page = await self._get_url(f'https://zhuanlan.zhihu.com/p/{id}')
    doc = fromstring(page)
    content = doc.xpath('//textarea[@id="preloadedState" and @hidden]')[0].text_content()
    # fix new Date("....") values
    content = re.sub(r'new Date\("([^"]+)"\)', r'"\1"', content)
    content = json.loads(content)

    post = content['database']['Post'][id]
    title = post['title']
    author = post['author']
    body = post['content']
    author = content['database']['User'][author]['name']

    doc = fromstring(body)
    body = tidy_content(doc)

    if pic:
      base.proxify_pic(doc, re_zhihu_img, pic)

    body = tostring(doc, encoding=str)
    self.set_header('Content-Type', 'text/html; charset=utf-8')
    self.finish(page_template.format_map(vars()))

  async def _get_url(self, url):
    res = await httpclient.fetch(url, raise_error=False)
    if res.code in [404, 429]:
      raise web.HTTPError(res.code)
    else:
      res.rethrow()
    return res.body.decode('utf-8')
