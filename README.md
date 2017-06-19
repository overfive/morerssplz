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

## 注意

1. [lxml installation error ubuntu 14.04 (internal compiler error)](https://stackoverflow.com/questions/24455238/lxml-installation-error-ubuntu-14-04-internal-compiler-error)
