import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.matrixTools as matrixTools
from autoRig3.modules import ribbonBezierSimple, aimTwistDivider
from autoRig3.modules import twistExtractor
import json
import logging

logger = logging.getLogger('autoRig')

class Spine:
    """
        Cria uma espinha
        Parametros:
            name (string): nome da espinha
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone

    """

    # IMPLEMENTAR:
    # fkCntrls
    # qual o comportamento do hip?
    # no fk o hip deve ficar parado?
    # um so hip para ik e fk?

    def __init__(self, name='spine', flipAxis=False, axis='X', ribbonJntNum=5, **kwargs):

        self.name = name
        self.flipAxis = flipAxis
        self.axis = axis
        self.guideMoveall = None
        self.skinJoints = []
        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'
        self.zeroJxtSulfix = 'Zero_jxt'
        self.grpSulfix = '_grp'
        self.ribbonJntNum = ribbonJntNum
        self.toExport = {'spineFkCntrlSetup', 'startFkCntrlSetup', 'endFkCntrlSetup', 'midFkCntrlSetup',
                         'midFkOffsetCntrlSetup', 'moveallGuideSetup', 'startGuideSetup', 'midGuideSetup', 'endGuideSetup',
                         'endTipGuideSetup', 'startTipGuideSetup', 'startJntSetup', 'axis', 'endJntSetup', 'guideDict',
                         'flipAxis', 'hipCntrlSetup', 'moveallSetup', 'startIkCntrlSetup',
                         'midIkCntrlSetup', 'endIkCntrlSetup', 'name', 'ribbonJntNum'}

        self.moveallSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'grp', 'size': 1.8,
                             'color': (1, 1, 0)}
        self.hipCntrlSetup = {'nameTempl': self.name + 'COG', 'icone': 'cog', 'size': 5.5,
                              'color': (1, 0, 0)}
        self.spineFkCntrlSetup = {'nameTempl': self.name + 'WaistFk', 'icone': 'circuloPontaY', 'size': 4,
                                  'color': (0, 1, 0)}
        self.startFkCntrlSetup = {'nameTempl': self.name + 'HipFk', 'icone': 'circuloPontaY', 'size': 3.0,
                                  'color': (1, 1, 0)}
        self.midFkOffsetCntrlSetup = {'nameTempl': self.name + 'AbdomenFkOff', 'icone': 'circuloY',
                                      'size': 2.5, 'color': (1, 1, 0)}
        self.midFkCntrlSetup = {'nameTempl': self.name + 'AbdomenFk', 'icone': 'circuloPontaY', 'size': 4,
                                'color': (1, 1, 0)}
        self.endFkCntrlSetup = {'nameTempl': self.name + 'ChestFk', 'icone': 'circuloPontaY', 'size': 4,
                                'color': (1, 1, 0)}
        self.startIkCntrlSetup = {'nameTempl': self.name + 'HipIk', 'icone': 'circuloPontaY', 'size': 4,
                                  'color': (1, 1, 0)}
        self.midIkCntrlSetup = {'nameTempl': self.name + 'AbdomenIk', 'icone': 'circuloY', 'size': 4,
                                'color': (1, 1, 0)}
        self.endIkCntrlSetup = {'nameTempl': self.name + 'ChestIk', 'icone': 'circuloPontaY', 'size': 4,
                                'color': (1, 1, 0)}
        self.moveallGuideSetup = {'nameTempl': self.name + 'Moveall', 'size': 8, 'icone': 'quadradoY',
                                  'color': (1, 0, 0)}
        self.startGuideSetup = {'nameTempl': self.name + 'Hip', 'size': 7, 'icone': 'circuloY',
                                'color': (0, 1, 0)}
        self.midGuideSetup = {'nameTempl': self.name + 'Abdomen', 'size': 7, 'icone': 'circuloY',
                              'color': (0, 1, 0)}
        self.endGuideSetup = {'nameTempl': self.name + 'Chest', 'size': 7, 'icone': 'circuloY',
                              'color': (0, 1, 0)}
        self.startTipGuideSetup = {'nameTempl': self.name + 'HipTip', 'size': 1, 'icone': 'bola',
                                   'color': (0, 1, 0)}
        self.endTipGuideSetup = {'nameTempl': self.name + 'ChestTip', 'size': 1, 'icone': 'bola',
                                 'color': (0, 1, 0)}

        self.startJntSetup = {'nameTempl': self.name + 'Hip', 'icone': 'Bone', 'size': 2}
        self.endJntSetup = {'nameTempl': self.name + 'Chest', 'icone': 'Bone', 'size': 2}

        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)], 'start': [(0, 0, 0), (0, 0, 0)],
                          'mid': [(0, 0, 0), (0, 0, 0)], 'end': [(0, 8, 0), (0, 0, 0)],
                          'startTip': [(0, -1, 0), (0, 0, 0)], 'endTip': [(0, 2, 0), (0, 0, 0)]}

    def createCntrl(self, cntrlName):
        displaySetup = self.__dict__[cntrlName+'Setup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True, **displaySetup)
        return guide

    def setCntrl (self, cntrl, posRot, space='object'):
        cntrl.setTranslation(self.guideDict[posRot][0], space=space)
        cntrl.setRotation(self.guideDict[posRot][1], space=space)
        # Felipe --> condicao para setar valor de escala no moveall dos limbs
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

        # self.guideMoveall=pm.group (n=guideName, em=True)
        # self.guideMoveall=pm.circle (n=guideName , c=(0,0,0),nr=(1,0,0), sw=360,r=1 ,d=3,ut=0,ch=0)[0]

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

        self.startGuide = self.createCntrl('startGuide')
        self.midGuide = self.createCntrl('midGuide')
        self.endGuide = self.createCntrl('endGuide')


        midGuideGrp = pm.group(em=True, n=self.name + 'midGuide_grp')
        pm.pointConstraint(self.startGuide, self.endGuide, midGuideGrp, mo=False)
        self.midGuide.setParent(midGuideGrp)

        self.endTipGuide = self.createCntrl('endTipGuide')
        self.endTipGuide.setParent(self.endGuide)

        self.startTipGuide = self.createCntrl('startTipGuide')
        self.startTipGuide.setParent(self.startGuide)

        pm.parent(self.startGuide, midGuideGrp, self.endGuide, self.guideMoveall)

        self.setCntrl(self.startGuide, 'start', space='object')
        self.setCntrl(self.endGuide, 'end', space='object')
        self.setCntrl(self.midGuide, 'mid', space='object')
        self.setCntrl(self.endTipGuide, 'endTip', space='object')
        self.setCntrl(self.startTipGuide, 'startTip', space='object')
        self.setCntrl(self.guideMoveall, 'moveall', space='world')

        pm.addAttr(self.guideMoveall, ln='spineDict', dt='string')
        self.guideMoveall.spineDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.spineDict.get()
            dictRestored = json.loads(jsonDict)
            self.__dict__.update(**dictRestored)

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

            guideName = self.endTipGuideSetup['nameTempl'] + self.guideSulfix
            self.endTipGuide = pm.PyNode(guideName)
            self.guideDict['endTip'][0] = self.endTipGuide.getTranslation(space='object').get()
            self.guideDict['endTip'][1] = tuple(self.endTipGuide.getRotation(space='object'))

            guideName = self.startTipGuideSetup['nameTempl'] + self.guideSulfix
            self.startTipGuide = pm.PyNode(guideName)
            self.guideDict['startTip'][0] = self.startTipGuide.getTranslation(space='object').get()
            self.guideDict['startTip'][1] = tuple(self.startTipGuide.getRotation(space='object'))
        except:
            pass


    def doRig(self):
        # se nao tiver guide, faz
        if not self.guideMoveall:
            self.doGuide()
        # se ja existir rig, apaga
        cntrlName = self.moveallSetup['nameTempl']

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        # cria o moveall da espinha
        self.moveall = pm.group(n=cntrlName, em=True)
        pos = pm.xform(self.guideMoveall, q=True, ws=True, t=True)

        pm.xform(self.moveall, ws=True, t=pos)
        if not pm.objExists('MOVEALL'):
            pm.group(self.moveall, n='MOVEALL')
        else:
            pm.parent(self.moveall, 'MOVEALL')
        spineRibbon = None

        # cria controles fk com nomes e setagem de display vindas do spineDict
        displaySetup = self.hipCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.cogCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)

        displaySetup = self.spineFkCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.spineFkCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)
        self.spineFkCntrl.getParent().setParent(self.cogCntrl)

        displaySetup = self.startFkCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.startFkCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)
        self.startFkCntrl.getParent().setParent(self.cogCntrl)

        displaySetup = self.midFkCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.midFkCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.midGuide, **displaySetup)

        displaySetup = self.midFkOffsetCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.midFkOffsetCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.midGuide,
                                                      **displaySetup)  # esse controle faz o offset do ribbon e permanece orientado corretamente
        self.midFkOffsetCntrl.getParent().setParent(self.midFkCntrl)
        self.midFkCntrl.getParent().setParent(self.spineFkCntrl)

        displaySetup = self.endFkCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.endFkCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.endGuide, **displaySetup)
        self.endFkCntrl.getParent().setParent(self.midFkCntrl)

        # cria controles ik com nomes e setagem de display vindas do spineDict
        displaySetup = self.startIkCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.startIkCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)
        self.startIkCntrl.getParent().setParent(self.cogCntrl)

        displaySetup = self.midIkCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.midIkCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.midGuide, **displaySetup)

        displaySetup = self.endIkCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.endIkCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.endGuide, **displaySetup)
        self.endIkCntrl.getParent().setParent(self.cogCntrl)

        # Cria os joints orientados em X down
        start = pm.xform(self.startGuide, q=True, t=True, ws=True)
        startTip = pm.xform(self.startTipGuide, q=True, t=True, ws=True)
        pm.select(cl=True)
        jntName = self.startJntSetup['nameTempl'] + self.zeroJxtSulfix
        self.startZeroJnt = pm.joint(p=(0, 0, 0), n=jntName)
        pm.select(cl=True)
        jntName = self.startJntSetup['nameTempl'] + self.jntSulfix
        self.startJnt = pm.joint(p=(0, 0, 0), n=jntName)
        self.skinJoints.append(self.startJnt)
        pm.select(cl=True)
        jntName = self.startJntSetup['nameTempl'] + self.tipJxtSulfix
        self.startTipJnt = pm.joint(p=(0, 0, 0), n=jntName)

        A = om.MVector(start)
        B = om.MVector(startTip)
        Z = om.MVector(0, 0, 1)
        AB = B - A

        dot = Z.normal() * AB.normal()  # se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        # vai acontecer qnd usarem a guide horizontal
        if abs(dot) > .95:
            Z = om.MVector(0, 1, 0)
        n = AB ^ Z

        m = matrixTools.orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)

        pm.xform(self.startZeroJnt, m=m, ws=True)
        pm.xform(self.startJnt, m=m, ws=True)
        pm.xform(self.startTipJnt, m=m, ws=True)
        pm.xform(self.startTipJnt, t=B, ws=True)
        pm.parent(self.startJnt, self.startZeroJnt)
        pm.parent(self.startTipJnt, self.startJnt)

        end = pm.xform(self.endGuide, q=True, t=True, ws=True)
        endTip = pm.xform(self.endTipGuide, q=True, t=True, ws=True)
        pm.select(cl=True)
        jntName = self.endJntSetup['nameTempl'] + self.zeroJxtSulfix
        self.endZeroJnt = pm.joint(p=(0, 0, 0), n=jntName)
        pm.select(cl=True)
        jntName = self.endJntSetup['nameTempl'] + self.jntSulfix
        self.endJnt = pm.joint(p=(0, 0, 0), n=jntName)
        self.skinJoints.append(self.endJnt)
        pm.select(cl=True)
        jntName = self.endJntSetup['nameTempl'] + self.tipJxtSulfix
        self.endTipJnt = pm.joint(p=(0, 0, 0), n=jntName)

        A = om.MVector(end)
        B = om.MVector(endTip)
        Z = om.MVector(0, 0, 1)
        AB = B - A

        dot = Z.normal() * AB.normal()  # se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        if abs(dot) > .95:
            Z = om.MVector(0, 1, 0)
        n = AB ^ Z
        m = matrixTools.orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)
        pm.xform(self.endZeroJnt, m=m, ws=True)
        pm.xform(self.endJnt, m=m, ws=True)
        pm.xform(self.endTipJnt, m=m, ws=True)
        pm.xform(self.endTipJnt, t=B, ws=True)
        pm.parent(self.endJnt, self.endZeroJnt)
        pm.parent(self.endTipJnt, self.endJnt)

        # cria os extratores de twist dos joints inicial e final
        # IMPLEMENTAR: twist do controle do meio
        twistExtractor1 = twistExtractor.twistExtractor(self.startJnt, flipAxis=True, name=self.name + 'TwistExtractor1')
        twistExtractor2 = twistExtractor.twistExtractor(self.endJnt, name=self.name + 'TwistExtractor2')
        twistExtractor1.extractorGrp.visibility.set(False)
        twistExtractor2.extractorGrp.visibility.set(False)

        # ribbon
        # calcular a distancia entre os guides pra fazer ribbon do tamanho certo
        A = om.MVector(start)
        B = om.MVector(end)
        Z = om.MVector(0, 0, -1)
        AB = B - A

        dot = Z.normal() * AB.normal()  # se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        if abs(dot) > .95:
            Z = om.MVector(0, -1, 0)

        spineRibbon = ribbonBezierSimple.RibbonBezierSimple(name=self.name + 'Ribbon_', size=AB.length(),
                                                            offsetStart=0.05, offsetEnd=0.05,
                                                            numJnts=self.ribbonJntNum)
        spineRibbon.doRig()
        self.skinJoints += spineRibbon.skinJoints
        # cria o sistema que vai orientar o controle do meio por calculo vetorial
        aimTwist = aimTwistDivider.AimTwistDivider(name=self.name + 'TwistDivider')
        aimTwist.start.setParent(spineRibbon.startCntrl, r=True)
        aimTwist.end.setParent(spineRibbon.endCntrl, r=True)
        aimTwist.mid.setParent(spineRibbon.moveall, r=True)

        # calculo para determinar a rotacao do ribbon
        # hardcoded orientacao X down do ribbon para funcionar com o extractor
        n = AB ^ Z
        x = n.normal() ^ AB.normal()
        t = x.normal() ^ n.normal()
        list = [t.x, t.y, t.z, 0, n.normal().x, n.normal().y, n.normal().z, 0, x.x * -1, x.y * -1, x.z * -1, 0, A.x,
                A.y, A.z, 1]
        m = om.MMatrix(list)
        pm.xform(spineRibbon.moveall, m=m, ws=True)

        ##Liga os controles do meio do ik e do meioOffset fk no aimTwist
        # eles trabalharam somente por translacao
        pm.pointConstraint(self.startIkCntrl, self.endIkCntrl, self.midIkCntrl.getParent(), mo=True)
        pm.orientConstraint(aimTwist.mid, self.midIkCntrl, mo=True)
        self.midIkCntrl.rotate.lock()
        self.midIkCntrl.rotate.setKeyable(0)
        pm.orientConstraint(aimTwist.mid, self.midFkOffsetCntrl, mo=True)
        self.midFkOffsetCntrl.rotate.lock()
        self.midFkOffsetCntrl.rotate.setKeyable(0)

        self.midIkCntrl.addAttr('twist', at='float', dv=0, k=1)
        self.midIkCntrl.twist >> spineRibbon.midCntrl.twist

        # faz os constraints do ribbon nos controles ik e fk pra fazer blend
        cns1 = pm.parentConstraint(self.startFkCntrl, self.startIkCntrl, spineRibbon.startCntrl, mo=True)
        mid = pm.xform(self.midGuide, q=True, t=True, ws=True)
        pm.xform(spineRibbon.midCntrl.getParent(), t=mid, ws=True)
        cns2 = pm.parentConstraint(self.midFkOffsetCntrl, self.midIkCntrl, spineRibbon.midCntrl, mo=True)
        cns3 = pm.parentConstraint(self.endFkCntrl, self.endIkCntrl, spineRibbon.endCntrl, mo=True)

        # parenteia os joints das pontas nos controles do ribbon
        self.startZeroJnt.setParent(spineRibbon.startCntrl.getParent())
        self.endZeroJnt.setParent(spineRibbon.endCntrl.getParent())
        # e cria os constraints point no start joint zero e orient no start joint
        # o joint zero eh necessario para o twist extractor
        pm.pointConstraint(spineRibbon.startCntrl, self.startZeroJnt, mo=True)
        pm.orientConstraint(spineRibbon.startCntrl, self.startJnt, mo=True)
        pm.pointConstraint(spineRibbon.endCntrl, self.endZeroJnt, mo=True)
        pm.orientConstraint(spineRibbon.endCntrl, self.endJnt, mo=True)

        # e parenteia todo mundo
        pm.parent(twistExtractor1.extractorGrp, twistExtractor2.extractorGrp, spineRibbon.moveall, self.cogCntrl)
        pm.parent(self.midIkCntrl.getParent(), self.cogCntrl.getParent(), self.moveall)

        # conecta os twist extractors nos twists do ribbon
        twistExtractor1.extractor.extractTwist >> spineRibbon.startCntrl.twist
        twistExtractor2.extractor.extractTwist >> spineRibbon.endCntrl.twist

        # cria o node tree do blend ikfk
        self.moveall.addAttr('ikfk', at='float', max=1, min=0, dv=1, k=1)
        ikfkRev = pm.createNode('reverse', n=self.name + 'IffkReverse')
        ikfkCond1 = pm.createNode('condition', n=self.name + 'IffkCond1')
        ikfkCond2 = pm.createNode('condition', n=self.name + 'IffkCond2')
        self.moveall.ikfk >> ikfkCond1.firstTerm
        self.moveall.ikfk >> ikfkCond2.firstTerm
        self.moveall.ikfk >> ikfkRev.inputX

        # visibilidade ik fk
        ikfkCond1.secondTerm.set(0)
        ikfkCond1.operation.set(2)
        ikfkCond1.colorIfTrueR.set(1)
        ikfkCond1.colorIfFalseR.set(0)
        ikfkCond1.outColorR >> self.startIkCntrl.getParent().visibility
        ikfkCond1.outColorR >> self.midIkCntrl.getParent().visibility
        ikfkCond1.outColorR >> self.endIkCntrl.getParent().visibility
        ikfkCond2.secondTerm.set(1)
        ikfkCond2.operation.set(4)
        ikfkCond2.colorIfTrueR.set(1)
        ikfkCond2.colorIfFalseR.set(0)
        ikfkCond2.outColorR >> self.startFkCntrl.getParent().visibility
        ikfkCond2.outColorR >> self.spineFkCntrl.getParent().visibility

        # blend dos constraints
        weightAttr = cns1.target.connections(p=True, t='parentConstraint')  # descobre parametros
        self.moveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]
        weightAttr = cns2.target.connections(p=True, t='parentConstraint')  # descobre parametros
        self.moveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]
        weightAttr = cns3.target.connections(p=True, t='parentConstraint')  # descobre parametros
        self.moveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]

        # IMPLEMENTAR guardar a posicao dos guides