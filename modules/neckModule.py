import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.rigFunctions as rigFunctions
from autoRig3.modules import aimTwistDivider
import json


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
        grpSulfix = '_grp'

        # parametros de aparencia dos controles
        self.neckDict = {'name': name, 'axis': axis, 'flipAxis': flipAxis}
        self.neckDict['moveallCntrlSetup'] = {'nameTempl': name + 'Moveall', 'icone': 'circuloX', 'size': 1,
                                              'color': (0, 1, 0)}
        self.neckDict['startCntrlSetup'] = {'nameTempl': 'Neck', 'icone': 'circuloY', 'size': 3, 'color': (0, 1, 0)}
        self.neckDict['endCntrlSetup'] = {'nameTempl': 'Head', 'icone': 'circuloZ', 'size': 2, 'color': (0, 1, 0)}

        self.neckDict['moveallGuideSetup'] = {'nameTempl': name + 'Moveall', 'icone': 'quadradoY', 'size': 2.5,
                                              'color': (1, 0, 0)}
        self.neckDict['startGuideSetup'] = {'nameTempl': 'neck', 'icone': 'circuloY', 'size': 2, 'color': (0, 0, 1)}
        self.neckDict['endGuideSetup'] = {'nameTempl': 'head', 'icone': 'circuloZ', 'size': 4, 'color': (0, 0, 1)}
        self.neckDict['midGuideSetup'] = {'nameTempl': 'midNeck', 'size': 1, 'color': (0, 1, 0)}

        self.neckDict['guideDict'] = {}
        self.neckDict.update(kwargs)
        self.neckGuideDict = {'moveall': [(0, 0, 0), (0, 0, 0)], 'start': [(0, 0, 0), (0, 0, 0)],
                              'end': [(0, 2, 0), (0, 0, 0)]}
        self.neckGuideDict.update(self.neckDict['guideDict'])
        self.neckDict['guideDict'] = self.neckGuideDict.copy()

    def doGuide(self, **kwargs):
        self.neckDict.update(kwargs)

        # apaga se existir
        displaySetup = self.neckDict['moveallGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.guideMoveall = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                  **displaySetup)

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

        displaySetup = self.neckDict['startGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        self.startGuide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                **displaySetup)

        displaySetup = self.neckDict['endGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        self.endGuide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                              **displaySetup)

        pm.parent(self.startGuide, self.endGuide, self.guideMoveall)

        pm.xform(self.endGuide, t=self.neckDict['guideDict']['end'][0], ro=self.neckDict['guideDict']['end'][1], os=True)
        pm.xform(self.startGuide, t=self.neckDict['guideDict']['start'][0], ro=self.neckDict['guideDict']['start'][1], os=True)

        self.guideMoveall.translate.set(self.neckDict['guideDict']['moveall'][0])
        self.guideMoveall.rotate.set(self.neckDict['guideDict']['moveall'][1])

        pm.addAttr(self.guideMoveall, ln='neckDict', dt='string')
        self.guideMoveall.neckDict.set(json.dumps(self.neckDict))

    def getGuideFromScene(self):
        try:
            cntrlName = self.neckDict['moveallGuideSetup']['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(cntrlName)

            cntrlName = self.neckDict['startGuideSetup']['nameTempl'] + self.guideSulfix
            self.startGuide = pm.PyNode(cntrlName)

            cntrlName = self.neckDict['endGuideSetup']['nameTempl'] + self.guideSulfix
            self.endGuide = pm.PyNode(cntrlName)
        except:
            print 'algum nao funcionou'

    def getDict(self):
        try:
            cntrlName = self.neckDict['moveallGuideSetup']['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(cntrlName)

            jsonDict = self.guideMoveall.neckDict.get()
            dictRestored = json.loads(jsonDict)
            self.neckDict.update(**dictRestored)

            self.neckDict['guideDict']['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.neckDict['guideDict']['moveall'][1] = tuple(self.guideMoveall.getRotation(space='world'))

            cntrlName = self.neckDict['startGuideSetup']['nameTempl'] + self.guideSulfix
            self.startGuide = pm.PyNode(cntrlName)
            self.neckDict['guideDict']['start'][0] = self.startGuide.getTranslation(space='object').get()
            self.neckDict['guideDict']['start'][1] = tuple(self.startGuide.getRotation(space='object'))

            cntrlName = self.neckDict['endGuideSetup']['nameTempl'] + self.guideSulfix
            self.endGuide = pm.PyNode(cntrlName)
            self.neckDict['guideDict']['end'][0] = self.endGuide.getTranslation(space='object').get()
            self.neckDict['guideDict']['end'][1] = tuple(self.endGuide.getRotation(space='object'))
        except:
            print 'algum nao funcionou'

        return self.neckDict

    def doRig(self):
        # se nao tiver guide faz um padrao
        if not self.guideMoveall:
            self.doGuide()

        # apagar se ja houver um grupo moveall
        cntrlName = self.neckDict['moveallCntrlSetup']['nameTempl']
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
        m = rigFunctions.orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)
        pm.select(cl=True)

        jntName = self.neckDict['startGuideSetup']['nameTempl'] + self.jntSulfix
        self.startJnt = pm.joint(n=jntName)
        self.skinJoints.append(self.startJnt)
        pm.xform(self.startJnt, m=m, ws=True)
        pm.makeIdentity(self.startJnt, apply=True, r=1, t=0, s=1, n=0, pn=0)

        jntName = self.neckDict['endGuideSetup']['nameTempl'] + self.jntSulfix
        self.endJnt = pm.joint(n=jntName)
        self.skinJoints.append(self.endJnt)
        pm.xform(self.endJnt, m=m, ws=True)
        pm.xform(self.endJnt, t=B, ws=True)
        pm.makeIdentity(self.endJnt, apply=True, r=1, t=0, s=1, n=0, pn=0)
        pm.select(cl=True)

        jntName = self.neckDict['midGuideSetup']['nameTempl'] + self.jntSulfix
        self.midJnt = pm.joint(n=jntName)
        self.skinJoints.append(self.midJnt)
        pm.xform(self.midJnt, m=m, ws=True)
        pm.xform(self.midJnt, t=(0, 0, 0), ws=True)
        pm.makeIdentity(self.midJnt, apply=True, r=1, t=0, s=1, n=0, pn=0)

        aimTwist = aimTwistDivider.AimTwistDivider()
        aimTwist.start.setParent(self.startJnt, r=True)
        aimTwist.end.setParent(self.endJnt, r=True)
        aimTwist.mid.setParent(self.moveall)
        self.midJnt.setParent(aimTwist.mid)
        self.midJnt.translate.set(0, 0, 0)
        self.midJnt.rotate.set(0, 0, 0)

        displaySetup = self.neckDict['startCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.startCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)
        pm.parentConstraint(self.startCntrl, self.startJnt, mo=True)
        displaySetup = self.neckDict['endCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.endCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.endGuide, **displaySetup)
        pm.parentConstraint(self.endCntrl, self.endJnt, mo=True)
        self.endCntrl.getParent().setParent(self.startCntrl)
        pm.parent(self.startJnt, self.startCntrl.getParent(), self.moveall)

        # IMPLEMENTAR: guardar as posicoes dos guides ao final
