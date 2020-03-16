import pymel.core as pm
import sys
import autoRig3.composites.quadrupedRig as quadruped
import autoRig3.tools.interface as interface
import os.path
import logging

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(10)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
pm.loadPlugin('matrixNodes')


class QuadrupedAutoRigUI:
    def __init__(self):
        self.QuadrupedWindow = None
        self.quadrupedInstance = None
        self.handFingersInterface = {}
        self.footFingersInterface = {}
        self.footFingersHeelCheckbox = {}

    def createWindow(self):
        if self.QuadrupedWindow:
            pm.deleteUI(self.QuadrupedWindow)

        self.QuadrupedWindow = pm.window(title='VZ Quadruped RIG', iconName='quadrupedRig')
        self.tabs = pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

        self.basicForm = pm.columnLayout(adj=True)

        pm.text(label='VZ Quadruped RIG', fn='boldLabelFont')
        pm.text(label='BASIC OPTIONS', fn='plainLabelFont')

        self.characterNameTextField = pm.textFieldGrp(label='Character Name:', w=200, h=18, ed=True, tx='character',
                                                      cw=[[1, 130], [2, 200]], cat=[(1, 'left', 5), (2, 'left', 0)])
        self.leftSidePrefixTextField = pm.textFieldGrp(label='Left Side Prefix:', w=60, h=18, ed=True, tx='L',
                                                       cw=[[1, 130], [2, 60]], cat=[(1, 'left', 5), (2, 'left', 0)])
        self.rightSidePrefixTextField = pm.textFieldGrp(label='Right Side Prefix:', w=60, h=18, ed=True, tx='R',
                                                        cw=[[1, 130], [2, 60]], cat=[(1, 'left', 5), (2, 'left', 0)])

        pm.separator(hr=True, h=30, st='single')

        self.fingerNames = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']

        for i, fingerName in enumerate(self.fingerNames):
            pm.rowLayout(nc=3, cw=(1, 180))
            self.handFingersInterface[fingerName] = {}
            self.handFingersInterface[fingerName]['checkBox'] = pm.checkBox(v=1, en=1, label=fingerName + ' fr Toe | Phalanx: ')
            self.handFingersInterface[fingerName]['radioBtn'] = pm.radioButtonGrp(labelArray2=['2', '3'], sl=1,
                                                                                  ct2=['left', 'left'], co2=[0, -65],
                                                                                  numberOfRadioButtons=2)
            pm.setParent('..')

        pm.separator(hr=True, h=30, st='single')

        for i, fingerName in enumerate(self.fingerNames):
            pm.rowLayout(nc=3, cw=(1, 180))
            self.footFingersInterface[fingerName]={}
            self.footFingersInterface[fingerName]['checkBox'] = pm.checkBox(v=1, en=1, label=fingerName + ' bk Toe | Phalanx: ')
            self.footFingersInterface[fingerName]['radioBtn'] = pm.radioButtonGrp(labelArray2=['2', '3'], sl=1,
                                                                       ct2=['left', 'left'], co2=[0, -65],
                                                                                numberOfRadioButtons=2)
            pm.setParent('..')

        pm.separator(hr=True, h=30, st='single')
        pm.rowLayout(nc=2, cw=(1, 180))
        self.hasTailCheckbox = pm.checkBox(v=1, en=1, label='Tail | Joints Number:')
        self.tailJointsIntField = pm.intField(w=62, h=18, ed=True, min=1, v=5)

        pm.setParent('..')

        pm.separator(hr=True, h=30, st='single')
        pm.rowLayout(nc=2, cw=(1, 180))
        pm.text(label='      Spine Joints')
        self.spineJointsIntField = pm.intField(w=62, h=18, ed=True, min=1, v=5)

        pm.setParent('..')
        pm.separator(hr=True, h=30, st='single')

        pm.rowLayout(nc=3, cw=(1, 180))

        self.hasArmRibbonsCheckbox = pm.checkBox(v=1, en=1, label='Front Leg Ribbons | Joints Number: ')
        self.armRibbonJointsIntField = pm.intField(w=62, h=18, ed=True, min=1, v=5)
        self.armRibbonFirstJointOffsetFloatField = pm.floatFieldGrp(l='First Joint Offset:', nf=1, v1=0.0,
                                                                    cat=[(1, 'left', 20), (2, 'left', -20)])
        pm.setParent('..')
        pm.rowLayout(nc=3, cw=(1, 180))
        self.hasLegRibbonsCheckbox = pm.checkBox(v=1, en=1, label='Back Leg Ribbons | Joints Number:')
        self.legRibbonJointsIntField = pm.intField(w=62, h=18, ed=True, min=1, v=5)
        self.legRibbonFirstJointOffsetFloatField = pm.floatFieldGrp(l='First Joint Offset:', nf=1, v1=0.0,
                                                                    cat=[(1, 'left', 20), (2, 'left', -20)])
        pm.setParent('..')

        pm.separator(hr=True, h=30, st='single')

        pm.rowLayout(nc=2, cw=(1, 180))
        pm.text(l='Modules connection:', fn='plainLabelFont')
        self.modulesConnectionRadioButton = pm.radioButtonGrp(labelArray2=['Hierarchy', 'Constraint'], sl=1,
                                                              ct2=['left', 'left'], numberOfRadioButtons=2)
        pm.setParent('..')


        pm.separator(hr=True, h=30, st='single')

        self.getFromSceneCheckbox = pm.checkBox(v=1, en=1, label='Get Guide From Scene')
        self.reapplySkinCheckbox = pm.checkBox(v=0, en=1, label='Reapply skin after rebuilding rig')
        pm.separator( h=30 )

        self.createGuideButton = pm.button(w=263, h=20, l='Create guide', c=self.createGuideCallback)
        self.createGuideButton = pm.button(w=263, h=20, l='Save Ctrls', c=self.saveCntrlsCallback)
        self.createGuideButton = pm.button(w=263, h=20, l='Load Ctrls', c=self.loadCntrlsCallback)
        self.toggleGuideButton = pm.button(w=263, h=20, l='Toggle Guide Visibility', c=self.toggleGuidesVizCallback)
        self.createRigButton = pm.button(w=263, h=30, l='Create Rig', c=self.createRigCallback)

        pm.showWindow(self.QuadrupedWindow)

    def putToUI(self):
        handFingers = [(y['name'], y['folds']) for x, y in self.quadrupedInstance.lhand.fingers.iteritems()]
        footFingers = self.quadrupedInstance.lfoot.fingers

    def getFingerSetup(self):
        handFingerSetup = []
        footFingerSetup = []
        fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        for finger in fingers:
            if pm.checkBox(self.handFingersInterface[finger]['checkBox'], q=True, v=True):
                folds = pm.radioButtonGrp(self.handFingersInterface[finger]['radioBtn'], q=True, sl=True)
                handFingerSetup.append((finger, folds))
            if pm.checkBox(self.footFingersInterface[finger]['checkBox'], q=True, v=True):
                folds = pm.radioButtonGrp(self.footFingersInterface[finger]['radioBtn'], q=True, sl=True)
                footFingerSetup.append ((finger, folds))
        return handFingerSetup, footFingerSetup

    def setFingerSetup(self, fingerSetup):

        fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        for finger in fingers:
            if finger in fingerSetup[0]:
                pm.checkBox(self.handFingersInterface[finger]['checkBox'], e=True, v=1)
                pm.radioButtonGrp(self.handFingersInterface[finger]['radioBtn'], e=True, sl=fingerSetup[0][finger])
            else:
                pm.checkBox(self.handFingersInterface[finger]['checkBox'], e=True, v=0)

            if finger in fingerSetup[1]:
                pm.checkBox(self.footFingersInterface[finger]['checkBox'], e=True, v=1)
                pm.radioButtonGrp(self.footFingersInterface[finger]['radioBtn'], e=True, sl=fingerSetup[1][finger])
            else:
                pm.checkBox(self.footFingersInterface[finger]['checkBox'], e=True, v=0)

    def getFingerSetupFromScene(self):
        handFingers = {x: y['folds'] for x, y in self.quadrupedInstance.lfrFoot.fingers.iteritems()}
        footFingers = {x: y['folds'] for x, y in self.quadrupedInstance.lbkFoot.fingers.iteritems()}
        return handFingers, footFingers

    def createGuideCallback(self, *args):
        fromScene = pm.checkBox(self.getFromSceneCheckbox, q=True, v=True)
        rigName = pm.textFieldGrp(self.characterNameTextField, tx=True, q=True)
        fingersSetup = self.getFingerSetup()
        hasTailChk = pm.checkBox(self.hasTailCheckbox, q=True, v=True)
        tailJnts = pm.intField(self.tailJointsIntField, q=True, v=True)
        spineJnts = pm.intField(self.spineJointsIntField, q=True, v=True)

        if not hasTailChk:
            tailJnts = 0

        self.quadrupedInstance = quadruped.Quadruped(rigName=rigName,spineJnts=spineJnts,
                                                     tailJnts=tailJnts,
                                                     handFingers=fingersSetup[0],
                                                     footFingers=fingersSetup[1])

        if fromScene:
            self.quadrupedInstance.getDictsFromScene()
            fingerSetup = self.getFingerSetupFromScene()
            self.setFingerSetup(fingerSetup=fingerSetup)

        self.quadrupedInstance.generateGuides()
        guideGrp = pm.PyNode('GUIDES')

        guideGrp.visibility.set(True)


        try:
            rigGrp = pm.PyNode(self.quadrupedInstance.name.upper())
            rigGrp.visibility.set(False)
        except:
            logger.warn('no rig yet')

    def getGuidesFromSceneCallback(self, *args):
        self.quadrupedInstance = quadruped.Quadruped()
        self.quadrupedInstance.getGuidesFromScene()


    def toggleGuidesVizCallback(self, *args):
        guideGrp = pm.PyNode('GUIDES')

        viz = guideGrp.visibility.get()
        guideGrp.visibility.set(not viz)

        try:
            rigGrp = pm.PyNode(self.quadrupedInstance.name.upper())
            rigGrp.visibility.set(viz)
        except:
            logger.error ('no rig')

    def createRigCallback(self, *args):
        reaply = pm.checkBox(self.reapplySkinCheckbox, q=True, v=True)
        armRibChk= pm.checkBox(self.hasArmRibbonsCheckbox, q=True, v=True)
        armRibbons = pm.intField(self.armRibbonJointsIntField, q=True, v=True)
        armOffset = pm.floatFieldGrp(self.armRibbonFirstJointOffsetFloatField, q=True, v1=True)

        legRibChk= pm.checkBox(self.hasLegRibbonsCheckbox, q=True, v=True)
        legRibbons = pm.intField(self.legRibbonJointsIntField, q=True, v=True)
        legOffset = pm.floatFieldGrp(self.legRibbonFirstJointOffsetFloatField, q=True, v1=True)
        parentModulesSel = pm.radioButtonGrp(self.modulesConnectionRadioButton, q=True, sl=True)
        spineJnts = pm.intField(self.spineJointsIntField, q=True, v=True)

        print 'parent', parentModulesSel

        if parentModulesSel == 1:

            parentModules=True
        else:
            parentModules=False


        print armRibbons, legRibbons
        if not legRibChk:
            legRibbons = 0

        if not armRibChk:
            armRibbons = 0

        if reaply:
            self.quadrupedInstance.saveSkin()

        self.quadrupedInstance.generateRig(armRibbons=armRibbons, armOffsetStart=armOffset, armOffsetEnd=armOffset,
                                       legRibbons=legRibbons, legOffsetStart=legOffset, legOffsetEnd=legOffset,
                                       parentModules=parentModules, spineJnts=spineJnts)

        if reaply:
            try:
                self.quadrupedInstance.loadSkin()
            except:
                logger.error('nao tem rig ainda...')

    def saveCntrlsCallback(self, *args):
        dirName = os.path.expanduser('~/maya/autoRig3')
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        path = os.path.join(dirName, 'temp.cntrls')
        objs = pm.ls('*_ctrl')
        interface.saveCntrlsShape(objs, path)

    def loadCntrlsCallback(self, *args):
        dirName = os.path.expanduser('~/maya/autoRig3')
        path = os.path.join(dirName,'temp.cntrls')
        interface.loadCntrlShape(path)