from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


import logging

logger = logging.getLogger('autoRig')

def getMayaWindow():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QMainWindow)

class IconButtonContextMenu(QtWidgets.QToolButton):
    def __init__(self, *args, **kwargs):
        QtWidgets.QToolButton.__init__(self, *args, **kwargs)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.buttonMenu)

    @QtCore.Slot()
    def on_button_released(self):
        print ('Doing Stuff when clicking on Button A')
        print (self.whatsThis())

    def buttonMenu(self, pos):
        menu = QtWidgets.QMenu()
        menu.addAction('X', lambda:self.changeAxis('X'))
        menu.addAction('Y', lambda:self.changeAxis('Y'))
        menu.addAction('Z', lambda:self.changeAxis('Z'))
        menu.exec_(QtGui.QCursor.pos())

    def changeAxis(self, axis):
        controlName = self.whatsThis().split('_')[0]
        self.setText(axis)
        self.setWhatsThis(controlName+'_'+axis)

    def SecondActionButton(self, objects):
        print ('Second Action working on :')
        print (objects)


