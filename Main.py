# coding:UTF-8

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui  import *
from PyQt4.QtCore  import *
import View
from Constants import Constants
from xlwt.Workbook import *
import xlrd
import os
import shutil
import codecs
import time
import sys
import re
import urllib
import urllib2
import cookielib
import HTMLParser
import HttpHelper
import webbrowser
from RowItem import RowItem
from BeautifulSoup import BeautifulSoup


class Example(QtGui.QMainWindow):
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):
        self.ui = View.Ui_MainWindow()
        self.ui.setupUi(self)
        # 初始化httpHelper
        self.httpHelper = HttpHelper.HttpHelper()
        self.constants = Constants()
        # 得到今天日期
        today = QDate.currentDate().toString('yyyy-MM-dd')
        temp = today.split('-')
        self.year = temp[0]
        self.month = temp[1]
        self.day = temp[2]
        # 设置默认ui
        self.ui.outputTextEdit.setReadOnly(True)
        # 设置event响应
        self.ui.payBtn.clicked.connect(self.directPayAll)
        self.ui.refreshBtn.clicked.connect(self.refreshAll)
        # self.ui.refreshBtn.clicked.connect(self.refreshYuKou)
        self.ui.mergeBtn.clicked.connect(self.mergeSameRTnum)
        # 得到Cookies
        self.getCookies()

    # 台账数据
    def getRowFromData(self, row):
        tds = row.findAll('td')
        action = ''
        date = tds[1].text.strip()
        liushuihao = tds[2].a.text.strip()
        danjuhao = tds[3].text.strip()
        yewuzhonglei = tds[4].text.strip()
        zhaiyao = tds[5].text.strip()
        jiefang = tds[6].text.strip()
        daifang = tds[7].text.strip()
        money = tds[8].text.strip()
        rtnum =tds[9].text.strip()
        kehuhao = tds[10].span.text.strip()
        name = tds[11].span.text.strip()
        return RowItem(action, date, liushuihao, danjuhao, yewuzhonglei, zhaiyao, jiefang, daifang, money, rtnum, kehuhao, name)

    def refreshAll(self):
        print 'start Refresh'
        self.allResult = []
        searchStr = ''
        i = 1
        while True:
            html = BeautifulSoup(self.refreshPage(i))
            # 发现为空,跳出循环
            # if html.find(class_="empty"):
            if html.find(attrs={'class':'empty'}):
                break
            else:
                rows = html.find(id="sheets").findAll("tr")
                for row in rows[1:]:
                    self.allResult.append(row)
                i = i + 1
        if(self.ui.cbNeedsYuKou.isChecked()):
            print u'下载预扣数据...'
            excel = xlrd.open_workbook(self.refreshYuKou(), formatting_info=True)
            table = excel.sheet_by_index(0)
            listRT = table.col_values(9)[1:]
        # 循环获得一个可用的文件名
        todayTime = '%s-%s-%s' % (self.year, self.month, self.day)
        path = 'source/' + todayTime
        if not os.path.exists(path):
            os.mkdir(path)
        path = path + '/' + todayTime
        while True:
            if os.path.exists(path +'.xls'):
                path += ' 1'
            else:
                path += '.xls'
                break
        excel = Workbook()
        w_sheet = excel.add_sheet('0')
        for i in range(len(self.allResult)):
            aRow = self.getRowFromData(self.allResult[i])
            w_sheet.write(i, 0, aRow.action)
            w_sheet.write(i, 1, aRow.date)
            w_sheet.write(i, 2, aRow.liushuihao)
            w_sheet.write(i, 3, aRow.danjuhao)
            w_sheet.write(i, 4, aRow.yewuzhonglei)
            w_sheet.write(i, 5, aRow.zhaiyao)
            w_sheet.write(i, 6, aRow.jiefang)
            w_sheet.write(i, 7, aRow.daifang)
            w_sheet.write(i, 8, aRow.money)
            w_sheet.write(i, 9, aRow.rtnum)
            w_sheet.write(i, 10, aRow.kehuhao)
            w_sheet.write(i, 11, aRow.name)
        if(self.ui.cbNeedsYuKou.isChecked()):
            for m in range(len(listRT)):
                w_sheet.write(i+m+1, 8, '99999999')
                w_sheet.write(i+m+1, 9, listRT[m])
        excel.save(path)
        print 'end Refresh'

    def refreshPage(self, page):
        url = self.constants.baseurl + "/vfs2/account/sheetRetailAccountBalanceMRSheetList.html" + "?searchFlag=true&mrDate1=%s&mrDate2=&d-447250-p=%d&status=1&moneyStart=&actDate2=&actDate1=&explain=&moneyEnd=" % (self.year + '-' + self.month + '-' + self.day, page)
        print page
        return self.httpHelper.sendRequest('get', url)

    def refreshYuKou(self):
        cookies = self.httpHelper.getCookies()
        url = self.constants.baseurl + "/vfs2/loanmanager/clearingInterfaceReportQuery.html"
        html = BeautifulSoup(self.httpHelper.sendRequest('get', url))
        searchform = html.find(id = "searchform")
        dic = {}
        dic['clearingType'] = 'PreDeduct'
        dic['clearingStatus'] = '1'
        dic['operDateBegin'] = '%s-%s-%s' % (self.year, self.month, self.day)
        dic['operDateEnd'] = '%s-%s-%s' % (self.year, self.month, self.day)
        dic['BRNO'] = '001'
        dic['BZ'] = 'R'
        dic['value'] = self.constants.baseurl + '/vfs2/account/cntSheetDetail.html'
        dic['params'] = html.find(id='params').attrs['value']
        dic['raq'] = '/loanAfter/clearingInterfaceQuery.raq'
        for cookie in cookies:
            dic['sessionId'] = cookie.value
        # print dic
        self.httpHelper.setTimeout(15)
        html = BeautifulSoup(self.httpHelper.sendRequest('post', self.constants.baseurl+'/vfs2/reportMain/reportMain.html', dic))
        html = BeautifulSoup(self.httpHelper.sendRequest('post', 'http://10.116.8.66:7001/VFS2RPT/reportJsp/showReport.jsp', dic))
        # print html
        report1_turnPageForm = html.find("form", attrs={"name":"report1_turnPageForm"})
        action = str(report1_turnPageForm.attrs['action'])
        t_i_m_e = action[action.index('=')+1:]
        reportParamsId = html.find("input", attrs={"name":"reportParamsId"})
        cachedId = html.find("input", attrs={"name":"report1_cachedId"})
        reportParamsId = str(reportParamsId.attrs['value'])
        cachedId = str(cachedId.attrs['value'])
        url = r"http://10.116.8.66:7001/VFS2RPT/reportServlet?action=3&file=%%2FloanAfter%%2FclearingInterfaceQuery.raq&columns=0&srcType=file&width=0&height=0&pageStyle=0&formula=0&reportParamsId=%s&cachedId=%s&t_i_m_e=%s" % (reportParamsId, cachedId, t_i_m_e)
        # print url
        resultData = self.httpHelper.sendRequest('get', url)
        path = u'yukou/%s-%s-%s预扣.xls' % (self.year, self.month, self.day)
        with open(path, 'wb') as f:
            for line in resultData:
                f.write(line)
        self.httpHelper.setTimeout(5)
        return path

    def mergeSameRTnum(self):
        print "begin merge the same rtnum"
        allResult = ''
        allDataArray = []
        allData = {}
        allDataCount = {}
        itemList = self.ui.inputTextEdit.toPlainText().split("\n")
        for line in itemList:
            items = str(line).split('\t')
            while '' in items:
                items.remove('')
            if len(items) > 0:
                items[0] = items[0].replace(',', '')
                print items[1]
                if items[1] not in allData:
                    allData[items[1]] = float(items[0])
                    allDataCount[items[1]] = 1
                    temp = (float(items[0]), items[1], 1)
                    allDataArray.append(temp)
                else:
                    allData[items[1]] += float(items[0])
                    allDataCount[items[1]] += 1
                    for (money, rtnum, count) in allDataArray:
                        if rtnum == items[1]:
                            allDataArray.remove((money, rtnum, count))
                            count += 1
                            money += float(items[0])
                            allDataArray.append((money, rtnum, count))
                            break
        for (money, rtnum, count) in allDataArray:
            allResult += str(money) + '\t' + rtnum + '\t' + str(count) + '\n'
        # for (k,v) in allData.items():
        #     allResult += str(v) + '\t' + k + '\t' + str(allDataCount[k]) + '\n'
        self.ui.inputTextEdit.setPlainText(allResult)
        print "end merge the same rtnum"

    def getAlreadyDirectPayList(self):
        result = []
        reStr = '%s-%s-%s' % (self.year, self.month, self.day)
        todayTime = '%s-%s-%s' % (self.year, self.month, self.day)
        path = 'result/' + todayTime
        if not os.path.exists(path):
            print u'no dict'
            self.log += "no dict" + '\n'
        else:
            print u'read alreadyDirectPayList'
            self.log += "read alreadyDirectPayList" + '\n'
            filelist = os.listdir(path)
            for item in filelist:
                temp = re.match(reStr, item)
                if temp:
                    with open(path + '/' + item, 'r') as f:
                        for line in f:
                            rtnum = line.split(':')[0]
                            if rtnum not in result:
                                result.append(rtnum)
                                print rtnum + u':已添加'
                                self.log += rtnum + u':已添加' + '\n'
                            else:
                                print rtnum + u':已存在'
                                self.log += rtnum + u':已存在' + '\n'
        return result

    def directPayAll(self):
        self.log = ''
        alreadyDirectPayList = self.getAlreadyDirectPayList()
        print "begin"
        self.log += "begin" + '\n'
        resultToWrite = ''
        resultToShow = ''
        itemList = self.ui.inputTextEdit.toPlainText().split("\n")
        index = 1
        # 得到输入框中输入的个数
        total = len(itemList)
        # 循环获得一个可用的文件名
        todayTime = '%s-%s-%s' % (self.year, self.month, self.day)
        path = 'result/' + todayTime
        if not os.path.exists(path):
            os.mkdir(path)
        path = path + '/' + todayTime
        while True:
            if os.path.exists(path + '.txt'):
                path += ' 1'
            else:
                path += '.txt'
                break
        for line in itemList:
            items = str(line).split('\t')
            # 去掉数组中的无用字符
            while '' in items:
                items.remove('')
            if len(items) > 0:
                # 去掉数字中3位一个的,
                items[0] = items[0].replace(',', '')
                if items[0] != '' and items[1] != '':
                    print '======================'
                    self.log += '======================' + '\n'
                    print items[0] + ":" + items[1]
                    self.log += items[0] + ":" + items[1] + '\n'
                #
                # (已解决,待测试)考虑了一下好像有问题,如果第一次钱不够是不是会被计入已点,这样如果补汇就不会再点了
                #
                # 如果已经点过了,就跳过不点了
                if items[1] in alreadyDirectPayList:
                    # writeHandle.write(items[1] + u':已经点过了\n')
                    # allResult最后会写入文件保存
                    # allResult += items[1] + u':已经点过了\n'
                    resultToWrite += items[1] + u':已经点过了\n'
                    resultToShow += items[1] + u':已经点过了\n'
                    total -= 1
                    print u'%s:已经点过了' % (items[1])
                    self.log += u'%s:已经点过了' % (items[1]) + '\n'
                    continue
                # 0-失败 1-成功 2-无 3-钱不够
                (result, status) = self.directPay(float(items[0]), items[1])
                if status == 0:
                    print u'进入页面错误,请检查'
                    self.log += u'进入页面错误,请检查' + '\n'
                # 成功的 无的都写入记录,钱不够的不记录,以免补汇后不点
                elif status == 1 or status == 2:
                    # writeHandle.write(result + '\n')
                    # allResult += result + '\n'
                    resultToWrite += result + '\n'
                    resultToShow += result + '\n'
                elif status == 3:
                    # 钱不够的
                    # 只显示,不写入文件,防止补汇后被误判为已经点过
                    resultToShow += result + '\n'
                temp = '(%d/%d)%s' % (index, total, result)
                index += 1
                print temp
                self.log += temp + '\n'
                # allResult += result + '\n'
        writeHandle = codecs.open(path, mode='w', encoding='utf-8')
        writeHandle.write(resultToWrite)
        writeHandle.close()
        self.ui.outputTextEdit.setPlainText(resultToShow)
        print "end"
        self.log += "end" + '\n'
        self.saveLog(self.log)
        self.log = ''

    def saveLog(self, log):
        curTime = QDateTime.currentDateTime()
        # 循环获得一个可用的文件名
        todayTime = '%s-%s-%s' % (self.year, self.month, self.day)
        path = 'log/' + todayTime
        if not os.path.exists(path):
            os.mkdir(path)
        path = path + '/' + todayTime
        while True:
            if os.path.exists(path + '.log'):
                path += ' 1'
            else:
                path += '.log'
                break
        # 开始记录log日志
        fileHandle = writeHandle = codecs.open(path, mode='w', encoding='utf-8')
        time = unicode(curTime.toString(QString('yyyy-MM-dd HH:mm:ss')), encoding='utf-8')
        log = u'操作时间：' + time + '\n' + log
        # fileHandle.write(u'操作时间：' + curTime.toString(QString('yyyy-MM-dd dddd HH:mm:ss')) + '\n')
        fileHandle.write(log)
        fileHandle.close()

    def directPay(self, payIn, rtnum):
        # 0-失败 1-成功 2-无 3-钱不够
        status = 0
        resultStr = ''
        dic = {}
        dic['applyId'] = ''
        dic['contractId'] = rtnum
        html = BeautifulSoup(self.httpHelper.sendRequest('post', self.constants.baseurl+"/vfs2/innerpage/loanafterportlet/disposalQueryList.html", dic))
        # req = urllib2.Request(baseUrl+"/vfs2/innerpage/loanafterportlet/disposalQueryList.html", urllib.urlencode(dic))
        # req.add_header("Referer", baseUrl+"/vfs2/innerpage/loanafterportlet/disposalQueryList.html")
        # resp = urllib2.urlopen(req)
        # html = BeautifulSoup(resp.read())
        # print html
        inputs = html.findAll("input")
        # 是否有总金额框
        rAmountInput = html.find(id='rAmount')
        if rAmountInput:
            rAmount = self.getShouldPayAmount(inputs)
            if payIn < rAmount:
                resultStr = rtnum + u':钱不够'
                status = 3
            else:
                postData = self.fillInPostDict(inputs)
                # print postData
                self.httpHelper.sendRequest('post', self.constants.baseurl+"/vfs2/innerpage/loanafterportlet/foot.html", postData)
                resultStr = rtnum + u':成功'
                status = 1
        # 判断一下到底是没有还是登陆错误
        else:
            titleStr = html.find('title').text
            if u'哦' in titleStr:
                resultStr = rtnum + u':错误'
                status = 0
            else:
                resultStr = rtnum + u':无'
                status = 2
        return (resultStr, status)
        # print html

    # 得到客户应还的金额
    def getShouldPayAmount(self, inputs):
        if len(inputs) == 0:
            return
        sum = 0
        for inputItem in inputs:
                if inputItem.has_attr('id'):
                    if inputItem.attrs['id'].find("repayamount") != -1:
                        sum += float(inputItem.attrs['value'])
        # 四舍五入，保留两位小数round(sum,2)不准确，详见python文档
        return round(sum * 100) / 100

    def fillInPostDict(self, inputs):
        postArray = []
        dic = {}
        cnameStr = ""
        feeStr = ""
        repayflgStr = ""
        length = len(inputs)
        # 此字段为运行中加入字段
        for i in range(length):
            inputItem = inputs[i]
            # print inputItem
            if inputItem.attrs["type"] == "checkbox":
                inputId = inputItem.attrs['id']
                if inputId.find("fee") != -1:
                    flg = inputId[3:len(inputId)]
                    feeStr = self.getFeeStr(inputs, flg)
                    postArray.append(("dfee" + str(i), feeStr))
                    # dic["dfee" + str(i)] = feeStr
                    cnameStr += "dfee" + str(i) + ","
                if inputId.find("repayflg") != -1:
                    flg = inputId[8:len(inputId)]
                    repayflgStr = self.getRepayflgStr(inputs, flg)
                    postArray.append(("drepay" + str(i), repayflgStr))
                    # dic["drepay" + str(i)] = repayflgStr
                    cnameStr += "drepay" + str(i) + ","
        # cname字段，根据上一字段运行结果生成
        postArray.append(("cname", cnameStr[:len(cnameStr)-1]))
        # dic["cname"] = cnameStr[:len(cnameStr)-1]
        for inputItem in inputs:
            if inputItem.has_attr('name') and inputItem.has_attr('value'):
                postArray.append((inputItem.attrs['name'], inputItem.attrs['value']))
            elif inputItem.has_attr('type') and inputItem.attrs['type'] == 'checkbox':
                postArray.append((inputItem.attrs['name'], 'on'))
                # dic[inputItem.attrs['name']] = inputItem.attrs['value']
        # 插入总金额
        postArray.append(("remitAmount", self.getShouldPayAmount(inputs)))
        return postArray
        # return dic

    # 得到fee的值，重复，只需获取一遍
    def getFeeStr(self, inputs, flg):
        string = ""
        string += self.getTagFromArrayById(inputs, "deductId" + flg).attrs["value"] + ","
        string += self.getTagFromArrayById(inputs, "fclearType" + flg).attrs["value"] + ","
        string += self.getTagFromArrayById(inputs, "amount" + flg).attrs["value"] + ","
        string += self.getTagFromArrayById(inputs, "applyerType" + flg).attrs["value"] + ","
        string += self.getTagFromArrayById(inputs, "applyerId" + flg).attrs["value"] + ","
        string += "f"
        return string

    # 得到repayflg的值，重复，只需获取一遍
    def getRepayflgStr(self, inputs, flg):
        string = ""
        string += self.getTagFromArrayById(inputs, "repayPlanId" + flg).attrs["value"] + ","
        string += self.getTagFromArrayById(inputs, "repayerType" + flg).attrs["value"] + ","
        string += self.getTagFromArrayById(inputs, "repayerId" + flg).attrs["value"] + ","
        string += self.getTagFromArrayById(inputs, "clearType" + flg).attrs["value"] + ","
        string += self.getTagFromArrayById(inputs, "repayamount" + flg).attrs["value"] + ","
        string += "r"
        return string

    def getTagFromArrayByName(self, inputs, name):
        for tag in inputs:
            if tag.has_attr('name'):
                if tag.attrs['name'] == name:
                    return tag
        return None

    def getTagFromArrayById(self, inputs, idd):
        for tag in inputs:
            if tag.has_attr('id'):
                if tag.attrs['id'] == idd:
                    return tag
        return None

    def getCookies(self):
        fileHandle = open('acc.txt', 'r')
        line = fileHandle.readline()
        aList = line.split('|')
        dic={}
        dic["loginName"] = aList[0]
        dic["password"] = aList[1]
        html = BeautifulSoup(self.httpHelper.sendRequest('post', self.constants.baseurl+"/vfs2/login.html", dic))
        # req = urllib2.Request(baseUrl+"/vfs2/login.html", urllib.urlencode(dic))
        # req.add_header("Referer", baseUrl+"/vfs2/login.html")
        # resp = urllib2.urlopen(req)
        # html = BeautifulSoup(resp.read())
        print html.find('title').text.encode('UTF-8')


def main():
    app = QtGui.QApplication([])
    ex = Example()
    ex.show()
    app.exec_()

if __name__ == '__main__':
    main()
