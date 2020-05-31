import pymel.core as pm
import sys
import autoRig3.composites.bipedRig as biped
import autoRig3.tools.interface as interface
import os.path
import logging

logger = logging.getLogger(__name__)
logger.setLevel(10)

class BipedAutoRigUI:
    def __init__(self):
        self.bipedWindow = None
        self.bipedInstance = None
        self.handFingersInterface = {}
        self.footFingersInterface = {}
        self.footFingersHeelCheckbox = {}

    def createWindow(self):
        print "lala"
        if self.bipedWindow:
            pm.deleteUI(self.bipedWindow)

        self.bipedWindow = pm.window(title='VZ BIPED RIG', iconName='bipedRig')
        self.tabs = pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

        self.basicForm = pm.columnLayout(adj=True)

        pm.text(label='VZ BIPED RIG', fn='boldLabelFont')
        pm.text(label='BASIC OPTIONS', fn='plainLabelFont')

        self.characterNameTextField = pm.textFieldGrp(label='Character Name:', w=200, h=18, ed=True, tx='character',
                                                      cw=[[1, 130], [2, 200]], cat=[(1, 'left', 5), (2, 'left', 0)])

        pm.separator(hr=True, h=30, st='single')

        self.fingerNames = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']

        for i, fingerName in enumerate(self.fingerNames):
            pm.rowLayout(nc=3, cw=(1, 180))
            self.handFingersInterface[fingerName] = {}
            self.handFingersInterface[fingerName]['checkBox'] = pm.checkBox(v=1, en=1, label=fingerName + ' Finger | Phalanx: ')
            self.handFingersInterface[fingerName]['radioBtn'] = pm.radioButtonGrp(labelArray2=['2', '3'], sl=2,
                                                                                  ct2=['left', 'left'], co2=[0, -65],
                                                                                  numberOfRadioButtons=2)
            pm.setParent('..')
        pm.radioButtonGrp(self.handFingersInterface['Thumb']['radioBtn'], e=True, sl=1)

        pm.separator(hr=True, h=30, st='single')

        for i, fingerName in enumerate(self.fingerNames):
            pm.rowLayout(nc=3, cw=(1, 180))
            self.footFingersInterface[fingerName]={}
            self.footFingersInterface[fingerName]['checkBox'] = pm.checkBox(v=1, en=1, label=fingerName + ' Toe | Phalanx: ')
            self.footFingersInterface[fingerName]['radioBtn'] =  pm.radioButtonGrp(labelArray2=['2', '3'], sl=1,
                                                                       ct2=['left', 'left'], co2=[0, -65],
                                                                                numberOfRadioButtons=2)
            pm.setParent('..')

        pm.separator(hr=True, h=30, st='single')

        pm.rowLayout(nc=3, cw=(1, 180))

        self.hasArmRibbonsCheckbox = pm.checkBox(v=1, en=1, label='Arm Ribbons | Joints Number: ')
        self.armRibbonJointsIntField = pm.intField(w=62, h=18, ed=True, min=1, v=5)
        self.armRibbonFirstJointOffsetFloatField = pm.floatFieldGrp(l='First Joint Offset:', nf=1, v1=0.1,
                                                                    cat=[(1, 'left', 20), (2, 'left', -20)])
        pm.setParent('..')
        pm.rowLayout(nc=3, cw=(1, 180))
        self.hasLegRibbonsCheckbox = pm.checkBox(v=1, en=1, label='Leg Ribbons | Joints Number:')
        self.legRibbonJointsIntField = pm.intField(w=62, h=18, ed=True, min=1, v=5)
        self.legRibbonFirstJointOffsetFloatField = pm.floatFieldGrp(l='First Joint Offset:', nf=1, v1=0.1,
                                                                    cat=[(1, 'left', 20), (2, 'left', -20)])
        pm.setParent('..')

        pm.separator(hr=True, h=30, st='single')
        pm.rowLayout(nc=2, cw=(1, 180))
        pm.text(label='      Spine Joints')
        self.spineJointsIntField = pm.intField(w=62, h=18, ed=True, min=1, v=5)
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

        pm.showWindow(self.bipedWindow)

    def putToUI(self):
        handFingers = [(y['name'], y['folds']) for x, y in self.bipedInstance.lhand.fingers.iteritems()]
        footFingers = self.bipedInstance.lfoot.fingers

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
                footFingerSetup.append((finger, folds))
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
        handFingers = {x: y['folds'] for x, y in self.bipedInstance.lhand.fingers.iteritems()}
        footFingers = {x: y['folds'] for x, y in self.bipedInstance.lfoot.fingers.iteritems()}
        return handFingers, footFingers

    def createGuideCallback(self, *args):
        fromScene = pm.checkBox(self.getFromSceneCheckbox, q=True, v=True)
        rigName = pm.textFieldGrp(self.characterNameTextField, tx=True, q=True)
        fingersSetup = self.getFingerSetup()

        self.bipedInstance = biped.Biped(rigName=rigName, handFingers=fingersSetup[0], footFingers=fingersSetup[1])

        if fromScene:
            self.bipedInstance.getDictsFromScene()
            fingerSetup = self.getFingerSetupFromScene()
            self.setFingerSetup(fingerSetup=fingerSetup)

        self.bipedInstance.generateGuides()
        guideGrp = pm.PyNode('GUIDES')

        guideGrp.visibility.set(True)


        try:
            rigGrp = pm.PyNode(self.bipedInstance.name.upper())
            rigGrp.visibility.set(False)
        except:
            logger.warn('no rig...')

    def getGuidesFromSceneCallback(self, *args):
        self.bipedInstance = biped.Biped()
        self.bipedInstance.getGuidesFromScene()

    def toggleGuidesVizCallback(self, *args):
        guideGrp = pm.PyNode('GUIDES')

        viz = guideGrp.visibility.get()
        guideGrp.visibility.set(not viz)

        try:
            rigGrp = pm.PyNode(self.bipedInstance.name.upper())
            rigGrp.visibility.set(viz)
        except:
            logger.warn('no rig...')

    def createRigCallback(self, *args):
        reaply = pm.checkBox(self.reapplySkinCheckbox, q=True, v=True)
        armRibChk= pm.checkBox(self.hasArmRibbonsCheckbox,q=True, v=True)
        armRibbons = pm.intField(self.armRibbonJointsIntField, q=True, v=True)
        armOffset = pm.floatFieldGrp(self.armRibbonFirstJointOffsetFloatField, q=True, v1=True)

        legRibChk= pm.checkBox(self.hasLegRibbonsCheckbox,q=True, v=True)
        legRibbons = pm.intField(self.legRibbonJointsIntField, q=True, v=True)
        legOffset = pm.floatFieldGrp(self.legRibbonFirstJointOffsetFloatField, q=True, v1=True)
        spineJnts = pm.intField(self.spineJointsIntField, q=True, v=True)

        if not legRibChk:
            legRibbons=0
        if not armRibChk:
            armRibbons=0


        if reaply:
            self.bipedInstance.saveSkin()

        self.bipedInstance.generateRig(armRibbons=armRibbons, armOffsetStart=armOffset, armOffsetEnd=armOffset,
                                       legRibbons=legRibbons, legOffsetStart=legOffset, legOffsetEnd=legOffset,
                                       parentModules=True, spineJnts=spineJnts)
        if reaply:
            try:
                self.bipedInstance.loadSkin()
            except:
                logger.warn('no rig...')

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