import pymel.core as pm
import maya.api.OpenMaya as om
import math
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(10)

import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.groupTools as groupTools
import autoRig3.tools.vertexWalkTools as vtxWalk
import autoRig3.tools.jointTools as jointTools

class MasterChain:
    """
        Cria uma cadeia de joints:
        Parametros:
            name (string):                                    Nome do sistema
            num (int):                                        Quantos jnts tem a cadeia (incluindo o 'end')

            #guideDict (dict):                                Coordenadas do guide onde o index 0 se refere ao moveall e seguintes aos demais guides
                                                              guideDict= {0: ((5, 5, 5), (45,45,45), (1,1,1)), 1: ((6,6,6),0), ...}
                                                              Somente o moveall leva orientacao geral e escala, os demais levam um tuple de translacao e o valor do attr orient

            ik (boolean):                                     True se tiver uma cadeia IK
            fk (boolean):                                     True se tiver uma cadeia FK
            dyn (boolean):                                    True se tiver uma cadeia Dinamica

            fkInterval (int):                                 Quantos jnts sao controlados por cada controle FK

            flipAxis (boolean):                               Se a cadeia eh flipada
            axis ('X', 'Y' ou 'Z'):                           Eixo ao longo do jnt

            chainParent ('string'):                           Se houver objeto selecionado na hora da criacao do guide, sera o pai da cadeia

            moveallGuideSetup (dict):                         Informacoes de cores, shapes e tamanhos dos guides (Moveall)
            fkGuideSetup (dict):                              Informacoes de cores, shapes e tamanhos dos guides (FK)
            fkTwkGuideSetup (dict):                           Informacoes de cores, shapes e tamanhos dos guides (FK - Twks)
            ikGuideSetup (dict):                              Informacoes de cores, shapes e tamanhos dos guides (IK)
            dynGuideSetup (dict):                             Informacoes de cores, shapes e tamanhos dos guides (Dyn)

            selection (list):                                 O guide usa selecao, se houver, para se posicionar. Se a classe nao receber esse input atualiza verificando se ha objetos selecionados na cena.
            selToGuide ('singleGuide' ou 'multipleGuides'):   Se houver selecao, no modo single cada jnt da chain eh criado em cima de uma selecao, no modo multiple cada selecao gera um novo guide.

            skinJoints (list):                                Lista de jnts skinaveis
            chainDict (dict):                                 Conteudo do atributo do moveall que carrega as infos de contrucao em json

            toExport (dict):                                  keys de conteudo para exportacao via json

    """

    def __init__(self, name='chain', fkInterval=1, axis='Y', flipAxis=False, chainParent=None, guideDict=None,
                 num=None, jntSuffix='jnt', **kwargs):

        logger.debug('__init__')

        globalParent = kwargs.pop('globalParent', None)
        if not globalParent:
            self.globalParent = {'GUIDES' : 'GUIDES',
                                 'DATA' : 'DATA',
                                 'globalMoveall' : 'characterMoveall_ctrl'}
        else:
            self.globalParent = globalParent


        self.name = name
        self.nameFill = name
        self.num = None
        self.inputNum = num
        if num:
            self.inputNum = num+1
        self.fkInterval = fkInterval
        self.axis = axis
        self.flipAxis = flipAxis
        self.chainParent = chainParent
        self.guideDict = guideDict
        self.guideBase = {}

        self.ik = kwargs.pop('ik', False)
        self.fk = kwargs.pop('fk', True)
        self.dyn = kwargs.pop('dyn', False)

        self.fkTwkGuideSetup = {}
        self.fkGuideSetup = {}
        self.ikGuideSetup = {}
        self.dynGuideSetup = {}

        self.guideObj = None
        self.guideSys = []
        self.guideOrientSys = []

        self.toExport = {'name', 'num', 'fkInterval', 'flipAxis', 'axis', 'chainParent', 'guideSys', 'guideOrientSys',
                         'ik', 'fk', 'dyn', 'moveallGuideSetup', 'fkGuideSetup', 'fkTwkGuideSetup', 'ikGuideSetup',
                         'dynGuideSetup', 'guideDict', 'driverMap', 'jntSuffix', 'preferredOrient'}

        self.selection = []
        self.selToGuide = kwargs.pop('selToGuide', 'singleGuide')

        self.guideSuffix = '_guide'
        self.jntSuffix = jntSuffix
        self.jxtSuffix = '_jxt'
        self.tipJxtSuffix = 'Tip_jxt'
        self.grpSuffix = '_grp'

        self.guideMoveall = None

        self.currentGuide = ''

        self.guideAxisAttr = 'orient'
        self.guideIsDriver = 'driver'

        self.moveallSetup = {'nameTempl': self.name + '_moveall', 'icone': ('circulo' + axis),
                             'color': (1, 0, 0), 'spaceSet': (0, 0, 0), 'hasZeroGrp': False}

        self.moveallGuideSetup = {'nameTempl': self.name + '_moveall', 'icone': ('circuloX'), 'size': 3,
                                  'color': (1, 0, 0), 'hasZeroGrp': False, 'cntrlSulfix': '', 'hasHandle': True}

        self.chainGuideSetup = {'nameTempl': self.name, 'icone': 'bola', 'size': 1, 'color': (.1, .8, .8),
                                'hasZeroGrp': False, 'cntrlSulfix': '', 'hasHandle': True,
                                'lockChannels': ['rx', 'ry', 'rz', 'v']}

        self.locGuideSetup = {'nameTempl': self.name + '_loc', 'icone': 'null', 'hasZeroGrp': False, 'localAxis': True,
                              'cntrlSulfix': '', 'size': 1,
                              'lockChannels': ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'],
                              'hideShape': True}

        # para construcao do rig:

        self.dummyMoveall = None
        self.moveall = None

        self.toParentName = self.name + 'MoveAll'
        self.ctrlGrp = None
        self.toParentDrv = None
        self.inputDiverMap = kwargs.pop('driverMap', {})
        self.driverMap = self.inputDiverMap
        self.chainMap = []

        self.skinJoints = []

        self.sysSize = 10 # usado como ref de tamanho para os ctrls na construcao do rig

        self.ctrlFkSetup = {'nameTempl': self.name + '_ctrl', 'icone': 'circulo' + axis, 'hasZeroGrp': False,
                            'localAxis': False, 'cntrlSulfix': '', 'lockChannels': ['v'],
                            'hideShape': False, 'color': (1, 1, 0)}

        self.locFkSetup = {'nameTempl': self.name + '_loc', 'icone': 'null', 'hasZeroGrp': False, 'localAxis': False,
                              'cntrlSulfix': '', 'size': 2, 'hideShape': False}

        self.ctrlFkTwkSetup = {'nameTempl': self.name + '_ctrl', 'icone': 'hexagono' + axis, 'hasZeroGrp': False,
                               'localAxis': False, 'cntrlSulfix': '', 'lockChannels': ['v'],
                               'hideShape': False, 'color': (0, 1, 0)}

        self.ctrlIkSetup = {'nameTempl': self.name + '_ctrl', 'icone': 'cubo', 'hasZeroGrp': True,
                            'localAxis': False, 'lockChannels': ['v'],
                            'hideShape': False, 'color': (1, 1, 0)}


        fkCtrlSysGrp = None
        self.ikCtrlGrp = None
        self.sysCtrlGrp = None

        self.preferredOrient = -90
        self.preferredValues = ()
        self.ikPreferredSuffix = '_ik_preferredAngle'
        self.ctrlDynSetup = {}
        logger.debug('# MasterChain instanciado.')



    ## ==================================================================================================

    def setCntrl(self, obj, objGrp, dict, posRotEsc, orientAttr = None, space='object', setType='guide'):

        logger.debug('setCntrl: Setando transforms')
        '''
        caso setType = guide: seta uma posicao para o objGrp                    formato de entrada: (x, y, z)
        caso setType = doRig: seta uma posicao, rotacao e escala para o objGrp  formato de entrada: [(x, y, z), (x, y, z), (x, y, z)]
        '''
        connect = ''

        if setType == 'guide':
            # print dict, posRotEsc

            if posRotEsc == 0:  # eh moveall
                connect = 'TransRotEsc'

            else:
                connect = 'Trans'

        elif setType == 'doRig':
            connect = 'TransRotEsc'

        if objGrp:
            pyObjGrp = pm.PyNode(objGrp)
        pyObj = pm.PyNode(obj)

        if connect == 'TransRotEsc':

            if objGrp:
                pyObjGrp.setTranslation(self.guideBase[posRotEsc][0], space=space)
                pyObjGrp.setRotation(self.guideBase[posRotEsc][1], space=space)
                pyObjGrp.setScale(self.guideBase[posRotEsc][2], space=space)

            pyObj.setTranslation(dict[posRotEsc][0], space=space)
            pyObj.setRotation(dict[posRotEsc][1], space=space)
            pyObj.setScale(dict[posRotEsc][2], space=space)

        elif connect == 'Trans':

            if objGrp:
                pyObjGrp.setTranslation(self.guideBase[posRotEsc][0], space=space)

            pyObj.setTranslation(dict[posRotEsc][0], space=space)

            if orientAttr:
                pm.setAttr(obj + '.' + orientAttr, self.guideDict[posRotEsc][1])

        logger.debug('# Fim do setCntrl')

    ## ==================================================================================================

    def getSelectionToGuide(self, selection, allMoveall=False):
        logger.debug('getSelectionToGuide: Listando transforms a partir da selecao')

        coords = {}
        select = selection
        tempList = []

        for e, i in enumerate(select):
            refCoord = i
            try:
                if pm.nodeType(i) != 'transform' and pm.nodeType(i) != 'joint':
                    tempClus = pm.cluster(i, n='tempClus')[1]
                    refCoord = tempClus
                    tempList.append(refCoord)

                coord = pm.xform(refCoord, rp=1, q=1, ws=1)
                if e == 0 or allMoveall == True:  # se for moveall
                    coords.update({e: (tuple(coord), (0, 0, 0), (1, 1, 1))})
                else:
                    coords.update({e: tuple(coord)})

            except:
                logger.error('nao foi possivel listar informacoes do transform')
                pm.warning('Os objetos selecionados nao foram reconhecidos')

        pm.delete(tempList)

        logger.debug('# Fim do getSelectionToGuide')
        return coords

    ## ==================================================================================================

    def createZeroGrp(self, obj=None, objGrpName=None, zeroWorldPos=False, parentGrp=None, parentGrpOnZero=False):

        logger.debug('createZeroGrp: Criando grupo zero para o ' + obj)
        '''
        cria um grupo acima do obj
        zeroWorldPos: True caso o grupo deva permanecer no zero do world space
        parentGrpOnZero: Quando True, o zero grp criado ao ser parenteado ao parentGrp tambem eh zerado
        '''

        if not objGrpName:
            objGrpName = obj + '_grp'

        grp = pm.group(n=objGrpName, em=1)

        if not zeroWorldPos:
            objMatrix = pm.xform(obj, q=1, m=1, ws=1)
            pm.xform(grp, m=objMatrix, ws=1)

        pm.parent(obj, grp)

        if parentGrp:
            pm.parent(grp, parentGrp)
            if parentGrpOnZero:
                try:
                    pm.xform(grp, t=(0, 0, 0), ro=(0, 0, 0), s=(1, 1, 1))
                except:
                    logger.debug ('nao foi possivel parentear '+parentGrp+' em '+parentGrpOnZero)

        logger.debug('# Fim do createZeroGrp')
        return (obj, grp)

    ## ==================================================================================================

    def createEachCtrlGuide(self, ctrlName, guideRunning, dictCoords, spaceSetKey, setUp, createZero=True,
                            moveall=False):
        logger.debug('createEachCtrlGuide: Criando ctrl guide')

        '''
        cria um ctrl de guide com setup predefinido, com ou sem grupo acima, na coordenada inputada
        '''

        if pm.objExists(ctrlName):
            pm.delete(ctrlName)

        guideRunning = controlTools.cntrlCrv(name=ctrlName, **setUp)

        if createZero:
            guideObjs = self.createZeroGrp(obj=guideRunning)
            parentObj = guideObjs[1]
        else:
            guideObjs = [guideRunning, None]
            parentObj = guideObjs[0]

        guideRunning = guideRunning.name()
        parentObj = parentObj.name()

        logger.debug('# Fim do createEachCtrlGuide')
        return guideRunning, parentObj

    ## ==================================================================================================

    def aimGuide(self, source, target, axis, flipAxis=False, worldUpObject=None, worldUpType='object',
                 upVector=(0, 1, 0), aim=(1, 0, 0), deleteConstraint=False):
        logger.debug('aimGuide: Criando aim do ' + source + ' para o ' + target)
        '''
        orienta o source atraves de um aim para o target
        '''

        if axis == 'X':
            upVector = (0, 1, 0)

            if flipAxis:
                aim = (-1, 0, 0)
            else:
                aim = (1, 0, 0)

        elif axis == 'Y':
            upVector = (1, 0, 0)

            if flipAxis:
                aim = (0, -1, 0)
            else:
                aim = (0, 1, 0)
        elif axis == 'Z':
            upVector = (0, 1, 0)

            if flipAxis:
                aim = (0, 0, -1)
            else:
                aim = (0, 0, 1)
        else:
            logger.warn('aimGuide(): Unrecognized axis')

        if worldUpObject:
            constraint = pm.aimConstraint(source, target, aim=aim, wut='objectrotation', wuo=worldUpObject,
                                          u=upVector, mo=0)
        else:
            constraint = pm.aimConstraint(source, target, aim=aim)

        if deleteConstraint == True:
            pm.delete(constraint)

        logger.debug('# Fim do aimGuide')
        return constraint

    ## ==================================================================================================

    def createAimLoc(self, objTarget, objSource, parentCtrl, setUp, axis, upObj, flipAxis=False):
        logger.debug('createAimLoc: Criando AimLoc do guide')

        '''
        cria o locator que fica dentro de cada ctrl de guide apontando para o proximo. 
        Esses locators indicarao a orientacao guide para cada jnt
        '''

        if objSource:  # caso exista um objAim (A ponta nao tem)
            # trazer setup do self, trazer nome com sufix
            aimLoc = controlTools.cntrlCrv(name=objTarget, **setUp)
            aimLocObjs = self.createZeroGrp(obj=aimLoc, parentGrp=parentCtrl, parentGrpOnZero=True)

            # aim Constraint do controle posterior para o atual
            aimLocGrp = aimLocObjs[1]
            aimNode = self.aimGuide(objSource, aimLocGrp, axis, flipAxis, worldUpObject=upObj)

            # criando atributos para rotacionar os locators aims

            if flipAxis:
                if self.axis == 'X':
                    aimLocObjs[1].scaleZ.set(-1)

                if self.axis == 'Y':
                    aimLocObjs[1].scaleZ.set(-1)

                if self.axis == 'Z':
                    aimLocObjs[1].scaleX.set(-1)

                # Caso seja um sistema flip axis somar 180 na rotacao do offset:
                addNode = pm.createNode('addDoubleLinear', n=aimNode.name() + '_add')
                addNode.input1.set(180)
                pm.connectAttr(parentCtrl + '.' + self.guideAxisAttr, addNode.input2)
                pm.connectAttr(addNode.output, aimNode + '.offset' + axis)

            else:
                pm.connectAttr(parentCtrl + '.' + self.guideAxisAttr, aimNode + '.offset' + axis)

        logger.debug('# Fim do createAimLoc')
        return objTarget, objSource

    ## ==================================================================================================

    def dictDefault(self, moveallPos=((0, 0, 0), (0, -90, 0), (1, 1, 1)), type='guideDict'):
        '''
        Aqui setamos valor default para o guide.
        Se nao tiver nada setado para o self.num, setar um valor default
        Se type = 'guideDict', os valores default sao setados para o self.guideDict e self.num
        Se type = 'guideBase', os valores default sao setados para o self.guideBase
        '''
        logger.debug('dictDefault: Criando guideDict default')

        self.moveallPos = moveallPos
        # print '>>> ',self.moveallPos
        value = 0
        dict = {}

        if not self.num:
            self.num = 6

        if self.inputNum:
            self.num = self.inputNum

        if not self.driverMap and self.inputDiverMap:
            self.driverMap = self.inputDiverMap

        keepDriver = False
        if self.driverMap:
            keepDriver = True
            self.num = len(self.driverMap)

        driver = True
        driverCount = 0
        for e, i in enumerate(range(self.num)):
            driverCount += 1

            if keepDriver:
                if e < self.num-1:
                    driver = self.driverMap['node' + str(e + 1)]
            else:
                if driverCount == self.fkInterval:
                    driverCount = 0
                    driver = True
                else:
                    if e == 0:
                        driver = True
                        driverCount = 0
                    else:
                        driver = False

            if e == 0:  # moveall
                dict.update({i: (
                            (self.moveallPos[0][0], self.moveallPos[0][1], value + self.moveallPos[0][2]),
                            self.moveallPos[1], self.moveallPos[2])})

            dict.update({i+1: (
            (self.moveallPos[0][0], self.moveallPos[0][1], value + self.moveallPos[0][2]),0)})
            if e < self.num - 1:
                self.driverMap.update({'node'+str(e+1): driver})

            value += 2

        if type == 'guideDict':
            self.guideDict = dict

        elif type == 'guideBase':
            self.guideBase = dict

        else:
            logger.debug('Tipo invalido para uso do metodo')

        logger.debug('# Fim do dictDefault')

    ## ==================================================================================================

    def doGuide(self, **kwargs):
        logger.debug('doGuide: Criando guide')
        if self.fk or self.ik or self.dyn:

            self.__dict__.update(**kwargs)
            #atualizando o nome da chain
            self.moveallGuideSetup['nameTempl'] = self.name + '_moveall'
            self.chainGuideSetup['nameTempl'] = self.name
            self.locGuideSetup['nameTempl'] = self.name + '_loc'
            self.moveallSetup['nameTempl'] = self.name + '_moveall'

            self.moveallSetup['icone'] = 'circulo' + self.axis
            self.ctrlFkSetup['icone'] = 'circulo' + self.axis
            self.ctrlFkTwkSetup['icone'] = 'hexagono' + self.axis

            self.nameFill = self.name

            self.dictDefault(type = 'guideBase')


            if self.selection == []:
                self.selection = pm.ls(os=1, fl=1)
                pm.selectPref(trackSelectionOrder=True, aa=1)

            if self.selection:
                print 'doGuide: Tem algo selecionado'

                if self.selToGuide == 'singleGuide':

                    if len(self.selection) < 2:
                        print 'eh uma coisa soh, vira multipleGuides'
                        self.selToGuide = 'multipleGuides'

                    else:
                        # print 'singleGuide: construindo um chain com cada item selecionado'

                        self.guideDict = self.getSelectionToGuide(self.selection) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

                        # print 'spaceSet: ', self.guideDict[0]
                        self.moveallGuideSetup['spaceSet'] = self.guideDict[0][0]

                        # print '- Construindo guide com as coordenadas: \n', self.guideDict, '\n- E num: \n', self.num

                        self.currentGuide = self.constructorGuide()

            if not self.selection:
                self.selToGuide = 'multipleGuides'

            if self.selToGuide == 'multipleGuides':
                print 'multipleGuides: construindo um chain para cada item selecionado'

                startChain = {}


                if self.guideDict == {} or self.guideDict == None:
                    startChain = self.getSelectionToGuide(self.selection, allMoveall=True) #<<<<<<<<<<<<<<<<<<<<<

                else:
                    print 'guideDict:', self.guideDict

                    startChain = self.guideDict

                    print 'startChain', startChain

                if self.guideDict == None or startChain == {}:
                    logger.debug('doGuide: guideDict eh vazio')

                    self.dictDefault()
                    startChain = self.guideDict[0]
                    self.currentGuide = self.constructorGuide()

                else:
                    logger.debug('doGuide: startChain nao eh vazio. Selecao: '+ str(self.selection))
                    print 'startChain: ', startChain

                    if not self.selection:
                        logger.debug('doGuide: nao temos selecao')
                        if self.guideDict == None or self.guideDict == {}:
                            self.dictDefault(startChain[0])

                        self.currentGuide = self.constructorGuide()

                        pass

                    elif self.selection:
                        logger.debug('doGuide: temos selecao'+str(self.selection))
                        for e, each in enumerate(self.selection):
                            logger.debug('doGuide: para cada item da selecao')
                            self.chainParent = str(each)

                            index = e + 1
                            logger.debug('doGuide: guideDict: ', self.guideDict)

                            if self.guideDict == None or self.guideDict == {}:
                                logger.debug('doGuide: guideDict esta vazio')
                                self.dictDefault(startChain[e])

                            # print '- Construindo guide com as coordenadas: \n', self.guideDict, '\n- E num: \n', self.num

                            if len(self.selection) > 1:  # incluindo preenchimento automatico
                                self.currentGuide = self.constructorGuide(name=self.nameFill + '_' + str(index).zfill(2))

                            else:  # sem preenchimento automatico
                                self.currentGuide = self.constructorGuide()

            logger.debug('# Fim do doGuide')
        else:
            pm.warning('Selecione ao menos um tipo de construcao: FK, IK e/ou DYN')
    ## ==================================================================================================

    def constructorGuide(self, **kwargs):
        logger.debug('constructorGuide: Construcao do guide')

        self.__dict__.update(**kwargs)

        if self.guideDict:
            self.num = len(self.guideDict)

        if self.guideSys:
            self.guideSys = []

        for guide in range(self.num):
            # print 'dicCOPY: '+str(self.guideDict)

            guideDict = self.guideDict.copy()

            if guide == 0:
                # criando o moveall guide
                displaySetup = self.moveallGuideSetup.copy()

                ctrlName = displaySetup['nameTempl'] + self.guideSuffix
                self.guideMoveall = self.createEachCtrlGuide(ctrlName, self.guideObj, guideDict, 0, displaySetup,
                                                             createZero=False, moveall=True)
                self.guideSys.append(self.guideMoveall)

                if self.ik:
                    # criando apontador do preferred angle

                    preferredAngleCtrlName = self.name + self.ikPreferredSuffix + self.guideSuffix
                    preferredAngleCtrl = controlTools.cntrlCrv(name=preferredAngleCtrlName, icone='seta', size=.3,
                                                               color=(.5,1,.5), lockChannels=('v', 'tx','ty','tz',
                                                                                              'sx','sy','sz'),
                                                               parent=self.guideMoveall[0], cntrlSulfix= '')

                    preferredAngleCtrl.getParent().rotateX.set(0)
                    preferredAngleCtrl.getParent().rotateY.set(90)
                    preferredAngleCtrl.getParent().rotateZ.set(0)

                    #preferredAngleCtrl.scale.set(.3, .3, .3)
                    #preferredAngleCtrl.rotateX.set(90)
                    preferredAngleCtrl.rotateY.set(90)
                    pm.makeIdentity(preferredAngleCtrl, a=1, r=1)
                    pm.setAttr(preferredAngleCtrl + '.rx', l=1, k=0)
                    pm.setAttr(preferredAngleCtrl + '.ry', l=1, k=0)


                    if self.preferredOrient:
                        preferredAngleCtrl.rotateZ.set(self.preferredOrient)
                    else:
                        preferredAngleCtrl.rotateZ.set(-90)
            else:
                # criando os demais ctrls guide

                displaySetup = self.chainGuideSetup.copy()
                guideName = displaySetup['nameTempl'] + '_' + str(guide) + self.guideSuffix

                guideIcon = displaySetup['icone']

                # print guideName, self.guideObj, guideDict, guide, displaySetup
                guideRunning = self.createEachCtrlGuide(guideName, self.guideObj, guideDict, guide, displaySetup)

                self.guideSys.append(
                    guideRunning)  # lista contendo cada guide da cadeia onde cada objeto da lista eh uma lista contendo: [obj, zeroGrp]

        aimSource = self.guideSys[2][0]
        aimTarget = self.guideSys[0][0]

        # verifica se o primeiro objeto da lista (moveall) ja existe
        if not pm.objExists(self.globalParent['GUIDES']):
            pm.group(aimTarget, n=self.globalParent['GUIDES'])

        else:
            pm.parent(aimTarget, self.globalParent['GUIDES'])

        pm.PyNode(self.globalParent['GUIDES']).v.set(1)

        # posicionamento default do guide:
        for e in range(self.num):
            self.setCntrl(self.guideSys[e][0], self.guideSys[e][1], self.guideBase, e, space='world')

        # orientando o moveall
        self.aimGuide(aimSource, aimTarget, self.axis, deleteConstraint=True)


        # parenteando cada guide no moveall:
        for e in range(self.num):
            if e > 0:
                pm.parent(self.guideSys[e][1], self.guideMoveall[0])

        # criando atributos no guide:
        pm.addAttr(self.guideMoveall[0], ln='chainDict', dt='string')

        for e in range(self.num):
            if e < self.num - 1 and e > 0:
                if not pm.attributeQuery(self.guideAxisAttr, node=self.guideSys[e][0], exists=True):

                    pm.addAttr(self.guideSys[e][0], ln=self.guideAxisAttr, k=1)

                    if e == 1:
                        pm.addAttr(self.guideSys[e][0], ln=self.guideIsDriver, at='enum', en='on=1', dv=1, k=1)
                        pm.setAttr(self.guideSys[e][0] + '.' + self.guideIsDriver, k=0, cb=1)

                        for shape in pm.listRelatives(pm.PyNode(self.guideSys[e][0]), c=1, s=1):
                            shape.overrideColorRGB.set(1, 1, 0)
                    if e > 1:
                        pm.addAttr(self.guideSys[e][0], ln=self.guideIsDriver, at='bool', dv=1, k=1)
                        pm.setAttr(self.guideSys[e][0] + '.' + self.guideIsDriver, k=0, cb=1)

                        if self.driverMap:
                            pm.setAttr(self.guideSys[e][0]+'.'+self.guideIsDriver, self.driverMap['node'+str(e)])

                        #mudando a cor do guide se for driver:
                        blendNode = pm.shadingNode('blendColors', n=self.guideSys[e][1] + '_blend', asUtility=1)
                        pm.connectAttr(self.guideSys[e][0]+'.'+self.guideIsDriver, blendNode+'.blender')

                        blendNode.color1.set(1, 1, 0)
                        blendNode.color2.set(.1, .8, .8)

                        for shape in pm.listRelatives(pm.PyNode(self.guideSys[e][0]), c=1, s=1):
                            blendNode.output >> shape.overrideColorRGB

        # criando sistema de aims
        for e in range(self.num):
            if e > 0:
                if e == len(self.guideDict) - 1:
                    nextGuide = None
                else:
                    nextGuide = self.guideSys[e + 1][0]

                locGuideName = self.locGuideSetup['nameTempl'] + str(e) + self.guideSuffix

                self.createAimLoc(locGuideName, nextGuide, self.guideSys[e][0], self.locGuideSetup, self.axis,
                                  self.guideMoveall[0], self.flipAxis)

                self.guideOrientSys.append(locGuideName)

        # usando inputs de coordenadas do guide
        if guideDict:
            for e in range(self.num):


                if e < (self.num - 1):
                    self.setCntrl(self.guideSys[e][0], None, self.guideDict, e, orientAttr=self.guideAxisAttr,
                                  space='world')
                else:
                    self.setCntrl(self.guideSys[e][0], None, self.guideDict, e, space='world')


        # criando uma curva de referencia de posicionamentos do guide:
        curveCoordList = []
        # encontrando posicao de cada ctrl do guide

        for ctrl in range(self.num):
            position = guideDict[ctrl][0]
            curveCoordList.append(position)

        refCurveName = displaySetup['nameTempl'] + '_refCurve'
        refCurve = pm.curve(n=refCurveName, p=curveCoordList, d=1)
        refCurve.setParent(self.guideMoveall[0])
        refCurve.inheritsTransform.set(1)

        #criando clusters para a curva de referencia
        refClusterList = []
        refClustGrp = groupTools.makeGroup(name=refCurveName+'_clus', parent=self.guideMoveall[0])
        for i, vtx in enumerate(refCurve.cv):
            refCluster = pm.cluster(refCurve.cv[i], n=refCurveName + '_' + str(i))
            refClusterList.append(refCluster)
            refCluster[1].setParent(refClustGrp)
            refCluster[0].relative.set(1)
            pm.pointConstraint(self.guideSys[i][0], refCluster[1], mo=0)
            refCluster[1].v.set(0)

        refCurve.template.set(1)


        self.exportDict()

        # print '____startChain: ', startChain

        pm.select (self.guideMoveall[0])

        logger.debug('# Fim do constructorGuide')
        om.MGlobal.displayInfo('# Success! O Guide ' + str(self.guideMoveall[0]) + ' foi gerado com sucesso.\n')
        return (self.guideMoveall[0])

    ## ==================================================================================================
    def uploadDict (self, guideSys = [], preferredAngleGuide=None):
        '''
        Aqui fazemos uma leitura do guide da cena e atualizamos toda as variaveis listadas em toExport
        '''

        logger.debug('uploadDict: Atualizando a instancia com as coords do guide')
        if guideSys == []:
            guideSys = self.guideSys

        if not preferredAngleGuide:
            preferredAngleGuide = self.name + self.ikPreferredSuffix + self.guideSuffix

        for e, eachGuide in enumerate(guideSys):
            ctrl = eachGuide[0]

            transCoords = pm.xform(ctrl, q=1, rp=1, ws=1)

            if e == 0:
                #moveall
                rotCoords = pm.xform(ctrl, q=1, ro=1, ws=1)
                scaleCoords = pm.xform(ctrl, q=1, s=1, ws=1)

                self.guideDict.update({e: (transCoords, rotCoords, scaleCoords)})
            else:
                # demais guides
                orient = 0
                if e < len(guideSys)-1:
                    # get do valor do attr orient:
                    if pm.objExists(ctrl):
                        #ctrlObj = pm.PyNode(ctrl)

                        orient = pm.getAttr(ctrl + '.' + self.guideAxisAttr)
                        driver = pm.getAttr(ctrl + '.' + self.guideIsDriver)

                        if preferredAngleGuide:
                            try:
                                preferredAngleOrient = pm.PyNode(preferredAngleGuide).rotateZ.get()
                                self.preferredOrient = preferredAngleOrient

                                if self.axis == 'X':
                                    coordX = math.sin(math.radians(preferredAngleOrient))
                                    coordY = math.cos(math.radians(preferredAngleOrient))

                                    self.preferredValues = (0, coordY, coordX)

                                elif self.axis == 'Y':

                                    coordX = math.sin(math.radians(preferredAngleOrient+90))
                                    coordY = math.cos(math.radians(preferredAngleOrient+90))

                                    self.preferredValues = (coordX, 0, coordY)

                                elif self.axis == 'Z':

                                    coordX = math.sin(math.radians(preferredAngleOrient+90))
                                    coordY = math.cos(math.radians(preferredAngleOrient+90))

                                    self.preferredValues = (coordY, coordX, 0)

                            except:
                                print 'nao rolou dar um get no ctrl de preferredAngle do guide. Setando valor default'
                                self.preferredValues = (0, 1, 0)


                    else:
                        pm.warning('nao foi possivel ler os attr de orientacao do guide')

                    self.guideDict.update({e: ((transCoords),orient)})

                    node = 'node'+str(e)
                    self.driverMap.update({node:driver})

                else:
                    self.guideDict.update({e: ((transCoords),0)})

        logger.debug('# Fim do uploadDict')

    ## ==================================================================================================

    def exportDict(self, guideInstance = None, **kwargs):
        '''
        formato do guideInstance = 'teste_moveall_guide' (unicode)

        Esse metodo xporta para o atributo chainDict no moveall um dicionario com tudo o que eh necessario
        para reconstruir a chain com base nas keys na variavel self.toExport
        '''

        logger.debug('exportDict: Exportando dicionario')

        expDict = {}

        if not guideInstance:

            self.__dict__.update(**kwargs)

            moveall = pm.PyNode(self.guideMoveall[0])
            #self.uploadDict()
            toExport = self.toExport


        for key in toExport:
            expDict[key] = self.__dict__[key]

        dictString = json.dumps(expDict)
        moveall.chainDict.set(dictString)

        logger.debug('# Fim do exportDict')
        return expDict

    ## ==================================================================================================

    def getDict(self, guideInstance = None, **kwargs):
        '''
        guideInstance = Guide que sera usado de base para o getDict

        aqui trazemos para a classe o dicionario guardado no dicionario json atualizado

        # formato do guideInstance = 'chain_moveall_guide'
        # caso nao tenha guideInstance o metodo procura o moveall no self
        '''
        if self.fk or self.ik or self.dyn:
            # atualizando para pegar da cena o guide, sem historico de instancia

            #self.guideMoveall = pm.PyNode(ctrlName)
            logger.debug('getDict: Trazendo informacoes do json para a instancia')
            chainDictRestored = {}

            moveall = None
            if not guideInstance:
                try:
                    moveall = pm.PyNode(self.moveallGuideSetup['nameTempl'] + self.guideSuffix)
                except:
                    #print 'Nao existe o guide na cena. Criando...'
                    self.doGuide()
                    moveall = self.guideMoveall[0]

            else:
                moveall = guideInstance


            logger.debug('pegando informacoes de posicionamento do guide')

            try:

                guideInstance = pm.PyNode(moveall)
                jsonDict = guideInstance.chainDict.get()

                chainDictRestored = json.loads(jsonDict)

                self.guideDict = chainDictRestored['guideDict']
                guideSys = chainDictRestored['guideSys']

                # identificando o tamanho do sistema:

                pyCtrlGuide = []
                print 'self.guideDict: ', guideSys
                for jnt in guideSys:
                    pyJnt = pm.PyNode(jnt[0])
                    pyCtrlGuide.append(pyJnt)

                width = vtxWalk.bbox(pyCtrlGuide)['width']
                heigh = vtxWalk.bbox(pyCtrlGuide)['height']
                deph = vtxWalk.bbox(pyCtrlGuide)['deph']

                sysSize = [width, heigh, deph]
                print 'sysSize > ', sysSize

                sysSize.sort()
                self.sysSize = sysSize[-1]
                print '>>>>>>>>>>>>>>>  self.sysSize', self.sysSize

            except:
                logger.error('nao foi possivel acessar o attr chainDict')


            # convertendo os key em inteiros:
            for key, value in self.guideDict.items():
                self.guideDict[int(key)] = self.guideDict.pop(key)

            self.__dict__.update(**chainDictRestored) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            self.uploadDict()
            self.__dict__.update(**kwargs)

            logger.debug('# Fim do getDict')
            om.MGlobal.displayInfo('# Success! Informacoes do Guide ' + str(moveall) + ' foram atualizadas.\n')
            return chainDictRestored

        else:
            pm.warning('Selecione ao menos um tipo de construcao: FK, IK e/ou DYN')

    ## ==================================================================================================


    def duplicateGuide (self, chain, **kwargs):
        '''

        :param self: sera a nova cadeia
        :param chain: a cadeia base
        '''

        logger.debug('duplicateGuide: Duplicando '+str(chain))
        if chain.name != self.name:
            self.__dict__.update(**kwargs)
            name = self.name
            pm.select(cl=1)
            duplicatedGuideMoveall = self.moveallSetup['nameTempl'] + self.guideSuffix

            if pm.objExists(duplicatedGuideMoveall):
                pm.delete(duplicatedGuideMoveall)
                self.guideMoveall = None

            self.guideSys = []

            if not chain.guideMoveall:
                chain.doGuide()

            dictOrig = chain.getDict()

            baseDict = dictOrig['guideDict']
            driverMap = dictOrig['driverMap']
            axis = dictOrig['axis']
            flipAxis = kwargs.pop('flipAxis', False)
            #self.__dict__.update(**dictOrig)

            #print 'duplicateGuide: baseDict: >>>>', baseDict

            self.guideDict = baseDict
            self.driverMap = driverMap
            self.axis = axis
            self.flipAxis = flipAxis

            if not self.guideMoveall:
                self.doGuide(flipAxis=flipAxis)

            om.MGlobal.displayInfo('# Success! O Guide ' + chain.name + ' foi duplicado como ' + self.name + '.\n')

        else:
            pm.warning('O nome da chain a ser duplicada eh igual a cadeia original')

        logger.debug('# Fim do duplicateGuide')
        return chain

    ## ==================================================================================================

    def mirrorConnectGuide(self, chain, flipAxis=True, **kwargs):
        '''
        chain: instancia da chain que vai receber mirror da cadeia self
        flipAxis: a nova cadeia flipa ou nao os eixos de acordo com o que tiver nessa variavel
        '''
        logger.debug('mirrorConnectGuide: Duplicando '+str(chain)+' e conectando na cadeia original')
        mirroredGuide = self.duplicateGuide(chain, flipAxis=flipAxis, **kwargs)

        connectionList = []
        for index, guide in enumerate (mirroredGuide.guideSys):
            ctrlMirrorGuide = guide[0]
            ctrlBaseGuide = self.guideSys[index][0]

            connectionList.append ((ctrlMirrorGuide, ctrlBaseGuide))

        for index, (source, target) in enumerate(connectionList):
            sourceObj = pm.PyNode(source)
            targetObj = pm.PyNode(target)

            if index == 0:
                sourceObj.rotate >> targetObj.rotate

            sourceObj.translate >> targetObj.translate
            sourceObj.scale >> targetObj.scale

            guideAxisAttr = self.guideAxisAttr
            if index > 0 and index < len(connectionList) - 1:
                sourceObj.driver >> targetObj.driver

                try:
                    mirrorOrientNode = pm.createNode('multDoubleLinear', n = targetObj+'_mirror_md')
                    pm.setAttr(mirrorOrientNode + '.input2', -1)
                    pm.connectAttr(sourceObj + '.' + guideAxisAttr, mirrorOrientNode + '.input1')

                    pm.connectAttr(mirrorOrientNode + '.output', targetObj + '.' + guideAxisAttr)

                except:
                    logger.debug('Nao foi possivel conectar atributos de orientacao dos guides')
                pass

        mirrorGroupName = self.name + 'MirrorGuide_grp'

        if pm.objExists(mirrorGroupName):
            pm.delete(mirrorGroupName)

        mirrorGroup = pm.group(n= mirrorGroupName, em=1)

        guideMoveall = pm.PyNode(self.guideMoveall[0])
        guideMoveall.setParent(mirrorGroup)
        mirrorGroup.setParent(self.globalParent['GUIDES'])


        mirrorGroup.scaleX.set(-1)
        pm.select(chain.guideMoveall[0])

        logger.debug('# Fim do mirrorConnectGuide')
        om.MGlobal.displayInfo('# Success! O Guide ' + self.name + ' foi conectado em mirror com ' + chain.name + '.\n')

        pass

    ## ==================================================================================================

    def updateChainMap(self):
        logger.debug('updateChainMap: Trazendo para a instancia informacoes de trans e orient do guide')

        self.chainMap = []
        for e, each in enumerate(self.guideSys):
            if e > 0:

                node = pm.PyNode(each[0])
                trans = node.getTranslation(space='world').get()

                rotNode = None

                if e < (len(self.guideSys) - 1):
                    rotNode = pm.PyNode(self.guideOrientSys[e-1])

                    rot = pm.xform(rotNode, q=1, ro=1, ws=1)

                node = tuple([trans, rot])
                self.chainMap.append(node)
        logger.debug('# Fim do updateChainMap')

    ## ==================================================================================================

    def createRigCtrl(self, i, index, coord, fkPrefix, fkCtrlList, nodeLoop, firstSuffix, moveall):
        logger.debug('createRigCtrl: Criando controladores')

        fkNodeCtrlList = {}
        prevDrvCtrl = None
        for e, each in enumerate(nodeLoop):
            nodeCtrl = None

            # criando demais controles
            coordenate = (coord[0], coord[1], (1, 1, 1))

            nodeSuffix = firstSuffix + each[0]
            nodeName = fkPrefix + '_' + index + '_' + nodeSuffix

            if i > 0 and e == 0:

                nodeParentCtrl = fkCtrlList[i-1]['ctrl'] # caso seja o primeiro grupo do node, parenteia no ctrl anterior

            else:
                if e == 0: # primeiro loop - Parenteia no Moveall
                    nodeParentCtrl = moveall

                else: # demais grupos parenteiam no anterior
                    nodeParentCtrl = prevDrvCtrl

            size = self.sysSize / 4.75
            print '*********************** ********** **** * size = ', size
            if each[1] == 'grp':
                nodeCtrl = groupTools.makeGroup(name=nodeName, coords=coordenate, parent=nodeParentCtrl, suffix='')

            elif each[1] == 'ctrl':
                nodeCtrl = controlTools.cntrlCrv(name=nodeName, coords=coordenate, parent=nodeParentCtrl,
                                                 size= size, **self.ctrlFkSetup)

                pm.addAttr(nodeCtrl, ln='stretch', k=1, min=0, max=1, dv=1)
                pm.addAttr(nodeCtrl, ln='factorStretch', k=1, min=1, max=5)

            fkNodeCtrlList.update({each[0]: nodeCtrl})
            prevDrvCtrl = nodeCtrl

        logger.debug('# Fim do createRigCtrl')
        return fkNodeCtrlList

    ## ==================================================================================================

    def makeMoveall(self, firstPrefix, coord, nodeParentCtrl):

        size = self.sysSize / 3.16
        print '*********************** ********** **** * size = ', size

        logger.debug('makeMoveall: Criando ctrl Moveall')

        moveallName = self.moveallSetup['nameTempl'] + firstPrefix
        coordenate = (coord[0], coord[1], (1, 1, 1))

        moveallGrp = groupTools.makeGroup(name=moveallName, coords=coordenate, parent=nodeParentCtrl)
        moveall = controlTools.cntrlCrv(name=moveallName, coords=coordenate, parent=moveallGrp, lockChannels=['v'],
                                        size= size, **self.moveallSetup)

        pm.addAttr(moveall, ln='fkStretch', k=1, min=0, max=1, dv=1)
        pm.addAttr(moveall, ln='extraCtrlsVisibility', attributeType='long', k=1, min=0, max=1, dv=1)

        pm.setAttr(moveall.extraCtrlsVisibility, cb=1, k=0)
        logger.debug('# Fim do makeMoveall')

        return moveall, moveallGrp

    def createRigTwkCtrl(self, i, index, twkGrp, indexAnt, nodeLoop, coord, fkPrefix, firstPrefix):
        logger.debug('createRigTwkCtrl: Criando controles twk do fk')

        fkNodeTwkList = {}
        prevDrvTwk = None
        for e, each in enumerate(nodeLoop):

            defaultCoordenate = (coord[0], coord[1], (1, 1, 1))
            if e > 0:
                upVectCoordenate = (self.chainMap[i - 1][0], self.chainMap[i - 1][1], (1, 1, 1))
            else:
                upVectCoordenate = defaultCoordenate

            nodeSuffix = firstPrefix + each[0]
            defaultNodeName = fkPrefix + '_' + index + '_' + nodeSuffix
            upVectName = fkPrefix + '_' + indexAnt + '_' + nodeSuffix

            if e == 4 or e == 5:  # caso seja upVector
                nodeName = upVectName
                coordenate = upVectCoordenate
            else:
                nodeName = defaultNodeName
                coordenate = defaultCoordenate

            if e == 0:  # primeiro loop - Parenteia no Moveall
                nodeParentTwk = twkGrp

            else:  # demais grupos parenteiam no anterior
                nodeParentTwk = prevDrvTwk

            size = self.sysSize / 6.333

            if each[1] == 'grp':

                if i == 0 and (e == 4 or e == 5):  # o primeiro upvector fica dentro do segundo controle
                    # nao criamos upvector no primeiro ctrl
                    pass

                else:
                    if e != 4:
                        nodeTwk = groupTools.makeGroup(name=nodeName, coords=coordenate,
                                                         parent=nodeParentTwk, suffix='')

                        fkNodeTwkList.update({each[0]: nodeTwk})
                        prevDrvTwk = nodeTwk
                    else:
                        if firstPrefix == 'dummy_':
                            nodeTwk = groupTools.makeGroup(name=nodeName, coords=coordenate,
                                                             parent=fkNodeTwkList['twk_ctrl'], suffix='')

                            fkNodeTwkList.update({each[0]: nodeTwk})
                            prevDrvTwk = nodeTwk

            elif each[1] == 'ctrl':
                nodeTwk = controlTools.cntrlCrv(name=nodeName, coords=coordenate,
                                                parent=nodeParentTwk, size=size, **self.ctrlFkTwkSetup)

                fkNodeTwkList.update({each[0]: nodeTwk})
                prevDrvTwk = nodeTwk

            elif each[1] == 'loc':
                if firstPrefix == 'dummy_':
                    if i == 0 and (e == 4 or e == 5):  # o primeiro upvector fica dentro do segundo controle
                        # nao criamos upvector no primeiro ctrl
                        pass
                    else:
                        nodeTwk = controlTools.cntrlCrv(name=nodeName, coords=coordenate,
                                                        parent=nodeParentTwk, **self.locFkSetup)
                        nodeTwk.v.set(0)

                        if e == 5:  # caso seja o upVector recebe um offset
                            if self.flipAxis:
                                upVectOffset = 10
                            else:
                                upVectOffset = -10

                            if self.axis == 'X':
                                nodeTwk.translateX.set(upVectOffset)

                            elif self.axis == 'Y':
                                nodeTwk.translateY.set(upVectOffset)

                            elif self.axis == 'Z':
                                nodeTwk.translateZ.set(upVectOffset)

                            nodeTwk.v.set(0)

                        fkNodeTwkList.update({each[0]: nodeTwk})
                        prevDrvTwk = nodeTwk
        logger.debug('# Fim do createRigTwkCtrl')
        return fkNodeTwkList

    def getDriverInfo(self, driverMap):
        logger.debug('getDriverInfo: Criando dicionarios para drivers e drivens para uso na construcao do sistema fk')

        prevDriver = None
        driverOf = 0
        driverDictNum = {}

        for i in range(len(driverMap)):

            index = i + 1
            nodeName = 'node' + str(index)

            if nodeName == 'node1':
                currentNode = nodeName
                prevDriver = currentNode
            else:
                currentNode = driverMap[nodeName]

            # gravando e zerando o tempBuffer
            if i > 0 and i < len(driverMap) - 1:  # enquanto nao for o ultimo
                if currentNode:
                    driverDictNum.update({prevDriver: driverOf})
                    driverOf = 0

            elif i == len(driverMap) - 1:  # o ultimo

                # caso o ultimo loop tambem seja driver:
                if not currentNode:
                    driverOf += 1

                driverDictNum.update({prevDriver: driverOf})

                if currentNode:
                    driverDictNum.update({nodeName: 1})

            if currentNode:
                driverOf = 1
                prevDriver = nodeName

            else:
                driverOf += 1

        #criando lista de valores de distribuicao para cada ctrl
        nodeValueDict = {}
        for nodeNum in range(len(driverMap)):
            nodeName = 'node' + str(nodeNum+1)
            if nodeName in driverDictNum:
                # print nodeName
                for qt in range(driverDictNum[nodeName]):
                    nodeValueName = 'node' + str(qt+1 + nodeNum)
                    nodeValue = 1.0 / driverDictNum[nodeName]
                    nodeValueDict.update({nodeValueName: nodeValue})

        logger.debug('# Fim do getDriverInfo')
        return {'nodeValueDict':nodeValueDict, 'driverDictNum':driverDictNum}

    def doFk(self):
        logger.debug('doFK: Criando sistema FK')

        self.getDict()
        self.exportDict()
        fkList = {}

        fkPrefix = self.name + '_fk'

        fkSysGrp = groupTools.makeGroup(name=self.name + '_fk_sys')
        fkCtrlSysGrp = groupTools.makeGroup(name=self.name + '_fk_ctrl_sys', parent=fkSysGrp)
        fkCtrlSysGrp.v.set(0)

        fkJntGrp = groupTools.makeGroup(name=fkPrefix + self.jxtSuffix, parent=fkSysGrp)
        twkDummyGrp = groupTools.makeGroup(name=fkPrefix + '_dummy_twk', parent=fkCtrlSysGrp)
        self.fkTwkGrp = groupTools.makeGroup(name=fkPrefix + '_twk', parent=self.baseCtrlGrp)

        fkJntGrp.v.set(0)

        fkJntList = []
        fkDummyCtrlList = []
        fkCtrlList = []
        fkDummyTwkList = []
        fkTwkList = []
        fkNodesList = []

        # criando estrutura fk

        fkJnt1SuffixList = [('cnx_grp', 'grp'),
                            ('cnx', 'jnt'),
                            ('twkParent', 'jnt'),
                            ('jxt', 'jnt'),
                            ('end', 'jnt')]

        fkJntSuffixList = [('parent_zero_grp', 'grp'),
                           ('parent_grp', 'grp'),
                           ('twkParent', 'jnt'),
                           ('cnx', 'jnt'),
                           ('jxt', 'jnt'),
                           ('end', 'jnt')]

        multDiv_MultScale_baseNode = pm.createNode('multDoubleLinear', n=self.name + '00_multDiv_MultScale_base')
        multDiv_MultScaleNodeList = [multDiv_MultScale_baseNode]

        driverInfo = self.getDriverInfo(self.driverMap)

        for i, coord in enumerate(self.chainMap):

            index = str(i + 1)
            indexAnt = str(i)

            iProx = i+1
            iAnt = i-1

            if i < len(self.chainMap) - 1:  # enquanto nao for o node end

                # criando joints fk

                logger.debug('Iniciando construcao do sistema de joint do fk ' + index)
                nextCoord = self.chainMap[i + 1]

                if i == 0: # se for o primeiro jnt da cadeia
                    nodeLoop = fkJnt1SuffixList

                elif i > 0: # se for o segundo em diante (menos o end)
                    nodeLoop = fkJntSuffixList

                prevDrv = ''
                fkNodeJntList = {}
                for e, each in enumerate(nodeLoop):

                    nodeJnt = None

                    nodeSuffix = each[0]
                    nodeName = fkPrefix + '_' + index + '_' + nodeSuffix

                    scaleCompensate = True

                    if nodeLoop == fkJnt1SuffixList:
                        if nodeSuffix == 'twkParent' or nodeSuffix == 'jxt':
                            scaleCompensate = False

                    if nodeLoop == fkJntSuffixList:
                        if nodeSuffix == 'cnx':
                            scaleCompensate = False

                    coordenate = (coord[0], coord[1], (1, 1, 1))
                    if e == len(nodeLoop)-1: # se for o end
                        coordenate = (nextCoord[0], nextCoord[1], (1, 1, 1))


                    if e == 0:
                        nodeParentJnt = fkJntGrp
                    else:
                        nodeParentJnt = prevDrvJnt
                    if each[1] == 'grp':
                        nodeJnt = groupTools.makeGroup(name=nodeName, coords=coordenate, parent=nodeParentJnt,
                                                         suffix='')

                    elif each[1] == 'jnt':
                        nodeJnt = jointTools.makeJoint(name=nodeName, coords=coordenate, connectToLast = True,
                                                         scaleCompensate = scaleCompensate)

                    prevDrvJnt = nodeJnt

                    fkNodeJntList.update({nodeSuffix: nodeJnt})

                # ----------------------------------
                # criando controles fk

                logger.debug('Iniciando construcao do sistema de ctrls do fk ' + index)
                fkCtrl1SuffixList = [('ctrl_grp', 'grp'),
                                     ('ctrl_offset_grp', 'grp'),
                                     ('ctrl_normaliza_grp', 'grp'),
                                     ('ctrl', 'ctrl')]

                nodeLoop = fkCtrl1SuffixList

                if i == 0:


                    pm.parentConstraint(self.toParentDrv, fkCtrlSysGrp, mo=1)
                    pm.scaleConstraint(self.toParentDrv, fkCtrlSysGrp, mo=1)

                    self.moveall.extraCtrlsVisibility >> self.fkTwkGrp.v


                fkDummyNodeCtrlList = self.createRigCtrl(i, index, coord, fkPrefix, fkDummyCtrlList,
                                                              nodeLoop, 'dummy_', self.dummyMoveall)

                fkNodeCtrlList = self.createRigCtrl(i, index, coord, fkPrefix, fkCtrlList,
                                                         nodeLoop, '', self.moveall)

                # ----------------------------------
                # criando sistema de tweaks fk

                logger.debug('Iniciando construcao do sistema de twks do fk ' + index)
                fkTwkSuffixList = [('twk_ctrl_zero_grp', 'grp'),
                                   ('twk_ctrl_parent_grp', 'grp'),
                                   ('twk_ctrl', 'ctrl'),
                                   ('dist_loc', 'loc'),
                                   ('upVec_loc_grp', 'grp'),
                                   ('upVec_loc', 'loc')]

                nodeLoop = fkTwkSuffixList

                fkDummyNodeTwkList = self.createRigTwkCtrl(i, index, twkDummyGrp, indexAnt, nodeLoop, coord,
                                                           fkPrefix, 'dummy_')

                fkNodeTwkList = self.createRigTwkCtrl(i, index, self.fkTwkGrp, indexAnt, nodeLoop, coord,
                                                      fkPrefix, '')

                # ----------------------------------

                if i < len(self.chainMap) - 2:  # com excecao do ultimo node

                    # criando nodes fk

                    fkNodeSuffixList = [(self.name + '_01_10_multDiv_ss_'+index,             'multDoubleLinear',
                                         '01_10_multDiv_ss'),

                                        (self.name + '_02_multDiv_MultScale_'+index,         'multDoubleLinear',
                                         '02_multDiv_MultScale'),

                                        (self.name + '_03_06_plusMinAvrg_minus1_'+index,     'plusMinusAverage',
                                         '03_06_plusMinAvrg_minus1'),

                                        (self.name + '_04_07_reverse_revTo1_'+index,         'reverse',
                                         '04_07_reverse_revTo1'),

                                        (self.name + '_05_distDim'+index,                    'distanceBetween',
                                         '05_distDim'),

                                        (self.name + '_06_02_multDiv_divDist_'+index,        'multiplyDivide',
                                         '06_02_multDiv_divDist'),

                                        (self.name + '_07_04_multDiv_divCurrentDist_'+index, 'multiplyDivide',
                                         '07_04_multDiv_divCurrentDist'),

                                        (self.name + '_08_05_multDiv_divScale_'+index,       'multiplyDivide',
                                         '08_05_multDiv_divScale'),

                                        (self.name + '_09_03_multDiv_divDistOrig_'+index,    'multiplyDivide',
                                         '09_03_multDiv_divDistOrig'),

                                        (self.name + '_10_08_multDiv_multFactorScale_'+index,'multDoubleLinear',
                                         '10_08_multDiv_multFactorScale'),

                                        (self.name + '_11_09_BlendClr_ScaleYZ_'+index,       'blendColors',
                                         '11_09_BlendClr_ScaleYZ'),

                                        (self.name + '_12_11_BlendClr_SqshStrch_'+index,     'blendColors',
                                         '12_11_BlendClr_SqshStrch')
                                        ]

                    nodeLoop = fkNodeSuffixList

                    fkNodeNodesList = {}

                    for e, each in enumerate(nodeLoop):
                        node = None
                        nodeSuffix = each[0]
                        nodeName = fkPrefix + '_' + index + '_' + nodeSuffix

                        if each[1] == 'multDoubleLinear':
                            node = pm.createNode(each[1], n=nodeName)
                            if each[2] == '02_multDiv_MultScale':
                                multDiv_MultScaleNodeList.append(node)
                            pass

                        elif each[1] == 'multiplyDivide':
                            node = pm.createNode(each[1], n=nodeName)
                            pass

                        elif each[1] == 'plusMinusAverage':
                            node = pm.shadingNode(each[1], n=nodeName, asUtility=True)
                            pass

                        elif each[1] == 'reverse':
                            node = pm.createNode(each[1], n=nodeName)
                            pass

                        elif each[1] == 'blendColors':
                            node = pm.createNode(each[1], n=nodeName)
                            pass

                        elif each[1] == 'distanceBetween':
                            node = pm.createNode(each[1], n=nodeName)

                        else:
                            logger.error('Nao foi possivel criar o node '+each[0])

                        fkNodeNodesList.update({each[2]: node})

                # ----------------------------------
                fkJntList.append(fkNodeJntList)
                fkDummyCtrlList.append(fkDummyNodeCtrlList)
                fkCtrlList.append(fkNodeCtrlList)
                fkDummyTwkList.append(fkDummyNodeTwkList)
                fkTwkList.append(fkNodeTwkList)
                fkNodesList.append(fkNodeNodesList)
                # ----------------------------------

                # conectando ctrls finais no dummy:
                ctrlDriver = None

                twk = fkTwkList[i]

                pm.parentConstraint(fkCtrlList[i]['ctrl'], twk['twk_ctrl_parent_grp'])
                pm.scaleConstraint(fkCtrlList[i]['ctrl'], twk['twk_ctrl_parent_grp'])

                twk['twk_ctrl'].translate >> fkDummyTwkList[i]['twk_ctrl'].translate
                twk['twk_ctrl'].rotate >> fkDummyTwkList[i]['twk_ctrl'].rotate
                twk['twk_ctrl'].scale >> fkDummyTwkList[i]['twk_ctrl'].scale

                fkCtrlList[i]['ctrl'].translate >> fkDummyCtrlList[i]['ctrl'].translate
                fkCtrlList[i]['ctrl'].rotate >> fkDummyCtrlList[i]['ctrl'].rotate
                fkCtrlList[i]['ctrl'].scale >> fkDummyCtrlList[i]['ctrl'].scale
                fkCtrlList[i]['ctrl'].stretch >> fkDummyCtrlList[i]['ctrl'].stretch
                fkCtrlList[i]['ctrl'].factorStretch >> fkDummyCtrlList[i]['ctrl'].factorStretch

                # normalizacao:

                normaliza = pm.createNode('multiplyDivide', n=fkCtrlList[i]['ctrl']+'_normal_md')
                fkCtrlList[i]['ctrl'].translate >> normaliza.input1
                normaliza.input2.set(-1,-1,-1)

                normaliza.output >> fkCtrlList[i]['ctrl_normaliza_grp'].translate
                normaliza.output >> fkDummyCtrlList[i]['ctrl_normaliza_grp'].translate

                # offset:

                offset = pm.createNode('multiplyDivide', n=fkCtrlList[i]['ctrl']+'_offset_md')
                fkCtrlList[i]['ctrl'].translate >> offset.input1
                offsetValue = driverInfo['nodeValueDict']['node'+str(i+1)]
                offset.input2.set(offsetValue, offsetValue, offsetValue)

                offset.output >> fkCtrlList[i]['ctrl_offset_grp'].translate
                offset.output >> fkDummyCtrlList[i]['ctrl_offset_grp'].translate




        for i, coord in enumerate(self.chainMap):
            index = str(i + 1)
            indexAnt = str(i)

            iProx = i + 1
            iAnt = i - 1

            if i < len(self.chainMap) - 1:  # enquanto nao for o node end

                # - interconectando controles:
                if self.driverMap['node' + str(i + 1)]:  # caso seja um driver:
                    ctrlDriver = fkCtrlList[i]['ctrl']
                    nextList = []
                    for e in range(self.num - 2):
                        if e > i:
                            if self.driverMap['node' + str(e+1)]:
                                nextList.append(e+1)

                    if nextList:
                        id = nextList[0]
                        nextCtrlDriver = fkCtrlList[id-1]['ctrl']
                else:

                    nextCtrlDriver.translate >> fkCtrlList[i]['ctrl'].translate
                    ctrlDriver.rotate >> fkCtrlList[i]['ctrl'].rotate

                    # visibilidade

                    ctrlShapes = pm.listRelatives(fkCtrlList[i]['ctrl'], s=1)
                    for shape in ctrlShapes:
                        shape.v.set(0)

                #------------------------------------ organizando drivers alternados

                driveList = []
                for each in self.driverMap.iterkeys():
                    if each:
                        index = each.split('node')[1]
                        driveList.append(int(index))

                driveList.sort()
                drivDict = {}

                for e, driver in enumerate(driveList):
                    drivDict.update({driver: []})

                    for inn in range(len(self.driverMap)):
                        index = inn + 1
                        #print 'node'+str(index), self.driverMap['node'+str(index)], inn

                        if e < len(driveList) - 1:
                            if index >= driver and index < driveList[e + 1]:
                                drivDict[driver].append(index)
                        else:
                            if index >= driver:
                                logger.debug(drivDict[driver].append(index))

                #------------------------------------

                logger.debug('Interconectando nodes do sistema fk')

                # conexoes entre transforms (todos os nodes):
                fkDummyTwkList[i]['twk_ctrl'].translate >> fkJntList[i]['twkParent'].translate
                fkDummyTwkList[i]['twk_ctrl'].rotate >> fkJntList[i]['twkParent'].rotate
                fkDummyTwkList[i]['twk_ctrl'].scale >> fkJntList[i]['twkParent'].scale

                pm.parentConstraint(fkDummyCtrlList[i]['ctrl'], fkDummyTwkList[i]['twk_ctrl_parent_grp'], mo=1)
                pm.scaleConstraint(fkDummyCtrlList[i]['ctrl'], fkDummyTwkList[i]['twk_ctrl_parent_grp'], mo=1)

                if i < len(self.chainMap) - 2:  # com excecao do ultimo node

                    # TO DO: Atualizar essas informacoes de acordo com o attr self.axis

                    if not self.flipAxis:
                        if self.axis == 'X':
                            jntAimUpVect = (-1, 0, 0)
                            jntAim = (1, 0, 0)

                        elif self.axis == 'Y':
                            jntAimUpVect = (0, -1, 0)
                            jntAim = (0, 1, 0)

                        elif self.axis == 'Z':
                            jntAimUpVect = (0, 0, -1)
                            jntAim = (0, 0, 1)

                    else:
                        if self.axis == 'X':
                            jntAimUpVect = (1, 0, 0)
                            jntAim = (-1, 0, 0)

                        elif self.axis == 'Y':
                            jntAimUpVect = (0, 1, 0)
                            jntAim = (0, -1, 0)

                        elif self.axis == 'Z':
                            jntAimUpVect = (0, 0, 1)
                            jntAim = (0, 0, -1)

                    pm.aimConstraint(fkJntList[iProx]['cnx'], fkJntList[i]['jxt'], u=jntAimUpVect, aim=jntAim,
                                     wut='object', wuo=fkDummyTwkList[iProx]['upVec_loc'])

                    if i == 0:

                        self.dummyMoveall.scaleY >> multDiv_MultScale_baseNode.input1
                        fkCtrlSysGrp.scaleY >> multDiv_MultScale_baseNode.input2

                    multDiv_MultScaleNodeList[i].output \
                    >> fkNodesList[i]['02_multDiv_MultScale'].input1

                    fkDummyCtrlList[i]['ctrl'].scaleY \
                    >> fkNodesList[i]['02_multDiv_MultScale'].input2

                    fkNodesList[i]['02_multDiv_MultScale'].output \
                    >> fkNodesList[i]['06_02_multDiv_divDist'].input2X

                    fkDummyTwkList[i]['dist_loc'].getShape().worldPosition[0] \
                    >> fkNodesList[i]['05_distDim'].point1

                    fkDummyTwkList[iProx]['dist_loc'].getShape().worldPosition[0] \
                    >> fkNodesList[i]['05_distDim'].point2

                    fkNodesList[i]['06_02_multDiv_divDist'].operation.set(2)

                    fkNodesList[i]['05_distDim'].distance \
                    >> fkNodesList[i]['06_02_multDiv_divDist'].input1X

                    fkNodesList[i]['07_04_multDiv_divCurrentDist'].operation.set(2)

                    fkNodesList[i]['06_02_multDiv_divDist'].outputX \
                    >> fkNodesList[i]['07_04_multDiv_divCurrentDist'].input1X

                    fkNodesList[i]['07_04_multDiv_divCurrentDist'].input2X.set \
                        (fkNodesList[i]['06_02_multDiv_divDist'].outputX.get())

                    fkNodesList[i]['08_05_multDiv_divScale'].operation.set(2)

                    fkNodesList[i]['08_05_multDiv_divScale'].input1X.set(1)

                    fkNodesList[i]['07_04_multDiv_divCurrentDist'].outputX \
                    >> fkNodesList[i]['08_05_multDiv_divScale'].input2X

                    fkNodesList[i]['08_05_multDiv_divScale'].outputX \
                    >> fkNodesList[i]['10_08_multDiv_multFactorScale'].input1

                    fkNodesList[i]['04_07_reverse_revTo1'].outputX \
                    >> fkNodesList[i]['10_08_multDiv_multFactorScale'].input2

                    fkNodesList[i]['03_06_plusMinAvrg_minus1'].output1D \
                    >> fkNodesList[i]['04_07_reverse_revTo1'].inputX

                    fkNodesList[i]['03_06_plusMinAvrg_minus1'].operation.set(2)

                    fkDummyCtrlList[i]['ctrl'].factorStretch \
                    >> fkNodesList[i]['03_06_plusMinAvrg_minus1'].input1D[0]
                    fkNodesList[i]['03_06_plusMinAvrg_minus1'].input1D[1].set(1)

                    fkNodesList[i]['09_03_multDiv_divDistOrig'].operation.set(2)

                    fkNodesList[i]['06_02_multDiv_divDist'].outputX \
                    >> fkNodesList[i]['09_03_multDiv_divDistOrig'].input2X

                    fkNodesList[i]['09_03_multDiv_divDistOrig'].input1X.set \
                        (fkNodesList[i]['06_02_multDiv_divDist'].outputX.get())

                    fkNodesList[i]['09_03_multDiv_divDistOrig'].outputX \
                    >> fkNodesList[i]['11_09_BlendClr_ScaleYZ'].blender

                    fkNodesList[i]['08_05_multDiv_divScale'].outputX \
                    >> fkNodesList[i]['11_09_BlendClr_ScaleYZ'].color1R

                    fkNodesList[i]['10_08_multDiv_multFactorScale'].output \
                    >> fkNodesList[i]['11_09_BlendClr_ScaleYZ'].color2R

                    self.dummyMoveall.fkStretch \
                    >> fkNodesList[i]['01_10_multDiv_ss'].input1

                    fkDummyCtrlList[i]['ctrl'].stretch \
                    >> fkNodesList[i]['01_10_multDiv_ss'].input2

                    fkNodesList[i]['01_10_multDiv_ss'].output \
                    >> fkNodesList[i]['12_11_BlendClr_SqshStrch'].blender

                    fkNodesList[i]['07_04_multDiv_divCurrentDist'].outputX \
                    >> fkNodesList[i]['12_11_BlendClr_SqshStrch'].color1R

                    fkNodesList[i]['07_04_multDiv_divCurrentDist'].outputX \
                    >> fkNodesList[i]['12_11_BlendClr_SqshStrch'].color2R

                    fkNodesList[i]['11_09_BlendClr_ScaleYZ'].outputR \
                    >> fkNodesList[i]['12_11_BlendClr_SqshStrch'].color1G

                    fkNodesList[i]['11_09_BlendClr_ScaleYZ'].outputR \
                    >> fkNodesList[i]['12_11_BlendClr_SqshStrch'].color1B

                    fkNodesList[i]['12_11_BlendClr_SqshStrch'].color2G.set(1)

                    fkNodesList[i]['12_11_BlendClr_SqshStrch'].color2B.set(1)

                    if self.axis == 'X':
                        fkNodesList[i]['12_11_BlendClr_SqshStrch'].output \
                        >> fkJntList[i]['jxt'].scale

                    elif self.axis == 'Y':
                        fkNodesList[i]['12_11_BlendClr_SqshStrch'].outputR \
                        >> fkJntList[i]['jxt'].scaleY

                        fkNodesList[i]['12_11_BlendClr_SqshStrch'].outputG \
                        >> fkJntList[i]['jxt'].scaleX

                        fkNodesList[i]['12_11_BlendClr_SqshStrch'].outputB \
                        >> fkJntList[i]['jxt'].scaleZ

                    elif self.axis == 'Z':
                        fkNodesList[i]['12_11_BlendClr_SqshStrch'].outputR \
                        >> fkJntList[i]['jxt'].scaleZ

                        fkNodesList[i]['12_11_BlendClr_SqshStrch'].outputG \
                        >> fkJntList[i]['jxt'].scaleX

                        fkNodesList[i]['12_11_BlendClr_SqshStrch'].outputB \
                        >> fkJntList[i]['jxt'].scaleY
                        # conexoes entre nodes (todos os nodes):

                if i == 0:
                    # conexoes entre transforms (primeiro node):
                    pm.parentConstraint(fkDummyCtrlList[i]['ctrl'], fkJntList[i]['cnx'], mo=1)
                    pm.scaleConstraint(fkDummyCtrlList[i]['ctrl'], fkJntList[i]['cnx'], mo=1)


                    pass

                else:
                    # conexoes entre transforms (demais nodes):
                    pm.parentConstraint(fkDummyCtrlList[i]['ctrl'], fkJntList[i]['parent_grp'], mo=1)
                    pm.scaleConstraint(fkDummyCtrlList[i]['ctrl'], fkJntList[i]['parent_grp'], mo=1)
                    fkDummyCtrlList[i]['ctrl'].scale >> fkJntList[i]['cnx'].scale


                    pass
        print 'fkJntList'
        print fkJntList
        fkList = {'dummyMoveall':self.dummyMoveall, 'moveall':self.moveall, 'fkCtrlList':fkCtrlList,
                  'fkSysGrp': fkSysGrp, 'fkJntGrp': fkJntGrp, 'fkCtrlGrpSys': fkCtrlSysGrp, 'twkDummyGrp': twkDummyGrp,
                  'fkJntList': fkJntList, 'fkDummyCtrlList': fkDummyCtrlList, 'fkDummyTwkList': fkDummyTwkList,
                  'fkNodesList': fkNodesList}

        logger.debug('# Fim do doFK')
        om.MGlobal.displayInfo('# Success! Sitema FK de ' + str(self.name) + ' foi criado.\n')
        return fkList

    def doIk(self):
        logger.debug('doIK: Criando sistema IK')

        self.getDict()
        self.exportDict()
        ikList = {}


        ikPrefix = self.name + '_ik'

        self.ikCtrlGrp = groupTools.makeGroup(name=ikPrefix + '_ctrl', parent=self.moveall)
        ikSysGrp = groupTools.makeGroup(name=ikPrefix + '_sys')
        ikParentGrp = groupTools.makeGroup(name=ikPrefix + '_parent', parent=ikSysGrp)
        ikMoveallParentGrpZero = groupTools.makeGroup(name=ikPrefix + '_moveall_parent', parent=ikParentGrp,
                                                        coords=(self.chainMap[0][0], self.chainMap[0][1], (1, 1, 1)))

        ikMoveallParentGrp = groupTools.makeGroup(name=ikPrefix + '_moveall_parent', parent=ikMoveallParentGrpZero,
                                                    coords=(self.chainMap[0][0], self.chainMap[0][1], (1, 1, 1)))

        ikCtrlGrpSys = groupTools.makeGroup(name=ikPrefix + '_ctrl_sys', parent=ikMoveallParentGrp)
        ikJntGrp = groupTools.makeGroup(name=ikPrefix + self.jxtSuffix, parent=ikMoveallParentGrp)

        pm.parentConstraint(self.toParentDrv, ikParentGrp, mo=1)
        pm.scaleConstraint(self.toParentDrv, ikParentGrp, mo=1)

        self.moveall.translate >> ikMoveallParentGrp.translate
        self.moveall.rotate >> ikMoveallParentGrp.rotate
        self.moveall.scale >> ikMoveallParentGrp.scale

        ikParentGrp.v.set(0)
        ikCtrlGrpSys.v.set(0)
        ikJntGrp.v.set(0)

        ikJntList = []
        ikDummyCtrlList = []
        ikCtrlList = []
        ikDummyTwkList = []
        ikNodesList = []

        # criando cadeia jnts ik:

        for jntNum in range(self.num-1):
            index = jntNum + 1

            jxtName = ikPrefix + str(index) + '_jxt'
            coordenate = (self.chainMap[jntNum][0], self.chainMap[jntNum][1], (1, 1, 1))
            jxt = jointTools.makeJoint(name=jxtName, connectToLast=True, coords=coordenate)

            pm.setAttr(jxt.name() + '.preferredAngle', self.preferredValues)

            ikJntList.append(dict({'jxt': jxt}))

            if jntNum == self.num - 2:
                # criando ikh:
                ikhName = jxtName + '_ikh'
                ikh = pm.ikHandle(name=ikhName ,sj=ikJntList[0]['jxt'], ee=ikJntList[-1]['jxt'])
                ikhGrp = groupTools.makeGroup(name=ikhName, coords=coordenate, parent=ikMoveallParentGrp)
                ikhParent = groupTools.makeGroup(name=ikhName, coords=coordenate, parent=ikhGrp)
                ikh[0].setParent(ikhParent)

                ikh[0].poleVectorX.set(0)
                ikh[0].poleVectorY.set(0)
                ikh[0].poleVectorZ.set(0)

                # criando ctrl:
                size = self.sysSize / 9.5
                ikCtrl = controlTools.cntrlCrv(name=ikPrefix, coords=coordenate, size=size,
                                               parent=self.ikCtrlGrp, **self.ctrlIkSetup)
                ikCtrlDummy = controlTools.cntrlCrv(name=ikPrefix, icone='null', coords=coordenate,
                                                    size= size, parent=ikCtrlGrpSys)

                ikCtrl.translate >>ikCtrlDummy.translate
                ikCtrl.rotate >> ikCtrlDummy.rotate
                ikCtrl.scale >> ikCtrlDummy.scale


                pm.addAttr(ikCtrl, ln='twist', k=1)

                ikCtrl.translate >> ikhParent.translate
                ikCtrl.rotate >> ikhParent.rotate
                ikCtrl.scale >> ikhParent.scale
                ikCtrl.twist >> ikh[0].twist

        print 'ikJntList'
        print ikJntList
        ikList = {'ikSysGrp': ikSysGrp, 'ikJntList':ikJntList}
        logger.debug('Fim da criacao do sistema IK')
        return ikList

    def doDyn(self):

        return ('sistema em construcao')

    ## ==================================================================================================

    def doRig(self):
        '''
        primeiro alimentamos o dicionario chainMap com as informacoes necessarias para construcao de qualquer chain.
        cada node contem uma tupple com translacao, uma de orientacao e uma booleana que registra se o node eh driver ou nao.
        Exemplo:
        chainMap = {'node1':((tx, ty, tz), (rx, ry, rz)), 'node2':((tx, ty, tz),(rx, ry, rz))... 'end':((tx, ty, tz), None)}
        :return:
        '''
        if self.fk or self.ik or self.dyn:
            try:
                pm.PyNode(self.globalParent['GUIDES']).v.set(0)
            except:
                logger.debug('Nao existe grupo GUIDES')

            logger.debug('doRig: Construindo o rig')
            self.getDict()
            self.updateChainMap()

            #print self.chainMap

            sysGrpName = self.name + '_NoMove'
            ctrlGrp = self.name + '_ctrl_zero_grp'
            moveallGrpName = self.toParentName + '_grp'

            if pm.objExists(sysGrpName):
                pm.delete(sysGrpName)

            if pm.objExists(moveallGrpName):
                moveallGrp = pm.PyNode(moveallGrpName)
                pm.delete(moveallGrp)

            self.ctrlGrp = groupTools.makeGroup(name=ctrlGrp, suffix='')

            # criando sistema de parentescos (MoveAll)
            coord = self.chainMap[0]
            coordenate = (coord[0], coord[1], (1, 1, 1))

            toParentLoc = controlTools.cntrlCrv(name=self.toParentName, icone='null', coords=coordenate,
                                                cntrlSulfix='')
            toParentLoc.getShape().v.set(0)

            self.ctrlGrp.setParent(toParentLoc)

            sysGrp = groupTools.makeGroup(name=sysGrpName, suffix='')

            toParentCtrlGrpZero = groupTools.makeGroup(name=self.toParentName + '_parent_zero',
                                                         coords=coordenate, parent=sysGrp, suffix='')

            self.toParentDrv = groupTools.makeGroup(name=self.toParentName + '_parent', coords=coordenate,
                                                     parent=toParentCtrlGrpZero)
            self.toParentDrv.getParent().v.set(0)

            toParentLoc.translate >> self.toParentDrv.translate
            toParentLoc.rotate >> self.toParentDrv.rotate
            toParentLoc.scale >> self.toParentDrv.scale



            # criando os jnts skinaveis do sistema:

            skinJntGrp = groupTools.makeGroup(name=self.name + '_skinJnt', parent=sysGrp)
            skinJntList = []
            for i, coord in enumerate(self.chainMap):
                if i < len(self.chainMap)-1: #enquanto nao for o node end

                    if i == 0:
                        self.baseCtrlGrp = groupTools.makeGroup(name=self.name + '_ctrl', parent=self.ctrlGrp)


                        dummyMoveall, dummyMoveallGrp = self.makeMoveall('_dummy', coord, self.toParentDrv)
                        moveall, moveallGrp = self.makeMoveall('', coord, self.baseCtrlGrp)

                        self.dummyMoveall = dummyMoveall
                        self.moveall = moveall

                        self.moveall.translate >> self.dummyMoveall.translate
                        self.moveall.rotate >> self.dummyMoveall.rotate
                        self.moveall.scale >> self.dummyMoveall.scale
                        self.moveall.fkStretch >> self.dummyMoveall.fkStretch

                        pm.addAttr(self.moveall, ln='skinJoints', dt='string')

                    index = str(i+1)

                    nextCoord = self.chainMap[i+1]

                    jointName = self.name + '_' + index + '_' + self.jntSuffix
                    jointEnd = self.name + '_' + index + '_end'
                    grpParent = self.name + '_' + index + '_zero'

                    zeroGrp = groupTools.makeGroup(name=grpParent, coords=(coord[0], coord[1], (1, 1, 1)))
                    skinJnt = jointTools.makeJoint(name=jointName, coords=(coord[0], coord[1], (1,1,1)),
                                                     connectToLast=True)

                    skinJntList.append(skinJnt)

                    endJnt = groupTools.makeJoint(name=jointEnd, coords=(nextCoord[0], nextCoord[1], (1, 1, 1)),
                                                    connectToLast=True)

                    zeroGrp.setParent(skinJntGrp)

                    self.skinJoints.append(skinJnt.name())

                skinJointsList = json.dumps(self.skinJoints)
                pm.setAttr(str(self.moveall.name())+'.skinJoints', skinJointsList)


            pass

            chainTypeList = []

            self.jntParentConstraintList = []
            self.jntScaleConstraintList = []
            parentConstraint = None
            scaleConstraint = None

            if self.fk:
                fkList = self.doFk()
                pm.parent(fkList['fkSysGrp'], sysGrp)
                chainTypeList.append('FK')
            if self.ik:
                ikList = self.doIk()
                pm.parent(ikList['ikSysGrp'], sysGrp)
                chainTypeList.append('IK')
            if self.dyn:
                dynList = self.doDyn()
                chainTypeList.append('Dyn')

            for e, jnt in enumerate(skinJntList):
                if self.fk:
                    fkJnt = fkList['fkJntList'][e]
                    parentConstraint = pm.parentConstraint(fkJnt['jxt'], jnt)
                    scaleConstraint = pm.scaleConstraint(fkJnt['jxt'], jnt)


                if self.ik:
                    ikJnt = ikList['ikJntList'][e]
                    parentConstraint = pm.parentConstraint(ikJnt['jxt'], jnt)
                    scaleConstraint = pm.scaleConstraint(ikJnt['jxt'], jnt)

                if self.dyn:
                    pass

                self.jntParentConstraintList.append(parentConstraint)
                self.jntScaleConstraintList.append(scaleConstraint)

            if len(chainTypeList) > 1:
                logger.debug('#### fazendo blend entre constraints')
                enumName = ''
                conditionNodeList = []
                for i, type in enumerate(chainTypeList):

                    if i == 0:
                        add=''
                    else:
                        add=':'
                    enumName += add+type

                    conditionName = self.name + '_' + type + '_cnd'
                    condition = pm.createNode('condition', name=conditionName)
                    conditionNodeList.append(condition)
                    condition.secondTerm.set(i)
                    condition.colorIfTrueR.set(1)
                    condition.colorIfFalseR.set(0)

                pm.addAttr(self.moveall, ln='driverType', at='enum', enumName=enumName, k=1)

                for i, type in enumerate(chainTypeList):
                    chainList = None
                    if type == 'FK':
                        conditionNodeList[i].outColorR >> self.fkTwkGrp.v
                        conditionNodeList[i].outColorR >> fkList['fkCtrlList'][0]['ctrl_grp'].v

                    elif type == 'IK':
                        conditionNodeList[i].outColorR >> self.ikCtrlGrp.v

                    elif type == 'Dyn:':
                        conditionNodeList[i].outColorR >> self.sysCtrlGrp.v

                    for e in range(self.num-2):
                        if type == 'FK':
                            chainList = fkList['fkJntList'][e]['jxt']

                        elif type == 'IK':
                            chainList = ikList['ikJntList'][e]['jxt']

                        elif type == 'Dyn:':
                            chainList = dynList['dynJntList'][e]['jxt']


                        self.moveall.driverType >> conditionNodeList[i].firstTerm
                        conditionNodeList[i].outColorR >> \
                        pm.general.Attribute(self.jntParentConstraintList[e].name() + '.' + chainList + 'W'+str(i))

                        conditionNodeList[i].outColorR >> \
                        pm.general.Attribute(self.jntScaleConstraintList[e].name() + '.' + chainList + 'W'+str(i))


                pass

            logger.debug('# Fim do doRig')
            pm.select(self.moveall)

        else:
            pm.warning('Selecione ao menos um tipo de construcao: FK, IK e/ou DYN')



## ==================================================================================================
## //////////////////////////////////////////// THE END /////////////////// Flavio Castello * 2019 //
## ==================================================================================================


'''
m = MasterChain(name='chain', fkInterval=2, num=5, axis='X', jntSuffix='jxt', fk=True, ik=True)
m = MasterChain(name='chain2', num=3, axis='X', driverMap={'node1': True, 'node2': False, 'node3': True})

m = MasterChain(name='chain3', 
                guideDict= 
                {0: ((5, 5, 5), (45,45,45), (1,1,1)), 
                 1: ((6,6,6), 10), 
                 2: ((4, 3, 2), 20), 
                 3: ((1, 0, 1), 30), 
                 4: ((2, 3, 4), 40)})

m.doGuide()
m.getDict()
m.getDict(axis='Y', jntSuffix='jnt') # < eh possivel alterar configuracoes do guide mesmo atualizando com base na cena
m.doRig()

______________________________________ Duplicate ou Mirror Chain:

r = MasterChain (name='chain_mirror')

r.doGuide()
--------------------------- ou
r.duplicateGuide(m)
--------------------------- ou
r.mirrorConnectGuide(m)

r.getDict()
r.doRig()






'''

#########
# TO-DO:
# Refinar guide por selecao
# Add auto parent por selecao

# add squash para ik




