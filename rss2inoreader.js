javascript: (
    function () {
        var u = 'https://www.inoreader.com/?add_feed=';
        var l = location;
        c = l.pathname.split('/')[1];
        if (l.host == 'medium.com') {
            u += l.protocol + '//' + l.host + '/feed/' + c;
        } else if (l.host == 'zhuanlan.zhihu.com') {
            u += l.protocol + '//' + l.host + '/' + c;
        } else if (l.host == 'www.jianshu.com') {
            cid = l.pathname.split('/')[2];
            if (c == 'u') {
                u += 'http://jianshu.milkythinking.com/feeds/users/' + cid;
            } else if (c == 'u') {
                u += 'http://jianshu.milkythinking.com/feeds/collections/' + cid;
            } else if (c == 'nb') {
                u += 'http://jianshu.milkythinking.com/feeds/notebooks/' + cid;
            } else {
                alert("not supported!");
                return
            }
        } else {
            u += l.protocol + '//' + l.host + '/feed';
        }
        if (confirm(u)) {
            l.href = u;
        } else {
            return
        }
    })()