#coding=utf-8
import sys
import MySQLdb
import MySQLdb.cursors
import HTMLParser
from lxml import etree
import re,urllib2,random
reload(sys)
sys.setdefaultencoding('utf-8')


def getRegex(pattern, content):
    group = re.search(pattern, content)
    if group:
        return group.groups()[0]
    else:
        return ''


def getXpath(xpath, content):  # xptah操作貌似会把中文变成转码&#xxxx;  /text()变unicode编码
    tree = etree.HTML(content)
    out = []

    results = tree.xpath(xpath)

    for result in results:
        if 'ElementStringResult' in str(type(result)) or 'ElementUnicodeResult' in str(type(result)):
            out.append(result)
        else:
            out.append(etree.tostring(result))
    return out

def download_page(url, proxy = None, referer = None):
    page_buf = ''
    i = 0
    for i in range(3):
        try:
            if proxy:
              handlers = [urllib2.ProxyHandler({'http': 'http://%s/' % proxy,'https': 'http://%s/' % proxy})]
              opener =  urllib2.build_opener(*handlers)
            else:
              opener   =  urllib2.build_opener()
              method   =  urllib2.Request(url)
            if referer:
              method.add_header('Referer', referer)
            USER_AGENT_LIST = [ \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
                "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
                "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1", \
                "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
                "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
                "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)", \
                "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)", \
                "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)", \
                "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)", \
                "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)", \
                "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)", \
                "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)", \
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)", \
                "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6", \
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1", \
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0", \
                "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5", \
                "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6", \
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11", \
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20"
            ]
            ua = random.choice(USER_AGENT_LIST)
            method.add_header('User-Agent', ua)
            method.add_header('Accept-Language', 'en-US,en;q=0.5')
            result   =  opener.open(method, timeout=10)
            page_buf =  result.read()
            return page_buf
        except urllib2.URLError, reason:
            return str(reason)
        except Exception, reason:
            if i == 2:
                raise Exception(reason)


if __name__ == '__main__':
    url='https://bbs.ppmoney.com/forum.php'
    data = download_page(url)
    h = HTMLParser.HTMLParser()

    #print data

    items = getXpath('//div[@class="mn sxpmn"]/div/div/div[@class="bm_c"]/table/tr/td/div/a/@href',data)
    for item in items:

        plateUrl='https://bbs.ppmoney.com/'+str(item)
        #print plateUrl
        urlDepth0 = plateUrl
        for start in range(10000):
            try:
                plateUrlData = download_page(urlDepth0)
                #plateUrlData =h.unescape(plateUrlData)
            except Exception,e:
                print e
                continue

            plateTitle = getRegex(u'%s">(.*?)<' % str(item),plateUrlData)
            #print plateTitle
            posts = getXpath('//table[@summary="forum_120"]/tbody',plateUrlData)
            for post in posts:
                postTitle = h.unescape(getRegex(u's xst">(.*?)<',post))
                #print postTitle
                post_url = getXpath('//tbody/tr/th/a[3]/@href',post)[0]
                postUrl = 'https://bbs.ppmoney.com/'+str(post_url)
                #print postUrl

                urlDepth1 = postUrl
                for start1 in range(10000):
                    try:
                        postUrlData = download_page(urlDepth1)
                        #postUrlData =  h.unescape(postUrlData)
                    except Exception, e:
                        print e
                        continue

                    postLists = getXpath('//div[@id="postlist"]/div',postUrlData)
                    for postList in postLists:
                        try:
                            dateOfPost = getXpath('//table/tr/td[@class="plc"]/div[@class="pi"]/div[@class="pti"]/div[@class="authi"]/em/span/@title',postList)[0]
                        except:
                            break
                        post_content = h.unescape(getRegex(u'class="t_f".*?>([\d\D]*?)<\/td>',postList))
                        postContent=re.sub('<.*?>','',post_content).strip()

                        #print postContent

                        posting_url =getXpath('//table/tr/td[@class="pls"]/div/div[@class="pi"]/div/a/@href',postList)[0]
                        postingUrl = 'https://bbs.ppmoney.com/'+str(posting_url)
                       # print 'postingUrl:'+postingUrl
                        try:
                            postingUrlData = download_page(postingUrl)
                        except Exception, e:
                            print e
                            continue

                        posting = h.unescape(getXpath('//h2[@class="mt"]/text()',postingUrlData)[0]).strip()
                       # print posting

                        postingUID = getRegex('UID: (\d+)',postingUrlData)
                        #print postingUID
                        friendsNum = getRegex('好友数 (\d+)<',postingUrlData)
                        #print friendsNum
                        logNum = getRegex('日志数 (\d+)<',postingUrlData)
                       # print logNum
                        subjectsNum = getRegex('主题数 (\d+)<',postingUrlData)
                       # print subjectsNum
                        repliesNum = getRegex('回帖数 (\d+)<',postingUrlData)
                       # print repliesNum
                        shareNum = getRegex('分享数 (\d+)<',postingUrlData)
                       # print shareNum
                        sex = h.unescape(getRegex('性别<\/em>(.*?)<',postingUrlData))
                       # print sex
                        birthday = getRegex('生日</em>(.*?)<',postingUrlData)
                       # print birthday
                        education = h.unescape(getRegex('学历</em>(.*?)<',postingUrlData))
                       # print education

                        onlineTime = getRegex('在线时间</em>([\d\D]*?)<',postingUrlData)
                       # print onlineTime
                        registrationTime = getRegex('注册时间</em>([\d\D]*?)<',postingUrlData)
                       # print registrationTime
                        finalVisit = getRegex('最后访问</em>([\d\D]*?)<',postingUrlData)
                       # print finalVisit
                        lastTimeOfActivity = getRegex('上次活动时间</em>([\d\D]*?)<',postingUrlData)
                       # print lastTimeOfActivity
                        lastTime = getRegex('上次发表时间</em>([\d\D]*?)<',postingUrlData)
                       # print lastTime
                        timeZone =h.unescape(getRegex('所在时区</em>([\d\D]*?)<',postingUrlData))
                        #print timeZone

                        wealthValue  = getRegex('财富值</em>([\d\D]*?)<',postingUrlData)
                        #print wealthValue
                        contribution = getRegex('贡献</em>([\d\D]*?)<',postingUrlData)
                        #print contribution

                        userGroup=h.unescape(getRegex('用户组.*?>(.*?)<',postingUrlData))
                        #print userGroup

                        conn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='password',
                                               db='otherProject',charset = 'utf8')
                        with conn:
                            cur = conn.cursor(MySQLdb.cursors.DictCursor)
                            sql="INSERT INTO ppmoney (plate,plateUrl,postTitle,postTitleUrl,postingUrl,posting,postingUID,friendsNum,logNum,repliesNum,subjectsNum,shareNum,sex,birthday,education,userGroup,onlineTime,registrationTime,finalVisit,lastTimeOfActivity,lastTime,timeZone,wealthValue,contribution,dateOfPost,postContent) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'); " % (plateTitle,plateUrl,postTitle,postUrl,postingUrl,posting,postingUID,friendsNum,logNum,repliesNum,subjectsNum,shareNum,sex,birthday,education,userGroup,onlineTime,registrationTime,finalVisit,lastTimeOfActivity,lastTime,timeZone,wealthValue,contribution,dateOfPost,postContent)
                            #print sql
                            cur.execute(sql)
                            conn.commit()
                        cur.close()
                        conn.close()


                    if 'class="nxt"' not in postUrlData:
                        break
                    else:
                        page =getXpath('//a[@class="nxt"]/@href',postUrlData)[0]
                        urlDepth1 = 'https://bbs.ppmoney.com/'+str(page)



            if 'class="nxt"' not in plateUrlData:
                break
            else:
                nextPage = getXpath('//a[@class="nxt"]/@href',plateUrlData)[0]
                urlDepth0='https://bbs.ppmoney.com/'+str(nextPage)
