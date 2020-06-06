import pymel.core as pm
from autoRig3.modules import fingerModule
import autoRig3.tools.controlTools as controlTools
import json
import logging

logger = logging.getLogger('autoRig')

class Hand:
    """
        Cria uma mao
        Parametros:
            name (string): nome da mao
            folds (int): quantas dobras os dedos terao
            fingerNum (int): quantos dedos tera a mao
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone
    """

    ## IMPLEMENTAR:
    #  os nomes derivados do handDict
    #  um handDict melhor q possa ser passado como parametro
    #  funcionalidades do conjunto da mao como curl lateral e offset para abrir e fechar todos os dedos

    def __init__(self, name='hand', axis='X', flipAxis=False, fingers=None, **kwargs):
        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'
        self.grpSulfix = '_grp'
        self.fingerInstances = {}
        self.toExport = {'name', 'axis', 'flipAxis', 'guideDict', 'moveallGuideSetup', 'fingers', 'fingerNum'}

        if not fingers:
            fingers = [('Thumb', 1), ('Index', 2), ('Middle', 2), ('Ring', 2), ('Pinky', 2)]
            self.fingerNum = 5
        else:
            self.fingerNum = len(fingers)

        self.fingers = {}
        self.name = name
        self.axis = axis
        self.flipAxis = flipAxis
        self.skinJoints = []
        self.guideMoveall = None
        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)]}
        self.moveallGuideSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'quadradoX',
                                              'size': 1.5, 'color': (1, 0, 0)}

        for i, finger in enumerate(fingers):
            fingerName = self.name + finger[0]
            fingerOffset = (((self.fingerNum / 2) * .3) - (i * .3))
            self.fingers[finger[0]] = {'name': fingerName,
                                       'folds': finger[1],
                                       'fingerId': i,
                                       'guideDict': {
                                                       'moveall': [(0, 0, fingerOffset), (0, 0, 0), (1, 1, 1)],
                                                       'palm': [(0, 0, 0), (0, 0, 0)],
                                                       'base': [(1, 0, 0), (0, 0, 0)],
                                                       'tip': [(2, 0, 0), (0, 0, 0)],
                                                       'fold1': [(0, 0.05, 0), (0, 0, 0)],
                                                       'fold2': [(0, 0, 0), (0, 0, 0)]
                                                    }}
            f = fingerModule.Finger(name=fingerName, fingerId=i, axis=self.axis, flipAxis=self.flipAxis, folds=finger[1],
                                    cntrlColor=(1.0, 1.0, 0.15))
            self.fingerInstances[finger[0]] = f

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

        self.guideMoveall = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='',
                                                  hasHandle=True, **displaySetup)

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

        for fgr in self.fingers:
            f = self.fingerInstances[fgr]
            f.doGuide(guideDict=self.fingers[fgr]['guideDict'])
            pm.parent(f.guideMoveall, self.guideMoveall)

        self.guideMoveall.setTranslation(self.guideDict['moveall'][0], space='world')
        self.guideMoveall.setRotation(self.guideDict['moveall'][1], space='world')
        self.guideMoveall.setScale(self.guideDict['moveall'][2], space='object')

        pm.addAttr(self.guideMoveall, ln='handDict', dt='string')
        self.guideMoveall.handDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + '_guide'
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.handDict.get()
            dictRestored = json.loads(jsonDict)
            self.__dict__.update(**dictRestored)

            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            for finger in self.fingers:
                instance = self.fingerInstances[finger]
                fingerDict = instance.getDict()

                self.fingers[finger] = fingerDict
        except:
            pass

    def mirrorConnectGuide(self, hand):
        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')
            self.guideMoveall = None

        if not self.guideMoveall:
            self.doGuide()
        if not hand.guideMoveall:
            hand.doGuide()

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')
        if not pm.objExists('GUIDES'):
            pm.group(self.name + 'MirrorGuide_grp', n='GUIDES')
        else:
            pm.parent(self.name + 'MirrorGuide_grp', 'GUIDES')

        self.guideMoveall.setParent(self.mirrorGuide)

        #Felipe --> seta valores globais de escala
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.scaleY.set(1)
        self.mirrorGuide.scaleZ.set(1)
        self.mirrorGuide.scale.lock()
        self.mirrorGuide.rotate.lock()
        self.mirrorGuide.translate.lock()
        self.mirrorGuide.template.set(1)

        hand.guideMoveall.translate >> self.guideMoveall.translate
        hand.guideMoveall.rotate >> self.guideMoveall.rotate
        hand.guideMoveall.scale >> self.guideMoveall.scale

        for a, b in zip(self.fingers, hand.fingers):
            f_mirror = self.fingerInstances[a]
            f_origin = hand.fingerInstances[b]

            f_origin.guideMoveall.translate >> f_mirror.guideMoveall.translate
            f_origin.guideMoveall.rotate >> f_mirror.guideMoveall.rotate
            f_origin.guideMoveall.scale >> f_mirror.guideMoveall.scale
            f_origin.palmGuide.translate >> f_mirror.palmGuide.translate
            f_origin.palmGuide.rotate >> f_mirror.palmGuide.rotate
            f_origin.baseGuide.translate >> f_mirror.baseGuide.translate
            f_origin.baseGuide.rotate >> f_mirror.baseGuide.rotate
            f_origin.baseGuide.scale >> f_mirror.baseGuide.scale
            f_origin.tipGuide.translate >> f_mirror.tipGuide.translate
            f_origin.tipGuide.rotate >> f_mirror.tipGuide.rotate
            f_origin.tipGuide.scale >> f_mirror.tipGuide.scale
            f_origin.fold1Guide.translate >> f_mirror.fold1Guide.translate
            f_origin.fold1Guide.rotate >> f_mirror.fold1Guide.rotate
            f_origin.fold1Guide.scale >> f_mirror.fold1Guide.scale

            if self.fingers[a]['folds'] == 2:
                f_origin.fold2Guide.translate >> f_mirror.fold2Guide.translate
                f_origin.fold2Guide.rotate >> f_mirror.fold2Guide.rotate
                f_origin.fold2Guide.scale >> f_mirror.fold2Guide.scale

        self.guideMoveall.handDict.set(json.dumps(self.exportDict()))

    def doRig(self, **kwargs):

        relaxOps1 = [[], [1], [.2, 1], [.2, .6, 1.0], [0.1, .33, .66, 1.0], [.2, .4, .6, .8, 1.0]]
        relaxOps2 = [[], [-1], [-1, -.2], [-1.0, -.6, -.2], [-1.0, -.66, -.33, -.1], [-1.0, -.8, -.6, -.4, -.2, ]]
        spreadOps = [[], [0], [-1, 1], [-1, -.1, 1], [-1, -.2, .3, 1], [-1, -.4, -.1, .4, 1]]

        thumb = [x for x in self.fingers if self.fingers[x]['fingerId'] == 0]
        relax1 = relaxOps1[len(self.fingers) - len(thumb)]
        relax2 = relaxOps2[len(self.fingers) - len(thumb)]
        spread = spreadOps[len(self.fingers) - len(thumb)]

        if not self.guideMoveall:
            self.doGuide()

        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')

        self.moveall = pm.group(n=self.name + 'Moveall', em=True)
        pos = pm.xform(self.guideMoveall, q=True, ws=True, t=True)
        pm.xform(self.moveall, ws=True, t=pos)

        if not pm.objExists('MOVEALL'):
            pm.group(self.moveall, n='MOVEALL')
        else:
            pm.parent(self.moveall, 'MOVEALL')


        globalCtrl = pm.curve( n=self.name+'GlobalFinger_cntrl',
                               d=1,
                               p=[(0, 0.25, 0), (0, 0, 0.25), (0.25, 0, 0), (0, 0.25, 0),
                                  (0, 0, -0.25), (0.25, 0, 0), (0, -0.25, 0), (0, 0, -0.25),
                                  (-0.25, 0, 0), (0, -0.25, 0), (0, 0, 0.25), (-0.25, 0, 0),
                                  (0, 0.25, 0)],
                               k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        globalCtrl.getShape().overrideEnabled.set(True)
        globalCtrlGrp = pm.group(n=self.name+'GlobalFinger_grp')
        pm.parent(globalCtrlGrp, self.moveall, r=True)
        globalCtrlGrp.translate.set(.5, .75, 0)

        globalCtrl.addAttr('curl', k=1, at=float, dv=0)
        globalCtrl.addAttr('lean', k=1, at=float, dv=0)
        globalCtrl.addAttr('scrunch', k=1, at=float, dv=0)
        globalCtrl.addAttr('spread', k=1, at=float, dv=0)
        globalCtrl.addAttr('twist', k=1, at=float, dv=0)
        globalCtrl.addAttr('relax', k=1, at=float, dv=0)

        for finger in self.fingers:
            i = 0

            f = self.fingerInstances[finger]
            f.flipAxis = self.flipAxis
            f.doRig()
            self.skinJoints += f.skinJoints
            pm.parent(f.moveall, self.moveall)
            i = f.fingerId - 1

            if f.fingerId != 0:
                ctrlBase = f.cntrl1
                twist_PMA = pm.listConnections(ctrlBase.twist, d=True)[0]
                globalCtrl.twist >> twist_PMA.input2D[1].input2Dx

                curl_PMA = pm.listConnections(ctrlBase.curl, d=True, t='plusMinusAverage')
                relaxMDL1 = pm.createNode('multDoubleLinear', n=self.name + 'RelaxMulti1')
                relaxMDL1.input2.set(relax1[i])
                globalCtrl.relax >> relaxMDL1.input1

                relaxMDL2 = pm.createNode('multDoubleLinear', n=self.name + 'RelaxMulti1')
                relaxMDL2.input2.set(relax2[i])
                globalCtrl.relax >> relaxMDL2.input1

                cond = pm.createNode('condition', n=self.name + 'RelaxCond')
                globalCtrl.relax >> cond.firstTerm
                cond.secondTerm.set(0)
                cond.operation.set(2)
                relaxMDL1.output >> cond.colorIfTrue.colorIfTrueR
                relaxMDL2.output >> cond.colorIfFalse.colorIfFalseR

                for node in curl_PMA:
                    globalCtrl.curl >> node.input1D[3]
                    cond.outColor.outColorR >> node.input1D[4]

                lean_PMA = pm.listConnections(ctrlBase.lean, d=True, t='plusMinusAverage')
                for node in lean_PMA:
                    globalCtrl.lean >> node.input2D[2].input2Dy

                scrunch_MDL = pm.listConnections(ctrlBase.scrunch, d=True, )
                scrunch_PMA = []
                multi = []
                for node in scrunch_MDL:
                    multi.append(node.input2.get())
                    scrunch_PMA = scrunch_PMA + pm.listConnections(node, d=True, t='plusMinusAverage')
                for j, node in enumerate(scrunch_PMA):
                    MDL = pm.createNode('multDoubleLinear', n=self.name + 'ScrunchMulti')
                    globalCtrl.scrunch >> MDL.input1
                    MDL.input2.set(multi[j])
                    MDL.output >> node.input1D[5]

                spread_PMA = pm.listConnections(ctrlBase.spread, d=True, t='plusMinusAverage')[0]
                spread_MDL = pm.createNode('multDoubleLinear', n=self.name + 'SpreadMulti')
                globalCtrl.spread >> spread_MDL.input1
                spread_MDL.input2.set(spread[i])
                spread_MDL.output >> spread_PMA.input2D[3].input2Dy
