import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.rigFunctions as rigFunctions
import json

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

    def __init__(self, name='finger', folds=2, axis='X', flipAxis=False, **kwargs):
        self.name = name
        self.folds = folds
        self.axis = axis
        self.flipAxis = flipAxis
        self.guideMoveall = None
        self.skinJoints = []
        ##IMPLEMENTAR padroes de nome
        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'
        grpSulfix = '_grp'

        ##setaqens de aparencia dos controles
        self.fingerDict = {'name': name, 'folds': folds, 'axis': axis, 'flipAxis': flipAxis}


        self.fingerDict['moveallCntrlSetup'] = {'nameTempl': self.name + 'MoveAll', 'icone': 'circuloX', 'size': 0.1,
                                                'color': (1, 1, 0)}
        self.fingerDict['palmCntrlSetup'] = {'nameTempl': self.name + 'palm', 'icone': 'cubo', 'size': 0.2,
                                             'color': (1, 0, 0)}
        if self.flipAxis:
            self.fingerDict['baseCntrlSetup'] = {'nameTempl': self.name + 'base', 'icone': 'dropZ', 'size': 0.1,
                                                 'color': (1, 1, 0)}
        else:
            self.fingerDict['baseCntrlSetup'] = {'nameTempl': self.name + 'base', 'icone': 'dropMenosZ', 'size': 0.1,
                                                 'color': (1, 1, 0)}
            # self.fingerDict['tipCntrlSetup']={'nameTempl':self.name+'tip', 'icone':'circuloX','size':0.3,'color':(0,1,1) }

        self.fingerDict['fold1CntrlSetup'] = {'nameTempl': self.name + 'fold1', 'icone': 'circuloX', 'size': 0.3,
                                              'color': (0, 1, 1)}
        self.fingerDict['fold2CntrlSetup'] = {'nameTempl': self.name + 'fold2', 'icone': 'circuloX', 'size': 0.3,
                                              'color': (0, 1, 1)}

        self.fingerDict['moveallGuideSetup'] = {'nameTempl': self.name + 'MoveAll', 'icone': 'quadradoX', 'size': 0.5,
                                                'color': (.6, 0, 0)}
        self.fingerDict['palmGuideSetup'] = {'nameTempl': self.name + 'palm', 'icone': 'circuloX', 'size': 0.4,
                                             'color': (0, 0, 1)}
        self.fingerDict['baseGuideSetup'] = {'nameTempl': self.name + 'base', 'icone': 'circuloX', 'size': 0.4,
                                             'color': (0, 0, 1)}
        self.fingerDict['tipGuideSetup'] = {'nameTempl': self.name + 'tip', 'icone': 'circuloX', 'size': 0.4,
                                            'color': (0, 0, 1)}
        self.fingerDict['fold1GuideSetup'] = {'nameTempl': self.name + 'fold1', 'icone': 'circuloX', 'size': 0.4,
                                              'color': (0, 0, 1)}
        self.fingerDict['fold2GuideSetup'] = {'nameTempl': self.name + 'fold2', 'icone': 'circuloX', 'size': 0.4,
                                              'color': (0, 0, 1)}

        self.fingerDict['palmJntSetup'] = {'nameTempl': self.name + 'Palm', 'icone': 'Bone', 'size': 0.2}
        self.fingerDict['baseJntSetup'] = {'nameTempl': self.name + 'Base', 'icone': 'Bone', 'size': 0.3}
        self.fingerDict['tipJntSetup'] = {'nameTempl': self.name, 'icone': 'Bone', 'size': 0.3}
        self.fingerDict['fold1JntSetup'] = {'nameTempl': self.name + 'Fold1', 'icone': 'Bone', 'size': 0.3}
        self.fingerDict['fold2JntSetup'] = {'nameTempl': self.name + 'Fold2', 'icone': 'Bone', 'size': 0.3}
        self.fingerDict['guideDict'] = {}
        self.fingerGuideDict = {'moveall': [(0, 0, 0), (0, 0, 0)], 'palm': [(0, 0, 0), (0, 0, 0)],
                                'base': [(1, 0, 0), (0, 0, 0)], 'tip': [(2, 0, 0), (0, 0, 0)],
                                'fold1': [(0, 0.05, 0), (0, 0, 0)], 'fold2': [(0, 0, 0), (0, 0, 0)]}

        self.fingerDict.update(kwargs)
        self.fingerGuideDict.update(self.fingerDict['guideDict'])
        self.fingerDict['guideDict'] = self.fingerGuideDict.copy()

    # guide
    def doGuide(self, **kwargs):
        self.fingerGuideDict = self.fingerDict['guideDict'].copy()
        self.fingerGuideDict.update(kwargs)  # atualiza com o q foi entrado

        # se existir apaga
        displaySetup = self.fingerDict['moveallGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.guideMoveall = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                  **displaySetup)

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

            # guideName=self.fingerDict['palmGuideSetup']['nameTempl']+self.guideSulfix

        displaySetup = self.fingerDict['palmGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        self.palmGuide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                               **displaySetup)

        displaySetup = self.fingerDict['baseGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        self.baseGuide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                               **displaySetup)

        displaySetup = self.fingerDict['tipGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        self.tipGuide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                              **displaySetup)

        pm.parent(self.tipGuide, self.baseGuide, self.palmGuide, self.guideMoveall)

        self.palmGuide.setTranslation(self.fingerGuideDict['palm'][0], space='object')
        self.palmGuide.setRotation(self.fingerGuideDict['palm'][1], space='object')

        self.baseGuide.setTranslation(self.fingerGuideDict['base'][0], space='object')
        self.baseGuide.setRotation(self.fingerGuideDict['base'][1], space='object')

        self.tipGuide.setTranslation(self.fingerGuideDict['tip'][0], space='object')
        self.tipGuide.setRotation(self.fingerGuideDict['tip'][1], space='object')

        # cria conforme o numero de dobras
        if self.folds == 2:
            displaySetup = self.fingerDict['fold1GuideSetup'].copy()
            cntrlName = displaySetup['nameTempl'] + self.guideSulfix
            self.fold1Guide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                    **displaySetup)

            displaySetup = self.fingerDict['fold2GuideSetup'].copy()
            cntrlName = displaySetup['nameTempl'] + self.guideSulfix
            self.fold2Guide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                    **displaySetup)

            fold1GuideGrp = pm.group(em=True)
            fold2GuideGrp = pm.group(em=True)

            pm.parent(self.fold1Guide, fold1GuideGrp)
            pm.parent(self.fold2Guide, fold2GuideGrp)
            pm.parent(fold1GuideGrp, fold2GuideGrp, self.guideMoveall)

            self.fold2Guide.setTranslation(self.fingerGuideDict['fold2'][0], space='object')
            self.fold2Guide.setRotation(self.fingerGuideDict['fold2'][1], space='object')

            self.fold1Guide.setTranslation(self.fingerGuideDict['fold1'][0], space='object')
            self.fold1Guide.setRotation(self.fingerGuideDict['fold1'][1], space='object')

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
            displaySetup = self.fingerDict['fold1GuideSetup'].copy()
            cntrlName = displaySetup['nameTempl'] + self.guideSulfix
            self.fold1Guide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                    **displaySetup)
            fold1GuideGrp = pm.group(em=True)

            pm.parent(self.fold1Guide, fold1GuideGrp)
            pm.parent(fold1GuideGrp, self.guideMoveall)

            self.fold1Guide.setTranslation(self.fingerGuideDict['fold1'][0], space='object')
            self.fold1Guide.setRotation(self.fingerGuideDict['fold1'][1], space='object')

            pm.aimConstraint(self.fold1Guide, self.baseGuide, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            pm.aimConstraint(self.tipGuide, fold1GuideGrp, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            pm.aimConstraint(self.fold1Guide, self.tipGuide, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            cns = pm.pointConstraint(self.baseGuide, self.tipGuide, fold1GuideGrp, mo=False)

        elif self.folds == 0:
            displaySetup = self.fingerDict['fold1GuideSetup'].copy()
            cntrlName = displaySetup['nameTempl'] + self.guideSulfix
            self.fold1Guide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                    **displaySetup)
            fold1GuideGrp = pm.group(em=True)

            pm.parent(self.fold1Guide, fold1GuideGrp)
            pm.parent(fold1GuideGrp, self.guideMoveall)

            self.fold1Guide.setTranslation(self.fingerGuideDict['fold1'][0], space='object')
            self.fold1Guide.setRotation(self.fingerGuideDict['fold1'][1], space='object')

            pm.aimConstraint(self.tipGuide, self.baseGuide, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            pm.aimConstraint(self.baseGuide, self.tipGuide, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=self.guideMoveall)
            cns = pm.pointConstraint(self.baseGuide, self.tipGuide, fold1GuideGrp, mo=False)

            self.fold1Guide.visibility.set(0)

        arrow = rigFunctions.cntrlCrv(obj=self.baseGuide, name=self.name + 'PlaneDir', icone='seta', size=.07,
                                      color=(0, 1, 1))
        arrow.getParent().setParent(self.baseGuide)
        pm.aimConstraint(self.tipGuide, arrow, weight=1, aimVector=(1, 0, 0), upVector=(0, 0, -1),
                         worldUpObject=self.fold1Guide, worldUpType='object')

        self.guideMoveall.setTranslation(self.fingerGuideDict['moveall'][0], space='object')
        self.guideMoveall.setRotation(self.fingerGuideDict['moveall'][1], space='object')

        pm.addAttr(self.guideMoveall, ln='fingerDict', dt='string')
        self.guideMoveall.fingerDict.set(json.dumps(self.fingerDict))

    def getGuideFromScene(self):
        try:
            # se existir apaga
            guideName = self.fingerDict['moveallGuideSetup']['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            guideName = self.fingerDict['palmGuideSetup']['nameTempl'] + self.guideSulfix
            self.palmGuide = pm.PyNode(guideName)

            guideName = self.fingerDict['baseGuideSetup']['nameTempl'] + self.guideSulfix
            self.baseGuide = pm.PyNode(guideName)

            guideName = self.fingerDict['tipGuideSetup']['nameTempl'] + self.guideSulfix
            self.tipGuide = pm.PyNode(guideName)

            guideName = self.fingerDict['fold1GuideSetup']['nameTempl'] + self.guideSulfix
            self.fold1Guide = pm.PyNode(guideName)

            if self.folds == 2:
                guideName = self.fingerDict['fold2GuideSetup']['nameTempl'] + self.guideSulfix
                self.fold2Guide = pm.PyNode(guideName)
        except:
            print 'algum nao funcionou'

    def getDict(self):
        try:
            # se existir apaga
            guideName = self.fingerDict['moveallGuideSetup']['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.fingerDict.get()
            dictRestored = json.loads(jsonDict)
            self.fingerDict.update(**dictRestored)

            self.fingerDict['guideDict']['moveall'] = rigFunctions.getObjTransforms (self.guideMoveall, 'object')

            guideName = self.fingerDict['palmGuideSetup']['nameTempl'] + self.guideSulfix
            self.palmGuide = pm.PyNode(guideName)
            self.fingerDict['guideDict']['palm'] = rigFunctions.getObjTransforms (self.palmGuide, 'object')


            guideName = self.fingerDict['baseGuideSetup']['nameTempl'] + self.guideSulfix
            self.baseGuide = pm.PyNode(guideName)
            self.fingerDict['guideDict']['base'] = rigFunctions.getObjTransforms(self.baseGuide, 'object')


            guideName = self.fingerDict['tipGuideSetup']['nameTempl'] + self.guideSulfix
            self.tipGuide = pm.PyNode(guideName)
            self.fingerDict['guideDict']['tip'] = rigFunctions.getObjTransforms (self.tipGuide, 'object')


            guideName = self.fingerDict['fold1GuideSetup']['nameTempl'] + self.guideSulfix
            self.fold1Guide = pm.PyNode(guideName)
            self.fingerDict['guideDict']['fold1'] = rigFunctions.getObjTransforms (self.fold1Guide, 'object')


            if self.folds == 2:
                guideName = self.fingerDict['fold2GuideSetup']['nameTempl'] + self.guideSulfix
                self.fold2Guide = pm.PyNode(guideName)
                self.fingerDict['guideDict']['fold2'] = rigFunctions.getObjTransforms (self.fold2Guide, 'object')

        except:
            print 'algum nao funcionou'

        return self.fingerDict

    def doRig(self):
        # se nao existir guide, cria um default
        if not self.guideMoveall:
            self.doGuide()

        # se existir um modulo igual, apaga
        moveallName = self.fingerDict['moveallCntrlSetup']['nameTempl']
        if pm.objExists(moveallName):
            pm.delete(moveallName)

        cntrlName = self.fingerDict['moveallCntrlSetup']['nameTempl']
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
            jntNames = [self.fingerDict['palmJntSetup']['nameTempl'], self.fingerDict['baseJntSetup']['nameTempl'],
                        self.fingerDict['fold1JntSetup']['nameTempl'], self.fingerDict['fold2JntSetup']['nameTempl'],
                        self.fingerDict['tipJntSetup']['nameTempl']]

        elif self.folds == 1:
            guide = [palm, base, fold1, tip]
            jntNames = [self.fingerDict['palmJntSetup']['nameTempl'], self.fingerDict['baseJntSetup']['nameTempl'],
                        self.fingerDict['fold1JntSetup']['nameTempl'], self.fingerDict['tipJntSetup']['nameTempl']]

        elif self.folds == 0:
            guide = [palm, base, tip]
            jntNames = [self.fingerDict['palmJntSetup']['nameTempl'], self.fingerDict['baseJntSetup']['nameTempl'],
                        self.fingerDict['tipJntSetup']['nameTempl']]

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

            m = rigFunctions.orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)
            jntName = jntNames[i] + self.jntSulfix
            j1 = pm.joint(n=jntName)
            fingerJnts.append(j1)
            self.skinJoints.append(j1)
            pm.xform(j1, m=m, ws=True)
            pm.makeIdentity(j1, apply=True, r=1, t=0, s=1, n=0, pn=0)

        jntName = self.fingerDict['tipJntSetup']['nameTempl'] + self.tipJxtSulfix
        j1 = pm.joint(n=jntName)
        fingerJnts.append(j1)
        pm.xform(j1, m=m, ws=True)
        pm.xform(j1, t=C, ws=True)
        pm.makeIdentity(j1, apply=True, r=1, t=0, s=1, n=0, pn=0)

        # cria os controles
        last = None
        displaySetup = self.fingerDict['palmCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        cntrl0 = rigFunctions.cntrlCrv(name=cntrlName, connType='parentConstraint', obj=fingerJnts[0], **displaySetup)

        displaySetup = self.fingerDict['baseCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        cntrl1 = rigFunctions.cntrlCrv(name=cntrlName, connType='parentConstraint', obj=fingerJnts[1], **displaySetup)

        pm.parent(cntrl1.getParent(), cntrl0)
        last = cntrl1

        # cria os controles conforme a o numero setado de dobras
        if self.folds > 0:
            cntrl1.addAttr('curl1', k=1, at=float, dv=0)
            displaySetup = self.fingerDict['fold1CntrlSetup'].copy()
            cntrlName = displaySetup['nameTempl']
            cntrl2 = rigFunctions.cntrlCrv(name=cntrlName, connType='parentConstraint', obj=fingerJnts[2], offsets=1,
                                           **displaySetup)
            pm.parent(cntrl2.getParent(2), cntrl1)
            cntrl1.curl1 >> cntrl2.getParent().rotateY
        if self.folds > 1:
            cntrl1.addAttr('curl2', k=1, at=float, dv=0)
            displaySetup = self.fingerDict['fold2CntrlSetup'].copy()
            cntrlName = displaySetup['nameTempl']
            cntrl3 = rigFunctions.cntrlCrv(name=cntrlName, connType='parentConstraint', obj=fingerJnts[3], offsets=1,
                                           **displaySetup)
            pm.parent(cntrl3.getParent(2), cntrl2)
            cntrl1.curl2 >> cntrl3.getParent().rotateY

        pm.parent(fingerJnts[0], cntrl0.getParent(), self.moveall)