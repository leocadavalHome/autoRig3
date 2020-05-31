import pymel.core as pm
from autoRig3.modules.baseModule import BaseModule
import json
import autoRig3.tools.controlTools as controlTools


class EyeLookAt(BaseModule):
    def __init__(self, name='eye', flipAxis=False, axis='X', **kwargs):
        super(EyeLookAt, self).__init__ ()
        self.name = name
        self.flipAxis = flipAxis
        self.axis = axis
        self.guideSulfix = '_guide'
        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)]}
        self.moveallGuideSetup = {'nameTempl': self.name + 'Moveall', 'icone': 'circuloZ', 'size': 2.5,
                                  'color': (1, 0, 0)}
        self.lookAtCntrlSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'circuloZ', 'size': 1.8,
                                               'color': (1, 1, 0)}

        self.toExport = {'name', 'axis', 'flipAxis', 'guideDict'}
        self.guideMoveall = None

    def doGuide(self, **kwargs):
        self.__dict__.update(kwargs)

        self.guideMoveall = self.createCntrl('moveallGuide')
        self.setCntrl(self.guideMoveall, 'moveall', space='world')

        pm.addAttr(self.guideMoveall, ln='eyeLookAtDict', dt='string')
        self.guideMoveall.eyeLookAtDict.set(json.dumps(self.exportDict()))

    def mirrorConnectGuide(self, eye):
        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')
            self.guideMoveall = None

        if not self.guideMoveall:
            self.doGuide()
        if not eye.guideMoveall:
            eye.doGuide()

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')

        if not pm.objExists('GUIDES'):
            pm.group(self.name + 'MirrorGuide_grp', n='GUIDES')
        else:
            pm.parent(self.name + 'MirrorGuide_grp', 'GUIDES')

        self.guideMoveall.setParent(self.mirrorGuide)
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.scaleY.set(1)
        self.mirrorGuide.scaleZ.set(1)
        self.mirrorGuide.scale.lock()
        self.mirrorGuide.rotate.lock()
        self.mirrorGuide.translate.lock()
        self.mirrorGuide.template.set(1)

        eye.guideMoveall.translate >> self.guideMoveall.translate
        eye.guideMoveall.rotate >> self.guideMoveall.rotate
        eye.guideMoveall.scale >> self.guideMoveall.scale

        if eye.flipAxis:
            self.flipAxis = False
        else:
            self.flipAxis = True

    def getDict(self):
        try:
            cntrlName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(cntrlName)

            jsonDict = self.guideMoveall.eyeLookAtDict.get()
            dictRestored = json.loads(jsonDict)
            self.__dict__.update(**dictRestored)
            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

        except:
            pass

    def doRig(self):
        # se nao tiver guide faz um padrao
        if not self.guideMoveall:
           self.doGuide()

        displaySetup = self.lookAtCntrlSetup.copy()
        cntrlName = self.lookAtCntrlSetup['nameTempl']

        if pm.objExists(cntrlName+'_grp'):
            pm.delete(cntrlName+'_grp')

        self.lookAt = controlTools.cntrlCrv(name=cntrlName, obj=self.guideMoveall, **displaySetup)


class LookAtCntrl(BaseModule):
    def __init__(self, name='EyeLookAt', eyes=None,  **kwargs):
        super(LookAtCntrl, self).__init__()
        self.toExport = {'name', 'guideDict', 'moveallGuideSetup', 'eyeGuideSetup', 'lookAtCntrlSetup', 'eyeCntrlSetup'}
        self.name = name
        self.guideSulfix='_guide'

        if not eyes:
            self.eyes = {'L_eye': [(1, 0, 0), (0, 0, 0), (1, 1, 1)], 'R_eye': [(-1, 0, 0), (0, 0, 0), (1, 1, 1)]}
        else:
            self.eyes = eyes

        self.eyeInstances = {}
        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)]}

        self.moveallGuideSetup = {'nameTempl': self.name + 'Moveall', 'icone': 'circuloZ', 'size': 2.5,
                                  'color': (1, 1, 0)}
        self.eyeGuideSetup = {'nameTempl': self.name, 'icone': 'circuloZ', 'size': 2.5, 'color': (1, 0, 0)}

        self.lookAtCntrlSetup = {'nameTempl': self.name, 'icone': 'circuloZ', 'size': 1.8, 'color': (1, 1, 0)}
        self.eyeCntrlSetup = {'nameTempl': self.name, 'icone': 'circuloZ', 'size': 1.8, 'color': (1, 1, 0)}

        for eye in self.eyes:
            self.eyeInstances[eye] = EyeLookAt(name=eye)

    def doGuide(self, **kwargs):
        self.__dict__.update(kwargs)

        displaySetup = self.moveallGuideSetup.copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.guideMoveall = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='',
                                                  hasHandle=True, **displaySetup)

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')


        for eye in self.eyes:
            guideDict={'moveall': self.guideDict[eye]}
            self.eyeInstances[eye].doGuide(name=eye, guideDict=guideDict)
            pm.parent(self.eyeInstances[eye].guideMoveall, self.guideMoveall)

        self.eyeInstances[self.eyes[-1]].mirrorConnectGuide(self.eyeInstances[self.eyes[0]])
        pm.parent(self.eyeInstances[self.eyes[-1]].mirrorGuide, self.guideMoveall)
        self.setCntrl(self.guideMoveall, 'moveall', space='world')

    def doRig(self):
        pass

    def getDict(self):
        pass

x= LookAtCntrl(name='teste')
x.doGuide()