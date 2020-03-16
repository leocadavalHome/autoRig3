# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'renameWidget.ui'
#
# Created: Sat Jan 11 01:29:25 2020
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_renameDialog(object):
    def setupUi(self, renameDialog):
        renameDialog.setObjectName("renameDialog")
        renameDialog.resize(308, 50)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(renameDialog.sizePolicy().hasHeightForWidth())
        renameDialog.setSizePolicy(sizePolicy)
        renameDialog.setMinimumSize(QtCore.QSize(240, 0))
        renameDialog.setMaximumSize(QtCore.QSize(16777215, 50))
        renameDialog.setBaseSize(QtCore.QSize(0, 50))
        self.verticalLayout = QtWidgets.QVBoxLayout(renameDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(renameDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QtCore.QSize(30, 30))
        self.pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.lineEdit = QtWidgets.QLineEdit(renameDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(renameDialog)
        QtCore.QMetaObject.connectSlotsByName(renameDialog)

    def retranslateUi(self, renameDialog):
        renameDialog.setWindowTitle(QtWidgets.QApplication.translate("renameDialog", "rename", None, -1))
        self.pushButton.setText(QtWidgets.QApplication.translate("renameDialog", ">", None, -1))

