import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.controlTools as controlTools
from autoRig3.modules import aimTwistDivider
import json
import logging

logger = logging.getLogger('autoRig')

class Neck:
    """
        Cria um pescoco com um joint de distribuicao de twist
        Parametros: 
            name (string): nome do novo limb            
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone

    """

    def __init__(self, name='neck', flipAxis=False, axis='X', **kwargs):
        self.axis = axis
        self.flipAxis = flipAxis
        self.name = name
        self.guideMoveall = None
        self.skinJoints = []
        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'
        self.zeroJxtSulfix = 'Zero_jxt'
        self.grpSulfix = '_grp'

        self.toExport = {'moveallCntrlSetup', 'startCntrlSetup', 'endCntrlSetup', 'moveallGuideSetup',
                         'startGuideSetup',  'endGuideSetup', 'midGuideSetup', 'guideDict', 'name', 'axis', 'flipAxis'}

        self.moveallCntrlSetup = {'nameTempl': name + 'Moveall', 'icone': 'circuloX', 'size': 1,
                                              'color': (0, 1, 0)}
        self.startCntrlSetup = {'nameTempl': 'Neck', 'icone': 'circuloY', 'size': 3, 'color': (0, 1, 0)}
        self.endCntrlSetup = {'nameTempl': 'Head', 'icone': 'circuloZ', 'size': 2, 'color': (0, 1, 0)}

        self.moveallGuideSetup = {'nameTempl': name + 'Moveall', 'icone': 'quadradoY', 'size': 2.5,
                                              'color': (1, 0, 0)}
        self.startGuideSetup = {'nameTempl': 'neck', 'icone': 'circuloY', 'size': 2, 'color': (0, 0, 1)}
        self.endGuideSetup = {'nameTempl': 'head', 'icone': 'circuloZ', 'size': 4, 'color': (0, 0, 1)}
        self.midGuideSetup = {'nameTempl': 'midNeck', 'size': 1, 'color': (0, 1, 0)}

        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)], 'start': [(0, 0, 0), (0, 0, 0)],
                          'end': [(0, 2, 0), (0, 0, 0)]}


    def exportDict(self):
        expDict = {}
        for key in self.toExport:
                expDict[key] = self.__dict__[key]
        return expDict

    def setCntrl (self, cntrl, posRot, space='object'):
        cntrl.setTranslation(self.guideDict[posRot][0], space=space)
        cntrl.setRotation(self.guideDict[posRot][1], space=space)
        # Felipe --> add valores de escala
        try:
            cntrl.setScale(self.guideDict[posRot][2])

        except:
            pass

    def doGuide(self, **kwargs):
        self.__dict__.update(kwargs)

        # apaga se existir
        displaySetup = self.moveallGuideSetup.copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.guideMoveall = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                  **displaySetup)

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

        displaySetup = self.startGuideSetup.copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        self.startGuide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                **displaySetup)

        displaySetup = self.endGuideSetup.copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        self.endGuide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                              **displaySetup)

        pm.parent(self.startGuide, self.endGuide, self.guideMoveall)
        self.setCntrl(self.endGuide, 'end', space='object')
        self.setCntrl(self.startGuide, 'start', space='object')
        self.setCntrl(self.guideMoveall, 'moveall', space='world')

        pm.addAttr(self.guideMoveall, ln='neckDict', dt='string')
        self.guideMoveall.neckDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            cntrlName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(cntrlName)

            jsonDict = self.guideMoveall.neckDict.get()
            dictRestored = json.loads(jsonDict)
            self.__dict__.update(**dictRestored)

            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            cntrlName = self.startGuideSetup['nameTempl'] + self.guideSulfix
            self.startGuide = pm.PyNode(cntrlName)
            self.guideDict['start'][0] = self.startGuide.getTranslation(space='object').get()
            self.guideDict['start'][1] = tuple(self.startGuide.getRotation(space='object'))

            cntrlName = self.endGuideSetup['nameTempl'] + self.guideSulfix
            self.endGuide = pm.PyNode(cntrlName)
            self.guideDict['end'][0] = self.endGuide.getTranslation(space='object').get()
            self.guideDict['end'][1] = tuple(self.endGuide.getRotation(space='object'))
        except:
            pass


    def doRig(self):
        # se nao tiver guide faz um padrao
        if not self.guideMoveall:
            self.doGuide()

        # apagar se ja houver um grupo moveall
        cntrlName = self.moveallCntrlSetup['nameTempl']

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.moveall = pm.group(empty=True, n=cntrlName)
        pos = pm.xform(self.guideMoveall, q=True, ws=True, t=True)
        pm.xform(self.moveall, ws=True, t=pos)

        if not pm.objExists('MOVEALL'):
            pm.group(self.moveall, n='MOVEALL')
        else:
            pm.parent(self.moveall, 'MOVEALL')

        # doRig
        start = pm.xform(self.startGuide, q=True, t=True, ws=True)
        end = pm.xform(self.endGuide, q=True, t=True, ws=True)

        A = om.MVector(start)
        B = om.MVector(end)
        Z = om.MVector(0, 0, -1)
        AB = B - A
        dot = Z.normal() * AB.normal()  # se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        if abs(dot) > .95:
            Z = om.MVector(0, -1, 0)

        n = AB ^ Z
        m = controlTools.orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)
        pm.select(cl=True)

        jntName = self.startGuideSetup['nameTempl'] + self.jntSulfix
        self.startJnt = pm.joint(n=jntName)
        self.skinJoints.append(self.startJnt)
        pm.xform(self.startJnt, m=m, ws=True)
        pm.makeIdentity(self.startJnt, apply=True, r=1, t=0, s=1, n=0, pn=0)

        jntName = self.endGuideSetup['nameTempl'] + self.jntSulfix
        self.endJnt = pm.joint(n=jntName)
        self.skinJoints.append(self.endJnt)
        pm.xform(self.endJnt, m=m, ws=True)
        pm.xform(self.endJnt, t=B, ws=True)
        pm.makeIdentity(self.endJnt, apply=True, r=1, t=0, s=1, n=0, pn=0)
        pm.select(cl=True)

        jntName = self.midGuideSetup['nameTempl'] + self.jntSulfix
        self.midJnt = pm.joint(n=jntName)
        self.skinJoints.append(self.midJnt)
        pm.xform(self.midJnt, m=m, ws=True)
        pm.xform(self.midJnt, t=(0, 0, 0), ws=True)
        pm.makeIdentity(self.midJnt, apply=True, r=1, t=0, s=1, n=0, pn=0)

        aimTwist = aimTwistDivider.AimTwistDivider(name=self.name + 'TwistDiv')
        aimTwist.start.setParent(self.startJnt, r=True)
        aimTwist.end.setParent(self.endJnt, r=True)
        aimTwist.mid.setParent(self.moveall)
        self.midJnt.setParent(aimTwist.mid)
        self.midJnt.translate.set(0, 0, 0)
        self.midJnt.rotate.set(0, 0, 0)

        displaySetup = self.startCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.startCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)
        pm.parentConstraint(self.startCntrl, self.startJnt, mo=True)

        displaySetup = self.endCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.endCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.endGuide, **displaySetup)
        pm.parentConstraint(self.endCntrl, self.endJnt, mo=True)
        self.endCntrl.scale >> self.endJnt.scale
        self.endCntrl.getParent().setParent(self.startCntrl)

        pm.parent(self.startJnt, self.startCntrl.getParent(), self.moveall)

        # IMPLEMENTAR: guardar as posicoes dos guides ao final
