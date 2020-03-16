import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.matrixTools as matrixTools
import autoRig3.tools.jointTools as jointTools
import pymel.core as pm
import json
import logging

logger = logging.getLogger('autoRig')

class Finger:
    """
        Cria um dedo
        Parametros:
            name (string): nome do novo dedo
            folds (int:0 a 2): numero de dobras no dedo
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone

    """

    # IMPLEMENTAR:
    # poder passar o fingerDict no momento da criacao
    # passar locators por variaveis e nao pelo dicionario

    def __init__(self, name='finger', folds=2, axis='X', fingerId=0, flipAxis=False, cntrlColor=(1,1, 0.15), **kwargs):
        self.name = name
        self.folds = folds
        self.axis = axis
        self.flipAxis = flipAxis
        self.fingerId = fingerId
        self.guideMoveall = None
        self.skinJoints = []
        self.object = None
        self.nodes = None
        self.spread = None
        ##IMPLEMENTAR padroes de nome
        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'

        grpSulfix = '_grp'

        self.toExport = {'name', 'axis', 'fingerId', 'flipAxis', 'guideDict', 'folds',
                         'moveallCntrlSetup', 'palmCntrlSetup', 'baseCntrlSetup', 'fold1CntrlSetup', 'fold2CntrlSetup',
                         'moveallGuideSetup', 'palmGuideSetup', 'baseGuideSetup', 'tipGuideSetup', 'fold1GuideSetup', 'fold2GuideSetup',
                         'palmJntSetup', 'baseJntSetup', 'tipJntSetup', 'fold1JntSetup', 'fold2JntSetup'}

        ##setaqens de aparencia dos controles
        self.moveallCntrlSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'circuloX', 'size': 0.1,
                                                'color': (1, 1, 0)}
        self.palmCntrlSetup = {'nameTempl': self.name + 'palm', 'icone': 'cubo', 'size': 0.2,
                                             'color': cntrlColor}
        if self.flipAxis:
            self.baseCntrlSetup = {'nameTempl': self.name + 'base', 'icone': 'dropZ', 'size': 0.1, 'color': cntrlColor}
        else:
            self.baseCntrlSetup = {'nameTempl': self.name + 'base', 'icone': 'circuloX', 'size': 0.5,
                                                 'color': cntrlColor}

        self.fold1CntrlSetup = {'nameTempl': self.name + 'fold1', 'icone': 'circuloX', 'size': 0.3,
                                              'color': cntrlColor}
        self.fold2CntrlSetup = {'nameTempl': self.name + 'fold2', 'icone': 'circuloX', 'size': 0.3,
                                              'color': cntrlColor}

        self.moveallGuideSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'quadradoX', 'size': 0.5,
                                                'color': (.6, 0, 0)}
        self.palmGuideSetup = {'nameTempl': self.name + 'palm', 'icone': 'circuloX', 'size': 0.4,
                                             'color': (0, 0, 1)}
        self.baseGuideSetup = {'nameTempl': self.name + 'base', 'icone': 'circuloX', 'size': 0.2,
                                             'color': (0, 0, 1)}
        self.tipGuideSetup = {'nameTempl': self.name + 'tip', 'icone': 'circuloX', 'size': 0.4,
                                            'color': (0, 0, 1)}
        self.fold1GuideSetup = {'nameTempl': self.name + 'fold1', 'icone': 'circuloX', 'size': 0.4,
                                              'color': (0, 0, 1)}
        self.fold2GuideSetup = {'nameTempl': self.name + 'fold2', 'icone': 'circuloX', 'size': 0.4,
                                              'color': (0, 0, 1)}

        self.palmJntSetup = {'nameTempl': self.name + 'Palm', 'icone': 'Bone', 'size': 0.2}
        self.baseJntSetup = {'nameTempl': self.name + 'Base', 'icone': 'Bone', 'size': 0.3}
        self.tipJntSetup = {'nameTempl': self.name, 'icone': 'Bone', 'size': 0.3}
        self.fold1JntSetup = {'nameTempl': self.name + 'Fold1', 'icone': 'Bone', 'size': 0.3}
        self.fold2JntSetup = {'nameTempl': self.name + 'Fold2', 'icone': 'Bone', 'size': 0.3}

        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)], 'palm': [(0, 0, 0), (0, 0, 0)],
                          'base': [(1, 0, 0), (0, 0, 0)], 'tip': [(2, 0, 0), (0, 0, 0)],
                          'fold1': [(0, 0.05, 0), (0, 0, 0)], 'fold2': [(0, 0, 0), (0, 0, 0)]}


    def createCntrl(self, cntrlName):
        displaySetup = self.__dict__[cntrlName+'Setup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        if pm.objExists(cntrlName):
            pm.delete(cntrlName)
        guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True, **displaySetup)
        return guide

    def setCntrl (self, cntrl, posRot, space='object'):
        cntrl.setTranslation(self.guideDict[posRot][0], space=space)
        cntrl.setRotation(self.guideDict[posRot][1], space=space)
        # Felipe --> add valores de escala
        try:
            cntrl.setScale(self.guideDict[posRot][2])

        except:
            pass

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
                expDict[key] = self.__dict__[key]
        return expDict


    def doGuide(self, **kwargs):
        self.__dict__.update(kwargs)  # atualiza com o q foi entrado

        # se existir apaga
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

            # guideName=self.fingerDict['palmGuideSetup']['nameTempl']+self.guideSulfix

        displaySetup = self.palmGuideSetup.copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        self.palmGuide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                               **displaySetup)

        displaySetup = self.baseGuideSetup.copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        self.baseGuide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                               **displaySetup)

        displaySetup = self.tipGuideSetup.copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        self.tipGuide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                              **displaySetup)

        pm.parent(self.tipGuide, self.baseGuide, self.palmGuide, self.guideMoveall)

        self.palmGuide.setTranslation(self.guideDict['palm'][0], space='object')
        self.palmGuide.setRotation(self.guideDict['palm'][1], space='object')

        self.baseGuide.setTranslation(self.guideDict['base'][0], space='object')
        self.baseGuide.setRotation(self.guideDict['base'][1], space='object')

        self.tipGuide.setTranslation(self.guideDict['tip'][0], space='object')
        self.tipGuide.setRotation(self.guideDict['tip'][1], space='object')

        # cria conforme o numero de dobras
        if self.folds == 2:
            displaySetup = self.fold1GuideSetup.copy()
            cntrlName = displaySetup['nameTempl'] + self.guideSulfix
            self.fold1Guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                    **displaySetup)

            displaySetup = self.fold2GuideSetup.copy()
            cntrlName = displaySetup['nameTempl'] + self.guideSulfix
            self.fold2Guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                    **displaySetup)

            fold1GuideGrp = pm.group(em=True)
            fold2GuideGrp = pm.group(em=True)

            pm.parent(self.fold1Guide, fold1GuideGrp)
            pm.parent(self.fold2Guide, fold2GuideGrp)
            pm.parent(fold1GuideGrp, fold2GuideGrp, self.guideMoveall)

            self.fold2Guide.setTranslation(self.guideDict['fold2'][0], space='object')
            self.fold2Guide.setRotation(self.guideDict['fold2'][1], space='object')

            self.fold1Guide.setTranslation(self.guideDict['fold1'][0], space='object')
            self.fold1Guide.setRotation(self.guideDict['fold1'][1], space='object')

            pm.aimConstraint(self.fold1Guide, self.baseGuide, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            pm.aimConstraint(self.fold2Guide, self.fold1Guide, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            pm.aimConstraint(self.fold2Guide, self.tipGuide, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            pm.aimConstraint(self.tipGuide, fold2GuideGrp, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)

            cns = pm.pointConstraint(self.baseGuide, self.tipGuide, fold1GuideGrp, mo=False)
            weightAttr = cns.target.connections(p=True, t='pointConstraint')
            pm.setAttr(weightAttr[0], 0.6)
            pm.setAttr(weightAttr[1], 0.4)
            pm.pointConstraint(self.fold1Guide, self.tipGuide, fold2GuideGrp, mo=False)

        elif self.folds == 1:
            displaySetup = self.fold1GuideSetup.copy()
            cntrlName = displaySetup['nameTempl'] + self.guideSulfix
            self.fold1Guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                    **displaySetup)
            fold1GuideGrp = pm.group(em=True)

            pm.parent(self.fold1Guide, fold1GuideGrp)
            pm.parent(fold1GuideGrp, self.guideMoveall)

            self.fold1Guide.setTranslation(self.guideDict['fold1'][0], space='object')
            self.fold1Guide.setRotation(self.guideDict['fold1'][1], space='object')

            pm.aimConstraint(self.fold1Guide, self.baseGuide, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            pm.aimConstraint(self.tipGuide, fold1GuideGrp, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            pm.aimConstraint(self.fold1Guide, self.tipGuide, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            cns = pm.pointConstraint(self.baseGuide, self.tipGuide, fold1GuideGrp, mo=False)

        elif self.folds == 0:
            displaySetup = self.fold1GuideSetup.copy()
            cntrlName = displaySetup['nameTempl'] + self.guideSulfix
            self.fold1Guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                    **displaySetup)
            fold1GuideGrp = pm.group(em=True)

            pm.parent(self.fold1Guide, fold1GuideGrp)
            pm.parent(fold1GuideGrp, self.guideMoveall)

            self.fold1Guide.setTranslation(self.guideDict['fold1'][0], space='object')
            self.fold1Guide.setRotation(self.guideDict['fold1'][1], space='object')

            pm.aimConstraint(self.tipGuide, self.baseGuide, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            pm.aimConstraint(self.baseGuide, self.tipGuide, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            cns = pm.pointConstraint(self.baseGuide, self.tipGuide, fold1GuideGrp, mo=False)

            self.fold1Guide.visibility.set(0)

        arrow = controlTools.cntrlCrv(obj=self.baseGuide, name=self.name + 'PlaneDir', icone='seta', size=.07,
                                      color=(0, 1, 1))
        arrow.template.set(1)
        arrow.getParent().setParent(self.baseGuide)
        pm.aimConstraint(self.tipGuide, arrow, weight=1, aimVector=(1, 0, 0), upVector=(0, 0, -1),
                         worldUpObject=self.fold1Guide, worldUpType='object')

        self.guideMoveall.setTranslation(self.guideDict['moveall'][0], space='object')
        self.guideMoveall.setRotation(self.guideDict['moveall'][1], space='object')
        self.guideMoveall.setScale(self.guideDict['moveall'][2], space='object')

        pm.addAttr(self.guideMoveall, ln='fingerDict', dt='string')
        # todo implantar funcao de exportacao de dict
        self.guideMoveall.fingerDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            # se existir apaga
            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.fingerDict.get()
            dictRestored = json.loads(jsonDict)
            self.__dict__.update(**dictRestored)

            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='object').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, r=True, os=True))

            guideName = self.palmGuideSetup['nameTempl'] + self.guideSulfix
            self.palmGuide = pm.PyNode(guideName)
            self.guideDict['palm'][0] = self.palmGuide.getTranslation(space='object').get()
            self.guideDict['palm'][1] = tuple(self.palmGuide.getRotation(space='object'))

            guideName = self.baseGuideSetup['nameTempl'] + self.guideSulfix
            self.baseGuide = pm.PyNode(guideName)
            self.guideDict['base'][0] = self.baseGuide.getTranslation(space='object').get()
            self.guideDict['base'][1] = tuple(self.baseGuide.getRotation(space='object'))

            guideName = self.tipGuideSetup['nameTempl'] + self.guideSulfix
            self.tipGuide = pm.PyNode(guideName)
            self.guideDict['tip'][0] = self.tipGuide.getTranslation(space='object').get()
            self.guideDict['tip'][1] = tuple(self.tipGuide.getRotation(space='object'))

            guideName = self.fold1GuideSetup['nameTempl'] + self.guideSulfix
            self.fold1Guide = pm.PyNode(guideName)
            self.guideDict['fold1'][0] = self.fold1Guide.getTranslation(space='object').get()
            self.guideDict['fold1'][1] = tuple(self.fold1Guide.getRotation(space='object'))

            if self.folds == 2:
                guideName = self.fold2GuideSetup['nameTempl'] + self.guideSulfix
                self.fold2Guide = pm.PyNode(guideName)
                self.guideDict['fold2'][0] = self.fold2Guide.getTranslation(space='object').get()
                self.guideDict['fold2'][1] = tuple(self.fold2Guide.getRotation(space='object'))
        except:
            pass

        return self.exportDict()

    def doRig(self):
        # se nao existir guide, cria um default
        if 'L_hand' in self.name or 'L_foot' in self.name:
            self.baseCntrlSetup = {'nameTempl': self.name + 'base', 'icone': 'circuloX', 'size': 0.5,
                                                 'color': (0.010, 0.050, 0.2)}
            self.palmCntrlSetup = {'nameTempl': self.name + 'palm', 'icone': 'cubo', 'size': 0.2,
                                                 'color': (0.010, 0.050, 0.2)}
            self.fold1CntrlSetup = {'nameTempl': self.name + 'fold1', 'icone': 'circuloX', 'size': 0.3,
                                                  'color': (0.010, 0.050, 0.2)}
            self.fold2CntrlSetup = {'nameTempl': self.name + 'fold2', 'icone': 'circuloX', 'size': 0.3,
                                                  'color': (0.010, 0.050, 0.2)}

        elif 'R_hand' in self.name or 'R_foot' in self.name:
            self.baseCntrlSetup = {'nameTempl': self.name + 'base', 'icone': 'circuloX', 'size': 0.5,
                                                 'color': (0.4, 0, 0)}
            self.palmCntrlSetup = {'nameTempl': self.name + 'palm', 'icone': 'cubo', 'size': 0.2,
                                                 'color': (0.4, 0, 0)}
            self.fold1CntrlSetup = {'nameTempl': self.name + 'fold1', 'icone': 'circuloX', 'size': 0.3,
                                                  'color': (0.4, 0, 0)}
            self.fold2CntrlSetup = {'nameTempl': self.name + 'fold2', 'icone': 'circuloX', 'size': 0.3,
                                                  'color': (0.4, 0, 0)}

        else:
            self.baseCntrlSetup = {'nameTempl': self.name + 'base', 'icone': 'circuloX', 'size': 0.5,
                                                 'color': (1, 1, 0.15)}
            self.palmCntrlSetup = {'nameTempl': self.name + 'palm', 'icone': 'cubo', 'size': 0.2,
                                                 'color': (1, 1, 0.15)}
            self.fold1CntrlSetup = {'nameTempl': self.name + 'fold1', 'icone': 'circuloX', 'size': 0.3,
                                                  'color': (1, 1, 0.15)}
            self.fold2CntrlSetup = {'nameTempl': self.name + 'fold2', 'icone': 'circuloX', 'size': 0.3,
                                                  'color': (1, 1, 0.15)}

        if not self.guideMoveall:
            self.doGuide()

        # se existir um modulo igual, apaga
        moveallName = self.moveallCntrlSetup['nameTempl']
        if pm.objExists(moveallName):
            pm.delete(moveallName)

        cntrlName = self.moveallCntrlSetup['nameTempl']
        self.moveall = pm.group(name=cntrlName, em=True)

        pos = pm.xform(self.guideMoveall, q=True, ws=True, t=True)
        pm.xform(self.moveall, ws=True, t=pos)

        base = pm.xform(self.baseGuide, q=True, ws=True, t=True)
        tip = pm.xform(self.tipGuide, q=True, ws=True, t=True)
        palm = pm.xform(self.palmGuide, q=True, ws=True, t=True)
        fold1 = pm.xform(self.fold1Guide, q=True, ws=True, t=True)

        # coordenadas dos 3 guides default para calculo da normal do plano de rotacao do dedo
        A = om.MVector(base)
        B = om.MVector(fold1)
        C = om.MVector(tip)

        if self.flipAxis:
            AB = A - B
            BC = B - C
        else:
            AB = B - A
            BC = C - B

        n = AB ^ BC

        # conforme o numero de dobras, especifica as guides
        # atualmente podem ser 0,1 ou 2 dobras
        if self.folds == 2:
            fold2 = pm.xform(self.fold2Guide, q=True, ws=True, t=True)
            guide = [palm, base, fold1, fold2, tip]
            jntNames = [self.palmJntSetup['nameTempl'], self.baseJntSetup['nameTempl'],
                        self.fold1JntSetup['nameTempl'], self.fold2JntSetup['nameTempl'],
                        self.tipJntSetup['nameTempl']]

        elif self.folds == 1:
            guide = [palm, base, fold1, tip]
            jntNames = [self.palmJntSetup['nameTempl'], self.baseJntSetup['nameTempl'],
                        self.fold1JntSetup['nameTempl'], self.tipJntSetup['nameTempl']]

        elif self.folds == 0:
            guide = [palm, base, tip]
            jntNames = [self.palmJntSetup['nameTempl'], self.baseJntSetup['nameTempl'],
                        self.tipJntSetup['nameTempl']]

        # cria os joints conforme a orientacao
        fingerJnts = []
        pm.select(cl=True)
        for i in range(0, len(guide) - 1):
            A = om.MVector(guide[i])
            B = om.MVector(guide[i + 1])
            if self.flipAxis:
                AB = A - B
            else:
                AB = B - A

            m = matrixTools.orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)
            jntName = jntNames[i] + self.jntSulfix
            j1 = pm.joint(n=jntName)
            fingerJnts.append(j1)
            self.skinJoints.append(j1)
            pm.xform(j1, m=m, ws=True)
            pm.makeIdentity(j1, apply=True, r=1, t=0, s=1, n=0, pn=0)

        jntName = self.tipJntSetup['nameTempl'] + self.tipJxtSulfix
        j1 = pm.joint(n=jntName)
        fingerJnts.append(j1)
        pm.xform(j1, m=m, ws=True)
        pm.xform(j1, t=C, ws=True)
        pm.makeIdentity(j1, apply=True, r=1, t=0, s=1, n=0, pn=0)

        # cria os controles
        last = None
        displaySetup = self.palmCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        cntrl0 = controlTools.cntrlCrv(name=cntrlName, connType='parentConstraint', obj=fingerJnts[0], offsets=1,**displaySetup)

        displaySetup = self.baseCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.cntrl1 = controlTools.cntrlCrv(name=cntrlName, connType='parentConstraint', obj=fingerJnts[1],offsets=1, **displaySetup)

        pm.parent(self.cntrl1.getParent(2), cntrl0)
        last = self.cntrl1

        # cria os controles conforme a o numero setado de dobras
        if self.folds > 0:
            self.cntrl1.addAttr('bend0', k=1, at=float, dv=0)
            self.cntrl1.addAttr('bend1', k=1, at=float, dv=0)
            displaySetup = self.fold1CntrlSetup.copy()
            cntrlName = displaySetup['nameTempl']
            self.cntrl2 = controlTools.cntrlCrv(name=cntrlName, connType='parentConstraint', obj=fingerJnts[2], offsets=1,
                                           **displaySetup)
            pm.parent(self.cntrl2.getParent(2), self.cntrl1)
            self.cntrl1.bend1 >> self.cntrl2.getParent().rotateY
        if self.folds > 1:
            self.cntrl1.addAttr('bend2', k=1, at=float, dv=0)
            displaySetup = self.fold2CntrlSetup.copy()
            cntrlName = displaySetup['nameTempl']
            self.cntrl3 = controlTools.cntrlCrv(name=cntrlName, connType='parentConstraint', obj=fingerJnts[3], offsets=1,
                                           **displaySetup)

            pm.parent(self.cntrl3.getParent(2), self.cntrl2)
            self.cntrl1.bend2 >> self.cntrl3.getParent().rotateY

        pm.parent(fingerJnts[0], cntrl0.getParent(2), self.moveall)

         #Henrique Ribeiro - add novos attrs
        if self.folds > 0:
            self.cntrl1.addAttr('curl', k=1, at=float, dv=0)
            self.cntrl1.addAttr('lean', k=1, at=float, dv=0)
            self.cntrl1.addAttr('scrunch', k=1, at=float, dv=0)
            self.cntrl1.addAttr('spread', k=1, at=float, dv=0)
            self.cntrl1.addAttr('twist', k=1, at=float, dv=0)

        #Henrique Ribeiro - create connections
            PMAbase = pm.createNode ('plusMinusAverage', n=self.name+'_curlBase_pma')
            PMAfold1 = pm.createNode ('plusMinusAverage', n=self.name+'_curlFold_pma')


        #curl and bend
            self.cntrl1.bend0 >> PMAbase.input1D[2]
            self.cntrl1.bend1 >> PMAfold1.input1D[0]

            self.cntrl1.curl >> PMAbase.input1D[0]
            self.cntrl1.curl >> PMAfold1.input1D[1]

            PMAbase.output1D >> self.cntrl1.getParent().rotateY
            PMAfold1.output1D >> self.cntrl2.getParent().rotateY


        #twist
            self.cntrl1.twist >> PMAbase.input2D[0].input2Dx
            PMAbase.output2Dx >> self.cntrl1.getParent().rotateX

        #spread
            self.cntrl1.spread >> PMAbase.input2D[0].input2Dy
            PMAbase.output2Dy >> self.cntrl1.getParent().rotateZ

        #scrunch
            MDLScrunchBase = pm.createNode ('multDoubleLinear', n=self.name+'_scrunchBase_pma')
            MDLScrunchFold1 = pm.createNode ('multDoubleLinear',n=self.name+'_scrunchFold1_pma')

            pm.setAttr(MDLScrunchBase + ".input2", -0.65)
            pm.setAttr(MDLScrunchFold1 + ".input2", 1.3)

            self.cntrl1.scrunch >> MDLScrunchBase.input1
            MDLScrunchBase.output >> PMAbase.input1D[1]
            self.cntrl1.scrunch >> MDLScrunchFold1.input1
            MDLScrunchFold1.output >> PMAfold1.input1D[2]


        #lean
            self.cntrl1.lean >> PMAbase.input2D[1].input2Dy
            self.cntrl1.lean >> PMAfold1.input2D[1].input2Dy
            PMAfold1.output2D.output2Dy >> self.cntrl2.getParent().rotateZ
            listNodes = [PMAbase, PMAfold1, MDLScrunchBase, MDLScrunchFold1]

        if self.folds > 1:
            PMAfold2 = pm.createNode ('plusMinusAverage', n=self.name+'_fold_pma')
            MDLScrunchFold2 = pm.createNode ('multDoubleLinear', n=self.name+'_scrunchFold2_pma')
            self.cntrl1.bend2 >> PMAfold2.input1D[0]
            self.cntrl1.curl >> PMAfold2.input1D[1]
            PMAfold2.output1D >> self.cntrl3.getParent().rotateY
            pm.setAttr(MDLScrunchBase + ".input2", -1)
            pm.setAttr(MDLScrunchFold1 + ".input2", 1)
            pm.setAttr(MDLScrunchFold2 + ".input2", 1.1)
            self.cntrl1.scrunch >> MDLScrunchFold2.input1
            MDLScrunchFold2.output >> PMAfold2.input1D[2]
            PMAfold1.output2D.output2Dy >> self.cntrl3.getParent().rotateZ
            self.cntrl1.lean >> PMAfold2.input2D[1].input2Dy
            listNodes.append(PMAfold2)
            listNodes.append(MDLScrunchFold2)

        #hide Outputs base fingers
        for cadaItem in listNodes:
            pm.setAttr(cadaItem +  ".isHistoricallyInteresting", 0)