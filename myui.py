# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\myui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Main_Form(object):
    def setupUi(self, Main_Form):
        Main_Form.setObjectName("Main_Form")
        Main_Form.resize(988, 761)
        self.next_pushButton = QtWidgets.QPushButton(Main_Form)
        self.next_pushButton.setGeometry(QtCore.QRect(530, 540, 75, 23))
        self.next_pushButton.setObjectName("next_pushButton")
        self.back_pushButton = QtWidgets.QPushButton(Main_Form)
        self.back_pushButton.setGeometry(QtCore.QRect(420, 540, 75, 23))
        self.back_pushButton.setObjectName("back_pushButton")
        self.listen_pushButton = QtWidgets.QPushButton(Main_Form)
        self.listen_pushButton.setGeometry(QtCore.QRect(470, 630, 75, 23))
        self.listen_pushButton.setObjectName("listen_pushButton")
        self.stop_pushButton = QtWidgets.QPushButton(Main_Form)
        self.stop_pushButton.setGeometry(QtCore.QRect(470, 690, 75, 23))
        self.stop_pushButton.setObjectName("stop_pushButton")
        self.image_label = QtWidgets.QLabel(Main_Form)
        self.image_label.setGeometry(QtCore.QRect(20, 50, 951, 261))
        self.image_label.setText("")
        self.image_label.setObjectName("image_label")

        self.retranslateUi(Main_Form)
        QtCore.QMetaObject.connectSlotsByName(Main_Form)

    def retranslateUi(self, Main_Form):
        _translate = QtCore.QCoreApplication.translate
        Main_Form.setWindowTitle(_translate("Main_Form", "auto turn sheet music"))
        self.next_pushButton.setText(_translate("Main_Form", "NEXT"))
        self.back_pushButton.setText(_translate("Main_Form", "BACK"))
        self.listen_pushButton.setText(_translate("Main_Form", "LISTEN"))
        self.stop_pushButton.setText(_translate("Main_Form", "STOP"))
