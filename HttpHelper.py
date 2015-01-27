#coding: utf-8

import urllib
import urllib2
import cookielib
import HTMLParser
import socket
import logging


class HttpHelper:
    def __init__(self):
        self.timeout = 5
        self.repeat = 5
        self.cj = cookielib.CookieJar()
        proxy_handler = urllib2.ProxyHandler({'http' : ''})
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj), proxy_handler)
        # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.1)')]
        urllib2.install_opener(opener)

    def setTimeout(self, timeout):
        self.timeout = int(timeout)

    def setRepeat(self, repeat):
        self.repeat = int(repeat)

    def getCookies(self):
        # for cookie in self.cj:
        #     print cookie.value
        return self.cj
        # for cookie in self.cj:
        #     print cookie

    def sendRequest(self, type, url, dic=None):
        self.url = url
        if type == 'get':
            if dic is not None:
                url += '?'
                for k,v in dic:
                    url += urllib.urlencode(k) + '=' + urllib.urlencode(v) + '&'
            req = urllib2.Request(url)
        elif type == 'post':
            req = urllib2.Request(url, urllib.urlencode(dic))
        else:
            print 'Unkown type'
            return
        req.add_header("Referer", url)
        # 多次尝试
        for tries in range(self.repeat):
            try:
                resp = urllib2.urlopen(req, timeout=self.timeout)
                # print resp.info()
                return resp.read()
                break # successfully, so break now
            except:
                if tries < (self.repeat - 1) :
                    logging.warning("Access url %s fail, do %d retry", url, (tries + 1));
                    continue;
                else: # last try also failed, so exit
                    logging.error("Has tried %d times to access url %s, all failed!", self.repeat, url);
                    break;

    def __del__(self):
        pass

# __all__ = [SendRequest,]
if __name__ == '__main__':
    pass
