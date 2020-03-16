import pymel.core as pm
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore, QtGui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import autoRig3.ui.transformsWidget as transformsWidget
import autoRig3.tools.groupTools as groupTools
import autoRig3.tools.attachTools as attachTools
import autoRig3.tools.spaceSwitchTools as spaceTools
import logging

logger = logging.getLogger('autoRig')
logger.setLevel(10)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def deleteControl(control):
    if pm.workspaceControl(control, q=True, exists=True):
        pm.workspaceControl(control, e=True, close=True)
        pm.deleteUI(control, control=True)


class DockableWidget(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=None, coreWidgetCls=None ):
        super(DockableWidget, self).__init__(parent=parent)
        # set the name and title of the widget
        self.setObjectName('transformWidget')
        self.setWindowTitle('TRANS')
        self.setLayout(self.createLayout())

    # create a widget and lay it out vertically
    def createLayout(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.central_widget = TransformsUI(parent=self)
        self.main_layout.addWidget(self.central_widget)
        return self.main_layout


def makeCoreWidgetMain():
    # delete any pre-existing widget before making a new one
    deleteControl("transformWidgetWorkspaceControl")
    Core = DockableWidget(parent=maya_main_window())

    # configure and show the new widget
    Core.show(dockable=True, uiScript='Core.createLayout()')
    # bring to the front
    Core.raise_()

class TransformsUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TransformsUI, self).__init__(parent=parent)
        self.ui = transformsWidget.Ui_Form()

        self.setStyleSheet(
            '''
            QToolTip
            {
                 border: 1px solid black;
                 background-color: #ffa02f;
                 padding: 1px;
                 border-radius: 3px;
                 opacity: 100;
            }

            QWidget
            {
                color: #b1b1b1;
                background-color: #323232;
            }

            QWidget:item:hover
            {
                background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #ca0619);
                color: #000000;
            }

            QWidget:item:selected
            {
                background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
            }

            QMenuBar::item
            {
                background: transparent;
            }

            QMenuBar::item:selected
            {
                background: transparent;
                border: 1px solid #ffaa00;
            }

            QMenuBar::item:pressed
            {
                background: #444;
                border: 1px solid #000;
                background-color: QLinearGradient(
                    x1:0, y1:0,
                    x2:0, y2:1,
                    stop:1 #212121,
                    stop:0.4 #343434/*,
                    stop:0.2 #343434,
                    stop:0.1 #ffaa00*/
                );
                margin-bottom:-1px;
                padding-bottom:1px;
            }

            QMenu
            {
                border: 1px solid #000;
            }

            QMenu::item
            {
                padding: 2px 20px 2px 20px;
            }

            QMenu::item:selected
            {
                color: #000000;
            }

            QWidget:disabled
            {
                color: #404040;
                background-color: #323232;
            }

            QAbstractItemView
            {
                background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4d4d4d, stop: 0.1 #646464, stop: 1 #5d5d5d);
            }

            QWidget:focus
            {
                /*border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);*/
            }

            QLineEdit
            {
                background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4d4d4d, stop: 0 #646464, stop: 1 #5d5d5d);
                padding: 1px;
                border-style: solid;
                border: 1px solid #1e1e1e;
                border-radius: 5;
            }

            QPushButton
            {
                color: #b1b1b1;
                background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
                border-width: 1px;
                border-color: #1e1e1e;
                border-style: solid;
                border-radius: 6;
                padding: 3px;
                font-size: 12px;
                padding-left: 5px;
                padding-right: 5px;
            }

            QToolButton
            {
                color: #b1b1b1;
                background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
                border-width: 1px;
                border-color: #1e1e1e;
                border-style: solid;
                border-radius: 6;
                padding: 3px;
                font-size: 10px;
                padding-left: 5px;
                padding-right: 5px;
            }

            QPushButton:pressed
            {
                background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);
            }

            QComboBox
            {
                selection-background-color: #ffaa00;
                background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
                border-style: solid;
                border: 1px solid #1e1e1e;
                border-radius: 5;
            }

            QComboBox:hover,QPushButton:hover,QToolButton:hover
            {
                border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
            }


            QComboBox:on
            {
                padding-top: 3px;
                padding-left: 4px;
                background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);
                selection-background-color: #ffaa00;
            }

            QComboBox QAbstractItemView
            {
                border: 2px solid darkgray;
                selection-background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
            }

            QComboBox::drop-down
            {
                 subcontrol-origin: padding;
                 subcontrol-position: top right;
                 width: 15px;

                 border-left-width: 0px;
                 border-left-color: darkgray;
                 border-left-style: solid; /* just a single line */
                 border-top-right-radius: 3px; /* same radius as the QComboBox */
                 border-bottom-right-radius: 3px;
             }

            QComboBox::down-arrow
            {
                 image: url(:/icons/icon/down_arrow.png);
            }

            QGroupBox:focus
            {
            border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
            }

            QTextEdit:focus
            {
                border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
            }

            QScrollBar:horizontal {
                 border: 1px solid #222222;
                 background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.0 #121212, stop: 0.2 #282828, stop: 1 #484848);
                 height: 7px;
                 margin: 0px 16px 0 16px;
            }

            QScrollBar::handle:horizontal
            {
                  background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffa02f, stop: 0.5 #d7801a, stop: 1 #ffa02f);
                  min-height: 20px;
                  border-radius: 2px;
            }

            QScrollBar::add-line:horizontal {
                  border: 1px solid #1b1b19;
                  border-radius: 2px;
                  background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffa02f, stop: 1 #d7801a);
                  width: 14px;
                  subcontrol-position: right;
                  subcontrol-origin: margin;
            }

            QScrollBar::sub-line:horizontal {
                  border: 1px solid #1b1b19;
                  border-radius: 2px;
                  background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffa02f, stop: 1 #d7801a);
                  width: 14px;
                 subcontrol-position: left;
                 subcontrol-origin: margin;
            }

            QScrollBar::right-arrow:horizontal, QScrollBar::left-arrow:horizontal
            {
                  border: 1px solid black;
                  width: 1px;
                  height: 1px;
                  background: white;
            }

            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
            {
                  background: none;
            }

            QScrollBar:vertical
            {
                  background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0.0 #121212, stop: 0.2 #282828, stop: 1 #484848);
                  width: 7px;
                  margin: 16px 0 16px 0;
                  border: 1px solid #222222;
            }

            QScrollBar::handle:vertical
            {
                  background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 0.5 #d7801a, stop: 1 #ffa02f);
                  min-height: 20px;
                  border-radius: 2px;
            }

            QScrollBar::add-line:vertical
            {
                  border: 1px solid #1b1b19;
                  border-radius: 2px;
                  background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
                  height: 14px;
                  subcontrol-position: bottom;
                  subcontrol-origin: margin;
            }

            QScrollBar::sub-line:vertical
            {
                  border: 1px solid #1b1b19;
                  border-radius: 2px;
                  background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #d7801a, stop: 1 #ffa02f);
                  height: 14px;
                  subcontrol-position: top;
                  subcontrol-origin: margin;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
            {
                  border: 1px solid black;
                  width: 1px;
                  height: 1px;
                  background: white;
            }


            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
            {
                  background: none;
            }

            QTextEdit
            {
                background-color: #242424;
            }

            QPlainTextEdit
            {
                background-color: #242424;
            }

            QHeaderView::section
            {
                background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #616161, stop: 0.5 #505050, stop: 0.6 #434343, stop:1 #656565);
                color: white;
                padding-left: 4px;
                border: 1px solid #6c6c6c;
            }

            QCheckBox:disabled
            {
            color: #414141;
            }

            QDockWidget::title
            {
                text-align: center;
                spacing: 3px; /* spacing between items in the tool bar */
                background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop: 0.5 #242424, stop:1 #323232);
            }

            QDockWidget::close-button, QDockWidget::float-button
            {
                text-align: center;
                spacing: 1px; /* spacing between items in the tool bar */
                background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop: 0.5 #242424, stop:1 #323232);
            }

            QDockWidget::close-button:hover, QDockWidget::float-button:hover
            {
                background: #242424;
            }

            QDockWidget::close-button:pressed, QDockWidget::float-button:pressed
            {
                padding: 1px -1px -1px 1px;
            }

            QMainWindow::separator
            {
                background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161616, stop: 0.5 #151515, stop: 0.6 #212121, stop:1 #343434);
                color: white;
                padding-left: 4px;
                border: 1px solid #4c4c4c;
                spacing: 3px; /* spacing between items in the tool bar */
            }

            QMainWindow::separator:hover
            {

                background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d7801a, stop:0.5 #b56c17 stop:1 #ffa02f);
                color: white;
                padding-left: 4px;
                border: 1px solid #6c6c6c;
                spacing: 3px; /* spacing between items in the tool bar */
            }

            QToolBar::handle
            {
                 spacing: 3px; /* spacing between items in the tool bar */
                 background: url(:/icons/icon/handle.png);
            }

            QMenu::separator
            {
                height: 2px;
                background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161616, stop: 0.5 #151515, stop: 0.6 #212121, stop:1 #343434);
                color: white;
                padding-left: 4px;
                margin-left: 10px;
                margin-right: 5px;
            }

            QProgressBar
            {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }

            QProgressBar::chunk
            {
                background-color: #d7801a;
                width: 2.15px;
                margin: 0.5px;
            }

            QTabBar::tab {
                color: #b1b1b1;
                border: 1px solid #444;
                border-bottom-style: none;
                background-color: #323232;
                padding-left: 10px;
                padding-right: 10px;
                padding-top: 3px;
                padding-bottom: 2px;
                margin-right: -1px;
            }

            QTabWidget::pane {
                border: 1px solid #444;
                top: 1px;
            }

            QTabBar::tab:last
            {
                margin-right: 0; /* the last selected tab has nothing to overlap with on the right */
                border-top-right-radius: 3px;
            }

            QTabBar::tab:first:!selected
            {
             margin-left: 0px; /* the last selected tab has nothing to overlap with on the right */


                border-top-left-radius: 3px;
            }

            QTabBar::tab:!selected
            {
                color: #b1b1b1;
                border-bottom-style: solid;
                margin-top: 3px;
                background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #212121, stop:.4 #343434);
            }

            QTabBar::tab:selected
            {
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                margin-bottom: 0px;
            }

            QTabBar::tab:!selected:hover
            {
                /*border-top: 2px solid #ffaa00;
                padding-bottom: 3px;*/
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #212121, stop:0.4 #343434, stop:0.2 #343434, stop:0.1 #ffaa00);
            }

            QRadioButton::indicator:checked, QRadioButton::indicator:unchecked{
                color: #b1b1b1;
                background-color: #323232;
                border: 1px solid #b1b1b1;
                border-radius: 6px;
            }

            QRadioButton::indicator:checked
            {
                background-color: qradialgradient(
                    cx: 0.5, cy: 0.5,
                    fx: 0.5, fy: 0.5,
                    radius: 1.0,
                    stop: 0.25 #ffaa00,
                    stop: 0.3 #323232
                );
            }

            QCheckBox::indicator{
                color: #b1b1b1;
                background-color: #323232;
                border: 1px solid #b1b1b1;
                width: 9px;
                height: 9px;
            }

            QRadioButton::indicator
            {
                border-radius: 6px;
            }

            QRadioButton::indicator:hover, QCheckBox::indicator:hover
            {
                border: 1px solid #ffaa00;
            }

            QCheckBox::indicator:checked
            {
                image:url(:/icons/icon/checkbox.png);
            }

            QCheckBox::indicator:disabled, QRadioButton::indicator:disabled
            {
                border: 1px solid #444;
            }         
            ''' )

        self.meshHookMode = 3
        self.curveHookMode = 1
        self.curveHookTangent = False

        self.ui.setupUi(self)

        self.ui.space_refresh_btn.clicked.connect(self.refreshSpaces)
        self.ui.space_createSpace_btn.clicked.connect(self.createSpace)
        self.ui.space_orient_btn.clicked.connect(self.addOrientSpace)
        self.ui.space_parent_btn.clicked.connect(self.addParentSpace)

        self.ui.transform_ZeroGrp_btn.clicked.connect(self.zeroGrp)
        self.ui.transform_InvMult_btn.clicked.connect(self.inverseMulti)
        self.ui.transform_meshHook_btn.clicked.connect(self.meshHook)
        self.ui.transform_curveHook_btn.clicked.connect(self.curveHook)
        self.ui.transform_matrixConn_btn.clicked.connect(self.matrixConnection)

        self.ui.transform_meshHook_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.transform_meshHook_btn.customContextMenuRequested.connect(self.meshHookMenu)
        self.ui.transform_curveHook_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.transform_curveHook_btn.customContextMenuRequested.connect(self.curveHookMenu)

        self.refreshSpaces()

    def setButtonOption(self,name, value):
        try:
            self.__dict__[name]=value
        except:
            logger.warn('cant set buttonOption %s' % name)

    def meshHookMenu(self):
        '''
        1 - parent
        2 - parentConstraint(maintainOffset=True)
        3 - pointConstraint(maintainOffset=True)
        4 - parentConstarint(maintainOffset=False)
        :return:
        '''
        menu = QtWidgets.QMenu()
        menu.addAction('parent', lambda:self.setButtonOption('meshHookMode', 1))
        menu.addAction('parentConstraint', lambda:self.setButtonOption('meshHookMode', 2))
        menu.addAction('pointConstraint', lambda:self.setButtonOption('meshHookMode', 3))
        menu.addAction('parentConstraintNoOffset', lambda:self.setButtonOption('meshHookMode', 4))
        menu.exec_(QtGui.QCursor.pos())

    def curveHookMenu(self):
        menu = QtWidgets.QMenu()
        menu.addAction('pointOnCurve', lambda: self.setButtonOption('curveHookTangent', False))
        menu.addAction('pointOnCurveTanget', lambda: self.setButtonOption('curveHookTangent', True))
        menu.exec_(QtGui.QCursor.pos())

    def zeroGrp(self):
        pm.undoInfo(openChunk=True)
        try:
            groupTools.zeroOut()
        finally:
            pm.undoInfo(closeChunk=True)

    def inverseMulti(self):
        pm.undoInfo(openChunk=True)
        try:
            groupTools.addMultiply()
        finally:
            pm.undoInfo(closeChunk=True)

    def meshHook(self):
        logger.debug(self.meshHookMode)
        pm.undoInfo(openChunk=True)
        try:
            attachTools.hookOnMesh(mode=self.meshHookMode)
        finally:
            pm.undoInfo(closeChunk=True)

    def curveHook(self):
        pm.undoInfo(openChunk=True)
        try:
            attachTools.hookOnCurve(mode=self.curveHookMode, tangent=self.curveHookTangent)
        finally:
            pm.undoInfo(closeChunk=True)


    def matrixConnection(self):
        logger.debug('matrix connection')
        pass

    def refreshSpaces(self):
        spaces = pm.ls("*_spc")
        spaceNames = [x.name().split('_spc')[0] for x in spaces]
        self.ui.spaceList_listWidget.clear()
        self.ui.spaceList_listWidget.addItems(spaceNames)

    def createSpace(self):
        sel = pm.ls (sl=True)
        if not sel:
            logger.warn('Selecione objeto para criar o space')
            return

        name, ok = QtWidgets.QInputDialog.getText(self, 'Name Input',
                                              'Enter Name:')
        if ok:
            pm.undoInfo(openChunk=True)
            try:
                spaceTools.createSpc(driver=sel[0], name=name, type=None)
            finally:
                pm.undoInfo(closeChunk=True)

            self.refreshSpaces()

    def addOrientSpace(self):
        sel = pm.ls(sl=True)
        if len(sel) > 2:
            logger.warn('Selecione um objeto para space switch e outro para posicao')
            return

        spacelist = [x.text() for x in self.ui.spaceList_listWidget.selectedItems()]
        logger.debug(spacelist)

        # todo ver se ja existe o space a ser adicionado no switcher
        pm.undoInfo(openChunk=True)
        try:
            spaceTools.addSpc(target=sel[0], switcher=sel[0].getParent(),
                              type='orient', spaceList=spacelist, posSpc=sel[1])
        finally:
            pm.undoInfo(closeChunk=True)


    def addParentSpace(self):
        sel = pm.ls(sl=True)

        if not sel:
            logger.warn('Selecione um objeto para space switch')
            return

        # todo se nao existir um grupo pai, pedir pra adicionar

        if not sel[0].getParent():
            flags = QtGui.QMessageBox.StandardButton.Yes
            flags |= QtGui.QMessageBox.StandardButton.No
            question = "criar um grupo acima?"
            response = QtGui.QMessageBox.question(self, "Question",
                                                  question,
                                                  flags)
            if response:
                groupTools.zeroOut()

        spacelist = [x.text() for x in self.ui.spaceList_listWidget.selectedItems()]
        logger.debug(spacelist)

        # todo ver se ja existe o space a ser adicionado no switcher
        pm.undoInfo(openChunk=True)
        try:
            spaceTools.addSpc(target=sel[0], switcher=sel[0].getParent(),
                              type='parent', spaceList=spacelist)
        finally:
            pm.undoInfo(closeChunk=True)

