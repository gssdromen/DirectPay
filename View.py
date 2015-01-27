# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'directPayView.ui'
#
# Created: Wed Oct 29 09:15:53 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.inputTextEdit = QtGui.QPlainTextEdit(self.centralwidget)
        self.inputTextEdit.setGeometry(QtCore.QRect(30, 20, 231, 521))
        self.inputTextEdit.setObjectName(_fromUtf8("inputTextEdit"))

        self.cbNeedsYuKou = QtGui.QCheckBox(MainWindow)
        self.cbNeedsYuKou.setGeometry(QtCore.QRect(300, 150, 71, 16))
        self.cbNeedsYuKou.setChecked(True)
        self.cbNeedsYuKou.setObjectName(_fromUtf8("cbNeedsYuKou"))

        self.refreshBtn = QtGui.QPushButton(self.centralwidget)
        self.refreshBtn.setGeometry(QtCore.QRect(300, 200, 75, 23))
        self.refreshBtn.setObjectName(_fromUtf8("payBtn"))
        self.mergeBtn = QtGui.QPushButton(self.centralwidget)
        self.mergeBtn.setGeometry(QtCore.QRect(300, 235, 75, 23))
        self.mergeBtn.setObjectName(_fromUtf8("payBtn"))
        self.payBtn = QtGui.QPushButton(self.centralwidget)
        self.payBtn.setGeometry(QtCore.QRect(300, 270, 75, 23))
        self.payBtn.setObjectName(_fromUtf8("payBtn"))
        self.outputTextEdit = QtGui.QPlainTextEdit(self.centralwidget)
        self.outputTextEdit.setGeometry(QtCore.QRect(410, 20, 261, 521))
        self.outputTextEdit.setObjectName(_fromUtf8("outputTextEdit"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 19))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.cbNeedsYuKou.setText(_translate("MainWindow", "下载预扣", None))
        self.payBtn.setText(_translate("MainWindow", "应用", None))
        self.refreshBtn.setText(_translate("MainWindow", "刷新", None))
        self.mergeBtn.setText(_translate("MainWindow", "合并", None))
