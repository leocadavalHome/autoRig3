import pymel.core as pm
from PySide2 import QtCore,QtWidgets
import maya.OpenMayaUI as omui
import inspect
from shiboken2 import wrapInstance

class Dockable(object):
    def __init__(self, widgetCls=None, label=None):
        self.widgetCls = widgetCls
        self.name = self.widgetCls.__name__

        if not label:
            self.label = getattr(self.widgetCls, "label", self.name)
        else:
            self.label = label

        if not pm.workspaceControl(self.name, q=True, ex=True):
            dockControl = pm.workspaceControl(
                self.name,
                label=self.label
            )
        else:
            dockControl = self.name

        dockPtr = omui.MQtUtil.findControl(dockControl)
        self.dockWidget = wrapInstance(long(dockPtr), QtWidgets.QWidget)

        self.createWidget()

        pm.workspaceControl(self.name, e=True, vis=True, r=True)


    def createWidget(self):
        hasWidget = [x for x in self.dockWidget.children() if isinstance(x, self.widgetCls)]

        if not hasWidget:
            child = self.widgetCls(self.dockWidget)
            self.dockWidget.layout().addWidget(child)
        else:
            child=hasWidget[0]

        return child

    
def createDock(widgetCls=None, label=None):
    dock = Dockable(widgetCls=widgetCls, label=label)
    pm.workspaceControl(
        dock.name,
        e=True,
        uiScript='try:\n\tdock.createWidget()\nexcept:\n\tpass'.format()
    )
