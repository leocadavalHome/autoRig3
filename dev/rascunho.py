from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

def deleteControl(control):
    if pm.workspaceControl(control, q=True, exists=True):
        pm.workspaceControl(control, e=True, close=True)
        pm.deleteUI(control, control=True)


class DockableWidget(MayaQWidgetDockableMixin, widgets.QDialog):
    def __init__(self, parent=None, coreWidgetCls=None ):
        super(DockableWidget, self).__init__(parent=parent)
        # set the name and title of the widget
        self.setObjectName('testeWidget')
        self.setWindowTitle('Database Asset Search')
        self.setLayout(self.createLayout())

    # create a widget and lay it out vertically
    def createLayout(self):
        self.main_layout = widgets.QVBoxLayout()
        self.central_widget = testeUI.autoRig3UI(parent=self)
        self.main_layout.addWidget(self.central_widget)
        return self.main_layout


def makeCoreWidgetMain():
    # delete any pre-existing widget before making a new one
    deleteControl("testeWidgetWorkspaceControl")
    Core = DockableWidget()

    # configure and show the new widget
    Core.show(dockable=True, uiScript='from autoRig3.dev.rascunho import *; Core.createLayout()')
    # bring to the front
    Core.raise_()

