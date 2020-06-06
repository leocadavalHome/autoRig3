import pymel.core as pm
from PySide2 import QtCore, QtWidgets
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

import autoRig3.ui.bodyRigUI as bodyRigUI


pm.deleteUI('RenamingUI')

pm.workspaceControl('BodyRigUI', e=True, vis=True)

dockPtr = omui.MQtUtil.findControl('BodyRigUI')
dockWidget = wrapInstance(long(dockPtr), QtWidgets.QWidget)
dockWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)


# dockWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)

class Dockable(object):
    def __init__(self, widgetCls=None, label=None):
        self.widgetCls = widgetCls
        self.name = self.widgetCls.__name__
        if not label==None or not len(label):
            self.label = getattr(self.widgetCls, "label", self.name)
        else:
            self.label=label

        if not pm.workspaceControl(self.name, q=True, ex=True):
            dockControl = pm.workspaceControl(
                self.name,
                label=self.label
            )
        else:
            dockControl=self.name

        dockPtr = omui.MQtUtil.findControl(dockControl)
        self.dockWidget = wrapInstance(long(dockPtr), QtWidgets.QWidget)
        self.dockWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.createWidget()

    def createWidget(self):
        for obj in  self.dockWidget.children():
            if isinstance(obj, self.widgetCls):
                child = obj

        if not child:
            child = self.widgetCls(self.dockWidget)
            self.dockWidget.layout().addWidget(child)

        return child


def createDock(widgetCls = None):
    dock = Dockable(widgetCls=widgetCls)
    pm.workspaceControl(
        dock.name,
        e=True,
        uiScript='dock.createWidget()'
    )

