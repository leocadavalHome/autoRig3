import pymel.core as pm
import autoRig3.composites.bipedRig as biped
import autoRig3.tools.interface as interface
import os.path

pm.loadPlugin('matrixNodes')


class BipedAutoRigUI:
    def __init__(self):
        self.bipedWindow = None
        self.bipedInstance = None
        self.handFingersCheckbox = []
        self.handFingersPhalanxRadioButton = []
        self.footFingersCheckbox = []
        self.footFingersHeelCheckbox = []
        self.footFingersPhalanxRadioButton = []
        print 'init ok'

    def createWindow(self):

        if self.bipedWindow:
            pm.deleteUI(self.bipedWindow)

        self.bipedWindow = pm.window(title='VZ BIPED RIG', iconName='bipedRig')
        self.tabs = pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

        self.basicForm = pm.columnLayout(adj=True)

        pm.text(label='VZ BIPED RIG', fn='boldLabelFont')
        pm.text(label='BASIC OPTIONS', fn='plainLabelFont')

        self.characterNameTextField = pm.textFieldGrp(label='Character Name:', w=200, h=18, ed=True, tx='character',
                                                      cw=[[1, 130], [2, 200]], cat=[(1, 'left', 5), (2, 'left', 0)])
        self.leftSidePrefixTextField = pm.textFieldGrp(label='Left Side Prefix:', w=60, h=18, ed=True, tx='L',
                                                       cw=[[1, 130], [2, 60]], cat=[(1, 'left', 5), (2, 'left', 0)])
        self.rightSidePrefixTextField = pm.textFieldGrp(label='Right Side Prefix:', w=60, h=18, ed=True, tx='R',
                                                        cw=[[1, 130], [2, 60]], cat=[(1, 'left', 5), (2, 'left', 0)])

        pm.separator(hr=True, h=30, st='single')

        self.fingerNames = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']

        for i, self.fingerName in enumerate(self.fingerNames):
            pm.rowLayout(nc=3, cw=(1, 180))
            self.handFingersCheckbox.append(pm.checkBox(v=1, en=1, label=self.fingerName + ' Finger | Phalanx: '))
            self.handFingersPhalanxRadioButton.append(
                pm.radioButtonGrp(labelArray2=['2', '3'], sl=2, ct2=['left', 'left'], co2=[0, -65],
                                  numberOfRadioButtons=2))
            pm.setParent('..')
        pm.radioButtonGrp(self.handFingersPhalanxRadioButton[0], e=True, sl=1)

        pm.separator(hr=True, h=30, st='single')

        for i, self.fingerName in enumerate(self.fingerNames):
            pm.rowLayout(nc=3, cw=(1, 180))
            self.footFingersCheckbox.append(pm.checkBox(v=1, en=1, label=self.fingerName + ' Toe | Phalanx: '))
            self.footFingersPhalanxRadioButton.append(
                pm.radioButtonGrp(labelArray2=['2', '3'], sl=1, ct2=['left', 'left'], co2=[0, -65],
                                  numberOfRadioButtons=2))
            self.footFingersHeelCheckbox.append(pm.checkBox(v=0, en=1, label=self.fingerName + ' is heel finger '))
            pm.setParent('..')

        pm.separator(hr=True, h=30, st='single')

        pm.rowLayout(nc=3, cw=(1, 180))

        self.hasArmRibbonsCheckbox = pm.checkBox(v=1, en=1, label='Arm Ribbons | Joints Number: ')
        self.armRibbonJointsIntField = pm.intField(w=62, h=18, ed=True, min=1, v=5)
        self.armRibbonFirstJointOffsetFloatField = pm.floatFieldGrp(l='First Joint Offset:', nf=1, v1=0.0,
                                                                    cat=[(1, 'left', 20), (2, 'left', -20)])
        pm.setParent('..')
        pm.rowLayout(nc=3, cw=(1, 180))
        self.hasLegRibbonsCheckbox = pm.checkBox(v=1, en=1, label='Leg Ribbons | Joints Number')
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
        self.createGuideButton = pm.button(w=263, h=20, l='saveCntrls', c=self.saveCntrlsCallback)
        self.createGuideButton = pm.button(w=263, h=20, l='loadCntrls', c=self.loadCntrlsCallback)
        self.toggleGuideButton = pm.button(w=263, h=20, l='Toggle Guide Visibility', c=self.toggleGuidesVizCallback)
        self.createRigButton = pm.button(w=263, h=30, l='Create Rig', c=self.createRigCallback)

        pm.showWindow(self.bipedWindow)

    def putToUI(self):
        pass


    def createGuideCallback(self, *args):
        fromScene = pm.checkBox(self.getFromSceneCheckbox,q=True ,v=True)
        rigName = pm.textFieldGrp(self.characterNameTextField, tx=True, q=True)
        handAllFingers = [(pm.checkBox(x, q=1, v=True), pm.checkBox(x, q=1, label=True).split(' ')[0],
                           pm.radioButtonGrp(y, q=True, sl=1)) for x, y in
                          zip(self.handFingersCheckbox, self.handFingersPhalanxRadioButton)]
        footAllFingers = [(pm.checkBox(x, q=1, v=True), pm.checkBox(x, q=1, label=True).split(' ')[0],
                           pm.radioButtonGrp(y, q=True, sl=1)) for x, y in
                          zip(self.footFingersCheckbox, self.footFingersPhalanxRadioButton)]


        handFingers = [(x[1], x[2]) for x in handAllFingers if x[0]]
        footFingers = [(x[1], x[2]) for x in footAllFingers if x[0]]

        self.bipedInstance = biped.Biped(rigName=rigName, handFingers=handFingers, footFingers=footFingers)

        if fromScene:
            self.bipedInstance.getDictsFromScene()
            self.putToUI()

        self.bipedInstance.generateGuides()

        guideGrp = pm.PyNode('GUIDES')

        guideGrp.visibility.set(True)
        try:
            rigGrp = pm.PyNode(self.bipedInstance.name.upper())
            rigGrp.visibility.set(False)
        except:
            print 'no rig'

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
            print 'no rig'

    def createRigCallback(self, *args):
        reaply = pm.checkBox(self.reapplySkinCheckbox, q=True, v=True)
        if reaply:
            self.bipedInstance.saveSkin()
        self.bipedInstance.generateRig()
        if reaply:
            self.bipedInstance.loadSkin()

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