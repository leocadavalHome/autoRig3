import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.controlTools as controlTools
import json
import logging

logger = logging.getLogger('autoRig')

class MasterChain:
    """
        Cria uma cadeia de joints:
        Parametros:
            name (string):            Nome do sistema
            num (int):                Quantos jnts tem a cadeia (incluindo o 'end')

            guidePosDict (dict):      Coordenadas de posicao do guide
            guideOrientDict (dict):   Coordenadas de orient do guide

            ik (boolean):             True se tiver uma cadeia IK
            fk (boolean):             True se tiver uma cadeia FK
            dyn (boolean):            True se tiver uma cadeia Dinamica

            fkInterval (int):         Quantos jnts sao controlados por cada controle FK

            flipAxis (boolean):       Se a cadeia eh flipada
            axis ('X', 'Y' ou 'Z'):   Eixo ao longo do jnt

            chainParent ('string'):   Se houver objeto selecionado na hora da criacao do guide, sera o pai da cadeia

            moveallGuideSetup (dict): Informacoes de cores, shapes e tamanhos dos guides (Moveall)
            fkGuideSetup (dict):      Informacoes de cores, shapes e tamanhos dos guides (FK)
            fkTwkGuideSetup (dict):   Informacoes de cores, shapes e tamanhos dos guides (FK - Twks)
            ikGuideSetup (dict):      Informacoes de cores, shapes e tamanhos dos guides (IK)
            dynGuideSetup (dict):     Informacoes de cores, shapes e tamanhos dos guides (Dyn)

            skinJoints (list):        Lista de jnts skinaveis

    """

    def __init__(self, name='chain', num=7, fkInterval=2, axis='X', flipAxis=False, chainParent=None, **kwargs):
        self.name = name
        self.num = num
        self.flInterval = fkInterval
        self.axis = axis
        self.flipAxis = flipAxis
        self.chainParent = chainParent

        self.guideDict = None

        self.ik = False
        self.fk = True
        self.dyn = False

        self.moveallGuideSetup = {'nameTempl': self.name + '_moveall', 'icone': ('circulo' + axis), 'size': 3,
                                  'color': (1, 0, 0), 'spaceSet': [(0, 0, 0), (0, 0, 0), (1, 1, 1)],
                                  'hasZeroGrp': False, 'cntrlSulfix': '', 'hasHandle': True}
        self.chainGuideSetup = {'nameTempl': self.name, 'icone': ('hexagono' + axis), 'size': 1, 'color': (1, 1, 0)}

        self.moveallSetup = {'nameTempl': self.name + '_moveall', 'icone': ('circulo' + axis), 'size': 3,
                             'color': (1, 0, 0), 'spaceSet': [(0, 0, 0), (0, 0, 0), (1, 1, 1)]}
        self.fkSetup = {}
        self.fkTwkSetup = {}
        self.ikSetup = {}
        self.dynSetup = {}

        self.skinJoints = []

        self.guideMoveall = None
        self.guideSys = []

        self.toExport = {'name', 'num', 'fkInterval', 'axis', 'flipAxis', 'chainParent',
                         'guidePosDict', 'guideOrientDict', 'ik', 'fk', 'dyn', 'moveallGuideSetup', 'fkGuideSetup',
                         'fkTwkGuideSetup', 'ikGuideSetup', 'dynGuideSetup'}

        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'
        self.grpSulfix = '_grp'

        # posicao default do guide:
        if not self.guideDict:
            value = 0

            self.guideDict = {}
            for i in range(num):
                self.guideDict.update({i: [(0, 0, value), (0, 0, 0), (1, 1, 1)]})

                value += 2

    def setCntrl(self, cntrl, dict, posRotEsc, space='object'):
        cntrl.setTranslation(dict[posRotEsc][0], space=space)
        cntrl.setRotation(dict[posRotEsc][1], space=space)
        cntrl.setScale(dict[posRotEsc][2], space=space)

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
            expDict[key] = self.__dict__[key]
        return expDict

    def doGuide(self, **kwargs):

        self.__dict__.update(kwargs)

        displaySetup = self.moveallGuideSetup.copy()

        def createEachCtrlGuide(ctrlName, guideRunning, setUp):
            if pm.objExists(ctrlName):
                pm.delete(ctrlName)

            guideRunning = controlTools.cntrlCrv(name=ctrlName, **setUp)
            self.setCntrl(pm.PyNode(ctrlName), displaySetup, 'spaceSet', 'world')

        ctrlName = displaySetup['nameTempl'] + self.guideSulfix

        createEachCtrlGuide(ctrlName, self.guideMoveall, self.moveallGuideSetup)

        '''


        self.guideMoveall = rigFunctions.cntrlCrv( name = ctrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True, **self.moveallGuideSetup)
        self.setCntrl(pm.PyNode(ctrlName), displaySetup, 'spaceSet', 'world')
        '''
        for guide in range(self.num):

            displaySetup = self.chainGuideSetup.copy()
            guideName = displaySetup['nameTempl'] + str(guide) + self.guideSulfix
            guideIcon = displaySetup['icone']

            if pm.objExists(guideName):
                pm.delete(guideName)

            runningGuide = controlTools.cntrlCrv(name=guideName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                 **self.chainGuideSetup)

            self.setCntrl(pm.PyNode(guideName), self.guideDict, guide, 'world')

            self.guideSys.append(runningGuide)

        print (self.guideSys)  # lista de todos os controles de guide a serem construidos

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

    def getDict(self):
        pass

    def mirrorConnectGuide(self, limb):
        pass

    def doRig(self):
        pass

'''
t = MasterChain().doGuide()
a = MasterChain().moveallGuideSetup
d = MasterChain().guideDict
'''

