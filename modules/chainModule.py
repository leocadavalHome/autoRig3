import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.matrixTools as matrixTools
import autoRig3.tools.jointTools as jointTools
import json
import logging

logger = logging.getLogger('autoRig')


## versao 2.0 16/01/2019: LEO -  eliminando o dicionario e transferindo para variaveis do objeto

class Chain:
    """
        Cria uma cadeia de joints com controles fk
        Parametros:
            name (string): nome do novo limb
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone
            divNum (int): numero de joints da cadeia

    """

    ## IMPLEMENTAR:
    #  nomes dos joints
    #  talvez conexoes diretas dos controles?
    #  algum tipo de controle ik para a cadeia

    def __init__(self, name='chain', flipAxis=False, divNum=2, axis='X', **kwargs):
        self.axis = axis
        self.flipAxis = flipAxis
        self.name = name
        self.divNum = divNum
        self.skinJoints = []
        self.guideList = []
        self.guideMoveall = None

        self.toExport = {'name', 'axis', 'flipAxis', 'guideDict', 'moveallGuideSetup', 'moveallCntrlSetup',
                         'fkCntrlSetup', 'guideSetup', 'jntSetup', 'divNum'}

        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'
        self.zeroJxtSulfix = 'Zero_jxt'
        self.grpSulfix = '_grp'

        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)]}
        for i in range(self.divNum):
            self.guideDict['guide' + str(i + 1)] = [(0 + i, 0, 0), (0, 0, 0), (1, 1, 1)]

        # parametros de aparencia dos controles

        self.moveallGuideSetup = {'nameTempl': self.name + 'Moveall', 'icone': 'quadradoX', 'size': 2.5,
                                               'color': (1, 0, 0)}
        self.moveallCntrlSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'circuloX', 'size': 1.8,
                                               'color': (1, 1, 0)}
        self.fkCntrlSetup = {'nameTempl': self.name + 'ChainFk', 'icone': 'cubo', 'size': .8,
                                          'color': (0, 1, 1)}
        self.guideSetup = {'nameTempl': self.name + 'Chain', 'icone': 'circuloX', 'size': 1.7,
                                        'color': (0, 1, 0)}
        self.jntSetup = {'nameTempl': self.name + 'Chain', 'icone': 'Bone', 'size': .8}

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
        self.__dict__.update(kwargs)

        # apaga se existir
        self.guideMoveall = self.createCntrl('moveallGuide')

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

        self.setCntrl(self.guideMoveall, 'moveall', space='world')

        self.guideList = []

        for i in range(len(self.guideDict.keys()) - 1):
            displaySetup = self.guideSetup.copy()
            cntrlName = displaySetup['nameTempl'] + str(i + 1) + self.guideSulfix
            guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                          **displaySetup)
            self.guideList.append(guide)
            pm.parent(guide, self.guideMoveall)

            if i == 0:
                self.setCntrl(guide, 'guide' + str(i + 1), space='object')
            else:
                self.setCntrl(guide, 'guide' + str(i + 1), space='object')


        pm.addAttr(self.guideMoveall, ln='chainDict', dt='string')
        # todo implantar funcao pra exportar dict
        self.guideMoveall.chainDict.set(json.dumps(self.exportDict()))

    def getGuideFromScene(self):
        try:
            cntrlName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(cntrlName)

            self.guideList = []
            for i in range(len(self.guideDict.keys()) - 1):
                guideName = self.guideSetup['nameTempl'] + str(i + 1) + self.guideSulfix
                guide = pm.PyNode(guideName)
                self.guideList.append(guide)
        except:
            logger.debug('GetDict nao funcionou')

    def getDict(self):
        try:
            cntrlName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(cntrlName)

            jsonDict = self.guideMoveall.chainDict.get()
            dictRestored = json.loads(jsonDict)
            self.__dict__.update(**dictRestored)
            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            tempGuideList = []
            for i in range(len(self.guideDict.keys()) - 1):
                guideName = self.guideSetup['nameTempl'] + str(i+1) + self.guideSulfix
                guide = pm.PyNode(guideName)
                self.guideDict['guide' + str(i + 1)][0] = guide.getTranslation(space='object').get()
                self.guideDict['guide' + str(i + 1)][1] = tuple(guide.getRotation(space='object'))
                try:
                    self.guideDict['guide' + str(i + 1)][2] = tuple(pm.xform(guide, q=True, s=True, r=True, os=True))
                except:
                    pass
                tempGuideList.append(guide)
            self.guideList = tempGuideList
        except:
            pass


    def mirrorConnectGuide(self, chain):
        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')
            self.guideMoveall = None

        if not self.guideMoveall:
            self.doGuide()
        if not chain.guideMoveall:
            chain.doGuide()

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

        chain.guideMoveall.translate >> self.guideMoveall.translate
        chain.guideMoveall.rotate >> self.guideMoveall.rotate
        chain.guideMoveall.scale >> self.guideMoveall.scale

        for origin, mirror in zip(chain.guideList, self.guideList):
            origin.translate >> mirror.translate
            origin.rotate >> mirror.rotate
            origin.scale >> mirror.scale

        if chain.flipAxis:
            self.flipAxis = False
        else:
            self.flipAxis = True

        self.guideMoveall.chainDict.set(json.dumps(self.exportDict()))

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

        A = []
        AB = []
        last = None
        for obj in self.guideList:
            p = pm.xform(obj, q=True, t=True, ws=True)
            P = om.MVector(p)
            # guarda na lista A as posicoes dos guides como MVector
            A.append(P)
            # calcula vetores de direcao entre os guides
            # guarda na lista AB
            if last:
                if self.flipAxis:
                    V = last - P
                else:
                    V = P - last
                AB.append(V)
            last = P

        if self.flipAxis:
            Z = om.MVector(0, 0, 1)
            X = om.MVector(-1, 0, 0)
        else:
            Z = om.MVector(0, 0, -1)
            X = om.MVector(1, 0, 0)

        m = [1, 0, 0, 0,
             0, 1, 0, 0,
             0, 0, 1, 0,
             0, 0, 0, 1]

        last = None
        self.jntList = []

        for i in range(len(AB)):
            # se a o vetor do bone coincidir com o eixo Z usa o eixo X de secundario
            dot = AB[i].normal() * Z
            if abs(dot) < 0.95:
                normal = AB[i] ^ Z
            else:
                normal = AB[i] ^ X
            # descobre a matriz de transformacao orientada e desenha os joints
            m = matrixTools.orientMatrix(AB[i], normal, A[i], self.axis)

            jntName = self.jntSetup['nameTempl'] + str(i) + self.jntSulfix
            jnt = jointTools.makeJoint(name=jntName, matrix=m)
            self.skinJoints.append(jnt)
            self.jntList.append(jnt)

            if last:
                pm.parent(jnt, last)
            last = jnt

        # desenha o ultimo joint (ou o unico)
        pm.select(cl=True)
        if self.divNum == 1:
            jntName = self.jntSetup['nameTempl'] + self.jntSulfix
            jnt = pm.joint(n=jntName)
            self.skinJoints.append(jnt)
            self.jntList.append(jnt)
        else:
            jntName = self.jntSetup['nameTempl'] + self.tipJxtSulfix
            jnt = pm.joint(n=jntName)
            self.jntList.append(jnt)

        pm.xform(jnt, m=m, ws=True)
        pm.xform(jnt, t=A[-1], ws=True)
        pm.makeIdentity(jnt, apply=True, r=1, t=0, s=1, n=0, pn=0)
        pm.parent(jnt, last)

        pm.parent(self.jntList[0], self.moveall)

        # faz controles para os joints exceto o da ponta

        cntrlTodo = []

        if len(self.jntList) > 1:
            cntrlToDo = self.jntList[:-1]
        else:
            cntrlToDo = self.jntList[0]

        self.cntrlList = []

        last = None

        for jnt in cntrlToDo:
            displaySetup = self.fkCntrlSetup.copy()
            cntrlName = self.fkCntrlSetup['nameTempl']
            cntrl = controlTools.cntrlCrv(name=cntrlName, obj=jnt, connType='parentConstraint', **displaySetup)
            self.cntrlList.append(cntrl)
            if last:
                pm.parent(cntrl.getParent(), last)
            last = cntrl

        pm.parent(self.cntrlList[0].getParent(), self.moveall)
        return self.skinJoints