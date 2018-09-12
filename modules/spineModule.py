import pymel.core as pm
import maya.api.OpenMaya as om
import autoRig3.tools.rigFunctions as rigFunctions
from autoRig3.modules import aimTwistDivider
from autoRig3.modules import ribbonBezierSimple
from autoRig3.modules import twistExtractor
import json

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

    def __init__(self, name='spine', flipAxis=False, axis='X', **kwargs):

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
        grpSulfix = '_grp'
        self.spineDict = {'name': name, 'axis': axis, 'flipAxis': flipAxis}

        self.setDefaults()

        self.spineDict.update(kwargs)


    def setDefaults(self):
        # dicionario q determina a aparencia dos controles
        self.spineDict['moveallSetup'] = {'nameTempl': self.name + 'MoveAll', 'icone': 'grp', 'size': 1.8,
                                          'color': (1, 1, 0)}
        self.spineDict['hipCntrlSetup'] = {'nameTempl': self.name + 'COG', 'icone': 'cog', 'size': 5.5,
                                           'color': (0, 0, 1)}
        self.spineDict['spineFkCntrlSetup'] = {'nameTempl': self.name + 'WaistFk', 'icone': 'circuloPontaY', 'size': 4,
                                               'color': (0, 1, 0)}
        self.spineDict['startFkCntrlSetup'] = {'nameTempl': self.name + 'HipFk', 'icone': 'circuloPontaY', 'size': 3.0,
                                               'color': (1, 1, 0)}
        self.spineDict['midFkOffsetCntrlSetup'] = {'nameTempl': self.name + 'AbdomenFkOff', 'icone': 'circuloY',
                                                   'size': 2.5, 'color': (1, 1, 0)}
        self.spineDict['midFkCntrlSetup'] = {'nameTempl': self.name + 'AbdomenFk', 'icone': 'circuloPontaY', 'size': 4,
                                             'color': (0, 1, 0)}
        self.spineDict['endFkCntrlSetup'] = {'nameTempl': self.name + 'ChestFk', 'icone': 'circuloPontaY', 'size': 4,
                                             'color': (0, 1, 0)}
        self.spineDict['startIkCntrlSetup'] = {'nameTempl': self.name + 'HipIk', 'icone': 'circuloPontaY', 'size': 4,
                                               'color': (1, 0, 0)}
        self.spineDict['midIkCntrlSetup'] = {'nameTempl': self.name + 'AbdomenIk', 'icone': 'circuloY', 'size': 4,
                                             'color': (1, 1, 0)}
        self.spineDict['endIkCntrlSetup'] = {'nameTempl': self.name + 'ChestIk', 'icone': 'circuloPontaY', 'size': 4,
                                             'color': (1, 0, 0)}

        self.spineDict['moveallGuideSetup'] = {'nameTempl': self.name + 'Moveall', 'size': 8, 'icone': 'quadradoY',
                                               'color': (1, 0, 0)}
        self.spineDict['startGuideSetup'] = {'nameTempl': self.name + 'Hip', 'size': 7, 'icone': 'circuloY',
                                             'color': (0, 1, 0)}
        self.spineDict['midGuideSetup'] = {'nameTempl': self.name + 'Abdomen', 'size': 7, 'icone': 'circuloY',
                                           'color': (0, 1, 0)}
        self.spineDict['endGuideSetup'] = {'nameTempl': self.name + 'Chest', 'size': 7, 'icone': 'circuloY',
                                           'color': (0, 1, 0)}
        self.spineDict['startTipGuideSetup'] = {'nameTempl': self.name + 'HipTip', 'size': 1, 'icone': 'bola',
                                                'color': (0, 1, 0)}
        self.spineDict['endTipGuideSetup'] = {'nameTempl': self.name + 'ChestTip', 'size': 1, 'icone': 'bola',
                                              'color': (0, 1, 0)}

        self.spineDict['startJntSetup'] = {'nameTempl': self.name + 'Hip', 'icone': 'Bone', 'size': 2}
        self.spineDict['endJntSetup'] = {'nameTempl': self.name + 'Chest', 'icone': 'Bone', 'size': 2}

        self.spineDict['guideDict'] = {}
        self.spineGuideDict = {'moveall': [(0, 0, 0), (0, 0, 0)], 'start': [(0, 0, 0), (0, 0, 0)],
                               'mid': [(0, 0, 0), (0, 0, 0)], 'end': [(0, 8, 0), (0, 0, 0)],
                               'startTip': [(0, -1, 0), (0, 0, 0)], 'endTip': [(0, 2, 0), (0, 0, 0)]}
        self.spineGuideDict.update(self.spineDict['guideDict'])
        self.spineDict['guideDict'] = self.spineGuideDict.copy()


    def createCntrl(self, cntrlName):
        displaySetup = self.spineDict[cntrlName+'Setup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        guide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True, **displaySetup)
        return guide

    def setCntrl (self, cntrl, posRot, space='object'):
        cntrl.setTranslation(self.spineDict['guideDict'][posRot][0], space=space)
        cntrl.setRotation(self.spineDict['guideDict'][posRot][1], space=space)

    def doGuide(self, **kwargs):
        self.spineDict.update(kwargs)

        displaySetup = self.spineDict['moveallGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.guideMoveall = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', **displaySetup)

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
        self.guideMoveall.spineDict.set(json.dumps(self.spineDict))

    def getGuideFromScene(self):
        guideName = self.spineDict['moveallGuideSetup']['nameTempl'] + self.guideSulfix
        self.guideMoveall = pm.PyNode(guideName)

        guideName = self.spineDict['startGuideSetup']['nameTempl'] + self.guideSulfix
        self.startGuide = pm.PyNode(guideName)

        guideName = self.spineDict['midGuideSetup']['nameTempl'] + self.guideSulfix
        self.midGuide = pm.PyNode(guideName)

        guideName = self.spineDict['endGuideSetup']['nameTempl'] + self.guideSulfix
        self.endGuide = pm.PyNode(guideName)

        guideName = self.spineDict['endTipGuideSetup']['nameTempl'] + self.guideSulfix
        self.endTipGuide = pm.PyNode(guideName)

        guideName = self.spineDict['startTipGuideSetup']['nameTempl'] + self.guideSulfix
        self.startTipGuide = pm.PyNode(guideName)

    def getDict(self):
        try:
            guideName = self.spineDict['moveallGuideSetup']['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.spineDict.get()
            dictRestored = json.loads(jsonDict)
            self.spineDict.update(**dictRestored)
            self.spineDict['guideDict']['moveall'] = rigFunctions.getObjTransforms (self.guideMoveall, 'world')

            guideName = self.spineDict['startGuideSetup']['nameTempl'] + self.guideSulfix
            self.startGuide = pm.PyNode(guideName)
            self.spineDict['guideDict']['start'] = rigFunctions.getObjTransforms (self.startGuide, 'object')

            guideName = self.spineDict['midGuideSetup']['nameTempl'] + self.guideSulfix
            self.midGuide = pm.PyNode(guideName)
            self.spineDict['guideDict']['mid'] = rigFunctions.getObjTransforms (self.midGuide, 'object')

            guideName = self.spineDict['endGuideSetup']['nameTempl'] + self.guideSulfix
            self.endGuide = pm.PyNode(guideName)
            self.spineDict['guideDict']['end'] = rigFunctions.getObjTransforms (self.endGuide, 'object')

            guideName = self.spineDict['endTipGuideSetup']['nameTempl'] + self.guideSulfix
            self.endTipGuide = pm.PyNode(guideName)
            self.spineDict['guideDict']['endTip'] = rigFunctions.getObjTransforms (self.endTipGuide, 'object')

            guideName = self.spineDict['startTipGuideSetup']['nameTempl'] + self.guideSulfix
            self.startTipGuide = pm.PyNode(guideName)
            self.spineDict['guideDict']['startTip'] = rigFunctions.getObjTransforms (self.startTipGuide, 'object')

        except:
            print 'algum nao funcionou'

        return self.spineDict

    def doRig(self):
        # se nao tiver guide, faz
        if not self.guideMoveall:
            self.doGuide()
        # se ja existir rig, apaga
        cntrlName = self.spineDict['moveallSetup']['nameTempl']

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
        displaySetup = self.spineDict['hipCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.cogCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)

        displaySetup = self.spineDict['spineFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.spineFkCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)
        self.spineFkCntrl.getParent().setParent(self.cogCntrl)

        displaySetup = self.spineDict['startFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.startFkCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)
        self.startFkCntrl.getParent().setParent(self.cogCntrl)

        displaySetup = self.spineDict['midFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.midFkCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.midGuide, **displaySetup)

        displaySetup = self.spineDict['midFkOffsetCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.midFkOffsetCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.midGuide,
                                                      **displaySetup)  # esse controle faz o offset do ribbon e permanece orientado corretamente
        self.midFkOffsetCntrl.getParent().setParent(self.midFkCntrl)
        self.midFkCntrl.getParent().setParent(self.spineFkCntrl)

        displaySetup = self.spineDict['endFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.endFkCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.endGuide, **displaySetup)
        self.endFkCntrl.getParent().setParent(self.midFkCntrl)

        # cria controles ik com nomes e setagem de display vindas do spineDict
        displaySetup = self.spineDict['startIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.startIkCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)
        self.startIkCntrl.getParent().setParent(self.cogCntrl)

        displaySetup = self.spineDict['midIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.midIkCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.midGuide, **displaySetup)

        displaySetup = self.spineDict['endIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.endIkCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.endGuide, **displaySetup)
        self.endIkCntrl.getParent().setParent(self.cogCntrl)

        # Cria os joints orientados em X down
        start = pm.xform(self.startGuide, q=True, t=True, ws=True)
        startTip = pm.xform(self.startTipGuide, q=True, t=True, ws=True)
        pm.select(cl=True)
        jntName = self.spineDict['startJntSetup']['nameTempl'] + self.zeroJxtSulfix
        self.startZeroJnt = pm.joint(p=(0, 0, 0), n=jntName)
        pm.select(cl=True)
        jntName = self.spineDict['startJntSetup']['nameTempl'] + self.jntSulfix
        self.startJnt = pm.joint(p=(0, 0, 0), n=jntName)
        self.skinJoints.append(self.startJnt)
        pm.select(cl=True)
        jntName = self.spineDict['startJntSetup']['nameTempl'] + self.tipJxtSulfix
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

        m = rigFunctions.orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)

        pm.xform(self.startZeroJnt, m=m, ws=True)
        pm.xform(self.startJnt, m=m, ws=True)
        pm.xform(self.startTipJnt, m=m, ws=True)
        pm.xform(self.startTipJnt, t=B, ws=True)
        pm.parent(self.startJnt, self.startZeroJnt)
        pm.parent(self.startTipJnt, self.startJnt)

        end = pm.xform(self.endGuide, q=True, t=True, ws=True)
        endTip = pm.xform(self.endTipGuide, q=True, t=True, ws=True)
        pm.select(cl=True)
        jntName = self.spineDict['endJntSetup']['nameTempl'] + self.zeroJxtSulfix
        self.endZeroJnt = pm.joint(p=(0, 0, 0), n=jntName)
        pm.select(cl=True)
        jntName = self.spineDict['endJntSetup']['nameTempl'] + self.jntSulfix
        self.endJnt = pm.joint(p=(0, 0, 0), n=jntName)
        self.skinJoints.append(self.endJnt)
        pm.select(cl=True)
        jntName = self.spineDict['endJntSetup']['nameTempl'] + self.tipJxtSulfix
        self.endTipJnt = pm.joint(p=(0, 0, 0), n=jntName)

        A = om.MVector(end)
        B = om.MVector(endTip)
        Z = om.MVector(0, 0, 1)
        AB = B - A

        dot = Z.normal() * AB.normal()  # se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        if abs(dot) > .95:
            Z = om.MVector(0, 1, 0)
        n = AB ^ Z
        m = rigFunctions.orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)
        pm.xform(self.endZeroJnt, m=m, ws=True)
        pm.xform(self.endJnt, m=m, ws=True)
        pm.xform(self.endTipJnt, m=m, ws=True)
        pm.xform(self.endTipJnt, t=B, ws=True)
        pm.parent(self.endJnt, self.endZeroJnt)
        pm.parent(self.endTipJnt, self.endJnt)

        # cria os extratores de twist dos joints inicial e final
        # IMPLEMENTAR: twist do controle do meio
        twistExtractor1 = twistExtractor.twistExtractor(self.startJnt)
        twistExtractor2 = twistExtractor.twistExtractor(self.endJnt)
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

        spineRibbon = ribbonBezierSimple.RibbonBezierSimple(name=self.name + 'Ribbon_', size=AB.length(), offsetStart=0.05,
                                                      offsetEnd=0.05)
        spineRibbon.doRig()
        self.skinJoints += spineRibbon.skinJoints
        # cria o sistema que vai orientar o controle do meio por calculo vetorial
        aimTwist = aimTwistDivider.AimTwistDivider()
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
        ikfkRev = pm.createNode('reverse')
        ikfkCond1 = pm.createNode('condition')
        ikfkCond2 = pm.createNode('condition')
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