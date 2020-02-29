import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QStringListModel, QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QShortcut
from Ui_gimy import Ui_MainWindow
from Ui_dialog import Ui_Dialog
import requests
import urllib.parse
import re

from bs4 import BeautifulSoup

class Dialog(QtWidgets.QDialog, Ui_Dialog) :
    def __init__(self) :
        super(Dialog, self).__init__()
        self.setupUi(self)

class MainWindow(QtWidgets.QMainWindow) :
    def __init__(self) :
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.setStyleSheet('color: #ffffff;'
                                        'background-color: #44a9f5;'
                                        'border-radius: 5px')
        self.ui.pushButton.clicked.connect(self.searchClick)

        self.ui.lineEdit.setStyleSheet('color: #ffffff;'
                                        'background-color: #31313a;'
                                        'border-radius: 10px')
        self.ui.lineEdit.returnPressed.connect(self.ui.pushButton.click)
        self.ui.lineEdit.setFocusPolicy(Qt.StrongFocus)

        self.ui.radioButton.toggled.connect(self.allResult)
        
        self.ui.pushButton_4.setStyleSheet('color: #ffffff;'
                                        'background-color: #44a9f5;'
                                        'border-radius: 5px')
        QShortcut(QtCore.Qt.Key_Right, self.ui.pushButton_4, self.ui.pushButton_4.animateClick)
        self.ui.pushButton_4.clicked.connect(self.nextPage)

        self.ui.pushButton_2.setStyleSheet('color: #ffffff;'
                                        'background-color: #44a9f5;'
                                        'border-radius: 5px')
        QShortcut(QtCore.Qt.Key_Left, self.ui.pushButton_2, self.ui.pushButton_2.animateClick)
        self.ui.pushButton_2.clicked.connect(self.previousPage)
        
        self.ui.spinBox.setStyleSheet('color: #ffffff;'
                                        'background-color: #31313a;'
                                        'border-radius: 10px')
        self.ui.spinBox.valueChanged.connect(self.spinboxPage)

        self.ui.listView.setStyleSheet('color: #ffffff;'
                                        'background-color: #31313a;'
                                        'selection-color: #ffffff;'
                                        'selection-background-color: #3b3b44;')
        self.ui.listView.doubleClicked.connect(self.clicked)

    def searchClick(self) :
        self.ui.spinBox.setValue(1)
        self.ui.pushButton_2.setEnabled(False)
        text = self.ui.lineEdit.text()
        path = 'searchResult'
        url = 'urlResult'

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cookie': '__cfduid=d2b34dd3b59a8ec2e1532b15f6cbf328c1581150229; __atuvc=3%7C6%2C5%7C7; _ym_uid=1581150239832564503; _ym_d=1581150239; _ym_isad=2; PHPSESSID=hkncj8heksainod7fjke0r82c5; __atuvs=5e42a0252adbb1cc000; _ym_visorc_54632110=b'
        }
        search =  urllib.parse.quote(text)
        searchlist = []
        urlist = []
        show = []
        url = 'https://gimy.tv/vod-search.html?wd='+search
        r = requests.get(url, headers=headers)

        soup = BeautifulSoup(r.text, 'lxml')
        ul = soup.find('ul',{'class':'stui-vodlist__media col-pd clearfix'})
        title = ul.find_all('h3', {'class':'title'})
        for t in title :
            a = t.find('a')
            urlist.append(a['href'] + '\n')
            searchlist.append(t.string+'\n')
            show.append(t.string)
        
        slm = QStringListModel()
        slm.setStringList(show)
        self.ui.listView.setModel(slm)

        file = open(path, 'w', encoding='utf8')#檔案不存在自動創建覆寫
        file.writelines(searchlist)
        file.close()

        pt = soup.find('ul', {'class':'stui-page-text text-center clearfix'})
        page = re.search(".(\d*)頁", pt.text)

        page1 = int(page.group(1))
        self.ui.label.setText('共' + str(page1) + '頁')
        self.ui.spinBox.setMaximum(page1)

        urllist = []
        def BeS(p) :
            url = 'https://gimy.tv/vod-search-pg-'+str(p)+'-wd-'+search+'.html'
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'lxml')
            ul = soup.find('ul',{'class':'stui-vodlist__media col-pd clearfix'})
            title = ul.find_all('h3', {'class':'title'})
            searchlist = []
            for t in title :
                searchlist.append(t.string+'\n')
                a = t.find('a')
                urllist.append(a['href'] + '\n')
            file = open('searchResult', 'a', encoding='utf8')
            file.writelines(searchlist)
            file.close()
        
        if (page1 <= 5) and (page1 != 1) :
            for p in range(2,page1+1) :
                BeS(p)
            file = open('url', 'w', encoding='utf8')
            file.writelines(urlist)
            file.writelines(urllist)
            file.close()
        elif (page1 > 5):
            for p in range(2,6) :
                BeS(p)
            file = open('url', 'w', encoding='utf8')
            file.writelines(urlist)
            file.writelines(urllist)
            file.close()
        else:
            self.ui.pushButton_2.setEnabled(False)
            self.ui.pushButton_4.setEnabled(False)
            file = open('url', 'w', encoding='utf8')
            file.writelines(urlist)
            file.writelines(urllist)
            file.close()
    
    def openUrl(self, index) :
        file = open('searchResult', 'r')
        lines = file.readlines()
        file.close()
        for l in range(len(lines)) :
            lines[l] = lines[l].replace('\n','')
        
        file = open('url', 'r')
        url = file.readlines()
        file.close()
        for l in range(len(url)) :
            url[l] = url[l].replace('\n','')
        
        v = self.ui.spinBox.value()
        QDesktopServices.openUrl(QUrl('https://gimy.tv/' + url[(v-1)*10 + index.row()]))

    def allResult(self) :
        file = open('searchResult', 'r')
        lines = file.readlines()
        file.close()
        for l in range(len(lines)) :
            lines[l] = lines[l].replace('\n','')
        if self.ui.radioButton.isChecked() :
            slm = QStringListModel()
            slm.setStringList(lines)
            self.ui.listView.setModel(slm)
        else:
            v = self.ui.spinBox.value()
            origin = []
            for i in range(v*10-10, v*10) :
                try:
                    origin.append(lines[i])
                except IndexError:
                    pass
            slm = QStringListModel()
            slm.setStringList(origin)
            self.ui.listView.setModel(slm)
    
    def previousPage(self) :
        #總頁數和讀檔
        self.ui.pushButton_4.setEnabled(True)
        file = open('searchResult', 'r')
        lines = file.readlines()
        file.close()
        for l in range(len(lines)) :
            lines[l] = lines[l].replace('\n','')#去掉換行符
        t = int(re.search('.(\d*).', self.ui.label.text()).group(1))#目前頁數
        origin = []
        spinValue = self.ui.spinBox.value() - 1

        def previous(v, lt) :
            for i in range(v*10-10, v*10) :
                try:
                    lt.append(lines[i])
                except IndexError:
                    pass
            slm = QStringListModel()
            slm.setStringList(lt)
            self.ui.listView.setModel(slm)
            self.ui.spinBox.setValue(v)

        if (self.ui.spinBox.value() == 1) :
            pass
        else :
            if (spinValue == 1) :
                previous(spinValue, origin)
                self.ui.pushButton_2.setEnabled(False)
                print('pushB2 disable')
            else :
                previous(spinValue, origin)

    def nextPage(self):
        #取總頁數和讀檔
        self.ui.pushButton_2.setEnabled(True)
        file = open('searchResult', 'r')
        lines = file.readlines()
        file.close()
        for l in range(len(lines)) :
            lines[l] = lines[l].replace('\n','')#去掉換行符
        t = int(re.search('.(\d*).', self.ui.label.text()).group(1))#目前頁數
        origin = []
        spinValue = self.ui.spinBox.value() + 1
        
        def next(v, lt) :
            for i in range(v*10-10, v*10) :
                try:
                    lt.append(lines[i])
                except IndexError:
                    pass
            slm = QStringListModel()
            slm.setStringList(lt)
            self.ui.listView.setModel(slm)
            self.ui.spinBox.setValue(spinValue)
        
        if (self.ui.spinBox.value() == t) :
            pass
        else :
            if (spinValue == t) :
                next(spinValue, origin)
                self.ui.pushButton_4.setEnabled(False)
                print('pushB4 disable')
            else :
                next(spinValue, origin)

    def spinboxPage(self, value) :
        t = int(re.search('.(\d*).', self.ui.label.text()).group(1))
        if (value == t) :
            self.ui.pushButton_4.setEnabled(False)
            self.ui.pushButton_2.setEnabled(True)
        elif (value == 1) :
            self.ui.pushButton_2.setEnabled(False)
            self.ui.pushButton_4.setEnabled(True)
        else :
            self.ui.pushButton_2.setEnabled(True)
            self.ui.pushButton_4.setEnabled(True)
        file = open('searchResult', 'r')
        lines = file.readlines()
        file.close()
        for l in range(len(lines)) :
            lines[l] = lines[l].replace('\n','')#去掉換行符
        lt = []

        for v in range(value*10 - 10, value*10) :
            try:
                lt.append(lines[v])
            except IndexError :
                pass
        slm = QStringListModel()
        slm.setStringList(lt)
        self.ui.listView.setModel(slm)

    def clicked(self, index) :
        self.d = Dialog()
        file = open('url', 'r')
        url = file.readlines()
        file.close()
        for l in range(len(url)) :
            url[l] = url[l].replace('\n','')

        v = self.ui.spinBox.value()

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cookie': '__cfduid=d2b34dd3b59a8ec2e1532b15f6cbf328c1581150229; __atuvc=3%7C6%2C5%7C7; _ym_uid=1581150239832564503; _ym_d=1581150239; _ym_isad=2; PHPSESSID=hkncj8heksainod7fjke0r82c5; __atuvs=5e42a0252adbb1cc000; _ym_visorc_54632110=b'
        }
        r = requests.get('https://gimy.tv/' + url[(v-1)*10 + index.row()], headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        div = soup.find('div', {'class': 'stui-content__item clearfix'})
        self.d.setStyleSheet('background-color: #31313A;'
                            'color: #B6B6B6')
        
        self.d.label.setText('<a style="color: #DBDBDB;" href="' + 'https://gimy.tv/' + url[(v-1)*10 + index.row()] + '">' + div.find('h3').string + '</a>')
        self.d.label.setStyleSheet('color: red;')
        pdata = div.find_all('p', {'class': 'data'})
        self.d.label_2.setText('類型：' + re.search(r'類型：(\w*)地區：', pdata[0].text).group(1))
        self.d.label_3.setText('地區：' + re.search(r'地區：(\w*)年份：', pdata[0].text).group(1))
        self.d.label_4.setText('年份：' + re.search(r'年份：(\w*)', pdata[0].text).group(1))
        self.d.label_5.setText('主演：' + pdata[1].text.strip('主演：'))
        self.d.label_5.setWordWrap(True)
        pdetail = div.find('p', {'class': 'desc detail hidden-xs'})
        self.d.textBrowser.setText(pdetail.find('span', {'class': 'detail-content'}).string)
        self.d.exec()#未關閉視窗不能操作原程式

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setStyleSheet('background-color: #3B3B43;'
                        'color: #ffffff;')
    window.show()
    window.ui.lineEdit.setFocus()
    sys.exit(app.exec_())