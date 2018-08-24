#!/usr/bin/python
# coding: utf-8
import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.rigFunctions as rigFunctions


class Tweaks:
    def __init__(self, name='tweak', num=1, type='static', **kwargs):
        self.name = name
        self.type = type
        self.num = num
        self.guideDict = {}
        self.jntPrefix = '_jnt'
        self.guideMoveall = None
        self.tweakDict = {'name': self.name, 'num': self.num, 'type': self.type, 'guideDict': {}}
        self.guideDict = {}
        for i in range(self.num):
            self.guideDict[self.name + str(i + 1)] = [i * .5, 0, 0]
        self.tweakDict['drvSetup'] = {'nameTempl': self.name + '_drv', 'icone': 'grp', 'size': 1, 'color': (1, 1, 0)}
        self.tweakDict['cntrlSetup'] = {'nameTempl': self.name, 'icone': 'circuloX', 'size': 1, 'color': (1, 1, 0)}

        self.tweakDict.update(kwargs)
        self.guideDict.update(self.tweakDict['guideDict'])
        self.tweakDict['guideDict'] = self.guideDict.copy()

    def doGuide(self):
        if pm.objExists(self.name + 'Moveall_guide'):
            pm.delete(self.name + 'Moveall_guide')
        self.guideMoveall = pm.group(em=True, n=self.name + 'Moveall_guide')

        self.guideList = []
        for i in range(self.num):
            guide = pm.spaceLocator(n=self.name + str(i + 1))
            guide.localScale.set(.2, .2, .2)
            guide.translate.set(self.guideDict[self.name + str(i + 1)])
            self.guideList.append(guide)
            guide.setParent(self.guideMoveall)

    def getGuideFromScene(self):
        self.guideMoveall = pm.PyNode(self.name + 'Moveall_guide')

        self.guideList = []
        for i in range(self.num):
            guide = pm.PyNode(self.name + str(i + 1))
            self.guideList.append(guide)

    def mirrorConnectGuide(self, tweak):
        if not self.guideMoveall:
            self.doGuide()
        if not tweak.guideMoveall:
            tweak.doGuide()

        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')
        # if not pm.objExists('GUIDES'):
        #    pm.group ( self.name+'MirrorGuide_grp', n='GUIDES' )
        # else:
        #    pm.parent ( self.name+'MirrorGuide_grp', 'GUIDES')

        self.guideMoveall.setParent(self.mirrorGuide)
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.template.set(1)

        tweak.guideMoveall.translate >> self.guideMoveall.translate
        tweak.guideMoveall.rotate >> self.guideMoveall.rotate
        tweak.guideMoveall.scale >> self.guideMoveall.scale

        for i in range(self.num):
            tweak.guideList[i].translate >> self.guideList[i].translate
            tweak.guideList[i].rotate >> self.guideList[i].rotate
            tweak.guideList[i].scale >> self.guideList[i].scale

    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()

        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')

        self.cntrlGrp = pm.group(em=True, n=self.name + 'Cntrls_grp')
        self.drvGrp = pm.group(em=True, n=self.name + 'Drivers_grp')
        self.moveall = pm.group(self.cntrlGrp, self.drvGrp, n=self.name + 'Moveall')

        self.cntrlList = []
        for i in range(self.num):
            pm.select(cl=True)
            jnt = pm.joint(n=self.name + str(i + 1) + self.jntPrefix)
            pos = pm.xform(self.guideList[i], q=True, ws=True, t=True)
            pm.xform(jnt, ws=True, t=pos)
            drvName = self.tweakDict['drvSetup']['nameTempl'] + str(i + 1) + '_drv'
            drv = rigFunctions.cntrlCrv(name=drvName, obj=jnt, connType='parent', **self.tweakDict['drvSetup'])
            cntrlName = self.tweakDict['cntrlSetup']['nameTempl'] + str(i + 1)
            cntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=drv, connType='connection', offsets=1,
                                          **self.tweakDict['cntrlSetup'])

            if self.type == 'static':
                print 'static cntrl'
                mlt = pm.createNode('multiplyDivide')
                mlt.input2.set([-1, -1, -1])
                cntrl.translate >> mlt.input1
                mlt.output >> cntrl.getParent().translate

            self.cntrlList.append(cntrl)
            cntrl.getParent(2).setParent(self.cntrlGrp)
            drv.getParent().setParent(self.drvGrp)


class Jaw:

    def __init__(self, name='jaw'):
        self.jawGuideDict = {'moveall': [0, 0, 0], 'lcorner': [.31, -0.01, -.1], 'rcorner': [-.31, -0.01, -.1],
                             'jaw': [0, -.18, -.03], 'upperLip': [0, .15, -.01], 'pivot': [0, .15, -1.15],
                             'hold': [0, -.2, -1.5]}
        self.guideMoveall = None
        self.name = name

    def doGuide(self):
        if pm.objExists(self.name + 'Moveall_guide'):
            pm.delete(self.name + 'Moveall_guide')

        self.guideMoveall = pm.group(em=True, n=self.name + 'Moveall_guide')
        self.guideMoveall.translate.set(self.jawGuideDict['moveall'])

        self.lcornerGuide = pm.spaceLocator(n='lcorner')
        self.lcornerGuide.translate.set(self.jawGuideDict['lcorner'])
        self.lcornerGuide.localScale.set(0.1, 0.1, 0.1)

        self.rcornerGuide = pm.spaceLocator(n='rcorner')
        self.rcornerGuide.translate.set(self.jawGuideDict['rcorner'])
        self.rcornerGuide.localScale.set(0.1, 0.1, 0.1)

        self.jawGuide = pm.spaceLocator(n='jaw')
        self.jawGuide.translate.set(self.jawGuideDict['jaw'])
        self.jawGuide.localScale.set(0.1, 0.1, 0.1)

        self.upperLipGuide = pm.spaceLocator(n='upperLip')
        self.upperLipGuide.translate.set(self.jawGuideDict['upperLip'])
        self.upperLipGuide.localScale.set(0.1, 0.1, 0.1)

        self.pivotGuide = pm.spaceLocator(n='pivot')
        self.pivotGuide.translate.set(self.jawGuideDict['pivot'])
        self.pivotGuide.localScale.set(0.1, 0.1, 0.1)

        self.holdGuide = pm.spaceLocator(n='hold')
        self.holdGuide.translate.set(self.jawGuideDict['hold'])
        self.holdGuide.localScale.set(0.1, 0.1, 0.1)

        pm.parent(self.lcornerGuide, self.rcornerGuide, self.jawGuide, self.upperLipGuide, self.pivotGuide,
                  self.holdGuide, self.guideMoveall)

    def getGuideFromScene(self):

        self.guideMoveall = pm.PyNode(self.name + 'Moveall_guide')
        self.lcornerGuide = pm.PyNode('lcorner')
        self.rcornerGuide = pm.PyNode('rcorner')
        self.jawGuide = pm.PyNode('jaw')
        self.upperLipGuide = pm.PyNode('upperLip')
        self.pivotGuide = pm.PyNode('pivot')
        self.holdGuide = pm.PyNode('hold')

    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()

        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')

        self.moveall = pm.group(em=True, n=self.name + 'Moveall')

        pm.select(cl=True)
        pivot = pm.xform(self.pivotGuide, q=True, ws=True, t=True)
        self.jawJnt = pm.joint(p=pivot, n='jaw_jxt')
        jaw = pm.xform(self.jawGuide, q=True, ws=True, t=True)
        pm.joint(p=jaw, n='jaw_jnt')

        pm.select(cl=True)
        self.lcornerJnt = pm.joint(p=pivot, n='lcorner_jxt')
        lcorner = pm.xform(self.lcornerGuide, q=True, ws=True, t=True)
        pm.joint(p=lcorner, n='lcorner_jnt')

        pm.select(cl=True)
        self.rcornerJnt = pm.joint(p=pivot, n='rcorner_jxt')
        rcorner = pm.xform(self.rcornerGuide, q=True, ws=True, t=True)
        pm.joint(p=rcorner, n='rcorner_jnt')

        pm.select(cl=True)
        self.upperLipJnt = pm.joint(p=pivot, n='upperLip_jxt')
        upperLip = pm.xform(self.upperLipGuide, q=True, ws=True, t=True)
        pm.joint(p=upperLip, n='upperLip_jnt')

        pm.select(cl=True)
        hold = pm.xform(self.holdGuide, q=True, ws=True, t=True)
        self.holdJnt = pm.joint(p=hold, n='hold_jnt')
        pivot = pm.xform(self.pivotGuide, q=True, ws=True, t=True)
        pivotJnt = pm.joint(p=pivot, n='pivot_jxt')

        jawCntrlDrv = rigFunctions.cntrlCrv(name='jawCntrl_drv', obj=self.jawJnt, connType='parentConstraint', size=.5,
                                            icone='grp')
        self.jawCntrl = rigFunctions.cntrlCrv(name='jawCntrl', obj=jawCntrlDrv, connType='connection', size=.5,
                                              icone='circuloZ')
        self.jawCntrl.addAttr('L_cornerFollow', at='float', dv=0.5, k=1)
        self.jawCntrl.addAttr('R_cornerFollow', at='float', dv=0.5, k=1)

        b = jaw
        a = pivot
        shape = self.jawCntrl.getShape()
        pm.move(b[0] - a[0], (b[1] - a[1]) - .3, (b[2] - a[2]) + .4, shape.cv, r=True)

        pm.parent(jawCntrlDrv.getParent(), self.jawJnt, self.lcornerJnt, self.rcornerJnt, self.upperLipJnt,
                  self.holdJnt, self.jawCntrl.getParent(), self.moveall)

        multi1 = pm.createNode('multiplyDivide')
        multi2 = pm.createNode('multiplyDivide')
        multi3 = pm.createNode('multDoubleLinear')
        cond = pm.createNode('condition')

        self.jawCntrl.L_cornerFollow >> multi1.input2.input2X
        self.jawCntrl.L_cornerFollow >> multi1.input2.input2Y
        self.jawCntrl.L_cornerFollow >> multi1.input2.input2Z
        self.jawCntrl.R_cornerFollow >> multi2.input2.input2X
        self.jawCntrl.R_cornerFollow >> multi2.input2.input2Y
        self.jawCntrl.R_cornerFollow >> multi2.input2.input2Z

        self.jawJnt.rotate >> multi1.input1
        self.jawJnt.rotate >> multi2.input1
        multi1.output >> self.lcornerJnt.rotate
        multi2.output >> self.rcornerJnt.rotate

        self.jawJnt.rotateX >> cond.firstTerm
        cond.secondTerm.set(0)
        cond.operation.set(4)
        cond.colorIfFalseR.set(0)
        multi3.input2.set(.3)
        self.jawJnt.rotateX >> multi3.input1
        multi3.output >> cond.colorIfTrue.colorIfTrueR
        cond.outColor.outColorR >> self.upperLipJnt.rotateX


class MouthCorners:
    def __init__(self, name='mouthCorners', bsDict=None, mesh=None, tgtMesh=None):
        self.name = name
        self.mesh = mesh
        self.tgtMesh = tgtMesh
        self.mouthCornersGuideDict = {'moveall': [0, 0, 0], 'lcorner': [.5, 0, 0], 'rcorner': [-.5, 0, 0]}
        if bsDict:
            self.bsDict = bsDict
        else:
            self.bsDict = {'L_up': None, 'R_up': None,
                           'L_down': None, 'R_down': None,
                           'L_narrow': None, 'R_narrow': None,
                           'L_wide': None, 'R_wide': None,
                           'L_wide_up': None, 'R_wide_up': None,
                           'L_wide_down': None, 'R_wide_down': None,
                           'L_narrow_up': None, 'R_narrow_up': None,
                           'L_narrow_down': None, 'R_narrow_down': None}

    def doGuide(self):
        if pm.objExists(self.name + 'Moveall_guide'):
            pm.delete(self.name + 'Moveall_guide')
        self.guideMoveall = pm.group(em=True, n=self.name + 'Moveall_guide')
        self.lcornerGuide = pm.spaceLocator(n=self.name + 'LCorner_guide')
        self.lcornerGuide.translate.set(self.mouthCornersGuideDict['lcorner'])
        self.lcornerGuide.localScale.set(0.1, 0.1, 0.1)
        self.rcornerGuide = pm.spaceLocator(n=self.name + 'RCorner_guide')
        self.rcornerGuide.translate.set(self.mouthCornersGuideDict['rcorner'])
        self.rcornerGuide.localScale.set(0.1, 0.1, 0.1)
        pm.parent(self.lcornerGuide, self.rcornerGuide, self.guideMoveall)

    def getGuideFromScene(self):
        self.guideMoveall = pm.PyNode(self.name + 'Moveall_guide')
        self.lcornerGuide = pm.PyNode(self.name + 'LCorner_guide')
        self.rcornerGuide = pm.PyNode(self.name + 'RCorner_guide')

    def doRig(self, bsDict=None):
        if not self.guideMoveall:
            self.doGuide()

        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')
        self.moveall = pm.group(em=True, n=self.name + 'Moveall')

        if bsDict:
            self.bsDict = bsDict

        self.lcornerCntrl = rigFunctions.cntrlCrv(name='LCorner', obj=self.lcornerGuide, icone='circuloZ', size=.5)
        self.lcornerCntrl.getParent().scaleX.set(-1)
        self.rcornerCntrl = rigFunctions.cntrlCrv(name='RCorner', obj=self.rcornerGuide, icone='circuloZ', size=.5)

        pm.parent(self.lcornerCntrl.getParent(), self.rcornerCntrl.getParent(), self.moveall)
        tmp = pm.ls(pm.listHistory(self.mesh, future=False), type='blendShape')
        if tmp:
            bsNode = tmp[0]
        else:
            print 'Nao encontrou blendShape node'

        self.connectToPainel(self.lcornerCntrl, bsNode, 'translateX', self.bsDict['L_narrow'], .3,
                             self.bsDict['L_wide'], -.3)
        self.connectToPainel(self.lcornerCntrl, bsNode, 'translateY', self.bsDict['L_up'], .3, self.bsDict['L_down'],
                             -.3)
        self.connectToPainel(self.rcornerCntrl, bsNode, 'translateX', self.bsDict['R_narrow'], .3,
                             self.bsDict['R_wide'], -.3)
        self.connectToPainel(self.rcornerCntrl, bsNode, 'translateY', self.bsDict['R_up'], .3, self.bsDict['R_down'],
                             -.3)

        for prefix in ['L_', 'R_']:
            for shpA in ['up', 'down']:
                for shpB in ['wide', 'narrow']:
                    multi1 = pm.createNode('multDoubleLinear')
                    bsNode.attr(bsDict[prefix + shpA]) >> multi1.input1
                    bsNode.attr(bsDict[prefix + shpB]) >> multi1.input2
                    multi1.output >> bsNode.attr(self.bsDict[prefix + shpA + '_' + shpB])

    def selToBsDict(self):
        ## funcao para povoar o dicionario com os nomes dos shapes
        ## a selecao deve ser feita na mesma ordem que aparece abaixo
        sel = pm.ls(sl=True)
        if len(sel) == 16:
            self.bsDict = {'L_up': sel[0].name(), 'R_up': sel[1].name(),
                           'L_down': sel[2].name(), 'R_down': sel[3].name(),
                           'L_narrow': sel[4].name(), 'R_narrow': sel[5].name(),
                           'L_wide': sel[6].name(), 'R_wide': sel[7].name(),
                           'L_up_wide': sel[8].name(), 'R_up_wide': sel[9].name(),
                           'L_down_wide': sel[10].name(), 'R_down_wide': sel[11].name(),
                           'L_up_narrow': sel[12].name(), 'R_up_narrow': sel[13].name(),
                           'L_down_narrow': sel[14].name(), 'R_down_narrow': sel[15].name()}
        print self.bsDict

    def invertBSBaseWeights(self, obj, bs):
        # inverte o mapa de influencia de um blendShape.
        # usado pra tirar o blend esquedo e direito
        allWeights = pm.polyEvaluate(obj, v=True)
        for i in range(allWeights):
            x = pm.getAttr(bs + '.inputTarget[0].baseWeights[' + str(i) + ']')
            pm.setAttr(bs + '.inputTarget[0].baseWeights[' + str(i) + ']', (1 - x))

    def splitShapes(self):
        # duplica um objeto q tenha todos os blends aplicados
        # e um mapa de influencia pintado na metade
        # criando versoes para esqueda e direita
        ##IMPLEMENTAR: mapa automatico
        obj = self.tgtMesh

        tmp = pm.ls(pm.listHistory(obj, future=False), type='blendShape')
        if tmp:
            bs = tmp[0]
        print bs
        numOfShapes = pm.blendShape(bs, query=True, weightCount=True)
        [pm.setAttr(bs + '.weight[%d]' % (i), 0) for i in range(numOfShapes)]

        for shp in range(numOfShapes):
            pm.setAttr(bs + '.weight[%d]' % shp, 1)
            name = pm.aliasAttr('%s.weight[%d]' % (bs, shp), query=True)

            pm.duplicate(obj, n='R_' + name)
            self.invertBSBaseWeights(obj, bs)
            pm.duplicate(obj, n='L_' + name)
            self.invertBSBaseWeights(obj, bs)
            pm.setAttr(bs + '.weight[%d]' % shp, 0)

    def connectToPainel(self, cntrl, bsNode, param, bsMax, vMax, bsMin='', vMin=None):
        ##funcao que conecta o movimento dos controles aos blendShapes
        sR = pm.createNode('setRange')
        c = pm.createNode('clamp')
        sR.maxX.set(1)
        sR.minX.set(0)
        sR.oldMaxX.set(vMax)
        sR.oldMinX.set(0)
        c.maxR.set(1)
        cntrl.attr(param) >> sR.valueX
        sR.outValueX >> c.inputR
        c.outputR >> bsNode.attr(bsMax)
        if bsMin:
            sR.maxY.set(0)
            sR.minY.set(1)
            sR.oldMaxY.set(0)
            sR.oldMinY.set(vMin)
            c.maxG.set(1)
            cntrl.attr(param) >> sR.valueY
            sR.outValueY >> c.inputG
            c.outputG >> bsNode.attr(bsMin)


class EyeBrow:

    def __init__(self, name='eyeBrow', flipAxis=False, mesh=None, **kwargs):
        ##def doRig(self):
        self.name = name
        self.flipAxis = flipAxis
        self.guideMoveall = None
        self.guideList = []
        self.mesh = mesh
        self.browGuideNames = ['inTip1', 'inTip2', 'in', 'out', 'outTip2', 'outTip1']
        self.browGuideDict = {'inTip1': [0.3, 0, 0], 'inTip2': [0, 0, 0], 'in': [.08, .09, 0], 'out': [-.08, .09, 0],
                              'outTip2': [0, 0, 0], 'outTip1': [-0.3, 0, 0]}

        self.browDict = {'name': self.name, 'flipAxis': self.flipAxis}
        self.browDict['moveallGuideSetup'] = {'nameTempl': self.name + 'MoveAll', 'size': 1, 'color': (1, 0, 0)}

        self.browDict['allCntrlSetup'] = {'nameTempl': self.name + 'All', 'size': .2, 'icone': 'cubo',
                                          'color': (0, 0, 1)}
        self.browDict['inTip1CntrlSetup'] = {'nameTempl': self.name + 'InTip', 'size': .1, 'icone': 'cubo',
                                             'color': (0, 1, 1)}
        self.browDict['inCntrlSetup'] = {'nameTempl': self.name + 'In', 'size': .1, 'icone': 'cubo', 'color': (0, 1, 1)}
        self.browDict['outCntrlSetup'] = {'nameTempl': self.name + 'Out', 'size': .1, 'icone': 'cubo',
                                          'color': (0, 1, 1)}
        self.browDict['outTip1CntrlSetup'] = {'nameTempl': self.name + 'OutTip', 'size': .1, 'icone': 'cubo',
                                              'color': (0, 1, 1)}
        self.browDict['guideDict'] = self.browGuideDict.copy()
        self.browDict.update(kwargs)
        self.browGuideDict.update(self.browDict['guideDict'])
        self.browDict['guideDict'] = self.browGuideDict.copy()

    def doGuide(self):  # doGuide
        if pm.objExists(self.name + 'Moveall_guide'):
            pm.delete(self.name + 'Moveall_guide')

        self.guideMoveall = pm.group(em=True, n=self.name + 'Moveall_guide')

        self.guideList = []

        for name in self.browGuideNames:
            guide = pm.spaceLocator(n=self.name + name)
            guide.setParent(self.guideMoveall)
            guide.translate.set(self.browGuideDict[name])
            guide.localScale.set(0.1, 0.1, 0.1)
            self.guideList.append(guide)

        grp1 = pm.group(self.guideList[1])
        grp2 = pm.group(self.guideList[4])

        pm.pointConstraint(self.guideList[0], self.guideList[2], grp1, mo=False)
        pm.pointConstraint(self.guideList[0], grp1, e=True, w=.7)
        pm.pointConstraint(self.guideList[2], grp1, e=True, w=.3)

        pm.pointConstraint(self.guideList[5], self.guideList[3], grp2, mo=False)
        pm.pointConstraint(self.guideList[5], grp2, e=True, w=.7)
        pm.pointConstraint(self.guideList[3], grp2, e=True, w=.3)

    def mirrorConnectGuide(self, brow):
        if not self.guideMoveall:
            self.doGuide()

        if not brow.guideMoveall:
            brow.doGuide()

        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')

        self.guideMoveall.setParent(self.mirrorGuide)
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.template.set(1)

        brow.guideMoveall.translate >> self.guideMoveall.translate
        brow.guideMoveall.rotate >> self.guideMoveall.rotate
        brow.guideMoveall.scale >> self.guideMoveall.scale

        for guide1, guide2 in zip(self.guideList, brow.guideList):
            guide2.translate >> guide1.translate
            guide2.rotate >> guide1.rotate
            guide2.scale >> guide1.scale

        if brow.flipAxis:
            self.flipAxis = False
        else:
            self.flipAxis = True

    def getGuideFromScene(self):
        self.guideMoveall = pm.PyNode(self.name + 'Moveall_guide')
        self.guideList
        for name in self.browGuideNames:
            guide = pm.PyNode(self.name + name)
            self.guideList.append(guide)

    def doRig(self):
        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')

        self.browMoveall = pm.group(em=True, n=self.name + 'Moveall')

        p = []
        V = []
        for guide in self.guideList:
            pos = pm.xform(guide, q=True, ws=True, t=True)
            p.append(pos)
            v = om.MVector(pos)
            V.append(v)

        self.wireCrv = pm.curve(n='wirecrv', p=p)

        clsInTip = pm.cluster(self.wireCrv.cv[0:1], n=self.name + 'InTip')
        clsIn = pm.cluster(self.wireCrv.cv[2], n=self.name + 'In')
        clsOut = pm.cluster(self.wireCrv.cv[3], n=self.name + 'Out')
        clsOutTip = pm.cluster(self.wireCrv.cv[4:5], n=self.name + 'OutTip')

        clsList = [clsInTip[1], clsIn[1], clsOut[1], clsOutTip[1]]
        nameList = ['inTip1', 'in', 'out', 'outTip1']
        pm.parent(self.wireCrv, clsList, self.browMoveall)

        self.cntrlList = []
        displaySetup = self.browDict['allCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + '_drv'

        cntrlAllDrv = rigFunctions.cntrlCrv(name=cntrlName, obj=self.guideList[2], icone='grp')
        cntrlAllDrv.getParent().setParent(self.browMoveall)

        cntrlName = displaySetup['nameTempl']
        self.cntrlAll = rigFunctions.cntrlCrv(name=cntrlName, obj=cntrlAllDrv, connType='connection', **displaySetup)
        self.cntrlAll.getParent().setParent(self.browMoveall)
        for cls, key in zip(clsList, nameList):
            grp = pm.group(em=True, n=cls.name() + 'Aux_grp')
            aux = pm.group(em=True, n=cls.name() + '_aux', p=grp)
            pos = pm.xform(cls, q=True, ws=True, rp=True)
            pm.xform(aux, t=pos, ws=True)
            if self.mesh:
                pm.geometryConstraint(self.mesh, aux)
            pm.parentConstraint(aux, cls, mo=True)

            displaySetup = self.browDict[key + 'CntrlSetup'].copy()
            cntrlName = displaySetup['nameTempl'] + '_drv'
            cntrlDrv = rigFunctions.cntrlCrv(name=cntrlName, obj=aux, icone='grp')
            cntrlName = displaySetup['nameTempl']
            cntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=cntrlDrv, connType='connection', **displaySetup)
            if self.flipAxis:
                cntrlDrv.getParent().scaleX.set(-1)
                cntrl.getParent().scaleX.set(-1)
            else:
                cntrlDrv.getParent().scaleX.set(1)
                cntrl.getParent().scaleX.set(1)
            pm.parentConstraint(cntrlDrv, aux, mo=True)
            self.cntrlList.append(cntrl)
            pm.parent(cntrlDrv.getParent(), cntrlAllDrv)
            pm.parent(cntrl.getParent(), self.cntrlAll)

            pm.parent(grp, aux, self.browMoveall)

# implementar colocar os grupos dentro do FAcial, cntrls
# x= Tweaks(name='hairTweaks', num=3, type=None, cntrlSetup = {'nameTempl':'lipTweaks', 'icone':'circuloX','size':.5,'color':(1,1,0) })
# x.guideDict
# x.getGuideFromScene()
# x.doGuide()
# x.doRig()

# j=Jaw(name='jaw')
# j.doGuide()
# j.getGuideFromScene()
# j.doRig()

# m= MouthCorners(mesh='corpo1', tgtMesh='BSMesh')
# m.getGuideFromScene()
# m.splitShapes()
# m.selToBsDict()
# m.doRig({'L_up_narrow': u'L_Corner_Up___Nar', 'L_down_narrow': u'L_Corner_Down___N', 'L_up_wide': u'L_Corner_Up___Wid', 'R_down_wide': u'R_Corner_Down___W', 'R_up_narrow': u'R_Corner_Up___Nar', 'R_wide': u'R_Wide', 'R_down': u'R_Corner_Down', 'R_narrow': u'R_Narrow', 'R_up_wide': u'R_Corner_Up___Wid', 'R_down_narrow': u'R_Corner_Down___N', 'L_narrow': u'L_Narrow', 'L_down_wide': u'L_Corner_Down___W', 'L_up': u'L_Corner_Up', 'L_wide': u'L_Wide', 'L_down': u'L_Corner_Down', 'R_up': u'R_Corner_Up'})

# x=EyeBrow(name='L_brow', mesh='corpo1')
# x.getGuideFromScene()
# x.doGuide()
# print x.guideMoveall
# y=EyeBrow(name='R_brow',mesh='corpo1', flipAxis=True)
# y.getGuideFromScene()
# y.mirrorConnectGuide(x)
# x.doRig()
# y.doRig()
