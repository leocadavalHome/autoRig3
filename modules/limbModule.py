import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.matrixTools as matrixTools
import json
import logging

logger = logging.getLogger('autoRig')

class Limb:
    """
        Cria um Limb
        Parametros:
            name (string): nome do novo limb
            ikCntrl (string): nome
            startCntrl (string): nome
            midCntrl (string): nome
            endCntrl (string): nome
            poleCntrl (string): nome
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            lastJoint (boolean): se exite joint da mao
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone

    """

    ## IMPLEMENTAR:
    # todo  setagem de parametros e formatacao de nomes
    # todo grupos de spaceSwitch acima dos controles
    # todo self.twoJoints=False RETIREI CODIGO DE ARTICULACAO DE DOIS JOINTS. PRECISA FAZER IMPLEMENTACAO COMPLETA

    def __init__(self, name='limb', axis='X', flipAxis=False, lastJoint=True, **kwargs):
        self.name = name
        self.flipAxis = flipAxis
        self.axis = axis
        self.lastJoint = lastJoint
        self.guideMoveall = None
        self.skinJoints = []
        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'
        self.grpSulfix = '_grp'
        self.GuideColor = (1, 0, 1)

        self.toExport = {'moveallGuideSetup', 'poleVecCntrlSetup', 'name', 'axis', 'flipAxis', 'startJntSetup',
                         'endJntSetup', 'midJntSetup', 'lastJoint', 'lastJntSetup', 'guideDict', 'startGuideSetup',
                         'midGuideSetup', 'endGuideSetup', 'lastGuideSetup', 'moveAll1CntrlSetup', 'startCntrlSetup',
                         'midCntrlSetup', 'endCntrlSetup', 'ikCntrlSetup'}

        #Felipe --> add valores de escala
        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)], 'start': [(0, 0, 0), (0, 0, 0), (1, 1, 1)],
                          'mid': [(3, 0, -1), (0, 0, 0), (1, 1, 1)], 'end': [(6, 0, 0), (0, 0, 0), (1, 1, 1)],
                          'last': [(2, 0, 0), (0, 0, 0), (1, 1, 1)]}


        self.moveAll1CntrlSetup = {'nameTempl': name + 'MoveAll', 'icone': 'grp',
                                   'size': (1.8), 'color': (1, 1, 0)}

        self.ikCntrlSetup = {'nameTempl': name + 'Ik', 'icone': 'circuloX', 'size': 1,
                             'color': (1, 0, 0)}

        self.startCntrlSetup = {'nameTempl': name + 'FkStart', 'icone': 'circuloX',
                                'size': 1.5, 'color': (0, 1, 0)}

        self.midCntrlSetup = {'nameTempl': name + 'FkMid', 'icone': 'circuloX',
                              'size': 1.5, 'color': (0, 1, 0)}

        self.endCntrlSetup = {'nameTempl': name + 'FkEnd', 'icone': 'circuloX',
                              'size': 1.5, 'color': (0, 1, 0)}

        self.poleVecCntrlSetup = {'nameTempl': name + 'PoleVec', 'icone': 'bola',
                                  'size': 0.4, 'color': (1, 0, 0)}

        self.startJntSetup = {'nameTempl': name + 'Start', 'size': 1}
        self.midJntSetup = {'nameTempl': name + 'Mid', 'size': 1}
        self.endJntSetup = {'nameTempl': name + 'End', 'size': 1}
        self.lastJntSetup = {'nameTempl': name + 'Last', 'size': 1}

        self.moveallGuideSetup = {'nameTempl': name + 'MoveAll', 'icone': 'quadradoX',
                                  'size': 2.5, 'color': (1, 0, 0)}
        self.startGuideSetup = {'nameTempl': name + 'Start', 'icone': 'circuloX',
                                'size': 2, 'color': (1, 1, 0)}
        self.midGuideSetup = {'nameTempl': name + 'Mid', 'icone': 'circuloX', 'size': 2,
                              'color': (1, 1, 0)}
        self.endGuideSetup = {'nameTempl': name + 'End', 'icone': 'circuloX', 'size': 2,
                              'color': (1, 1, 0)}
        self.lastGuideSetup = {'nameTempl': name + 'Last', 'icone': 'bola', 'size': 0.5,
                               'color': (.5, 0.4, 0.35)}

    def createCntrl(self, cntrlName):
        displaySetup = self.__dict__[cntrlName+'Setup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True, **displaySetup)
        return guide

    def setCntrl (self, cntrl, posRot, space='object'):
        cntrl.setTranslation(self.guideDict[posRot][0], space=space)
        cntrl.setRotation(self.guideDict[posRot][1], space=space)
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
        self.__dict__.update(kwargs)

        displaySetup = self.moveallGuideSetup.copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.guideMoveall = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', **displaySetup)

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

        self.startGuide = self.createCntrl('startGuide')
        self.midGuide = self.createCntrl('midGuide')
        self.endGuide = self.createCntrl('endGuide')

        pm.parent(self.startGuide, self.midGuide, self.endGuide, self.guideMoveall)

        if self.lastJoint:
            self.lastGuide = self.createCntrl('lastGuide')

            pm.parent(self.lastGuide, self.endGuide)
            self.setCntrl( self.lastGuide, 'last', space='object')

        self.setCntrl(self.startGuide, 'start', space='object')
        self.setCntrl(self.midGuide, 'mid', space='object')
        self.setCntrl(self.endGuide, 'end', space='object')

        arrow = controlTools.cntrlCrv(obj=self.startGuide, name=self.name + 'PlaneDir', icone='seta', size=.35,
                                      color=(0, 1, 1))
        arrow.template.set(1)
        arrow.getParent().setParent(self.startGuide)
        pm.aimConstraint(self.endGuide, arrow, weight=1, aimVector=(1, 0, 0), upVector=(0, 0, -1),
                         worldUpObject=self.midGuide, worldUpType='object')

        self.setCntrl(self.guideMoveall, 'moveall', space='world')

        pm.addAttr(self.guideMoveall, ln='limbDict', dt='string')
        # todo implementar funcao de exportar o dict
        self.guideMoveall.limbDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.limbDict.get()
            limbDictRestored = json.loads(jsonDict)

            self.__dict__.update(**limbDictRestored)

            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            guideName = self.startGuideSetup['nameTempl'] + self.guideSulfix
            self.startGuide = pm.PyNode(guideName)
            self.guideDict['start'][0] = self.startGuide.getTranslation(space='object').get()
            self.guideDict['start'][1] = tuple(self.startGuide.getRotation(space='object'))

            guideName = self.midGuideSetup['nameTempl'] + self.guideSulfix
            self.midGuide = pm.PyNode(guideName)
            self.guideDict['mid'][0] = self.midGuide.getTranslation(space='object').get()
            self.guideDict['mid'][1] = tuple(self.midGuide.getRotation(space='object'))

            guideName = self.endGuideSetup['nameTempl'] + self.guideSulfix
            self.endGuide = pm.PyNode(guideName)
            self.guideDict['end'][0] = self.endGuide.getTranslation(space='object').get()
            self.guideDict['end'][1] = tuple(self.endGuide.getRotation(space='object'))

            if self.lastJoint:
                guideName = self.lastGuideSetup['nameTempl'] + self.guideSulfix
                self.lastGuide = pm.PyNode(guideName)
                self.guideDict['last'][0] = self.lastGuide.getTranslation(space='object').get()
                self.guideDict['last'][1] = tuple(self.lastGuide.getRotation(space='object'))

        except:
            pass

    def mirrorConnectGuide(self, limb):
        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')
            self.guideMoveall = None

        if not self.guideMoveall:
            self.doGuide()

        if not limb.guideMoveall:
            limb.doGuide()

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')

        if not pm.objExists('GUIDES'):
            pm.group(self.name + 'MirrorGuide_grp', n='GUIDES')
        else:
            pm.parent(self.name + 'MirrorGuide_grp', 'GUIDES')

        self.guideMoveall.setParent(self.mirrorGuide)

        #Felipe --> seta valores globais de escala
        scaleValue = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.scaleY.set(1)
        self.mirrorGuide.scaleZ.set(1)
        self.mirrorGuide.scale.lock()
        self.mirrorGuide.rotate.lock()
        self.mirrorGuide.translate.lock()
        self.mirrorGuide.template.set(1)

        limb.guideMoveall.translate >> self.guideMoveall.translate
        limb.guideMoveall.rotate >> self.guideMoveall.rotate
        limb.guideMoveall.scale >> self.guideMoveall.scale
        limb.startGuide.translate >> self.startGuide.translate
        limb.startGuide.rotate >> self.startGuide.rotate
        limb.startGuide.scale >> self.startGuide.scale
        limb.midGuide.translate >> self.midGuide.translate
        limb.midGuide.rotate >> self.midGuide.rotate
        limb.midGuide.scale >> self.midGuide.scale
        limb.endGuide.translate >> self.endGuide.translate
        limb.endGuide.rotate >> self.endGuide.rotate
        limb.endGuide.scale >> self.endGuide.scale

        if self.lastJoint:
            limb.lastGuide.translate >> self.lastGuide.translate
            limb.lastGuide.rotate >> self.lastGuide.rotate
            limb.lastGuide.scale >> self.lastGuide.scale

        if limb.flipAxis:
            self.flipAxis = False
        else:
            self.flipAxis = True

        self.guideMoveall.limbDict.set(json.dumps(self.exportDict()))

    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()

        # apagar todos os node ao reconstruir
        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')

        # Cria o grupo moveAll
        self.moveall = pm.group(empty=True, n=self.name + 'Moveall')

        pos = pm.xform(self.guideMoveall, q=True, ws=True, t=True)
        pm.xform(self.moveall, ws=True, t=pos)

        if not pm.objExists('MOVEALL'):
            pm.group(self.moveall, n='MOVEALL')
        else:
            pm.parent(self.moveall, 'MOVEALL')

        self.moveall.addAttr('ikfk', at='float', min=0, max=1, dv=1, k=1)

        # define pontos do guide como vetores usando api para faciitar os calculos
        p1 = pm.xform(self.startGuide, q=True, t=True, ws=True)
        p2 = pm.xform(self.midGuide, q=True, t=True, ws=True)
        p3 = pm.xform(self.endGuide, q=True, t=True, ws=True)

        A = om.MVector(p1)
        B = om.MVector(p2)
        C = om.MVector(p3)

        if self.lastJoint:
            p4 = pm.xform(self.lastGuide, q=True, t=True, ws=True)
            D = om.MVector(p4)

        # Calculando a normal do plano definido pelo guide
        # invertendo inverte a direcao do eixo ao longo do vetor
        if self.flipAxis:
            AB = A - B
            BC = B - C
            CD = C - D
        else:
            AB = B - A
            BC = C - B
            CD = D - C

        n = BC ^ AB

        self.jointLength = AB.length() + BC.length()

        m = matrixTools.orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)
        # cria joint1
        pm.select(cl=True)
        jntName = self.startJntSetup['nameTempl'] + self.jntSulfix
        self.startJnt = pm.joint(n=jntName)
        self.skinJoints.append(self.startJnt)
        pm.xform(self.startJnt, m=m, ws=True)
        pm.makeIdentity(self.startJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)

        # cria joint2
        # criando a matriz do joint conforme a orientacao setada
        m = matrixTools.orientMatrix(mvector=BC, normal=n, pos=B, axis=self.axis)
        pm.select(cl=True)
        jntName = self.midJntSetup['nameTempl'] + self.jntSulfix
        self.midJnt = pm.joint(n=jntName)
        self.skinJoints.append(self.midJnt)
        pm.xform(self.midJnt, m=m, ws=True)
        pm.makeIdentity(self.midJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)

        # cria joint3
        # aqui so translada o joint, usa a mesma orientacao
        pm.select(cl=True)
        jntName = self.endJntSetup['nameTempl'] + self.jntSulfix
        self.endJnt = pm.joint(n=jntName)
        self.skinJoints.append(self.endJnt)
        pm.xform(self.endJnt, m=m, ws=True)
        pm.xform(self.endJnt, t=C, ws=True)
        pm.makeIdentity(self.endJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)

        # hierarquia
        pm.parent(self.midJnt, self.startJnt)
        pm.parent(self.endJnt, self.midJnt)
        self.startJnt.setParent(self.moveall)

        ##joint4(hand) se estiver setado nas opcoes
        if self.lastJoint:
            # joint4
            # Faz a orientacao do ultimo bone independente da normal do braco
            # Se o cotovelo estiver para frente inverte a normal
            # limitacao: se o limb for criado no eixo Z o calculo nao eh preciso
            if self.flipAxis:
                if n.y < 0:
                    Z = om.MVector(0, 0, 1)
                else:
                    Z = om.MVector(0, 0, -1)
            else:
                if n.y > 0:
                    Z = om.MVector(0, 0, -1)
                else:
                    Z = om.MVector(0, 0, 1)
            n = CD ^ Z

            m = matrixTools.orientMatrix(mvector=CD, normal=n, pos=C, axis=self.axis)
            pm.select(cl=True)
            jntName = self.lastJntSetup['nameTempl'] + self.jntSulfix
            self.lastJnt = pm.joint(n=jntName)
            pm.xform(self.lastJnt, m=m, ws=True)
            pm.makeIdentity(self.lastJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)

            # cria joint5 e so move
            pm.select(cl=True)
            jntName = self.lastJntSetup['nameTempl'] + self.tipJxtSulfix
            self.lastTipJnt = pm.joint(n=jntName)
            pm.xform(self.lastTipJnt, m=m, ws=True)
            pm.xform(self.lastTipJnt, t=D, ws=True)
            pm.makeIdentity(self.lastTipJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)

            # hierarquia
            pm.parent(self.lastJnt, self.endJnt)
            pm.parent(self.lastTipJnt, self.lastJnt)

            ##Estrutura FK
        if self.axis == 'Y' or self.axis == 'Z' or self.axis == 'X':
            axisName = self.axis
        else:
            axisName = 'X'

        displaySetup = self.moveAll1CntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.moveAll1Cntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.startJnt, **displaySetup)

        displaySetup = self.endCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.endCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.startJnt, connType='parentConstraint',
                                              **displaySetup)
        self.endCntrl.addAttr('manualStretch', at='float', min=.1, dv=1, k=1)

        displaySetup = self.midCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.midCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.midJnt, connType='orientConstraint',
                                              **displaySetup)
        self.midCntrl.addAttr('manualStretch', at='float', min=.1, dv=1, k=1)

        pm.pointConstraint(self.midJnt, self.midCntrl.getParent(), mo=True)

        ##Estrutura IK
        ikH = pm.ikHandle(sj=self.startJnt, ee=self.endJnt, sol="ikRPsolver")

        displaySetup = self.ikCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.ikCntrl = controlTools.cntrlCrv(name=cntrlName, obj=ikH[0], **displaySetup)

        # orienta o controle ik de modo a ter aproximadamente a orientacao do eixo global
        # mas aponta o eixo X para a ponta do ultimo bone
        mat = pm.xform(self.ikCntrl.getParent(), q=True, m=True, ws=True)
        matrix = om.MMatrix(mat)
        Zcomponent = om.MVector(0, 0, -1)
        Zaxis = matrix * Zcomponent
        normal = CD ^ Zaxis

        # CD eh o vetor de direcao do ultimo joint
        ori = matrixTools.orientMatrix(CD, normal, C, self.axis)
        pm.xform(self.ikCntrl.getParent(), m=ori, ws=True)
        ikH[0].setParent(self.ikCntrl)
        ikH[0].translate.lock()
        ikH[0].rotate.lock()

        self.ikCntrl.addAttr('pin', at='float', min=0, max=1, dv=0, k=1)
        self.ikCntrl.addAttr('bias', at='float', min=-0.9, max=0.9, k=1)
        self.ikCntrl.addAttr('autoStretch', at='float', min=0, max=1, dv=1, k=1)
        self.ikCntrl.addAttr('manualStretch', at='float', dv=1, k=1)
        self.ikCntrl.addAttr('twist', at='float', dv=0, k=1)

        # pole vector
        displaySetup = self.poleVecCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.poleVec = controlTools.cntrlCrv(name=cntrlName, obj=self.midJnt, **displaySetup)

        # calcula a direcao q deve ficar o polevector
        BA = B - A
        CA = C - A
        U = BA * CA.normal()
        dist = CA.length()
        V = U / dist * dist
        T = A + V * CA.normal()
        D = B - T
        Pole = (D.normal() * 4) + B

        # test=pm.spaceLocator (p=(0,0,0)) # locator de teste de onde calculou o ponto mais proximo
        # pm.xform (test, t=T)

        pm.xform(self.poleVec.getParent(), t=Pole)
        pm.xform(self.poleVec.getParent(), ro=(0, 0, 0))
        poleCnst = pm.poleVectorConstraint(self.poleVec, ikH[0])

        pm.parent(self.midCntrl.getParent(), self.endCntrl)
        pm.parent(self.endCntrl.getParent(), self.moveAll1Cntrl)
        pm.parent(self.moveAll1Cntrl.getParent(), self.poleVec.getParent(), self.ikCntrl.getParent(), self.moveall)

        # handCntrls se houver
        if self.lastJoint:
            displaySetup = self.startCntrlSetup
            cntrlName = displaySetup['nameTempl']
            self.startCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.lastJnt, **displaySetup)
            buf = pm.group(em=True, n='startBuf')
            matrix = pm.xform(self.lastJnt, q=True, ws=True, m=True)
            pm.xform(buf, m=matrix, ws=True)
            pm.parent(buf, self.ikCntrl)
            handCnst = pm.orientConstraint(buf, self.startCntrl, self.lastJnt, mo=False)
            handCnstScale = pm.scaleConstraint(buf, self.startCntrl, self.lastJnt, mo=False)
            self.lastJnt.segmentScaleCompensate.set(False)
            pm.pointConstraint(self.endJnt, self.startCntrl.getParent(), mo=True)
            pm.parent(self.startCntrl.getParent(), self.midCntrl)

        # display
        ikH[0].visibility.set(0)

        # grupos de stretch
        startGrp = pm.group(empty=True, n='startStretch_grp')
        endGrp = pm.group(empty=True, n='endStretch_grp')
        pm.parent(endGrp, self.ikCntrl, r=True)
        pm.xform(startGrp, t=p1, ws=True)
        pm.parent(startGrp, self.endCntrl)

        ##NODE TREE#######
        # cria um blend entre uso de poleVector ou so twist
        poleBlendColor = pm.createNode('blendColors', n=self.name+'poleVecBlend')
        poleAdd = pm.createNode('addDoubleLinear', n=self.name+'PoleAdd')
        poleCond = pm.createNode('condition', n=self.name+'poleCond')
        poleCnst.constraintTranslate >> poleBlendColor.color1
        poleBlendColor.color2.set(0, 0, 0)
        # poleCnst.constraintTranslateX // ikH[0].poleVectorX
        # poleCnst.constraintTranslateY // ikH[0].poleVectorY
        # poleCnst.constraintTranslateZ // ikH[0].poleVectorZ
        poleBlendColor.outputR >> ikH[0].poleVectorX
        poleBlendColor.outputG >> ikH[0].poleVectorY
        poleBlendColor.outputB >> ikH[0].poleVectorZ
        self.moveall.addAttr('poleVec', at='float', k=1, dv=0, max=1, min=0)
        self.moveall.poleVec >> poleAdd.input1
        self.ikCntrl.pin >> poleAdd.input2
        poleAdd.output >> poleCond.firstTerm
        poleCond.secondTerm.set(0)
        poleCond.operation.set(2)
        poleCond.colorIfFalseR.set(0)
        poleCond.colorIfTrueR.set(1)
        poleCond.outColorR >> poleBlendColor.blender
        poleCond.outColorR >> self.poleVec.visibility

        # Pin
        p5 = pm.xform(self.poleVec.getParent(), q=True, t=True, ws=True)
        E = om.MVector(p5)

        AE = A - E
        CE = E - C
        distMax = AB.length() + BC.length()  # distancia somada dos bones
        pinScaleJnt1 = AE.length() / AB.length()
        pinScaleJnt2 = CE.length() / BC.length()

        pinDist1 = pm.createNode('distanceBetween', n=self.name+'pinDist1')  # distance do pole vector a ponta do joint1
        pinDist2 = pm.createNode('distanceBetween', n=self.name+'pinDist2')  # distance do pole vector a ponta do joint2
        pinNorm1 = pm.createNode('multiplyDivide', n=self.name+'pinNorm1')  # normalizador distancia1 para escala
        pinNorm2 = pm.createNode('multiplyDivide', n=self.name+'pinNorm2')  # normalizador distancia2 para escala
        pinMultiScale1 = pm.createNode('multDoubleLinear',
                                       n=self.name+'pinMultiScale1')  # multiplicador da distancia inicial pela escala Global
        pinMultiScale2 = pm.createNode('multDoubleLinear',
                                       n=self.name+'pinMultiScale2')  # multiplicador da distancia inicial pela escala Global
        pinMultiOffset1 = pm.createNode('multDoubleLinear',
                                        n=self.name+'pinMultiOffset1')  # multiplicador escala para chegar ao pole vec pela escala Global
        pinMultiOffset2 = pm.createNode('multDoubleLinear',
                                        n=self.name+'pinMultiOffset2')  # multiplicador escala para chegar ao pole vec pela escala Global
        pinMulti1 = pm.createNode('multDoubleLinear', n=self.name+'pinMulti1')  # multiplicador do normalizador
        pinMulti2 = pm.createNode('multDoubleLinear', n=self.name+'pinMulti2')  # multiplicador do normalizador

        startGrp.worldMatrix[0] >> pinDist1.inMatrix1
        endGrp.worldMatrix[0] >> pinDist2.inMatrix1

        self.poleVec.worldMatrix[0] >> pinDist1.inMatrix2
        self.poleVec.worldMatrix[0] >> pinDist2.inMatrix2

        self.moveall.scaleX >> pinMultiScale1.input1
        self.moveall.scaleX >> pinMultiScale2.input1

        pinMultiScale1.input2.set(AE.length())
        pinMultiScale2.input2.set(CE.length())

        pinMultiOffset1.input2.set(pinScaleJnt1)
        pinMultiOffset2.input2.set(pinScaleJnt2)
        pinMultiOffset1.input1.set(1)
        pinMultiOffset2.input1.set(1)

        pinDist1.distance >> pinNorm1.input1X
        pinDist2.distance >> pinNorm2.input1X
        pinMultiScale1.output >> pinNorm1.input2X
        pinMultiScale2.output >> pinNorm2.input2X
        pinNorm1.operation.set(2)
        pinNorm2.operation.set(2)

        pinNorm1.outputX >> pinMulti1.input1
        pinNorm2.outputX >> pinMulti2.input1
        pinMultiOffset1.output >> pinMulti1.input2
        pinMultiOffset2.output >> pinMulti2.input2

        ##Stretch
        stretchDist = pm.createNode('distanceBetween', n=self.name+'stretchDist')  # distance
        stretchNorm = pm.createNode('multiplyDivide', n=self.name+'stretchNorm')  # normalizador
        stretchMultiScale = pm.createNode('multDoubleLinear',
                                          n=self.name+'stretchMultiScale')  # mutiplica valor maximo pela escala do moveAll
        stretchCond = pm.createNode('condition', n=self.name+'stretchCond')  # condicao so estica se for maior q distancia maxima

        ##Manual Stretch
        stretchManualStretch1 = pm.createNode('multDoubleLinear',
                                              n=self.name+'stretchManualStretch1')  # mutiplica valor maximo pela escala do moveAll
        stretchManualStretch2 = pm.createNode('multDoubleLinear',
                                              n=self.name+'stretchManualStretch2')  # mutiplica valor maximo pela escala do moveAll
        stretchManualStretch3 = pm.createNode('multDoubleLinear',
                                              n=self.name+'stretchManualStretch3')  # mutiplica valor maximo pela escala do moveAll

        startGrp.worldMatrix[0] >> stretchDist.inMatrix1
        endGrp.worldMatrix[0] >> stretchDist.inMatrix2

        stretchDecompMatrix = pm.createNode('decomposeMatrix', n=self.name+'StretchDecompose')
        self.moveall.worldMatrix[0] >> stretchDecompMatrix.inputMatrix
        stretchDecompMatrix.outputScale.outputScaleX >> stretchMultiScale.input1

        stretchMultiScale.input2.set(distMax)
        stretchMultiScale.output >> stretchManualStretch1.input2
        stretchManualStretch1.output >> stretchNorm.input2X
        stretchNorm.operation.set(2)

        stretchDist.distance >> stretchNorm.input1X

        stretchNorm.outputX >> stretchCond.colorIfTrue.colorIfTrueR
        stretchNorm.outputX >> stretchCond.firstTerm
        stretchCond.operation.set(2)
        stretchCond.secondTerm.set(1)
        stretchCond.colorIfFalseR.set(1)

        ##AutoStretch switch
        autoStretchSwitch = pm.createNode('blendTwoAttr', n=self.name+'autoStretchSwitch')
        stretchCond.outColor.outColorR >> autoStretchSwitch.input[1]
        autoStretchSwitch.input[0].set(1)

        ##Bias
        biasAdd1 = pm.createNode('plusMinusAverage', n=self.name+'biasAdd1')
        biasAdd2 = pm.createNode('plusMinusAverage', n=self.name+'biasAdd2')
        biasMulti1 = pm.createNode('multDoubleLinear', n=self.name+'biasMult1')
        biasMulti2 = pm.createNode('multDoubleLinear', n=self.name+'biasMult2')

        biasAdd1.input1D[1].set(1)
        biasAdd1.operation.set(1)
        biasAdd1.output1D >> biasMulti1.input1
        autoStretchSwitch.output >> biasMulti1.input2
        biasMulti1.output >> stretchManualStretch2.input2
        biasAdd2.input1D[0].set(1)
        biasAdd2.operation.set(2)
        biasAdd2.output1D >> biasMulti2.input1
        autoStretchSwitch.output >> biasMulti2.input2
        biasMulti2.output >> stretchManualStretch3.input2

        ##Twist offset
        twistBlend1 = pm.createNode('blendTwoAttr', n=self.name+'twistBlend')
        twistBlend1.input[0].set(1)
        twistBlend1.output >> ikH[0].twist

        ##Blend stretch e pin
        stretchPinBlend1 = pm.createNode('blendTwoAttr', n=self.name+'stretchPinBlend1')
        stretchPinBlend2 = pm.createNode('blendTwoAttr', n=self.name+'stretchPinBlend2')
        stretchManualStretch2.output >> stretchPinBlend1.input[0]
        stretchManualStretch3.output >> stretchPinBlend2.input[0]
        pinMulti1.output >> stretchPinBlend1.input[1]
        pinMulti2.output >> stretchPinBlend2.input[1]

        ##Blend ikfk
        ikfkBlend1 = pm.createNode('blendTwoAttr', n=self.name+'ikfkBlend1')
        ikfkBlend2 = pm.createNode('blendTwoAttr', n=self.name+'ikfkBlend2')
        ikfkReverse = pm.createNode('reverse', n=self.name+'ikfkReverse')
        stretchPinBlend1.output >> ikfkBlend1.input[0]
        stretchPinBlend2.output >> ikfkBlend2.input[0]

        self.endCntrl.manualStretch >> ikfkBlend1.input[1]
        self.midCntrl.manualStretch >> ikfkBlend2.input[1]

        self.moveall.ikfk >> ikfkReverse.inputX
        ikfkReverse.outputX >> ikfkBlend1.attributesBlender
        ikfkReverse.outputX >> ikfkBlend2.attributesBlender

        cnstrConn = self.midCntrl.connections(t='orientConstraint', d=True, s=False)[
            0]  ## arriscando em pegar o primeiro...
        weightAttr = cnstrConn.target.connections(p=True,
                                                  t='orientConstraint')  ##Descobre o parametro de peso do constraint
        ikfkReverse.outputX >> weightAttr[0]

        if self.lastJoint:
            handTargetAttrs = handCnst.target.connections(p=True, t='orientConstraint')
            handTargetAttrsScale = handCnstScale.target.connections(p=True, t='scaleConstraint')
            ikfkReverse.outputX >> handTargetAttrs[1]
            self.moveall.ikfk >> handTargetAttrs[0]
            ikfkReverse.outputX >> handTargetAttrsScale[1]
            self.moveall.ikfk >> handTargetAttrsScale[0]

        self.moveall.ikfk >> ikH[0].ikBlend
        ikfkBlend1.output >> self.startJnt.attr('scale' + axisName)
        ikfkBlend2.output >> self.midJnt.attr('scale' + axisName)

        ##ikfk visibility
        ikCntrlVisCond = pm.createNode('condition', n=self.name+'ikVisCond')
        fkCntrlVisCond = pm.createNode('condition', n=self.name+'fkVisCond')
        self.moveall.ikfk >> ikCntrlVisCond.ft
        ikCntrlVisCond.secondTerm.set(0)
        ikCntrlVisCond.operation.set(1)
        ikCntrlVisCond.colorIfTrueR.set(1)
        ikCntrlVisCond.colorIfFalseR.set(0)
        self.moveall.ikfk >> fkCntrlVisCond.ft
        fkCntrlVisCond.secondTerm.set(1)
        fkCntrlVisCond.operation.set(1)
        fkCntrlVisCond.colorIfTrueR.set(1)
        fkCntrlVisCond.colorIfFalseR.set(0)

        ikCntrlVisCond.outColor.outColorR >> self.ikCntrl.getParent().visibility
        ikCntrlVisCond.outColor.outColorR >> self.poleVec.getParent().visibility
        fkCntrlVisCond.outColor.outColorR >> self.endCntrl.getParent().visibility

        ##Atributos e conexoes do controle ik
        self.ikCntrl.bias >> biasAdd2.input1D[1]
        self.ikCntrl.bias >> biasAdd1.input1D[0]
        self.ikCntrl.pin >> stretchPinBlend1.attributesBlender
        self.ikCntrl.pin >> stretchPinBlend2.attributesBlender
        self.ikCntrl.manualStretch >> stretchManualStretch1.input1
        self.ikCntrl.manualStretch >> stretchManualStretch2.input1
        self.ikCntrl.manualStretch >> stretchManualStretch3.input1
        self.ikCntrl.autoStretch >> autoStretchSwitch.attributesBlender
        self.ikCntrl.pin >> twistBlend1.attributesBlender
        self.ikCntrl.twist >> twistBlend1.input[0]

        # IMPLEMENTAR atualizar guideDict com valores atuais
