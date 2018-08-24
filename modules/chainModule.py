import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.rigFunctions as rigFunctions
import json

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

        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'
        self.zeroJxtSulfix = 'Zero_jxt'
        grpSulfix = '_grp'

        self.chainGuideDict = {'moveall': [(0, 0, 0), (0, 0, 0)]}
        for i in range(self.divNum):
            self.chainGuideDict['guide' + str(i + 1)] = [(0 + i, 0, 0), (0, 0, 0)]

        # parametros de aparencia dos controles
        self.chainDict = {'name': name, 'axis': axis, 'flipAxis': flipAxis}
        self.chainDict['moveallGuideSetup'] = {'nameTempl': self.name + 'Moveall', 'icone': 'quadradoX', 'size': 2.5,
                                               'color': (1, 0, 0)}
        self.chainDict['moveallCntrlSetup'] = {'nameTempl': self.name + 'MoveAll', 'icone': 'circuloX', 'size': 1.8,
                                               'color': (1, 1, 0)}
        self.chainDict['fkCntrlSetup'] = {'nameTempl': self.name + 'ChainFk', 'icone': 'cubo', 'size': .8,
                                          'color': (0, 1, 0)}
        self.chainDict['guideSetup'] = {'nameTempl': self.name + 'Chain', 'icone': 'circuloX', 'size': 1.7,
                                        'color': (0, 1, 0)}
        self.chainDict['jntSetup'] = {'nameTempl': self.name + 'Chain', 'icone': 'Bone', 'size': .8}

        self.chainDict['guideDict'] = {}
        self.chainDict.update(kwargs)
        self.chainGuideDict.update(self.chainDict['guideDict'])
        self.chainDict['guideDict'] = self.chainGuideDict.copy()

    def createCntrl(self, cntrlName):
        displaySetup = self.chainDict[cntrlName+'Setup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        if pm.objExists(cntrlName):
            pm.delete(cntrlName)
        guide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True, **displaySetup)
        return guide

    def setCntrl (self, cntrl, posRot, space='object'):
        cntrl.setTranslation(self.chainDict['guideDict'][posRot][0], space=space)
        cntrl.setRotation(self.chainDict['guideDict'][posRot][1], space=space)

    def doGuide(self, **kwargs):
        self.chainDict.update(kwargs)

        # apaga se existir
        self.guideMoveall  = self.createCntrl('moveallGuide')

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

        self.setCntrl(self.guideMoveall, 'moveall', space='world')

        self.guideList = []

        for i in range(len(self.chainDict['guideDict'].keys()) - 1):
            displaySetup = self.chainDict['guideSetup'].copy()
            cntrlName = displaySetup['nameTempl'] + str(i + 1) + self.guideSulfix
            guide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                          **displaySetup)
            self.guideList.append(guide)

            guidePos = self.chainDict['guideDict']['guide' + str(i + 1)][0]
            guideRot = self.chainDict['guideDict']['guide' + str(i + 1)][1]

            pm.parent(guide, self.guideMoveall)
            pm.xform(guide, t=guidePos, ro=guideRot, os=True)

        pm.addAttr(self.guideMoveall, ln='chainDict', dt='string')
        self.guideMoveall.chainDict.set(json.dumps(self.chainDict))

    def getGuideFromScene(self):
        try:
            cntrlName = self.chainDict['moveallGuideSetup']['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(cntrlName)

            self.guideList = []
            for i in range(len(self.chainGuideDict.keys()) - 1):
                guideName = self.chainDict['guideSetup']['nameTempl'] + str(i + 1) + self.guideSulfix
                guide = pm.PyNode(guideName)
                self.guideList.append(guide)
        except:
            print 'algum nao funcionou'

    def getDict(self):
        try:
            cntrlName = self.chainDict['moveallGuideSetup']['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(cntrlName)

            jsonDict = self.guideMoveall.chainDict.get()
            dictRestored = json.loads(jsonDict)
            self.chainDict.update(**dictRestored)

            self.chainDict['guideDict']['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.chainDict['guideDict']['moveall'][1] = tuple(self.guideMoveall.getRotation(space='world'))

            for i in range(len(self.chainGuideDict.keys()) - 1):
                guideName = self.chainDict['guideSetup']['nameTempl'] + str(i+1) + self.guideSulfix
                print guideName
                guide = pm.PyNode(guideName)
                print self.chainDict['guideSetup']['nameTempl'] + str(i + 1)
                print self.chainDict['guideDict']
                self.chainDict['guideDict']['guide' + str(i + 1)][0] = guide.getTranslation(space='object').get()
                self.chainDict['guideDict']['guide' + str(i + 1)][1] = tuple(guide.getRotation(space='object'))
        except:
            print 'algum nao funcionou'

        return self.chainDict

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

    def doRig(self):
        # se nao tiver guide faz um padrao
        if not self.guideMoveall:
            self.doGuide()

        # apagar se ja houver um grupo moveall
        cntrlName = self.chainDict['moveallCntrlSetup']['nameTempl']
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
            m = rigFunctions.orientMatrix(AB[i], normal, A[i], self.axis)
            pm.select(cl=True)
            jntName = self.chainDict['jntSetup']['nameTempl'] + str(i) + self.jntSulfix
            jnt = pm.joint(n=jntName)
            self.skinJoints.append(jnt)
            self.jntList.append(jnt)
            pm.xform(jnt, m=m, ws=True)
            pm.makeIdentity(jnt, apply=True, r=1, t=0, s=1, n=0, pn=0)
            if last:
                pm.parent(jnt, last)
            last = jnt

        # desenha o ultimo joint (ou o unico)
        pm.select(cl=True)
        if self.divNum == 1:
            jntName = self.chainDict['jntSetup']['nameTempl'] + self.jntSulfix
            jnt = pm.joint(n=jntName)
            self.skinJoints.append(jnt)
            self.jntList.append(jnt)
        else:
            jntName = self.chainDict['jntSetup']['nameTempl'] + self.tipJxtSulfix
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
            displaySetup = self.chainDict['fkCntrlSetup'].copy()
            cntrlName = self.chainDict['fkCntrlSetup']['nameTempl']
            cntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=jnt, connType='parentConstraint', **displaySetup)
            self.cntrlList.append(cntrl)
            if last:
                pm.parent(cntrl.getParent(), last)
            last = cntrl

        pm.parent(self.cntrlList[0].getParent(), self.moveall)

        return self.skinJoints