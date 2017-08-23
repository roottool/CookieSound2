# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainform.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(270, 30)
        Form.setMaximumSize(QtCore.QSize(270, 16777215))
        self.InputLabel = QtWidgets.QLabel(Form)
        self.InputLabel.setGeometry(QtCore.QRect(0, 0, 271, 31))
        self.InputLabel.setObjectName("InputLabel")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Cookie☆☆Sound"))
        self.InputLabel.setText(_translate("Form", "Waiting for typing a hookkey"))

