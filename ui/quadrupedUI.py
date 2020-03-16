import pymel.core as pm
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore, QtGui

import os.path
import autoRig3.ui.quadrupedWidget as quadrupedWidget
import autoRig3.composites.quadrupedRig as quadruped
import autoRig3.tools.controlTools as controlTools

import logging

logger = logging.getLogger('autoRig')


def getMayaWindow():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QMainWindow)

class QuadrupedUI(QtWidgets.QScrollArea):
    def __init__(self, parent=None, mainUI=None):
        if not parent:
            parent = getMayaWindow()
        super(QuadrupedUI, self).__init__(parent)

        self.ui = quadrupedWidget.Ui_quadrupedWidget()
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

            QComboBox:hover,QPushButton:hover
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
            '''
        )
        self.ui.setupUi(self)

        self.instance = None
        self.mainUI = mainUI

        noGuide = self.getGuidesSetupFromScene()

        if noGuide:
            self.getGuidesSetupFromUI()
        else:
            self.setUIFromGuideSetup()

    def setUIFromGuideSetup(self):
        logger.debug('setando UI...')
        self.mainUI.__dict__['rigName_txt'].setText(self.instance.name)

        if self.instance.moduleConnection == 1:
            self.mainUI.__dict__['hierarchy_rdBtn'].setChecked(1)
        else:
            self.mainUI.__dict__['constraint_rdBtn'].setChecked(0)

        fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Extra']
        for finger, fold in self.instance.handFingers:
            self.ui.__dict__['hand' + finger + '_chk'].setChecked(1)
            self.ui.__dict__['hand' + finger + '_spin'].setValue(fold)
            fingers.remove(finger)

        for finger in fingers:
            self.ui.__dict__['hand' + finger + '_chk'].setChecked(0)

        fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Extra']
        for finger, fold in self.instance.footFingers:
            self.ui.__dict__['feet' + finger + '_chk'].setChecked(1)
            self.ui.__dict__['feet' + finger + '_spin'].setValue(fold)
            fingers.remove(finger)

        for finger in fingers:
            self.ui.__dict__['feet' + finger + '_chk'].setChecked(0)

        if self.instance.armRibbonJnts > 0:
            self.ui.__dict__['armRibbon_chk'].setChecked(1)
            self.ui.__dict__['armNumJnts_spin'].setValue(self.instance.armRibbonJnts)
            self.ui.__dict__['armFirstOffset_spin'].setValue(self.instance.armRibbonFirstOffset)
            self.ui.__dict__['armLastOffset_spin'].setValue(self.instance.armRibbonLastOffset)
        else:
            self.ui.__dict__['armRibbon_chk'].setChecked(1)

        if self.instance.legRibbonJnts > 0:
            self.ui.__dict__['legRibbon_chk'].setChecked(1)
            self.ui.__dict__['legNumJnts_spin'].setValue(self.instance.legRibbonJnts)
            self.ui.__dict__['legFirstOffset_spin'].setValue(self.instance.legRibbonFirstOffset)
            self.ui.__dict__['legLastOffset_spin'].setValue(self.instance.legRibbonLastOffset)
        else:
            self.ui.__dict__['legRibbon_chk'].setChecked(1)
        self.ui.__dict__['spineNumJnts_spin'].setValue(self.instance.spineRibbonJnts)

    def getGuidesSetupFromScene(self):
        logger.debug('Getting setup from Scene...')
        noGuide = False
        rigName = self.mainUI.__dict__['rigName_txt'].text()

        moveallGuide = pm.ls(rigName + 'MoveAll_guide')
        try:
            name = moveallGuide[0].split('MoveAll_guide')[0]
        except:
            name = 'character'
            noGuide = True
            logger.debug('No previous guide found!')

        self.instance = quadruped.Quadruped(rigName=name)
        self.instance.getDict()
        return noGuide

    def getGuidesSetupFromUI(self):
        logger.debug('Getting setup from UI...')
        rigName = self.mainUI.__dict__['rigName_txt'].text()

        handFingerSetup = []
        footFingerSetup = []
        fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Extra']
        for finger in fingers:
            if self.ui.__dict__['hand' + finger + '_chk'].isChecked():
                folds = self.ui.__dict__['hand' + finger + '_spin'].value()
                handFingerSetup.append((finger, folds))
            if self.ui.__dict__['feet' + finger + '_chk'].isChecked():
                folds = self.ui.__dict__['feet' + finger + '_spin'].value()
                footFingerSetup.append((finger, folds))

        if self.mainUI.__dict__['hierarchy_rdBtn'].isChecked():
            moduleConnection = 1
        else:
            moduleConnection = 2

        if self.ui.__dict__['armRibbon_chk'].isChecked():
            armRibbonJnts = self.ui.__dict__['armNumJnts_spin'].value()
            armRibbonFirstOffset = self.ui.__dict__['armFirstOffset_spin'].value()
            armRibbonLastOffset = self.ui.__dict__['armLastOffset_spin'].value()
        else:
            armRibbonJnts = 0
            armRibbonFirstOffset = 1
            armRibbonLastOffset = 1

        if self.ui.__dict__['legRibbon_chk'].isChecked():
            legRibbonJnts = self.ui.__dict__['legNumJnts_spin'].value()
            legRibbonFirstOffset = self.ui.__dict__['legFirstOffset_spin'].value()
            legRibbonLastOffset = self.ui.__dict__['legLastOffset_spin'].value()
        else:
            legRibbonJnts = 0
            legRibbonFirstOffset = 1
            legRibbonLastOffset = 1

        spineRibbonJnts = self.ui.__dict__['spineNumJnts_spin'].value()
        # todo implementar offset dos joints da spine
        # spineRibbonFirstOffset = self.ui.__dict__['spineFistOffset_spin'].value()
        # spineRibbonLastOffset = self.ui.__dict__['spineLastOffset_spin'].value()

        self.instance = quadruped.Quadruped(rigName=rigName,
                                            handFingers=handFingerSetup,
                                            footFingers=footFingerSetup,
                                            moduleConnection=moduleConnection,
                                            armRibbonJnts=armRibbonJnts,
                                            armRibbonFirstOffset=armRibbonFirstOffset,
                                            armRibbonLastOffset=armRibbonLastOffset,
                                            legRibbonJnts=legRibbonJnts,
                                            legRibbonFirstOffset=legRibbonFirstOffset,
                                            legRibbonLastOffset=legRibbonLastOffset,
                                            spineRibbonJnts=spineRibbonJnts)

    def doGuideCallback(self):
        gfs = self.mainUI.getGuide_chk.isChecked()
        pm.undoInfo(openChunk=True)
        try:
            self.doGuide(getFromScene=gfs)
        finally:
            pm.undoInfo(closeChunk=True)


    def doRigCallback(self):
        rs = self.mainUI.reapplySkin_chk.isChecked()
        pm.undoInfo(openChunk=True)
        try:
            self.doRig(reapplySkin=rs)
        finally:
            pm.undoInfo(closeChunk=True)


    def doGuide(self, getFromScene=True):
        if getFromScene:
            noGuide = self.getGuidesSetupFromScene()
            logger.debug(noGuide)
            if noGuide:
                self.getGuidesSetupFromUI()
            else:
                self.setUIFromGuideSetup()
        else:
            self.getGuidesSetupFromUI()

        self.instance.progressBar = self.mainUI.progressBar
        self.instance.doGuides()

        guideGrp = pm.PyNode('GUIDES')

        guideGrp.visibility.set(True)

        # todo modificar pra nao esconder mesh junto com o rig
        try:
            rigGrp = pm.PyNode(self.instance.name.upper())
            rigGrp.visibility.set(False)
            mesh = pm.PyNode('MESH')
            pm.parent(mesh, w=True)
        except:
            logger.debug('No previus rig found!')
        logger.debug('Guide construction done!')

    def doRig(self, reapplySkin=False):
        if reapplySkin:
            self.instance.saveSkin()

        self.instance.progressBar = self.mainUI.progressBar
        self.instance.doRig()

        if reapplySkin:
            try:
                self.instance.loadSkin()
            except:
                logger.debug('No Rig instance found to reskin...')

        logger.debug('Rig construction done!')

    # todo verificar se nao e melhor deicar esses metodos como tools na interface geral
    @staticmethod
    def saveCtrlsShape():
        logger.debug('save ctrls')
        dirName = os.path.expanduser('~/maya/autoRig3')
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        path = os.path.join(dirName, 'temp.cntrls')
        objs = pm.ls('*_ctrl')
        controlTools.saveCntrlsShape(objs, path)

    @staticmethod
    def loadCtrlsShape():
        logger.debug('load ctrls')
        dirName = os.path.expanduser('~/maya/autoRig3')
        path = os.path.join(dirName, 'temp.cntrls')
        controlTools.loadCntrlShape(path)

    @staticmethod
    def saveSkin(self):
        logger.debug('save skin')

    @staticmethod
    def loadSkin(self):
        logger.debug('load skin')