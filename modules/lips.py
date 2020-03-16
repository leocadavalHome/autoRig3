# flip versao scale
import pymel.core as pm
import autoRig3.tools.matrixTools as matrixTools
import autoRig3.tools.attachTools as attatchTools
import autoRig3.tools.jointTools as jointTools
import autoRig3.tools.groupTools as groupTools
import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.vertexWalkTools as vtxWalking
import autoRig3.tools.skinTools as skinTools
import maya.api.OpenMaya as om

reload(vtxWalking)

import logging

logger = logging.getLogger(__name__)
logger.setLevel(10)
import json

class Lips:
    ''''
    Cria uma ribbon reta ou circular
    '''

    def __init__(self, name='lips', width=10, type='circle', drivers=3, rbbnJnts=18, spansPerDriver=3):
        '''
        :param drivers = Quantos drivers para cada quadrante, entre entre os polos. (Garantindo que vamos ter simetria)
        :param rbbnJnts = Skin jnts levados pela rbbn. Se tiver edge loop selecionado a var. sera o num. de vtx do loop
        :param guideDict = para cada ctrl do guide, extraimos somente translacao e para guide locs extraimos uma tupple
                           com ((tx,ty,tz), slidePosition)
        '''
        self.selection = []
        self.name = name
        self.width = width
        self.type = type
        self.drivers = (drivers * 4) + 4
        self.spansPerDriver = spansPerDriver

        self.structureSections = self.drivers * self.spansPerDriver
        self.guideSections = float(self.drivers)

        self.locDrvList = []  # lista de locators que servem de base para construcao da ribbon
        self.skinPvtLocList = []  # lista dos locators pivos de rotacao
        self.skinLocList = []
        self.mainLocDrvList = []
        self.mainSkinPvtLocList = []
        self.mainSkinLocList = []
        self.guideMoveall = None

        self.mainCurveGuide = None
        self.rollCurveGuide = None
        self.transJnts = []
        self.scaleJnts = []
        self.toExport = ['name', 'type', 'drivers', 'spansPerDriver', 'locDrvList', 'skinLocList', 'skinPvtLocList',
                         'mainLocDrvList', 'mainCurveGuide', 'rollCurveGuide', 'structureSections', 'selection',
                         'drvCtrlList', 'rbbnJntsCoordList', 'sysSize', 'mainCtrlsGuide', 'rollCtrlsGuide']

        self.toExportRig = ['name', 'skinJnts', 'drvJntList', 'drvCtrlList']

        self.guideSufix = '_guide'
        self.moveallGuideSetup = {'nameTempl': self.name + '_moveall' + self.guideSufix}
        self.moveallPvtGuideSetup = {'nameTempl': self.name + '_moveallPvt' + self.guideSufix}

        self.guideDict = {'moveall': None, 'moveallPvt': None, 'guideCtrls': {}, 'guidePvtCtrls': {},
                          'structureGuide': {}, 'skinGuide': {}, 'skinPvtGuide': {}}

        self.slidePosition = 'slidePosition'
        self.mainCtrlsGuide = []
        self.rollCtrlsGuide = []

        # exclusive doRig:
        self.moveall = None
        self.rbbnJnts = rbbnJnts
        self.rbbnJntsCoordList = []  # coordenadas das jnts presas na ribbon

        self.mainPos = []  # essa lista recebe quatro itens, os index da posicao top, l_corner, lw e r_corner

        self.globalPrefix = {'middle': 'MD_', 'left': 'L_', 'right': 'R_', 'up': 'UP_', 'lower': 'LW_',
                             'corner': 'CORNER_'}
        self.globalParent = {'GUIDES': 'facial_guides_grp', 'DATA': 'DATA', 'globalMoveall': 'characterMoveall_ctrl'}

        self.skinJnts = []
        self.drvJntList = []
        self.drvCtrlList = []

        self.sysSize = 1
        # comecando do superior da direita em sentido horario

    def getTransform(self, var):
        if isinstance(var, list):
            transform = pm.ls(var, type='transform')[0]
        else:
            transform = var

        return transform

    def exportDict(self, moveall=None, **kwargs):
        '''
        formato do guideInstance = 'teste_moveall_guide' (unicode)

        Esse metodo exporta para o atributo ribbonDict no moveall um dicionario com tudo o que eh necessario
        para reconstruir a ribbon com base nas keys na variavel self.toExport
        '''

        logger.debug('exportando dicionario')
        logger.debug('exportando dicionario da ribbon ' + self.guideMoveall)
        #print '>>>>> ', self.skinJnts
        expDict = {}

        self.__dict__.update(**kwargs)
        toExport = self.toExportRig

        if not moveall:
            toExport = self.toExport
            moveall = pm.PyNode(self.guideMoveall)

        for key in toExport:
            expDict[key] = self.__dict__[key]

        dictString = json.dumps(expDict)
        moveall.ribbonDict.set(dictString)

        return expDict

    def getDict(self, guideInstance=None):
        '''
        aqui trazemos para a classe o dicionario guardado no dicionario json atualizado

        # formato do guideInstance = 'ribbon_moveall_guide'
        # caso nao tenha guideInstance o metodo procura o moveall no self
        '''
        # self.guideMoveall = pm.PyNode(ctrlName)
        logger.debug('getDict: ')

        ribbonDictRestored = {}

        if not guideInstance:
            try:
                self.guideMoveall = pm.PyNode(self.moveallGuideSetup['nameTempl'])
            except:
                #print 'Nao existe o guide na cena. Criando...'
                self.doGuide()
        else:
            self.guideMoveall = guideInstance

        try:
            guideInstance = self.guideMoveall

        except:
            logger.error('nao foi possivel identificar o moveall de self')

        try:
            guideInstance = pm.PyNode(guideInstance)

            jsonDict = guideInstance.ribbonDict.get()

            ribbonDictRestored = json.loads(jsonDict)

        except:
            logger.error('nao foi possivel acessar o attr ribbonDict')

        self.__dict__.update(**ribbonDictRestored)

        logger.debug('pegando informacoes de posicionamento do guide')

        self.guideDict['moveall'] = tuple([pm.xform(self.moveallGuideSetup['nameTempl'], q=1, rp=1, ws=1),
                                           pm.xform(self.moveallGuideSetup['nameTempl'], q=1, ro=1, ws=1),
                                           pm.xform(self.moveallGuideSetup['nameTempl'], q=1, s=1, r=1)])

        self.guideDict['moveallPvt'] = tuple([pm.xform(self.moveallPvtGuideSetup['nameTempl'], q=1, rp=1, ws=1),
                                              pm.xform(self.moveallPvtGuideSetup['nameTempl'], q=1, ro=1, ws=1),
                                              pm.xform(self.moveallPvtGuideSetup['nameTempl'], q=1, s=1, r=1)])

        for index, key in enumerate(['guideCtrls', 'guidePvtCtrls', 'structureGuide', 'skinGuide', 'skinPvtGuide']):
            currentList = [self.mainCtrlsGuide,
                           self.rollCtrlsGuide,
                           self.mainLocDrvList,
                           self.mainSkinPvtLocList,
                           self.mainSkinLocList]
            for each in currentList[index]:
                if index <= 1:
                    self.guideDict[key][each] = pm.xform(each, q=1, rp=1, ws=1)
                else:
                    self.guideDict[key][each] = (
                    pm.xform(each, q=1, rp=1, ws=1), pm.getAttr(each + '.' + self.slidePosition))
        #print self.guideDict
        return ribbonDictRestored

    def createMotionPath(self, object, curve, uValue, fractionMode=False):
        #print '>>>>>>', object, curve, uValue
        logger.debug('criando motion path')

        motionPath = pm.pathAnimation(object, curve, follow=1)
        PyMotionPath = pm.PyNode(motionPath)
        #print 'criado ', PyMotionPath
        animNode = pm.listConnections(motionPath, t='animCurve')
        pm.delete(animNode)
        PyMotionPath.fractionMode.set(fractionMode)
        # PyMotionPath.uValue.set(uValue)
        #print 'fim do motionPath'

        return PyMotionPath

    def locsOnCurve(self, type, baseName, locAmount, locList, mainLocList, curve, parent, color, curveRange=None,
                    putOnParams=[], putOnCoords=[]):
        '''
        :param type: (str) 'structure', 'skinDrv' ou 'guideBase'
        :param baseName:
        :param locAmount: quantos jnts vao estar presos na rbbn
        :param locList:
        :param mainLocList:
        :param curve:
        :param parent:
        :param color: cor do main loc
        :param putOnParams: especificamos aqui os parametros exatos dos motioPaths
        :param putOnCoords: especificamos aqui as coordenadas exatas onde queremos que os locators sejam criados
        :return:

        especificando putOnParams e putOnCoords conseguimos que tanto parametros
        quanto coordenadas juntos posicionem os locatos do guide o mais proximo
        dos vertices da mesh, no caso de usarmos como base a selecao
        '''
        logger.debug('locsOnCurve()')
        # conexao simetrica para os locators

        offset = 0
        index = 0
        driver = 0

        if type == 'guideBase':
            offset = curveRange / float(locAmount)
        else:
            offset = self.drivers / float(locAmount)
        # #print '-------------------------------drivers =', self.drivers
        # #print '-------------------------------locAmount =', locAmount

        while index < locAmount:
            #print locAmount, 'locAmout while ', index
            if type == 'structure':
                module = index % self.spansPerDriver
            else:
                module = 0

            if putOnParams:
                pathOffset = putOnParams[index]
            else:
                pathOffset = index * float(offset)

            #print '======================== pathOffset: ', pathOffset, ' - index (', index, ') x offset (', offset, ')'

            locName = self.name + '_' + baseName + '_curve' + str(index) + self.guideSufix

            loc = controlTools.cntrlCrv(name=locName, icone='null', color=(.6,.6,.6), cntrlSulfix='_loc')
            pm.addAttr(loc, ln=self.slidePosition, k=1)
            locShape = loc.getShape()
            locList.append(str(loc))

            loc.getParent().setParent(parent)

            motionPath = self.createMotionPath(loc.getParent(), curve, pathOffset)

            if module == 0:  # mainLoc
                #print 'mainLoc settings'
                mainLocList.append(str(loc))
                driver += 1
                if baseName == 'rotPivot':
                    loc.getShape().overrideColorRGB.set((.5, .5, .7))
                    locShape.localScaleX.set(vtxWalking.bbox(curve)['height'] / 25)
                    locShape.localScaleY.set(vtxWalking.bbox(curve)['height'] / 25)
                    locShape.localScaleZ.set(vtxWalking.bbox(curve)['height'] / 25)
                else:
                    loc.getShape().overrideColorRGB.set(color)
                    locShape.localScaleX.set(vtxWalking.bbox(curve)['height'] / 5)
                    locShape.localScaleY.set(vtxWalking.bbox(curve)['height'] / 5)
                    locShape.localScaleZ.set(vtxWalking.bbox(curve)['height'] / 5)
            else:
                #print 'secondary settings'
                # secondaryLoc
                locShape.localScaleX.set(vtxWalking.bbox(curve)['height'] / 10)
                locShape.localScaleY.set(vtxWalking.bbox(curve)['height'] / 10)
                locShape.localScaleZ.set(vtxWalking.bbox(curve)['height'] / 10)

            # sliding Attr:
            pm.setAttr(loc + '.' + self.slidePosition, (pathOffset))
            pm.connectAttr(loc + '.' + self.slidePosition,  motionPath + '.uValue')

            if putOnCoords:
                pm.xform(loc, t=putOnCoords[index], ws=1)

            index += 1
        #print 'secondary sliding attr'
        # secondary sliding Attr:
        if type == 'structure':
            for i, mainLoc in enumerate(mainLocList):
                prevDriver = pm.PyNode(mainLoc)

                if i < len(mainLocList) - 1:
                    nextDriver = pm.PyNode(mainLocList[i + 1])
                else:
                    nextDriver = pm.PyNode(mainLocList[0])

                # #print '>> ', prevDriver, nextDriver

                offset = (float(1) / self.spansPerDriver)

                for secIndex in range(self.spansPerDriver)[:-1]:

                    #print ' // - // - // - // - // - // - // - // - // - // - // - // - // - // - // - // - '
                    #print locList
                    #print i
                    #print self.spansPerDriver
                    #print i * self.spansPerDriver
                    #print secIndex
                    #print secIndex + 1
                    #print (i * self.spansPerDriver) + (secIndex + 1)
                    #print locList[(i * self.spansPerDriver) + (secIndex + 1)]
                    #print ' // - // - // - // - // - // - // - // - // - // - // - // - // - // - // - // - '

                    currentSecondary = pm.PyNode(locList[(i * self.spansPerDriver) + (secIndex + 1)])

                    currentValue = 1 - (offset * (secIndex + 1))

                    # #print currentSecondary, currentValue

                    blenderNodeName = self.name + '_' + str(i) + '_' + str(secIndex) + '_blend'
                    blenderNode = pm.shadingNode('blendColors', n=blenderNodeName, asUtility=True)

                    blenderNode.blender.set(currentValue)
                    prevDriver.slidePosition >> blenderNode.color1R
                    nextDriver.slidePosition >> blenderNode.color2R
                    blenderNode.outputR >> currentSecondary.slidePosition

                    if i == len(mainLocList) - 1:
                        addOffsetNodeName = self.name + '_' + str(i) + '_' + str(secIndex) + '_add'
                        addOffsetNode = pm.createNode('addDoubleLinear', n=addOffsetNodeName)

                        nextDriver.slidePosition >> addOffsetNode.input1
                        addOffsetNode.input2.set(self.drivers)
                        addOffsetNode.output >> blenderNode.color2R

        #print 'if != guideBase'
        if type != 'guideBase':
            connectionList = []
            # lista com os locators que fazem conexao de simetria [l,r]
            for i, loc in enumerate(locList[1:(len(locList) / 2)]):
                index = i + 1
                # #print '> > > > > > > > ', i, loc, locList[-index]

                # invertendo o mirror dos jnts ao lado dos extremos top e bttm:
                dirSlide = -1

                input = pm.PyNode(locList[-index])
                output = pm.PyNode(loc)

                connectionList.append([loc, locList[-index]])
                mirror_normalizaNodeName = loc + '_normal_adl'
                mirror_inverseNodeName = loc + '_inverse_adl'
                mirror_addNodeName = loc + '_add_adl'

                mirror_normalizaNode = pm.createNode('addDoubleLinear', n=mirror_normalizaNodeName)
                mirror_inverseNode = pm.createNode('multDoubleLinear', n=mirror_inverseNodeName)
                mirror_addNode = pm.createNode('addDoubleLinear', n=mirror_addNodeName)

                output.slidePosition >> mirror_normalizaNode.input1
                mirror_normalizaNode.input2.set(output.slidePosition.get() * -1)

                mirror_normalizaNode.output >> mirror_inverseNode.input1
                mirror_inverseNode.input2.set(dirSlide)

                mirror_inverseNode.output >> mirror_addNode.input1
                mirror_addNode.input2.set(input.slidePosition.get())

                mirror_addNode.output >> input.slidePosition

                mirror_rotationMdName = loc + '_rotation_mirror_md'
                mirror_rotationMd = pm.createNode('multiplyDivide', n=mirror_rotationMdName)

                mirror_positionMdName = loc + '_position_mirror_md'
                mirror_positionMd = pm.createNode('multiplyDivide', n=mirror_positionMdName)

                output.translate >> mirror_positionMd.input1
                mirror_positionMd.input2.set(1,-1,1)
                mirror_positionMd.output >> input.translate

                output.rotate >> mirror_rotationMd.input1
                mirror_rotationMd.input2.set(-1,1,-1)
                mirror_rotationMd.output >> input.rotate

        #print 'fim do locsOnCurve()'
        return locList

    def ctrlsToCurve(self, name, curveNode, parentCtrls, parentClusters, size):
        ctrlDict = {}
        ctrlList = []

        curveNode = self.getTransform(curveNode)
        try:
            curveNode = pm.PyNode(curveNode)
        except:
            pm.warning(str(curveNode) + 'nao eh um objeto Valido')

        curvePoints = len(curveNode.cv)
        for e, cv in enumerate(curveNode.cv):
            if e > 0:
                index = e
                strIndex = str(e)

            else:
                index = curvePoints
                strIndex = str(index)

            ctrlName = self.name + '_' + name + '_' + strIndex.zfill(2) + '_ctrl' + self.guideSufix
            clusterName = pm.PyNode(cv).getParent() + '_clus_' + name + '_' + strIndex.zfill(2) + self.guideSufix

            cluster = pm.cluster(cv, n=clusterName)[1]
            cluster.setParent(parentClusters)
            position = pm.xform(cluster, q=1, rp=1, ws=1)

            if name == 'pvt_drv':
                color = (0, 1, 0)
            else:
                color = (1, 1, 0)
            ctrl = controlTools.cntrlCrv(name=ctrlName, parent=parentCtrls, color=color,
                                         coords=(position, (0, 0, 0), (1, 1, 1)), size=size,
                                         lockChannels=['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

            ctrlDict.update({index: ctrl})
            ctrlList.append(str(ctrl.name()))
            pm.pointConstraint(ctrl, cluster, mo=1)

        # conexao de simetrias:
        for i in range(curvePoints):

            if i > 1 and i < curvePoints / 2 + 1:
                revIndex = (curvePoints + 2) - i

                target = ctrlDict[revIndex]

                pySource = pm.PyNode(ctrlDict[i])
                pyTarget = pm.PyNode(target)

                ctrlParent = pm.PyNode(target).getParent()
                ctrlParent.scaleX.set(ctrlParent.scaleX.get() * -1)
                pySource.translate >> pyTarget.translate

                # cores de L e R:
                L_ctrlShape = pySource.getShape()
                R_ctrlShape = pyTarget.getShape()


                if name == 'pvt_drv':
                    L_ctrlShape.overrideColorRGB.set(.45, .45, 1)
                    R_ctrlShape.overrideColorRGB.set(.9, .3, .3)
                else:
                    L_ctrlShape.overrideColorRGB.set(.15, .15, .9)
                    R_ctrlShape.overrideColorRGB.set(.7, .05, .05)

        return ctrlList

    def makeCurveByCoords(self, name, coordList):
        logger.debug('makeCurveByCoords')

        knots = []
        for i in range(
                len(coordList) + 3 + 2):  # numero de pontos + 3 para periodic + 2 pela regra de knots
            index = i - 2
            knots.append(index)

        curve = pm.curve(n=name, per=1,
                         p=[coordList[-1]] +
                           coordList +
                           [coordList[0]] +
                           [coordList[1]],
                         k=knots)
        #print 'fim da makeCurveByCoords'
        return curve

    def guideBySelection(self, name, sections, parent):
        logger.debug('guideBySelection')
        walkingInfo = vtxWalking.vtxWalking()
        curveByVtxName = name + '_temp'
        curveByVtx = self.makeCurveByCoords(name=curveByVtxName, coordList=walkingInfo['vtxCoordList'])

        # criando locators na curva original para serem base de coordenadas para construcao da curva final
        # contruindo uma curva usando os vertices do edge loop como base:
        baseName = 'guideBase'
        guideBaseGrp = groupTools.makeGroup(name=baseName)
        locList = []
        mainLocList = []

        locDistributedList = []

        locDistributedList = self.locsOnCurve('guideBase', baseName, sections, locList, mainLocList, curveByVtx,
                                              guideBaseGrp, (.5, .1, .1), curveRange=len(walkingInfo['vtxCoordList']))

        # construindo a curva guide final (com a qt de cvs = qt de drivers)
        coordsByLocdrivers = []
        for i in locDistributedList:
            #print 'construindo a curva. Coord ',i
            coordsByLocdrivers.append(pm.xform(i, q=1, rp=1, ws=1))
        curveByVtxName = name
        mainCurve = self.makeCurveByCoords(name=curveByVtxName, coordList=coordsByLocdrivers)
        #print 'curva ok'
        # excluindo curva criada com base nos vertices e os locs nela (base dos drivers):
        pm.delete(curveByVtx, guideBaseGrp)

        mainCurve.setParent(parent)
        toReturn = {'curve': mainCurve}
        toReturn.update(walkingInfo)
        #print 'fim da GuideBySelection'
        return toReturn

    def returnClosestPointOnCurve(self, coords=[], curve=None, objList=[]):
        '''
        :param coords: [(x,y,z),(x,y,z)]
        :param objList: lista de objetos a serem extraidas as coordenadas. Essa lista sobrepoe a de coordenadas
        :param curve: curva base
        :return:
        '''
        curve = self.getTransform(curve)
        #print '=============================== curve: ', curve

        if objList:
            coords = []
            for obj in objList:
                coord = pm.xform(obj, q=1, rp=1, ws=1)
                coords.append(coord)

        paramList = []

        reader = pm.createNode('nearestPointOnCurve', n='nearestPointOnCurve_reader')
        curve.getShape().local >> reader.inputCurve

        for coord in coords:
            reader.inPosition.set(coord)
            paramList.append(reader.result.parameter.get())

        pm.delete(reader)

        #print paramList
        return paramList

    def doGuide(self, edges=None):
        if not edges:
            edges = pm.ls(sl=1, fl=True)

        self.edgeLoop = edges

        try:
            if not self.selection:
                for item in edges:
                    if isinstance(item, pm.general.MeshEdge):
                        self.selection.append(str(item.name()))

        except:
            pm.warning('sem selecao')

        rbbnGrpName = self.name + 'Guide_grp'

        if pm.objExists(rbbnGrpName):
            pm.delete(rbbnGrpName)

        guideGrp = self.globalParent['GUIDES']

        if not pm.objExists(guideGrp):
            logger.error('guide grp nao existe')
            pm.group(n=guideGrp, em=1)

        pm.PyNode(guideGrp).visibility.set(1)

        if self.moveall:
            pm.PyNode(self.moveall).visibility.set(0)

        rbbnCurvesGrpName = self.name + '_curves' + self.guideSufix
        clusterGrpGuideName = self.name + '_cluster' + self.guideSufix
        moveallGuideName = self.moveallGuideSetup['nameTempl']
        moveallPvtGuideName = self.moveallPvtGuideSetup['nameTempl']
        curveGuideGrpName = self.name + '_refCurve' + self.guideSufix

        rbbnGrp = groupTools.makeGroup(name=rbbnGrpName, parent=guideGrp, suffix='')
        rbbnCurvesGrp = groupTools.makeGroup(name=rbbnCurvesGrpName, parent=rbbnGrp)
        clusterGrp = groupTools.makeGroup(name=clusterGrpGuideName, parent=rbbnGrp)
        clusterGrp.v.set(0)

        moveallGuide = controlTools.cntrlCrv(name=moveallGuideName, size=.7, icone='circuloZ', cntrlSulfix='',
                                             parent=rbbnGrp, color=(1, 1, 0), lockChannels=['v'])

        moveallPvtGuide = controlTools.cntrlCrv(name=moveallPvtGuideName, icone='quadradoZ', size=.3,
                                                parent=moveallGuide, color=(1, 1, 0), lockChannels=['v'],
                                                cntrlSulfix='')

        curveGuideGrp = groupTools.makeGroup(name=rbbnGrp, parent=rbbnGrp)

        self.guideMoveall = moveallGuide  # criar um ctrl moveall depois

        locGrpName = self.name + '_loc' + self.guideSufix
        structureGrpName = self.name + '_structure' + self.guideSufix
        skinDrvGrpName = self.name + '_skinDrv' + self.guideSufix

        curveGuideName = self.name + '_curve' + self.guideSufix
        curveRollGuideName = self.name + '_roll_curve' + self.guideSufix

        guideCtrlGrpName = self.name + '_ctrl' + self.guideSufix
        guidePvtCtrlGrpName = self.name + '_pvt_ctrl' + self.guideSufix

        locGrp = groupTools.makeGroup(name=locGrpName, parent=rbbnGrp)
        structureGrp = groupTools.makeGroup(name=structureGrpName, parent=locGrp)
        skinDrvGrp = groupTools.makeGroup(name=skinDrvGrpName, parent=locGrp)
        guideCtrlGrp = groupTools.makeGroup(name=guideCtrlGrpName, parent=moveallGuide)
        guidePvtCtrlGrp = groupTools.makeGroup(name=guidePvtCtrlGrpName, parent=moveallPvtGuide)

        pm.addAttr(self.guideMoveall, ln='ribbonDict', dt='string')
        pm.addAttr(self.guideMoveall, ln='structureGuide', max=1, min=0, k=1)
        pm.addAttr(self.guideMoveall, ln='skinGuide', max=1, min=0, k=1)
        pm.addAttr(self.guideMoveall, ln='guideCtrls', max=1, min=0, k=1, dv=1)

        self.guideMoveall.structureGuide >> structureGrp.v
        self.guideMoveall.skinGuide >> skinDrvGrp.v
        self.guideMoveall.guideCtrls >> guideCtrlGrp.v
        self.guideMoveall.guideCtrls >> guidePvtCtrlGrp.v

        vtxCoords = []
        #print 'fase1'
        if self.selection:  # caso tenhamos algo na selecao
            # #print selection
            pm.select(self.selection)

            guideBySelectionInfo = self.guideBySelection(curveGuideName, self.guideSections, rbbnCurvesGrp)
            curveGuide = guideBySelectionInfo['curve']
            vtxCoords = guideBySelectionInfo['vtxCoordList']
            self.rbbnJnts = len(vtxCoords)

            systemWidth = vtxWalking.bbox(curveGuide)['width']
            self.sysSize = systemWidth / 13.5

            pm.makeIdentity(curveGuide, a=True, t=True, r=True, s=True, n=False)

        else:  # caso contrario criamos uma curva default de guide
            curveGuide = pm.circle(n=curveGuideName)

            # #print 'curveGuide[1] para sections', curveGuide[1]

            curveGuide[0].setParent(rbbnCurvesGrp)

            curveGuide[1].radius.set(.5)
            curveGuide[1].sections.set(self.guideSections)
            curveGuide[0].scale.set(self.width, self.width, self.width)
            pm.reverseCurve(curveGuide[0], ch=False, replaceOriginal=True)
            pm.makeIdentity(curveGuide[0], a=True, t=True, r=True, s=True, n=False)
            curveGuide = curveGuide[0]
            self.sysSize = .5

        #print 'fase2'
        sysPvt = vtxWalking.bbox(curveGuide)['globalPvt']
        sysPvt = sysPvt[0], sysPvt[1], vtxWalking.bbox(curveGuide)['maxZ']
        curveGuide.rotatePivot.set(sysPvt)
        curveGuide.scalePivot.set(sysPvt)

        moveallGuide.getParent().translateX.set(sysPvt[0])
        moveallGuide.getParent().translateY.set(sysPvt[1])
        moveallGuide.getParent().translateZ.set(sysPvt[2] + (self.sysSize * 5))

        moveallGuide.setScale((self.sysSize * 3, self.sysSize * 3, self.sysSize * 3))

        pm.makeIdentity(moveallGuide, a=True, t=True, r=True, s=True, n=False)
        pm.makeIdentity(moveallPvtGuide, a=True, t=True, r=True, s=True, n=False)

        self.mainCurveGuide = str(self.getTransform(curveGuide))
        # criando guide base para os jnts roll:

        curveRollGuide = pm.duplicate(curveGuide, n=curveRollGuideName)
        self.rollCurveGuide = str(curveRollGuide[0])

        if self.selection:
            pm.xform(curveRollGuide, s=(1.2, 5, 1.7))
        else:
            pm.xform(curveRollGuide, s=(1.5, 1.5, 1))

        pm.makeIdentity(curveRollGuide, a=True, t=True, r=True, s=True, n=False)

        # pm.blendShape(curveGuide[0], curveRollGuide[0], n=curveGuideBs, w=(0, 1.0))

        # criando os controles para cada cv do guide

        obj = pm.PyNode(pm.ls(sl=1)[0])
        #print 'criando ctrls to curve'
        self.mainCtrlsGuide = self.ctrlsToCurve('drv', curveGuide, guideCtrlGrp, clusterGrp, (self.sysSize * .7))
        self.rollCtrlsGuide = self.ctrlsToCurve('pvt_drv', curveRollGuide, guidePvtCtrlGrp, clusterGrp,
                                                (self.sysSize * .7))
        curveGuide.template.set(1)
        curveRollGuide[0].template.set(1)

        # criando guide locators para os drivers

        self.locDrvList = []
        self.mainLocDrvList = []

        self.skinLocList = []
        self.mainSkinLocList = []

        self.skinPvtLocList = []
        self.mainSkinPvtLocList = []

        structureLocGuidelist = self.locsOnCurve(type='structure', baseName='main', locList=self.locDrvList,
                                                 locAmount=self.structureSections, mainLocList=self.mainLocDrvList,
                                                 curve=curveGuide, parent=structureGrp, color=(1, 0, 0))

        drvLocGuidelist = self.locsOnCurve(type='skinDrv', baseName='rotBasePivot', locList=self.skinLocList,
                                           locAmount=self.rbbnJnts, mainLocList=self.mainSkinLocList,
                                           curve=curveGuide, parent=skinDrvGrp, color=(0, 0.5, .5),
                                           putOnParams=self.returnClosestPointOnCurve(curve=curveGuide,
                                                                                      coords=vtxCoords),
                                           putOnCoords=vtxCoords)

        pvtDrvLocGuidelist = self.locsOnCurve(type='skinDrv', baseName='rotPivot', locList=self.skinPvtLocList,
                                              locAmount=self.rbbnJnts, mainLocList=self.mainSkinPvtLocList,
                                              curve=curveRollGuide, parent=skinDrvGrp, color=(0, 0.5, .5))

        for e, drv in enumerate(drvLocGuidelist):
            #print 'fase3'
            drvCoord = pm.xform(drv, q=1, rp=1, ws=1)
            pvtDrv = pvtDrvLocGuidelist[e]
            pvtDrvCoord = pm.xform(pvtDrv, q=1, rp=1, ws=1)

            curveName = drv + '_refCurve'
            refCurve = pm.curve(n=curveName, d=1, p=[drvCoord, pvtDrvCoord], ws=1)
            refCurve.getShape().template.set(1)
            refCurve.setParent(curveGuideGrp)
            for i, cv in enumerate(refCurve.cv):
                clusterName = curveName + '_' + str(e)
                clusterRef = pm.cluster(cv, n=clusterName)[1]
                clusterRef.visibility.set(0)

                if i == 0:
                    parentCluster = drv
                else:
                    parentCluster = pvtDrv

                clusterRef.setParent(parentCluster)

        # #print '>>>>>>>>>>>>>>>>>>>'
        # #print self.locDrvList
        # #print self.skinPvtLocList
        self.exportDict()
        pm.select(self.guideMoveall)

        # se houver informacoes no self.guideDict, aqui reposicinamos
        if self.guideDict['moveall']:
            pm.xform(self.guideMoveall, t=self.guideDict['moveall'][0], ws=1)
            pm.xform(self.guideMoveall, ro=self.guideDict['moveall'][1], ws=1)
            pm.xform(self.guideMoveall, s=self.guideDict['moveall'][2], ws=1)


        if self.guideDict['moveallPvt']:
            pm.xform(moveallPvtGuide, t=self.guideDict['moveallPvt'][0], ws=1)
            pm.xform(moveallPvtGuide, ro=self.guideDict['moveallPvt'][1], ws=1)
            pm.xform(moveallPvtGuide, s=self.guideDict['moveallPvt'][2], os=1)

        self.connectItens(self.guideDict['guideCtrls'])
        self.connectItens(self.guideDict['guidePvtCtrls'])
        self.connectItens(self.guideDict['structureGuide'], attr=True)
        self.connectItens(self.guideDict['skinGuide'], attr=True)
        self.connectItens(self.guideDict['skinPvtGuide'], attr=True)

        self.selection = []

        om.MGlobal.displayInfo('# Success! O Guide '+self.name+' foi gerado com sucesso.\n')


    def connectItens(self, dict, attr=False):

        if dict:
            for ctrl, value in dict.iteritems():
                try:
                    if attr:
                        pm.xform(ctrl, t=value[0], ws=1)
                        pm.setAttr(ctrl + '.slidePosition', value[1])
                    else:
                        pm.xform(ctrl, t=value, ws=1)
                except:
                    pm.warning('Nao foi possivel setar os valores para ' + ctrl)


    def rollScaleConnections(self, driverIndex, driverParam, driverParamNext, driver1, driver2,
                             drivenIndex, drivenParam, drivenJnt, **kwargs):

        upIndexList = kwargs.pop('upIndexList', [])
        lwIndexList = kwargs.pop('lwIndexList', [])
        rollAttrName = kwargs.pop('rollAttrName', '')
        ctrlUp = kwargs.pop('ctrlUp', '')
        ctrlLw = kwargs.pop('ctrlLw', '')

        rbbnJntTransList = kwargs.pop('rbbnJntTransList', [])
        rbbnJntRollList = kwargs.pop('rbbnJntRollList', [])
        rbbnJntSkinList = kwargs.pop('rbbnJntSkinList', [])

        masterRollDict = kwargs.pop('masterRollDict', {})

        if drivenIndex in upIndexList:
            masterDriver = ctrlUp + '.' + rollAttrName
            ctrlMaster = ctrlUp + '.scaleZ'
            upLw = '_' + self.globalPrefix['up']

        if drivenIndex in lwIndexList:
            masterDriver = ctrlLw + '.' + rollAttrName
            ctrlMaster = ctrlLw + '.scaleZ'
            upLw = '_' + self.globalPrefix['lower']

            # #print '- driven:', drivenParam, '  --  Drivers: ', driverParam, ' | ', driverParamNext
        blenderParam = (drivenParam - driverParam) / (driverParamNext - driverParam)

        # criando nodes de range para cada driven:
        blenderRollLocalNodeName = self.name + '_' + str(drivenIndex + 1) + '_roll_blend'
        blenderRollMasterNodeName = self.name + '_' + str(drivenIndex + 1) + '_roll_blend'
        blenderScaleLocalNodeName = self.name + '_' + str(drivenIndex + 1) + '_scale_blend'
        blenderScaleMasterNodeName = self.name + '_' + str(drivenIndex + 1) + '_scale_blend'
        addRollNodeName = self.name + '_' + str(drivenIndex + 1) + '_roll_add'
        mdRollMasterNodeName = self.name + '_' + str(drivenIndex + 1) + '_roll_md'
        addScaleNodeName = self.name + '_' + str(drivenIndex + 1) + '_scale_add'
        mdScaleMasterNodeName = self.name + '_' + str(drivenIndex + 1) + '_scale_md'
        mdRollNodeName = self.name + '_' + str(drivenIndex + 1) + '_eachRoll_md'

        blenderRollLocalNode = pm.shadingNode('blendColors', n=blenderRollLocalNodeName, asUtility=True)
        blenderRollMasterNode = pm.shadingNode('blendColors', n=blenderRollMasterNodeName, asUtility=True)
        blenderScaleLocalNode = pm.shadingNode('blendColors', n=blenderScaleLocalNodeName, asUtility=True)
        blenderScaleMasterNode = pm.shadingNode('blendColors', n=blenderScaleMasterNodeName, asUtility=True)

        addRollNode = pm.createNode('addDoubleLinear', n=addRollNodeName)
        mdRollMasterNode = pm.createNode('multDoubleLinear', n=mdRollMasterNodeName)
        addScaleNode = pm.createNode('addDoubleLinear', n=addScaleNodeName)
        mdScaleMasterNode = pm.createNode('multDoubleLinear', n=mdScaleMasterNodeName)

        jntTransDriven = pm.PyNode(rbbnJntTransList[drivenIndex])
        jntRollDriven = pm.PyNode(rbbnJntRollList[drivenIndex])
        jntScaleDriven = pm.PyNode(rbbnJntSkinList[drivenIndex])

        mdRollNode = pm.createNode('multDoubleLinear', n=mdRollNodeName)

        # atribuindo prefixo up ou lw aos jnts:

        jntName = jntTransDriven.nodeName()
        pm.rename(jntTransDriven,
                  (jntName.split('_', 1)[:-1][0]) + upLw + (jntName.split('_', 1)[1:][0])
                  )
        self.transJnts.append(jntTransDriven)
        jntName = jntScaleDriven.nodeName()
        pm.rename(jntScaleDriven,
                  (jntName.split('_', 1)[:-1][0]) + upLw + (jntName.split('_', 1)[1:][0])
                  )
        self.scaleJnts.append(jntScaleDriven)
        logger.debug('inicio das conexoes')

        blenderRollLocalNode.blender.set(blenderParam)

        pm.connectAttr(driver2 + '.' + rollAttrName, blenderRollLocalNode + '.color1R')
        pm.connectAttr(driver1 + '.' + rollAttrName, blenderRollLocalNode + '.color2R')

        # driver2.rotateX >> blenderRollLocalNode.color1R
        # driver1.rotateX >> blenderRollLocalNode.color2R

        blenderScaleLocalNode.blender.set(blenderParam)
        driver2.scaleZ >> blenderScaleLocalNode.color1R
        driver1.scaleZ >> blenderScaleLocalNode.color2R

        logger.debug('refinando inputs dos parametros do blend')
        # #print '>> Se tiver ',drivenIndex, ' no dicionario ', masterRollDict, '...'
        if drivenIndex in masterRollDict:
            masterParam = masterRollDict[drivenIndex][0]
            minMasterParam = masterRollDict[drivenIndex][1]
            maxMasterParam = masterRollDict[drivenIndex][2]

            masterBlendParam = ((masterParam - minMasterParam) / (maxMasterParam - minMasterParam)) * 2

            # revertendo o blend param depois que passa da metade do range
            if masterBlendParam > 1:
                p = masterBlendParam
                masterBlendParam = ((p - 1) / -1) + 1

            # #print masterParam, ' ____ ', minMasterParam, ', ', maxMasterParam
            # #print 'masterBlendParam', masterBlendParam

        else:
            masterBlendParam = 0

        logger.debug('fim do refinamento')

        blenderRollMasterNode.blender.set(masterBlendParam)
        pm.connectAttr(masterDriver, blenderRollMasterNode + '.color1R')

        blenderRollLocalNode.outputR >> mdRollNode.input1
        mdRollNode.input2.set(90)

        mdRollNode.output >> addRollNode.input1
        blenderRollMasterNode.outputR >> mdRollMasterNode.input1
        mdRollMasterNode.input2.set(90)
        mdRollMasterNode.output >> addRollNode.input2
        addRollNode.output >> jntRollDriven.rotateX

        blenderScaleMasterNode.blender.set(masterBlendParam)
        blenderScaleMasterNode.color2R.set(1)
        pm.connectAttr(ctrlMaster, blenderScaleMasterNode + '.color1R')

        blenderScaleLocalNode.outputR >> addScaleNode.input1
        blenderScaleMasterNode.outputR >> mdScaleMasterNode.input1
        mdScaleMasterNode.input2.set(1)
        mdScaleMasterNode.output >> addScaleNode.input2
        addScaleNode.output >> jntScaleDriven.scaleX
        addScaleNode.output >> jntScaleDriven.scaleY
        addScaleNode.output >> jntScaleDriven.scaleZ

    def doRig(self):
        pm.PyNode(self.globalParent['GUIDES']).visibility.set(0)
        logger.debug('doRig Function...')

        mainCoords = []

        if pm.objExists('head_contrained'):
            head_constrained_grp = 'head_contrained'
        else:
            head_constrained_grp = pm.group(n='head_contrained', em=True)

        self.moveall = self.name + '_sys'
        ctrlMoveallName = self.name + '_ctrl'

        if pm.objExists(self.moveall):
            pm.delete(self.moveall)

        if pm.objExists(ctrlMoveallName + '_grp'):
            pm.delete(ctrlMoveallName + '_grp')

        self.getDict()

        curveRbbnName = self.name + '_rbbnBase_curve'
        curve2RbbnName = self.name + '_rbbnDeph_curve'
        rbbnName = self.name + '_rbbn'

        moveallGrp = pm.group(n=self.moveall, em=1)

        curveCvcoords = []

        for index, loc in enumerate(self.locDrvList):

            PyLoc = pm.PyNode(loc)
            coord = tuple(pm.xform(PyLoc, rp=1, q=1, ws=1))

            curveCvcoords.append(coord)

            if loc in self.mainLocDrvList:
                mainCoords.append(coord)
            #print 'oficial:'
            #print '>>> ', loc
        for extraCv in range(3):
            #print 'extra:'
            #print '>>> ', self.locDrvList[extraCv]
            curveCvcoords.append(curveCvcoords[extraCv])

        knots = []
        for i in range(len(self.locDrvList) + 2 + 3):
            knots.append(i)

        # criando a ribbon:
        curveBaseRbbn = pm.curve(n=curveRbbnName, per=True, p=curveCvcoords, k=knots)
        pm.move(0, 0, self.sysSize * .5)
        curveBaseRbbn2 = pm.duplicate(curveBaseRbbn, n=curve2RbbnName)
        pm.move(0, 0, self.sysSize * -.5)

        bbLips = pm.exactWorldBoundingBox(curveBaseRbbn, curveBaseRbbn2)
        centerLipsPos = (((bbLips[3] + bbLips[0]) / 2), ((bbLips[4] + bbLips[1]) / 2), ((bbLips[5] + bbLips[2]) / 2))

        rbbn = pm.loft(curveBaseRbbn, curveBaseRbbn2[0], ch=False, ar=True, d=1, n=rbbnName)

        rbbnVRange = rbbn[0].getShape().minMaxRangeV.get()
        rbbnVSize = rbbnVRange[1] - rbbnVRange[0]

        pm.delete(curveBaseRbbn, curveBaseRbbn2)

        # orientInQuadrants = [(0,0,0), (180,0,0), (180,540,0), (0,180,0)]
        scaleInQuadrants = [(1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1)]
        # scaleInQuadrants = [(1,1,1),(1,1,1),(1,1,1),(1,1,1)]
        currentPartition = ''

        self.drvJntList = []
        drvJntList = []

        for e, eachCoord in enumerate(mainCoords):
            segmentNum = len(mainCoords) / 4
            mod = e % segmentNum

            if mod == 0:  # is current Main Position
                self.mainPos.append(e)

        # criando grupos de organizacao

        drvGrp = groupTools.makeGroup(name=self.name + '_drv', parent=moveallGrp,
                                        coords=(centerLipsPos, (0, 0, 0), (1, 1, 1)))
        jntDrvZeroGrp = groupTools.makeGroup(name=self.name + '_jnt_drv_zero', parent=drvGrp,
                                               coords=(centerLipsPos, (0, 0, 0), (1, 1, 1)))
        jntDrvGrp = groupTools.makeGroup(name=self.name + '_jnt_drv', parent=jntDrvZeroGrp,
                                           coords=(centerLipsPos, (0, 0, 0), (1, 1, 1)))

        ctrlDrvGrp = groupTools.makeGroup(name=self.name + '_ctrl_drv', parent=drvGrp)


        ctrlMoveall = controlTools.cntrlCrv(icone='circuloZ', name=ctrlMoveallName, color=(1, 1, 0),
                                            size=self.sysSize * 3, cntrlSulfix='',
                                            lockChannels=['v'], coords=(centerLipsPos, (0, 0, 0), (1, 1, 1)))

        driverCoordAttr = 'ribbonDict'

        pm.addAttr(ctrlMoveall.name(), ln=driverCoordAttr, dt='string')
        for cv in ctrlMoveall.cv:
            pm.move(cv, self.sysSize * 5, z=1, r=1, os=1)

        # pm.makeIdentity(ctrlMoveall, a=1, t=1)

        upZeroGrp = groupTools.makeGroup(name=self.name + '_offset_up_zero', parent=jntDrvGrp)
        upGrp = groupTools.makeGroup(name=self.name + '_offset_up', parent=upZeroGrp)

        lwZeroGrp = groupTools.makeGroup(name=self.name + '_offset_lw_zero', parent=jntDrvGrp)
        lwGrp = groupTools.makeGroup(name=self.name + '_offset_lw', parent=lwZeroGrp)

        drivenGrp = groupTools.makeGroup(name=self.name + '_driven', parent=moveallGrp)

        jntDrivenGrp = groupTools.makeGroup(name=self.name + '_jnt_driven', parent=drivenGrp)

        # criando ctrls principais:

        ctrlUpName = self.name + '_up'
        ctrlLwName = self.name + '_lw'

        rollAttrName = 'lipRoll'
        ctrlUp = controlTools.cntrlCrv(icone='retanguloZ', name=ctrlUpName, size=self.sysSize,
                                       color=(1, 1, 0), parent=ctrlMoveall, lockChannels=['v'])

        ctrlUp.addAttr(rollAttrName, at='float', k=1)
        ctrlLw = controlTools.cntrlCrv(icone='retanguloZ', name=ctrlLwName, size=self.sysSize,
                                       color=(1, 1, 0), parent=ctrlMoveall, lockChannels=['v'])

        ctrlLw.addAttr(rollAttrName, at='float', k=1)

        for cv in ctrlUp.cv:
            pm.move(cv, self.sysSize * 1, y=1, r=1, os=1)

        for cv in ctrlLw.cv:
            pm.move(cv, self.sysSize * 1, y=1, r=1, os=1)

        ctrlMoveall.translate >> jntDrvGrp.translate
        ctrlMoveall.rotate >> jntDrvGrp.rotate
        ctrlMoveall.scale >> jntDrvGrp.scale

        ctrlMoveall.rotate >> drivenGrp.rotate

        # ajustando coordenadas dos grupos principais up e lw
        for e, eachCoord in enumerate(mainCoords):
            if e == self.mainPos[0]:

                pm.xform(upZeroGrp, t=eachCoord, s=scaleInQuadrants[0], ro=(0, 0, 0), ws=1)
                pm.xform(ctrlUp.getParent(), t=eachCoord, s=scaleInQuadrants[0], ro=(0, 0, 0), ws=1)

            elif e == self.mainPos[2]:

                pm.xform(lwZeroGrp, t=eachCoord, s=scaleInQuadrants[2], ro=(0, 0, 0), ws=1)
                pm.xform(ctrlLw.getParent(), t=eachCoord, s=scaleInQuadrants[2], ro=(0, 0, 0), ws=1)

        self.drvCtrlList = []

        # criando itens drivers da ribbon
        for e, eachCoord in enumerate(mainCoords):
            index = str(e + 1)

            # separando os drivers em quadrantes:
            if (e >= self.mainPos[0]) and (e < self.mainPos[1] + 1):
                # currentQuadrantOrient = orientInQuadrants[0]
                currentQuadrantScale = scaleInQuadrants[0]

            elif (e > self.mainPos[1]) and (e < self.mainPos[2] + 1):
                # currentQuadrantOrient = orientInQuadrants[1]
                currentQuadrantScale = scaleInQuadrants[1]

            elif (e > self.mainPos[2]) and (e < self.mainPos[3]):
                # currentQuadrantOrient = orientInQuadrants[2]
                currentQuadrantScale = scaleInQuadrants[2]

            elif (e >= self.mainPos[3]):
                # currentQuadrantOrient = orientInQuadrants[3]
                currentQuadrantScale = scaleInQuadrants[3]

            # separando drivers em up, lw, ou corners:
            if (e < self.mainPos[1]) or (e > self.mainPos[3]):
                currentPartition = self.globalPrefix['up']
                partitionJntGroup = upGrp
                partitionCtrlGroup = ctrlUp
                ctrlColor = (0, 0.588, 1)

            elif (e > self.mainPos[1]) and (e < self.mainPos[3]):
                currentPartition = self.globalPrefix['lower']
                partitionJntGroup = lwGrp
                partitionCtrlGroup = ctrlLw
                ctrlColor = (.978, .404, .278)

            elif e == self.mainPos[1]:
                currentPartition = self.globalPrefix['corner']
                partitionJntGroup = jntDrvGrp
                partitionCtrlGroup = ctrlMoveall
                ctrlColor = (0, 0, 1)

            elif e == self.mainPos[3]:
                currentPartition = self.globalPrefix['corner']
                partitionJntGroup = jntDrvGrp
                partitionCtrlGroup = ctrlMoveall
                ctrlColor = (1, 0, 0)

            if e == self.mainPos[0] or e == self.mainPos[2]:
                ctrlColor = (1, 1, 0)

            drvlocName = currentPartition + self.name + '_drv_' + index + '_offset'
            drvJntZeroName = currentPartition + self.name + '_drv_' + index + '_zero'
            drvJntName = currentPartition + self.name + '_drv_' + index + '_jxt'
            ctrlParentGrpName = currentPartition + self.name + '_drv_' + index + '_parent'
            ctrlParentZeroGrpName = currentPartition + self.name + '_drv_' + index + '_zero'

            locGrp = controlTools.cntrlCrv(icone='null', cntrlSulfix='_loc', name=drvlocName,
                                           coords=(eachCoord, (0, 0, 0), (1, 1, 1)))

            ctrlParentZeroGrp = groupTools.makeGroup(name= ctrlParentZeroGrpName,
                                         coords=(eachCoord, (0, 0, 0), currentQuadrantScale))

            ctrlParentGrp = groupTools.makeGroup(name= ctrlParentGrpName, parent=ctrlParentZeroGrp,
                                         coords=(eachCoord, (0, 0, 0), currentQuadrantScale))

            ctrl = controlTools.cntrlCrv(icone='cubo', name=drvlocName, lockChannels=['rx', 'ry', 'v'],
                                         size=self.sysSize * .7,
                                         coords=(eachCoord, (0, 0, 0), currentQuadrantScale), color=ctrlColor)

            pm.select(locGrp)
            drvOrient = pm.xform(ctrl, q=1, ro=1, ws=1)
            drvScale = pm.xform(ctrl, q=1, s=1, ws=1)

            jntZero = jointTools.makeJoint(name=drvJntZeroName,
                                             coords=(eachCoord, (0, 0, 0), (1, 1, 1)), connectToLast=True)

            pm.xform(jntZero, ro=drvOrient, s=drvScale, ws=1)

            jnt = jointTools.makeJoint(name=drvJntName,
                                         coords=(eachCoord, (0, 0, 0), (1, 1, 1)), connectToLast=True)

            jnt.setRotation((0, 0, 0))
            jnt.setScale((1, 1, 1))
            jnt.jointOrient.set((0, 0, 0))
            self.drvJntList.append(str(jnt.name()))
            drvJntList.append(jnt)

            pm.addAttr(ctrl, ln=rollAttrName, k=1)

            self.drvCtrlList.append(ctrl.name())

            locGrp.getParent().setParent(partitionJntGroup)

            ctrl.getParent().setParent(ctrlParentGrp)
            ctrlParentZeroGrp.setParent(partitionCtrlGroup)

            ctrl.translate >> jnt.translate
            # ctrl.rotateX >> jnt.rotateX
            # ctrl.rotateY >> jnt.rotateY
            ctrl.rotateZ >> jnt.rotateZ
            # ctrl.scale >> jnt.scale

            # ctrlMoveall.scale >> locGrp.scale

        # conectando ctrls principais

        ctrlUp.translate >> upGrp.translate
        ctrlUp.rotate >> upGrp.rotate
        ctrlUp.scale >> upGrp.scale

        ctrlLw.translate >> lwGrp.translate
        ctrlLw.rotate >> lwGrp.rotate
        ctrlLw.scale >> lwGrp.scale

        rbbn[0].setParent(moveallGrp)

        ribbonSkin = pm.skinCluster(rbbn, drvJntList, tsb=True, dr=10, mi=2)

        # editando skin da ribbon:
        # criando uma lista de influencias para cada cv
        count = 0  # conta qual eh o driver da vez
        for cv in range(self.drivers * self.spansPerDriver):
            interval = cv % self.spansPerDriver

            if interval == 0:
                count += 1

            fractionalInfluence = (float(interval) / self.spansPerDriver)
            influenceJnt1 = 1 - fractionalInfluence
            influenceJnt2 = fractionalInfluence

            jnt1 = count
            jnt2 = count + 1
            if jnt2 > len(self.mainLocDrvList):
                jnt2 = 1

            # #print 'span influence:    | cv: ', cv, ' | jnt: ',jnt1, ' - influence: ', influenceJnt1, ' | jnt: ', jnt2, ' - influence: ', influenceJnt2

            # pintando a ribbon:
            for cvInSpan in range(2):
                pm.skinPercent(str(ribbonSkin), str(rbbn[0]) + '.cv[' + str(cvInSpan) + '][' + str(cv) + ']', nrm=True,
                               transformValue=[(str(drvJntList[jnt1 - 1]), influenceJnt1),
                                               (str(drvJntList[jnt2 - 1]), influenceJnt2)])

        # criando sistema para mapear ordem e influencias das jnts na ribbon:

        tempGrp = groupTools.makeGroup(name=self.name + '_temp')

        reader = controlTools.cntrlCrv(name=self.name + '_reader_loc_temp', icone='null', cntrlSulfix='',
                                       parent=tempGrp)

        # o locator passa pela ribbon atraves do motion Path:
        # #print '>> mpath1'
        readerMotionPath = self.createMotionPath(reader, self.mainCurveGuide, 0)
        # #print '>> mpath2'
        closestReaderName = self.name + '_reader_closest_temp'
        closestReader = pm.createNode('closestPointOnSurface', n=closestReaderName)

        reader.translate >> closestReader.inPosition
        rbbn[0].worldSpace[0] >> closestReader.inputSurface

        # criando jnts presos na ribbon:
        # caso nao tenhamos input de coordenadas para os drivens (self.rbbnJntsCoordList), preenchemos a lista.

        drivenParameterList = []
        self.rbbnJntsCoordList = []

        for each in self.skinLocList:
            coord = pm.xform(each, q=1, rp=1, ws=1)
            self.rbbnJntsCoordList.append(coord)

            reader.translate.set(coord)
            param = closestReader.parameterV.get()

            # alimentando lista com parameterV de cada jnt referente a ribbon:
            drivenParameterList.append(param)
        #print 'self.skinLocList', self.skinLocList
        # criando objetos driven em cada coordenada e preenchendo a lista de parametroV relativa a ribbon:

        rbbnJntTransList = []
        rbbnJntRollList = []
        rbbnJntSkinList = []

        rbbnJntGrpName = self.name + '_rbbn_jnt_grp'
        rbbnJntGrp = groupTools.makeGroup(name=rbbnJntGrpName, parent=jntDrivenGrp)

        vzRivetGrp = 'vzRivet_grp'
        for eachDriven, drivenCoord in enumerate(self.rbbnJntsCoordList):

            # criando driven transforms:
            trsDrivenCoord = (drivenCoord, (0, 0, 0), (1, 1, 1))

            # identificando objetos como middle, left, side:
            if trsDrivenCoord[0][0] > 0.01:
                side = 'left'
                sidePrefix = self.globalPrefix['left']

            elif trsDrivenCoord[0][0] < -0.01:
                side = 'right'
                sidePrefix = self.globalPrefix['right']

            else:
                side = 'middle'
                sidePrefix = self.globalPrefix['middle']

            prefix = sidePrefix + self.name

            eachDrivenIndex = eachDriven + 1
            eachDrivenAntIndex = eachDriven

            rbbnLocName = prefix + '_rbbn_' + str(eachDrivenIndex) + '_loc'
            rbbnLocRollZeroAntName = prefix + '_rbbn_' + str(eachDrivenAntIndex) + '_loc'

            rbbnJntTransZeroName = prefix + '_rbbn_' + str(eachDrivenIndex) + '_trans_zero'
            rbbnJntTransName = prefix + '_rbbn_' + str(eachDrivenIndex) + '_trans_jxt'
            rbbnJntRollZeroName = prefix + '_rbbn_' + str(eachDrivenIndex) + '_roll_zero'
            rbbnJntRollName = prefix + '_rbbn_' + str(eachDrivenIndex) + '_roll_jxt'
            rbbnJntName = prefix + '_rbbn_' + str(eachDrivenIndex) + '_skin_jxt'
            baseRollLocName = prefix + '_' + str(eachDrivenIndex)

            logger.debug('guardando coordenadas do loc base roll')

            locTempCoord = pm.xform(self.skinPvtLocList[eachDriven], q=1, rp=1, ws=1)

            rbbnLoc = controlTools.cntrlCrv(name=rbbnLocName, coords=trsDrivenCoord, icone='null', cntrlSulfix='')
            rbbnJntTransZero = jointTools.makeJoint(name=rbbnJntTransZeroName, coords=trsDrivenCoord,
                                                      connectToLast=True)
            rbbnJntTrans = jointTools.makeJoint(name=rbbnJntTransName, coords=trsDrivenCoord, connectToLast=True,
                                                  label=(side, prefix + '_trans_' + str(eachDrivenIndex)))
            rbbnJntRollZero = jointTools.makeJoint(name=rbbnJntRollZeroName, coords=trsDrivenCoord,
                                                     connectToLast=True)
            rbbnJntRoll = jointTools.makeJoint(name=rbbnJntRollName, coords=trsDrivenCoord, connectToLast=True)
            rbbnJnt = jointTools.makeJoint(name=rbbnJntName, connectToLast=True,
                                             label=(side, prefix + '_roll_' + str(eachDrivenIndex)))

            rbbnLoc.getParent().setParent(rbbnJntGrp)

            # parent driven transforms na ribbon:

            rbbnFoll = attatchTools.hookOnMesh(inputs=(rbbnLoc.getParent(), rbbn[0]), mode=3, follOn=vzRivetGrp)

            # orientando as jnts roll:
            logger.debug('orientando jnts roll')
            if eachDriven > 0:
                aimTemp = pm.aimConstraint(rbbnLocName, rbbnJntRollZero, u=(-1, 0, 0), aim=(0, -1, 0),
                                           wuo=self.skinPvtLocList[eachDriven - 1], wut='object', mo=False)

            pm.xform(rbbnJntTransZero, t=locTempCoord, ws=1)
            pm.xform(rbbnJnt, t=drivenCoord, ws=1)

            if eachDriven > 0:
                pm.delete(aimTemp)

            # criando nodes para distribuicao da orientacao entre os jnts:
            # usar param para drive do blend
            rbbnJntTransList.append(rbbnJntTrans)
            rbbnJntRollList.append(rbbnJntRoll)
            rbbnJntSkinList.append(rbbnJnt)
            self.skinJnts.append(str(rbbnJntTrans.name()))
            self.skinJnts.append(str(rbbnJnt.name()))

        pm.PyNode(vzRivetGrp).setParent(moveallGrp)

        # criando sistema de influencias do roll:

        logger.debug('definindo influencias dos jnts roll')
        # criando a param list dos self.drvJntList
        driverParameterList = []

        for drvCoord in mainCoords:
            reader.translate.set(drvCoord)
            param = closestReader.parameterV.get()
            driverParameterList.append(param)
            # #print param

        # criando lista para drivers e drivens onde os valores superiores ao tamanho da rbbn
        # assumem valores correspondentes ao inicio

        driverParameterLinearList = []
        for i, paramDriver in enumerate(driverParameterList):
            paramDriverLinear = paramDriver
            if paramDriver > self.structureSections:
                paramDriverLinear = paramDriver - self.structureSections

            driverParameterLinearList.append(paramDriverLinear)

        drivenParameterLinearList = []
        for i, paramDriven in enumerate(drivenParameterList):
            paramDrivenLinear = paramDriven

            if paramDriven > self.structureSections:
                paramDrivenLinear = paramDriven - self.structureSections

            drivenParameterLinearList.append(paramDrivenLinear)

        drvList = self.drvCtrlList

        logger.debug('distribuindo orientacao jnts roll')
        # criando sistema de orientacao do jnt roll distribuida a partir dos drivers:

        quadrantJntList = [[], [], []]  # essa lista contem uma lista para cada quadrante
        # comecando pelo superior direito e seguindo em sentido horario

        # limites dos quadrantes da rbbn.:

        overStart = rbbnVRange[1] - self.structureSections
        quad3 = (rbbnVRange[1] / 2)
        paramCornerLeft = quad3 - (self.structureSections / 4)
        paramCornerRight = quad3 + (self.structureSections / 4)

        # #print 'quadrantes: ', paramCornerLeft, quad3, paramCornerRight

        for drivenIndex, drivenParam in enumerate(drivenParameterLinearList):

            # #print 'drivenIndex', drivenIndex,'drivenParam', drivenParam, 'left:', paramCornerLeft, 'right: ', paramCornerRight

            if drivenParam < paramCornerLeft:
                quadrantJntList[0].append(drivenIndex)

            elif drivenParam > paramCornerLeft and drivenParam < paramCornerRight:
                quadrantJntList[1].append(drivenIndex)

            elif drivenParam > paramCornerRight:
                quadrantJntList[2].append(drivenIndex)

        quadrantJntList[1].reverse()
        upIndexList = quadrantJntList[2] + quadrantJntList[0]
        lwIndexList = quadrantJntList[1]

        masterRollDict = {}  # formato: index:(param, minRange, maxRange)

        # Alimentando a lista upMasterRollParamList:
        # #print '#---'

        # #print upIndexList
        # #print lwIndexList

        logger.debug('alimentando listas de parametros')
        for lwCurrentIndex in lwIndexList:
            # #print 'lw   -   ',lwCurrentIndex,'   -   ', drivenParameterLinearList[lwCurrentIndex],'   -   ',paramCornerLeft, ' - ', paramCornerRight

            masterRollDict.update({lwCurrentIndex:
                                       (drivenParameterLinearList[lwCurrentIndex], paramCornerLeft, paramCornerRight)})

        # Alimentando a lista lwMasterRollParamList:

        for upCurrentIndex in upIndexList:
            index = drivenParameterLinearList[upCurrentIndex]

            if upCurrentIndex in quadrantJntList[0]:
                index += self.structureSections

            # #print 'up   -   ',upCurrentIndex,'   -   ', index, '   -   ', paramCornerRight, ' - ',paramCornerLeft + self.structureSections
            masterRollDict.update({upCurrentIndex:
                                       (index, paramCornerRight, paramCornerLeft + self.structureSections)})

        masterDriverList = []
        for each in driverParameterList:

            if each <= quad3:
                masterDriverList.append(each + self.structureSections)
            else:
                masterDriverList.append(each)

        # #print masterRollDict # lista de parametros dos skinaveis com valores iniciais maiores que o tamanho da rbbn
        # #print drivenParameterList # lista de parametros dos skinaveis com valores iniciais partindo do inicio real

        # #print masterDriverList # lista de parametros dos drivers com valores iniciais maiores que o tamanho da rbbn
        # #print driverParameterList # lista de parametros dos skinaveis com valores iniciais partindo do inicio real

        logger.debug('inicio da aplicacao de influncias de roll e scale')

        # para definicao de influencia dos drivers de cada skin jnt precisamos definir um limite no inicio
        # entre o valor inicial (proximo a zero) e o final que excede o tamanho da ribbon
        # por conta disso, fiz uma condicao que a partir do parametro do segundo driver, considera-se os valores dos
        # drivens a partir do zero

        for driverIndex in range(self.drivers):

            # caso seja o primeiro  driver, o anterior eh o ultimo e caso seja o ultimo o diver eh o primeiro

            if driverIndex == 0:
                driverIndexNext = driverIndex + 1
                driverIndexPrev = self.drivers - 1

            elif driverIndex == self.drivers - 1:
                driverIndexNext = 0
                driverIndexPrev = driverIndex - 1

            else:
                driverIndexNext = driverIndex + 1
                driverIndexPrev = driverIndex - 1

            if driverIndex > 1:  # caso seja o segundo driver em diante, a referencia de parametrizacao parte do zero
                driverList = driverParameterList

            else:  # caso contrario, os valores iniciais desses parametros vao ser continuacao do final da rbbn
                driverList = masterDriverList

            # identificando os ctrl drivers:
            driver1 = pm.PyNode(drvList[driverIndex])

            if driverIndex < self.drivers - 1:
                driver2 = pm.PyNode(drvList[driverIndex + 1])
            else:
                driver2 = pm.PyNode(drvList[0])

            driverParam = driverList[driverIndex]
            driverParamNext = driverList[driverIndexNext]
            driverParamPrev = driverList[driverIndexPrev]

            # #print 'toDriver: ', driverIndex, driverParam, driverParamNext, ' - ', driver1, driver2

            for drivenIndex in range(self.rbbnJnts):

                if driverIndex > 1:  # caso seja o segundo driver em diante, a referencia de parametrizacao parte do zero
                    drivenParam = drivenParameterList[drivenIndex]
                else:  # caso contrario, os valores iniciais desses parametros vao ser continuacao do final da rbbn
                    drivenParam = masterRollDict[drivenIndex][0]

                drivenJnt = rbbnJntTransList[drivenIndex]
                # #print '--- ',drivenParam, driverParamPrev, driverParamNext
                if drivenParam < driverParamNext and drivenParam >= driverParam:
                    # #print '___set: ', drivenIndex, drivenParam, drivenJnt

                    systemInfo = {
                        'upIndexList': upIndexList,
                        'lwIndexList': lwIndexList,
                        'rollAttrName': rollAttrName,
                        'ctrlUp': ctrlUp,
                        'ctrlLw': ctrlLw,
                        'rbbnJntTransList': rbbnJntTransList,
                        'rbbnJntRollList': rbbnJntRollList,
                        'rbbnJntSkinList': rbbnJntSkinList,
                        'masterRollDict': masterRollDict
                    }
                    self.rollScaleConnections(driverIndex, driverParam, driverParamNext, driver1, driver2,
                                              drivenIndex, drivenParam, drivenJnt, **systemInfo)

        pm.delete(tempGrp)

        moveallGrp.visibility.set(0)



        self.exportDict(ctrlMoveall)
        #pm.parent(ctrlMoveallName.getParent(), head_constrained_grp)
        om.MGlobal.displayInfo('# Success! O Sistema ' + self.name + ' foi gerado com sucesso.\n')
        # ############
        # jnts de skin salvos no dict estao com os nomes sem UP ou LW
        # linkar com sistema inteligente de drivers do jaw e stiky
        # corners como base de distribuicao dos drivers
        # linkar com sistema de salvar pintura de jnts e shapes dos controles

    def autoSkin(self, paralelLoops1=2, paralelLoops2=3, holdJoint=None):

        mesh = pm.ls(self.edgeLoop[0], o=True)[0]
        edgeloop = self.edgeLoop
        skinCls = skinTools.findSkinCluster(mesh)

        if not skinCls:
            skinCls = pm.skinCluster(mesh, holdJoint)
            influencesToAdd = self.transJnts
            print self.transJnts
        else:
            influenceList = pm.skinCluster(skinCls, query=True, influence=True)
            influencesToAdd = [x for x in self.transJnts if x not in influenceList]
            print influencesToAdd

        pm.skinCluster(skinCls, e=True, ai=influencesToAdd, wt=0)
        vtx = vtxWalking.edgeLoopToVextex(edgeloop)
        pm.skinPercent(skinCls, vtx, resetToDefault=True)
        skinTools.edgeSkin(edgeLoopOriginal=edgeloop, paralelLoopNum=paralelLoops2+paralelLoops1)

        influenceList = pm.skinCluster(skinCls, query=True, influence=True)
        print self.scaleJnts
        influencesToAdd = [x for x in self.scaleJnts if x not in influenceList]
        print influencesToAdd

        pm.skinCluster(skinCls, e=True, ai=influencesToAdd, wt=0)
        vtx = vtxWalking.edgeLoopToVextex(edgeloop)
        pm.skinPercent(skinCls, vtx, resetToDefault=True)
        skinTools.edgeSkin(edgeLoopOriginal=edgeloop, paralelLoopNum=paralelLoops2)

#l = Lips()
#l.getDict()
#l.doGuide()
#l.doRig()


