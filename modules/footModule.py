import pymel.core as pm
import maya.api.OpenMaya as om
from autoRig3.modules import fingerModule
import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.matrixTools as matrixTools
import autoRig3.tools.jointTools as jointTools
import json
import logging

logger = logging.getLogger('autoRig')

## versao 2.0 16/01/2019: LEO -  eliminando o dicionario e transferindo para variaveis do objeto

#VERSAO 1.1
# 01/11/2018 - FELIPE GIMENES:
#  - corrigido sentido dos footRolls
#  - incluida atualizacao de escala dos guides

class Foot:
    """
        Cria um pe
        Parametros:
            name (string): nome do novo pe
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone

    """

    # IMPLEMENTAR:
    # guides com restricao de rotacao
    # Dedos do pe

    def __init__(self, name='foot', flipAxis=False, axis='X', fingers=None, **kwargs):

        if not fingers:
            fingers = [('Thumb', 1), ('Index', 2), ('Middle', 2), ('Ring', 2), ('Pinky', 2)]
            self.fingerNum = 5
        else:
            self.fingerNum = len(fingers)


        self.fingers = {}
        self.name = name
        self.flipAxis = flipAxis
        self.axis = axis
        self.skinJoints = []
        self.guideMoveall = None

        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'
        self.grpSulfix = '_grp'

        self.toExport = {'slideCntrlSetup', 'tipCntrlSetup', 'moveallCntrlSetup', 'toLimbCntrlSetup', 'ankleFkCntrlSetup',
                         'jointGuideSetup', 'axis', 'toeFkCntrlSetup', 'inGuideSetup', 'ankleJntSetup', 'ballGuideSetup',
                         'ankleGuideSetup', 'rollCntrlSetup', 'rollGuideSetup', 'outGuideSetup', 'toeGuideSetup',
                         'fingerNames', 'outCntrlSetup', 'heelGuideSetup', 'fingers', 'heelCntrlSetup', 'ballCntrlSetup',
                         'baseGuideSetup', 'name', 'moveallGuideSetup', 'slideGuideSetup', 'centerCntrlSetup',
                         'baseCntrlSetup', 'toeCntrlSetup', 'toeJntSetup', 'ankleCntrlSetup', 'centerGuideSetup',
                         'flipAxis', 'inCntrlSetup', 'tipGuideSetup', 'guideDict'}

        self.moveallCntrlSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'circuloX', 'size': 1.8,
                                              'color': (1, 1, 0)}
        self.centerCntrlSetup = {'nameTempl': self.name + 'Center', 'icone': 'circuloX', 'size': 2,
                                             'color': (0, 0, 1)}
        self.tipCntrlSetup = {'nameTempl': self.name + 'Tip', 'icone': 'bola', 'size': 0.5,
                                          'color': (0, 1, 1)}
        self.heelCntrlSetup = {'nameTempl': self.name + 'Heel', 'icone': 'bola', 'size': 0.5,
                                           'color': (0, 1, 1)}
        self.ankleCntrlSetup = {'nameTempl': self.name + 'Ankle', 'icone': 'cubo', 'size': 1,
                                            'color': (0, 1, 1)}
        self.ballCntrlSetup = {'nameTempl': self.name + 'Ball', 'icone': 'circuloX', 'size': 1.5,
                                           'color': (0.01, 0.05, 0.2 )}
        self.inCntrlSetup = {'nameTempl': self.name + 'In', 'icone': 'bola', 'size': 0.4,
                                         'color': (0, 1, 1)}
        self.outCntrlSetup = {'nameTempl': self.name + 'Out', 'icone': 'bola', 'size': 0.4,
                                          'color': (0, 1, 1)}
        self.rollCntrlSetup = {'nameTempl': self.name + 'Roll', 'icone': 'cubo', 'size': 0.4,
                                           'color': (0, .6, 1)}
        self.baseCntrlSetup = {'nameTempl': self.name + 'Base', 'icone': 'cubo', 'size': 3,
                                           'color': (0, 0, 1)}
        self.slideCntrlSetup = {'nameTempl': self.name + 'Slide', 'icone': 'bola', 'size': 0.4,
                                            'color': (0, 1, 1)}
        self.toLimbCntrlSetup = {'nameTempl': self.name + 'ToLimb', 'icone': 'grp', 'size': 0.5,
                                             'color': (1, 1, 0)}
        self.toeCntrlSetup = {'nameTempl': self.name + 'Toe', 'icone': 'circuloX', 'size': 1.0,
                                          'color': (0.01, 0.05, 0.2 )}

        self.ankleFkCntrlSetup = {'nameTempl': self.name + 'AnkleFk', 'icone': 'grp', 'size': 1.0,
                                              'color': (0, 1, 0)}
        self.toeFkCntrlSetup = {'nameTempl': self.name + 'ToeFk', 'icone': 'circuloX', 'size': 1.0,
                                            'color': (0.01, 0.05, 0.2)}

        self.moveallGuideSetup = {'nameTempl': self.name + 'MoveAll', 'size': 1.8, 'icone': 'quadradoY',
                                              'color': (1, 0, 0)}
        self.centerGuideSetup = {'nameTempl': self.name + 'Center', 'size': .5, 'icone': 'grp',
                                             'color': (1, 1, 0)}
        self.tipGuideSetup = {'nameTempl': self.name + 'Tip', 'size': 0.5, 'icone': 'bola',
                                          'color': (0, 1, 1)}
        self.heelGuideSetup = {'nameTempl': self.name + 'Heel', 'size': 0.5, 'icone': 'bola',
                                           'color': (0, 1, 1)}
        self.ankleGuideSetup = {'nameTempl': self.name + 'Ankle', 'size': 0.5, 'icone': 'bola',
                                            'color': (0, 1, 1)}
        self.ballGuideSetup = {'nameTempl': self.name + 'Ball', 'size': 0.5, 'icone': 'bola',
                                           'color': (0, 1, 1)}
        self.inGuideSetup = {'nameTempl': self.name + 'In', 'size': 0.4, 'icone': 'bola',
                                         'color': (0, 0, 1)}
        self.outGuideSetup = {'nameTempl': self.name + 'Out', 'size': 0.4, 'icone': 'bola',
                                          'color': (0, 0, 1)}
        self.rollGuideSetup = {'nameTempl': self.name + 'Roll', 'size': 0.4, 'icone': 'bola',
                                           'color': (1, 0, 1)}
        self.baseGuideSetup = {'nameTempl': self.name + 'Base', 'size': 3, 'icone': 'quadradoY',
                                           'color': (1, 0, 1)}
        self.slideGuideSetup = {'nameTempl': self.name + 'Slide', 'size': 0.4, 'icone': 'null',
                                            'color': (1, 0, 1)}
        self.jointGuideSetup = {'nameTempl': self.name + 'Joint', 'size': 0.5, 'icone': 'null',
                                            'color': (1, 0, 1)}
        self.toeGuideSetup = {'nameTempl': self.name + 'Toe', 'size': 1.0, 'icone': 'null',
                                          'color': (1, 1, 0)}

        self.fingerInstances = {}
        self.fingerNames = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Other', 'Other1']

        self.ankleJntSetup = {'nameTempl': self.name + 'Ankle', 'icone': 'Bone', 'size': 1.0}
        self.toeJntSetup = {'nameTempl': self.name + 'Toe', 'icone': 'Bone', 'size': 1.0}
        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), [1, 1, 1]], 'center': [(0, 0, 0), (0, 0, 0)],
                              'tip': [(3, 0, 0), (0, 0, 0)], 'heel': [(-1, 0, 0), (0, 0, 0)],
                              'ankle': [(0, 1, 0), (0, 0, 0)], 'ball': [(-1, 0.5, 0), (0, 0, 0)],
                              'in': [(-1, 0, -1), (0, 0, 0)], 'out': [(-1, 0, 1), (0, 0, 0)]}

        for i, finger in enumerate(fingers):
            fingerName = self.name + finger[0]
            fingerOffset = (((self.fingerNum / 2) * .3) - (i * .3))
            self.fingers[finger[0]] = {'name': fingerName,
                                       'folds': finger[1],
                                       'fingerId': i,
                                       'isHeelFinger': False,
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

    def getCntrlXform(self, key, cntrl, space='object'):
        pos = self.guideDict[key][0] = cntrl.getTranslation(space='world').get()
        rot = self.guideDict[key][1] = tuple(cntrl.getRotation(space='world'))
        return [pos, rot]

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

        self.guideMoveall = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                  **displaySetup)

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

        # cria guides segundo os nomes dos controles e nas posicoes definidas no dicionario footGuideDict

        self.centerGuide = self.createCntrl('centerGuide')

        guideName = self.centerGuideSetup['nameTempl'] + self.grpSulfix
        self.centerGuideGrp = pm.group(self.centerGuide, n=guideName)

        self.tipGuide = self.createCntrl('tipGuide')
        self.heelGuide = self.createCntrl('heelGuide')
        self.ankleGuide = self.createCntrl('ankleGuide')
        self.ballGuide = self.createCntrl('ballGuide')
        self.inGuide =  self.createCntrl('inGuide')
        self.outGuide = self.createCntrl('outGuide')

        for finger in self.fingers:
            f = self.fingerInstances[finger] 
            f.doGuide(guideDict=self.fingers[finger]['guideDict'])
            pm.parent(f.guideMoveall, self.tipGuide)

        # pm.parent (self.fingerGrp, self.tipGuide)
        pm.parent(self.ballGuide, self.inGuide, self.outGuide, self.tipGuide)
        self.ankleGuide.setParent(self.centerGuide)
        pm.parent(self.centerGuideGrp, self.tipGuide, self.heelGuide, self.guideMoveall)

        self.setCntrl(self.tipGuide, 'tip', space='object')
        self.setCntrl(self.heelGuide, 'heel', space='object')
        self.setCntrl(self.ankleGuide, 'ankle', space='object')
        self.setCntrl(self.ballGuide, 'ball', space='object')
        self.setCntrl(self.inGuide, 'in', space='object')
        self.setCntrl(self.outGuide, 'out', space='object')

        pm.pointConstraint(self.tipGuide, self.heelGuide, self.centerGuideGrp)
        pm.pointConstraint(self.tipGuide, self.centerGuideGrp, e=True, w=0.25)
        pm.pointConstraint(self.heelGuide, self.centerGuideGrp, e=True, w=0.75)

        pm.aimConstraint(self.heelGuide, self.tipGuide, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0),
                         worldUpVector=(0, 1, 0), worldUpType='objectrotation' , worldUpObject=self.guideMoveall)
        pm.aimConstraint(self.tipGuide, self.centerGuide, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                         worldUpVector=(0, 1, 0), worldUpType='objectrotation' , worldUpObject=self.guideMoveall)

        self. setCntrl(self.guideMoveall, 'moveall', space='world')

        pm.addAttr(self.guideMoveall, ln='footDict', dt='string')
        #todo implementar funcao pra exportar dict
        self.guideMoveall.footDict.set(json.dumps(self.exportDict()))

        guideShape = self.guideMoveall.getShape()
        guideShape.template.set(1)


    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + '_guide'
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.footDict.get()
            dictRestored = json.loads(jsonDict)
            self.__dict__.update(**dictRestored)

            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))
            #Felipe --> armazena valores de escala nos dict

            guideName = self.centerGuideSetup['nameTempl'] + self.guideSulfix
            self.centerGuide = pm.PyNode(guideName)
            self.guideDict['center'][0] = self.centerGuide.getTranslation(space='object').get()
            self.guideDict['center'][1] = tuple(self.centerGuide.getRotation(space='object'))


            guideName = self.centerGuideSetup['nameTempl'] + self.grpSulfix
            self.centerGuideGrp = pm.PyNode(guideName)

            guideName = self.tipGuideSetup['nameTempl'] + self.guideSulfix
            self.tipGuide = pm.PyNode(guideName)
            self.guideDict['tip'][0] = self.tipGuide.getTranslation(space='object').get()
            self.guideDict['tip'][1] = tuple(self.tipGuide.getRotation(space='object'))


            guideName = self.heelGuideSetup['nameTempl'] + self.guideSulfix
            self.heelGuide = pm.PyNode(guideName)
            self.guideDict['heel'][0] = self.heelGuide.getTranslation(space='object').get()
            self.guideDict['heel'][1] = tuple(self.heelGuide.getRotation(space='object'))


            guideName = self.ankleGuideSetup['nameTempl'] + self.guideSulfix
            self.ankleGuide = pm.PyNode(guideName)
            self.guideDict['ankle'][0] = self.ankleGuide.getTranslation(space='object').get()
            self.guideDict['ankle'][1] = tuple(self.ankleGuide.getRotation(space='object'))

            guideName = self.ballGuideSetup['nameTempl'] + self.guideSulfix
            self.ballGuide = pm.PyNode(guideName)
            self.guideDict['ball'][0] = self.ballGuide.getTranslation(space='object').get()
            self.guideDict['ball'][1] = tuple(self.ballGuide.getRotation(space='object'))

            guideName = self.inGuideSetup['nameTempl'] + self.guideSulfix
            self.inGuide = pm.PyNode(guideName)
            self.guideDict['in'][0] = self.inGuide.getTranslation(space='object').get()
            self.guideDict['in'][1] = tuple(self.inGuide.getRotation(space='object'))

            guideName = self.outGuideSetup['nameTempl'] + self.guideSulfix
            self.outGuide = pm.PyNode(guideName)
            self.guideDict['out'][0] = self.outGuide.getTranslation(space='object').get()
            self.guideDict['out'][1] = tuple(self.outGuide.getRotation(space='object'))

            for finger in self.fingers:
                fingerDict = self.fingerInstances[finger].getDict()
                self.fingers[finger].update(fingerDict)

        except:
            pass

    def mirrorConnectGuide(self, foot):
        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')
            self.guideMoveall = None

        if not self.guideMoveall:
            self.doGuide()

        if not foot.guideMoveall:
            foot.doGuide(**self.guideDict)

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')

        if not pm.objExists('GUIDES'):
            pm.group(self.mirrorGuide, n='GUIDES')
        else:
            pm.parent(self.mirrorGuide, 'GUIDES')

        self.guideMoveall.setParent(self.mirrorGuide)

        scaleValue = tuple(pm.xform(foot.guideMoveall, q=True, s=True, ws=True))
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.scaleY.set(1)
        self.mirrorGuide.scaleZ.set(1)
        self.mirrorGuide.scale.lock()
        self.mirrorGuide.rotate.lock()
        self.mirrorGuide.translate.lock()
        self.mirrorGuide.template.set(1)


        foot.guideMoveall.translate >> self.guideMoveall.translate
        foot.guideMoveall.rotate >> self.guideMoveall.rotate
        foot.guideMoveall.scale >> self.guideMoveall.scale

        foot.centerGuide.translate >> self.centerGuide.translate
        foot.centerGuide.rotate >> self.centerGuide.rotate
        foot.centerGuide.scale >> self.centerGuide.scale

        foot.tipGuide.translate >> self.tipGuide.translate
        foot.tipGuide.rotate >> self.tipGuide.rotate
        foot.tipGuide.scale >> self.tipGuide.scale

        foot.heelGuide.translate >> self.heelGuide.translate
        foot.heelGuide.rotate >> self.heelGuide.rotate
        foot.heelGuide.scale >> self.heelGuide.scale

        foot.ankleGuide.translate >> self.ankleGuide.translate
        foot.ankleGuide.rotate >> self.ankleGuide.rotate
        foot.ankleGuide.scale >> self.ankleGuide.scale

        foot.ballGuide.translate >> self.ballGuide.translate
        foot.ballGuide.rotate >> self.ballGuide.rotate
        foot.ballGuide.scale >> self.ballGuide.scale

        foot.inGuide.translate >> self.inGuide.translate
        foot.inGuide.rotate >> self.inGuide.rotate
        foot.inGuide.scale >> self.inGuide.scale

        foot.outGuide.translate >> self.outGuide.translate
        foot.outGuide.rotate >> self.outGuide.rotate
        foot.outGuide.scale >> self.outGuide.scale

        for a, b in zip(self.fingers, foot.fingers):
            f_mirror = self.fingerInstances[a]
            f_origin = foot.fingerInstances[b]

            f_origin.guideMoveall.translate >> f_mirror.guideMoveall.translate
            f_origin.guideMoveall.rotate >> f_mirror.guideMoveall.rotate
            f_origin.guideMoveall.scale >> f_mirror.guideMoveall.scale
            f_origin.palmGuide.translate >> f_mirror.palmGuide.translate
            f_origin.palmGuide.rotate >> f_mirror.palmGuide.rotate
            f_origin.palmGuide.scale >> f_mirror.palmGuide.scale
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

        if foot.flipAxis:
            self.flipAxis = False
        else:
            self.flipAxis = True

        self.guideMoveall.footDict.set(json.dumps(self.exportDict()))

    def doRig(self):
        relaxOps1 = [[], [1], [.2, 1], [.2, .6, 1.0], [0.1, .33, .66, 1.0], [.2, .4, .6, .8, 1.0]]
        relaxOps2 = [[], [-1], [-1, -.2], [-1.0, -.6, -.2], [-1.0, -.66, -.33, -.1], [-1.0, -.8, -.6, -.4, -.2 ]]
        spreadOps = [[], [0], [-1, 1], [-1, -.1, 1], [-1, -.2, .3, 1], [-1, -.4, -.1, .4, 1]]

        #thumb = [x for x in self.fingers if self.fingers[x]['fingerId'] == 0]
        thumb=[]
        relax1 = relaxOps1[len(self.fingers) - len(thumb)]
        relax2 = relaxOps2[len(self.fingers) - len(thumb)]
        spread = spreadOps[len(self.fingers) - len(thumb)]

        if not self.guideMoveall:
            self.doGuide()

        cntrlName = self.moveallCntrlSetup['nameTempl']

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        # esqueleto
        center = pm.xform(self.centerGuide, q=True, ws=True, t=True)
        tip = pm.xform(self.tipGuide, q=True, ws=True, t=True)
        ankle = pm.xform(self.ankleGuide, q=True, ws=True, t=True)
        ball = pm.xform(self.ballGuide, q=True, ws=True, t=True)

        A = om.MVector(ankle)
        B = om.MVector(center)
        C = om.MVector(tip)
        D = om.MVector(ball)

        # calcula a normal do sistema no triangulo entre center, ankle e tip.
        # pode ser q isso de problemas se mal colocados.
        # IMPLEMENTAR limites dos guides para evitar ma colocacao

        if self.flipAxis:
            AB = A - B
            BC = B - C
            AD = A - D
            CD = D - C
        else:
            AB = B - A
            BC = C - B
            AD = D - A
            CD = C - D

        n =  AB ^ BC

        pm.select(cl=True)
        m = matrixTools.orientMatrix(mvector=AD, normal=n, pos=A, axis=self.axis)
        jntName = self.ankleJntSetup['nameTempl'] + self.jntSulfix
        j1 = pm.joint(n=jntName)
        self.skinJoints.append(j1)
        pm.xform(j1, m=m, ws=True)
        pm.makeIdentity(j1, apply=True, r=1, t=0, s=1, n=0, pn=0)

        # cria os joints
        m = matrixTools.orientMatrix(mvector=CD, normal=n, pos=D, axis=self.axis)
        jntName = self.toeJntSetup['nameTempl'] + self.jntSulfix
        j2 = pm.joint(n=jntName)
        self.skinJoints.append(j2)
        pm.xform(j2, m=m, ws=True)
        pm.makeIdentity(j2, apply=True, r=1, t=0, s=1, n=0, pn=0)

        jntName = self.toeJntSetup['nameTempl'] + self.tipJxtSulfix
        j3 = pm.joint(n=jntName)
        self.skinJoints.append(j3)
        pm.xform(j3, m=m, ws=True)
        pm.xform(j3, t=C, ws=True)
        pm.makeIdentity(j3, apply=True, r=1, t=0, s=1, n=0, pn=0)
        # e faz os ikhandles
        ballIkh = pm.ikHandle(n=self.name+'ballIKHandle', sj=j1, ee=j2, sol="ikRPsolver")
        tipIkh = pm.ikHandle(n=self.name+'toeIKHandle',sj=j2, ee=j3, sol="ikRPsolver")

        self.moveall = pm.group(em=True, n=cntrlName)
        self.moveall.translate.set(center)
        if not pm.objExists('MOVEALL'):
            pm.group(self.moveall, n='MOVEALL')
        else:
            pm.parent(self.moveall, 'MOVEALL')

        # esse controle deve levar o controle ik da ponta do limb para funcionar o pe
        displaySetup = self.toLimbCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.limbConnectionCntrl = controlTools.cntrlCrv(name=cntrlName, obj=j1, connType='parentConstraint', cntrlSulfix = "_null",
                                                         **displaySetup)

        # base cntrl
        displaySetup = self.baseCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.baseCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.centerGuide, **displaySetup)
        pm.move(.8, 0.225, 0, self.baseCntrl, r=True, os=True)
        pm.xform(self.baseCntrl, rp=ankle, ws=True)
        pm.scale(self.baseCntrl, [1, .15, .5], r=True)
        pm.makeIdentity(self.baseCntrl, apply=True, r=0, t=1, s=1, n=0, pn=0)
        self.baseCntrl.addAttr('extraRollCntrls', min=0, max=1, dv=0, k=1)

        # slidePivot
        displaySetup = self.slideCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        slideCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.centerGuide, **displaySetup)
        slideCompensateGrp = pm.group(em=True, n=self.name + 'Slide_grp')
        pm.parent(slideCompensateGrp, slideCntrl, r=True)
        slideMulti = pm.createNode('multiplyDivide', n=self.name+'slideMulti')
        slideCntrl.translate >> slideMulti.input1
        slideMulti.input2.set(-1, -1, -1)
        slideMulti.output >> slideCompensateGrp.translate

        # bank cntrls
        displaySetupOut = self.outCntrlSetup.copy()
        outNameCntrl = displaySetupOut['nameTempl']
        outCntrl = controlTools.cntrlCrv(name=outNameCntrl, obj=self.inGuide, **displaySetup)
        displaySetup = self.inCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        inCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.outGuide, **displaySetup)
        self.baseCntrl.extraRollCntrls >> inCntrl.getParent().visibility

        # tip/heel
        displaySetup = self.tipCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        tipCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.tipGuide, **displaySetup)

        displaySetup = self.heelCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        heelCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.heelGuide, **displaySetup)

        # toe
        displaySetup = self.toeCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        toeCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.ballGuide, **displaySetup)
        toeCntrl.translate.set(0.5, 0, 0)
        pm.makeIdentity(toeCntrl, apply=True, r=0, t=1, s=0, n=0, pn=0)
        pm.xform(toeCntrl, rp=(-0.5, 0, 0), r=True)

        # ball
        displaySetup = self.ballCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.ballCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.ballGuide, **displaySetup)

        # rollCntrl
        displaySetup = self.rollCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        rollCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.ballGuide, **displaySetup)
        rollCntrl.getParent().translateBy((0, 1.5, 1))

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
            if self.fingers[finger]['isHeelFinger']:
                pm.parent(f.moveall, j1)
            else:
                pm.parent(f.moveall, j2)
            i = f.fingerId

            #if f.fingerId != 0:
            if True:
                ctrlBase = f.cntrl1
                twist_PMA = pm.listConnections(ctrlBase.twist, d=True)[0]
                globalCtrl.twist >> twist_PMA.input2D[1].input2Dx

                curl_PMA = pm.listConnections(ctrlBase.curl, d=True, t='plusMinusAverage')
                relaxMDL1 = pm.createNode('multDoubleLinear', n=self.name+'relaxMulti1')
                relaxMDL1.input2.set(relax1[i])
                globalCtrl.relax >> relaxMDL1.input1

                relaxMDL2 = pm.createNode('multDoubleLinear', n=self.name+'relaxMulti2')
                relaxMDL2.input2.set(relax2[i])
                globalCtrl.relax >> relaxMDL2.input1

                cond = pm.createNode('condition', n=self.name+'relaxCond')
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
                    MDL = pm.createNode('multDoubleLinear', n=self.name+'scrunchMult')
                    globalCtrl.scrunch >> MDL.input1
                    MDL.input2.set(multi[j])
                    MDL.output >> node.input1D[5]

                spread_PMA = pm.listConnections(ctrlBase.spread, d=True, t='plusMinusAverage')[0]
                spread_MDL = pm.createNode('multDoubleLinear', n=self.name+'spreadMult')
                globalCtrl.spread >> spread_MDL.input1
                spread_MDL.input2.set(spread[i])
                spread_MDL.output >> spread_PMA.input2D[3].input2Dy



        # hierarquia
        pm.parent(self.ballCntrl.getParent(), toeCntrl.getParent(), heelCntrl)
        heelCntrl.getParent().setParent(tipCntrl)
        tipCntrl.getParent().setParent(outCntrl)
        outCntrl.getParent().setParent(inCntrl)
        inCntrl.getParent().setParent(slideCompensateGrp)
        rollCntrl.getParent().setParent(slideCompensateGrp)
        slideCntrl.getParent().setParent(self.baseCntrl)
        ballIkh[0].setParent(self.ballCntrl)
        ballIkh[0].visibility.set(0)
        tipIkh[0].setParent(toeCntrl)
        tipIkh[0].visibility.set(0)
        self.limbConnectionCntrl.getParent().setParent(self.ballCntrl)
        pm.parent(j1, self.baseCntrl.getParent(), self.moveall)

        # rollCntrl
        rollCntrl.addAttr('heelLimit', dv=50, k=1, at='float')
        rollBlend = pm.createNode('blendColors', n=self.name+'rollBlend')
        rollCntrl.heelLimit >> rollBlend.color1.color1R

        # setDrivens do controle do Roll
        animUU = pm.createNode('animCurveUU', n=self.name+'RollAnimCrv1')  # cria curva
        multi = pm.createNode('multDoubleLinear', n=self.name+'RollMulti')
        multi.input2.set(-1)
        pm.setKeyframe(animUU, float=float(0), value=float(0), itt='Linear', ott='Linear')
        pm.setKeyframe(animUU, float=float(1.5), value=float(1), itt='Linear', ott='Linear')
        pm.setKeyframe(animUU, float=float(3), value=float(0), itt='Linear', ott='Linear')
        rollCntrl.translateX >> animUU.input
        animUU.output >> rollBlend.blender
        rollBlend.outputR >> multi.input1
        multi.output >> self.ballCntrl.getParent().rotateZ

        animUA = pm.createNode('animCurveUA', n=self.name+'RollAnimCrv2')
        pm.setKeyframe(animUA, float=float(-3), value=float(75), itt='Linear', ott='Linear')
        pm.setKeyframe(animUA, float=float(0), value=float(0), itt='Linear', ott='Linear')
        rollCntrl.translateX >> animUA.input
        animUA.output >> heelCntrl.getParent().rotateZ

        animUA = pm.createNode('animCurveUA', n=self.name+'RollAnimCrv3')
        pm.setKeyframe(animUA, float=float(1.5), value=float(0), itt='Linear', ott='Linear')
        pm.setKeyframe(animUA, float=float(7), value=float(-180), itt='Linear', ott='Linear')
        rollCntrl.translateX >> animUA.input
        animUA.output >> tipCntrl.getParent().rotateZ

        animUA = pm.createNode('animCurveUA', n=self.name+'RollAnimCrv4')
        pm.setKeyframe(animUA, float=float(0), value=float(0), itt='Linear', ott='Linear')
        pm.setKeyframe(animUA, float=float(-2.5), value=float(-120), itt='Linear', ott='Linear')
        rollCntrl.translateZ >> animUA.input
        # inverte se for mirror pq o controle tem

        if self.flipAxis:
            animUA.output >> inCntrl.getParent().rotateX
        else:
            animUA.output >> outCntrl.getParent().rotateX

        animUA = pm.createNode('animCurveUA', n=self.name+'RollAnimCrv5')
        pm.setKeyframe(animUA, float=float(0), value=float(0), itt='Linear', ott='Linear')
        pm.setKeyframe(animUA, float=float(2.5), value=float(120), itt='Linear', ott='Linear')
        rollCntrl.translateZ >> animUA.input

        if self.flipAxis:
            animUA.output >> outCntrl.getParent().rotateX
        else:
            animUA.output >> inCntrl.getParent().rotateX

        # controles fk
        displaySetup = self.ankleFkCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.ankleFkCntrl = controlTools.cntrlCrv(name=cntrlName, obj=j1, connType='parentConstraint', **displaySetup)

        displaySetup = self.toeFkCntrlSetup.copy()
        cntrlName = displaySetup['nameTempl']
        self.toeFkCntrl = controlTools.cntrlCrv(name=cntrlName, obj=self.ballGuide, align='parent',  connType=None, **displaySetup)

        if self.flipAxis:
            pm.xform(self.toeFkCntrl.getParent(), ws=True, ro=[0, 0, 90])
        else:
            pm.xform(self.toeFkCntrl.getParent(), ws=True, ro=[180, 0, -90])


        pm.orientConstraint (self.toeFkCntrl, j2, mo=True)
        self.toeFkCntrl.getParent().setParent(self.ankleFkCntrl)
        self.ankleFkCntrl.getParent().setParent(self.moveall)

        # node tree ikfk Blend
        self.moveall.addAttr('ikfk', at='float', min=0, max=1, dv=1, k=1)
        ikfkRev = pm.createNode('reverse', n=self.name+'IkFkReverse')
        ikfkVisCond1 = pm.createNode('condition', n=self.name+'IkFkCond1')
        ikfkVisCond2 = pm.createNode('condition', n=self.name+'IkFkCond2')

        # visibilidade ik fk
        self.moveall.ikfk >> ikfkRev.inputX
        self.moveall.ikfk >> ballIkh[0].ikBlend
        self.moveall.ikfk >> tipIkh[0].ikBlend
        self.moveall.ikfk >> ikfkVisCond1.firstTerm
        ikfkVisCond1.secondTerm.set(0)
        ikfkVisCond1.operation.set(2)
        ikfkVisCond1.colorIfTrueR.set(1)
        ikfkVisCond1.colorIfFalseR.set(0)
        ikfkVisCond1.outColorR >> self.baseCntrl.getParent().visibility

        # blend dos constraints
        self.moveall.ikfk >> ikfkVisCond2.firstTerm
        ikfkVisCond2.secondTerm.set(1)
        ikfkVisCond2.operation.set(4)
        ikfkVisCond2.colorIfTrueR.set(1)
        ikfkVisCond2.colorIfFalseR.set(0)
        ikfkVisCond2.outColorR >> self.ankleFkCntrl.getParent().visibility
        parCnstr = j1.connections(type='parentConstraint')[0]  # descobre constraint
        weightAttr = parCnstr.target.connections(p=True, t='parentConstraint')  # descobre parametros
        self.moveall.ikfk >> weightAttr[0]
        ikfkRev.outputX >> weightAttr[1]

