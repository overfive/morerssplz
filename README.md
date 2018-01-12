各种转 RSS 服务。目前支持**知乎专栏**、**知乎动态**和**v2ex 评论**。

网站的使用方法见 [https://rss.qiwihui.com](https://rss.qiwihui.com)。

程序依赖：

* Python >= 3.5
* Tornado
* PyRSS2Gen
* lxml

程序源码许可证： GPLv3


## Installation

1. 安装 python3.5+环境

see [Installing Python 3 on Linux](http://python-guide.readthedocs.io/en/latest/starting/install3/linux/)

2. 安装

```bash
aptitude install python3-pip libxml2-dev libxslt-dev python-dev
pip3 install -r requirements.txt
```

## 运行

```bash
python3 main.py
```

## 小脚本

添加以下服务到InoReader中：

- 知乎专栏
- Medium
  - User
  - Publications
  - Custom domains
- 简书
  - 专题(`http://www.jianshu.com/c/`)
  - 作者(`http://www.jianshu.com/u/`)
  - 文集(`http://www.jianshu.com/nb/`)

将以下代码添加到书签栏即可

```js
javascript:(function(){var u='https://www.inoreader.com/?add_feed=';var l=location;c=l.pathname.split('/')[1];if(l.host=='medium.com'){u+=l.protocol+'//'+l.host+'/feed/'+c}else if(l.host=='zhuanlan.zhihu.com'){u+=l.protocol+'//'+l.host+'/'+c}else if(l.host=='www.jianshu.com'){cid=l.pathname.split('/')[2];if(c=='u'){u+='http://jianshu.milkythinking.com/feeds/users/'+cid}else if(c=='u'){u+='http://jianshu.milkythinking.com/feeds/collections/'+cid}else if(c=='nb'){u+='http://jianshu.milkythinking.com/feeds/notebooks/'+cid}else{alert("not supported!");return}}else{u+=l.protocol+'//'+l.host+'/feed'}if(confirm(u)){l.href=u}else{return}})()
```
或者将 [RSS2InoReader](javascript:(function(){var u='https://www.inoreader.com/?add_feed=';var l=location;c=l.pathname.split('/')[1];if(l.host=='medium.com'){u+=l.protocol+'//'+l.host+'/feed/'+c}else if(l.host=='zhuanlan.zhihu.com'){u+=l.protocol+'//'+l.host+'/'+c}else if(l.host=='www.jianshu.com'){cid=l.pathname.split('/')[2];if(c=='u'){u+='http://jianshu.milkythinking.com/feeds/users/'+cid}else if(c=='u'){u+='http://jianshu.milkythinking.com/feeds/collections/'+cid}else if(c=='nb'){u+='http://jianshu.milkythinking.com/feeds/notebooks/'+cid}else{alert("not supported!");return}}else{u+=l.protocol+'//'+l.host+'/feed'}if(confirm(u)){l.href=u}else{return}})()) 拖入书签栏即可

## 注意

1. [lxml installation error ubuntu 14.04 (internal compiler error)](https://stackoverflow.com/questions/24455238/lxml-installation-error-ubuntu-14-04-internal-compiler-error)
