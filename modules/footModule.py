import pymel.core as pm
import maya.api.OpenMaya as om
from autoRig3.modules import fingerModule
import autoRig3.tools.rigFunctions as rigFunctions
import json


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


        self.fingers = fingers
        if not fingers:
            fingers = [('Thumb', 1), ('Index', 2), ('Middle', 2), ('Ring', 2), ('Pink', 2)]
            self.fingers = fingers
            self.fingerNum = 5
        else:
            self.fingerNum = len(fingers)

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
        self.footDict = {'name': name, 'axis': axis, 'flipAxis': flipAxis}
        self.setDefaults()

        self.footDict.update(kwargs)

        for finger, values in self.footDict['fingers'].iteritems():
            f = fingerModule.Finger(name=values['name'], axis=self.axis, flipAxis=self.flipAxis, folds=values['folds'])
            self.fingerInstances[finger] = f

        self.footGuideDict.update(self.footDict['guideDict'])
        self.footDict['guideDict'] = self.footGuideDict.copy()

    def setDefaults(self):
        # definicoes da aparencia dos controles
        if not self.fingers:
            fingers = [('Thumb', 1), ('Index', 1), ('Middle', 1), ('Ring', 1), ('Pink', 1)]

        self.footDict['moveallCntrlSetup'] = {'nameTempl': self.name + 'MoveAll', 'icone': 'circuloX', 'size': 1.8,
                                              'color': (1, 1, 0)}
        self.footDict['centerCntrlSetup'] = {'nameTempl': self.name + 'Center', 'icone': 'circuloX', 'size': 2,
                                             'color': (0, 0, 1)}
        self.footDict['tipCntrlSetup'] = {'nameTempl': self.name + 'Tip', 'icone': 'bola', 'size': 0.5,
                                          'color': (0, 1, 1)}
        self.footDict['heelCntrlSetup'] = {'nameTempl': self.name + 'Heel', 'icone': 'bola', 'size': 0.5,
                                           'color': (0, 1, 1)}
        self.footDict['ankleCntrlSetup'] = {'nameTempl': self.name + 'Ankle', 'icone': 'cubo', 'size': 1,
                                            'color': (0, 1, 1)}
        self.footDict['ballCntrlSetup'] = {'nameTempl': self.name + 'Ball', 'icone': 'circuloX', 'size': 1.5,
                                           'color': (1, 1, 0)}
        self.footDict['inCntrlSetup'] = {'nameTempl': self.name + 'In', 'icone': 'bola', 'size': 0.4,
                                         'color': (0, 1, 1)}
        self.footDict['outCntrlSetup'] = {'nameTempl': self.name + 'Out', 'icone': 'bola', 'size': 0.4,
                                          'color': (0, 1, 1)}
        self.footDict['rollCntrlSetup'] = {'nameTempl': self.name + 'Roll', 'icone': 'cubo', 'size': 0.4,
                                           'color': (0, .6, 1)}
        self.footDict['baseCntrlSetup'] = {'nameTempl': self.name + 'Base', 'icone': 'quadradoY', 'size': 3,
                                           'color': (0, 0, 1)}
        self.footDict['slideCntrlSetup'] = {'nameTempl': self.name + 'Slide', 'icone': 'bola', 'size': 0.4,
                                            'color': (1, 0, 0)}
        self.footDict['toLimbCntrlSetup'] = {'nameTempl': self.name + 'ToLimb', 'icone': 'bola', 'size': 0.5,
                                             'color': (1, 1, 0)}
        self.footDict['toeCntrlSetup'] = {'nameTempl': self.name + 'Toe', 'icone': 'circuloX', 'size': 1.0,
                                          'color': (1, 1, 0)}

        self.footDict['ankleFkCntrlSetup'] = {'nameTempl': self.name + 'TnkleFk', 'icone': 'grp', 'size': 1.0,
                                              'color': (0, 1, 0)}
        self.footDict['toeFkCntrlSetup'] = {'nameTempl': self.name + 'ToeFk', 'icone': 'circuloX', 'size': 1.0,
                                            'color': (0, 1, 0)}

        self.footDict['moveallGuideSetup'] = {'nameTempl': self.name + 'MoveAll', 'size': 1.8, 'icone': 'quadradoY',
                                              'color': (1, 0, 0)}
        self.footDict['centerGuideSetup'] = {'nameTempl': self.name + 'Center', 'size': .5, 'icone': 'grp',
                                             'color': (1, 1, 0)}
        self.footDict['tipGuideSetup'] = {'nameTempl': self.name + 'Tip', 'size': 0.5, 'icone': 'bola',
                                          'color': (0, 1, 1)}
        self.footDict['heelGuideSetup'] = {'nameTempl': self.name + 'Heel', 'size': 0.5, 'icone': 'bola',
                                           'color': (0, 1, 1)}
        self.footDict['ankleGuideSetup'] = {'nameTempl': self.name + 'Ankle', 'size': 0.5, 'icone': 'bola',
                                            'color': (0, 1, 1)}
        self.footDict['ballGuideSetup'] = {'nameTempl': self.name + 'Ball', 'size': 0.5, 'icone': 'bola',
                                           'color': (0, 1, 1)}
        self.footDict['inGuideSetup'] = {'nameTempl': self.name + 'In', 'size': 0.4, 'icone': 'bola',
                                         'color': (0, 0, 1)}
        self.footDict['outGuideSetup'] = {'nameTempl': self.name + 'Out', 'size': 0.4, 'icone': 'bola',
                                          'color': (0, 0, 1)}
        self.footDict['rollGuideSetup'] = {'nameTempl': self.name + 'Roll', 'size': 0.4, 'icone': 'bola',
                                           'color': (1, 0, 1)}
        self.footDict['baseGuideSetup'] = {'nameTempl': self.name + 'Base', 'size': 3, 'icone': 'quadradoY',
                                           'color': (1, 0, 1)}
        self.footDict['slideGuideSetup'] = {'nameTempl': self.name + 'Slide', 'size': 0.4, 'icone': 'null',
                                            'color': (1, 0, 1)}
        self.footDict['jointGuideSetup'] = {'nameTempl': self.name + 'Joint', 'size': 0.5, 'icone': 'null',
                                            'color': (1, 0, 1)}
        self.footDict['toeGuideSetup'] = {'nameTempl': self.name + 'Toe', 'size': 1.0, 'icone': 'null',
                                          'color': (1, 1, 0)}

        self.footDict['fingers'] = {}
        self.fingerInstances = {}
        self.footDict['fingerNames'] = ['Thumb', 'Index', 'Middle', 'Ring', 'Pink', 'Other', 'Other1']

        self.footDict['ankleJntSetup'] = {'nameTempl': self.name + 'Ankle', 'icone': 'Bone', 'size': 1.0}
        self.footDict['toeJntSetup'] = {'nameTempl': self.name + 'Toe', 'icone': 'Bone', 'size': 1.0}
        self.footDict['guideDict'] = {}
        self.footGuideDict = {'moveall': [(0, 0, 0), (0, 0, 0)], 'center': [(0, 0, 0), (0, 0, 0)],
                              'tip': [(3, 0, 0), (0, 0, 0)], 'heel': [(-1, 0, 0), (0, 0, 0)],
                              'ankle': [(0, 1, 0), (0, 0, 0)], 'ball': [(-1, 0.5, 0), (0, 0, 0)],
                              'in': [(-1, 0, -1), (0, 0, 0)], 'out': [(-1, 0, 1), (0, 0, 0)]}

        for i, finger in enumerate(self.fingers):
            fingerName = self.name + finger[0]
            step = (1.8 / self.fingerNum)
            ini = (0.9 - step / 2.0)
            offset = (0.9 - (1.8 / self.fingerNum) / 2.0) - (i * (1.8 / self.fingerNum))
            self.footDict['fingers'][finger[0]] = {'name': fingerName,
                                                               'guideDict': {'moveall': [(-1, 0, offset), (0, 0, 0)],
                                                                             'palm': [(0, 0, 0), (0, 0, 0)],
                                                                             'base': [(0.3, 0, 0), (0, 0, 0)],
                                                                             'tip': [(0.8, 0, 0), (0, 0, 0)],
                                                                             'fold1': [(0, 0.05, 0), (0, 0, 0)],
                                                                             'fold2': [(0, 0, 0), (0, 0, 0)]},
                                                               'folds': finger[1], 'isHeelFinger': False
                                                               }
            self.fingerInstances[finger[0]] = None

        for finger, values in self.footDict['fingers'].iteritems():
            f = fingerModule.Finger(name=values['name'], axis=self.axis, flipAxis=self.flipAxis, folds=values['folds'])
            self.fingerInstances[finger] = f

        self.footGuideDict.update(self.footDict['guideDict'])
        self.footDict['guideDict'] = self.footGuideDict.copy()

    def createCntrl(self, cntrlName):
        displaySetup = self.footDict[cntrlName+'Setup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        guide = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True, **displaySetup)
        return guide

    def setCntrlXform (self, cntrl, posRot, space='object'):
        cntrl.setTranslation(self.footDict['guideDict'][posRot][0], space=space)
        cntrl.setRotation(self.footDict['guideDict'][posRot][1], space=space)

    def doGuide(self, **kwargs):
        # atualiza o footGuideDict com o q for entrado aqui nesse metodo
        # ex: doGuide (center=[0,0,0], tip=[10,10,0]
        self.footDict.update(kwargs)

        displaySetup = self.footDict['moveallGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.guideMoveall = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', hasHandle=True,
                                                  **displaySetup)

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

        # cria guides segundo os nomes dos controles e nas posicoes definidas no dicionario footGuideDict

        self.centerGuide = self.createCntrl('centerGuide')

        guideName = self.footDict['centerGuideSetup']['nameTempl'] + self.grpSulfix
        self.centerGuideGrp = pm.group(self.centerGuide, n=guideName)

        self.tipGuide = self.createCntrl('tipGuide')
        self.heelGuide = self.createCntrl('heelGuide')
        self.ankleGuide = self.createCntrl('ankleGuide')
        self.ballGuide = self.createCntrl('ballGuide')
        self.inGuide =  self.createCntrl('inGuide')
        self.outGuide = self.createCntrl('outGuide')

        for finger in self.footDict['fingers']:
            f = self.fingerInstances[finger]
            dict = self.footDict['fingers'][finger]['guideDict']
            f.doGuide(**dict)
            pm.parent(f.guideMoveall, self.tipGuide)

        # pm.parent (self.fingerGrp, self.tipGuide)
        pm.parent(self.ballGuide, self.inGuide, self.outGuide, self.tipGuide)
        self.ankleGuide.setParent(self.centerGuide)
        pm.parent(self.centerGuideGrp, self.tipGuide, self.heelGuide, self.guideMoveall)

        self.setCntrlXform(self.tipGuide, 'tip', space='object')
        self.setCntrlXform(self.heelGuide, 'heel', space='object')
        self.setCntrlXform(self.ankleGuide, 'ankle', space='object')
        self.setCntrlXform(self.ballGuide, 'ball', space='object')
        self.setCntrlXform(self.inGuide, 'in', space='object')
        self.setCntrlXform(self.outGuide, 'out', space='object')

        pm.pointConstraint(self.tipGuide, self.heelGuide, self.centerGuideGrp)
        pm.pointConstraint(self.tipGuide, self.centerGuideGrp, e=True, w=0.25)
        pm.pointConstraint(self.heelGuide, self.centerGuideGrp, e=True, w=0.75)

        pm.aimConstraint(self.heelGuide, self.tipGuide, weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0),
                         worldUpVector=(0, 1, 0), worldUpType='objectrotation' , worldUpObject=self.guideMoveall)
        pm.aimConstraint(self.tipGuide, self.centerGuide, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                         worldUpVector=(0, 1, 0), worldUpType='objectrotation' , worldUpObject=self.guideMoveall)

        self. setCntrlXform(self.guideMoveall, 'moveall', space='world')

        pm.addAttr(self.guideMoveall, ln='footDict', dt='string')
        self.guideMoveall.footDict.set(json.dumps(self.footDict))

    def getGuideFromScene(self):
        try:
            guideName = self.footDict['moveallGuideSetup']['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            guideName = self.footDict['centerGuideSetup']['nameTempl'] + self.guideSulfix
            self.centerGuide = pm.PyNode(guideName)

            guideName = self.footDict['centerGuideSetup']['nameTempl'] + self.grpSulfix
            self.centerGuideGrp = pm.PyNode(guideName)

            guideName = self.footDict['tipGuideSetup']['nameTempl'] + self.guideSulfix
            self.tipGuide = pm.PyNode(guideName)

            guideName = self.footDict['heelGuideSetup']['nameTempl'] + self.guideSulfix
            self.heelGuide = pm.PyNode(guideName)

            guideName = self.footDict['ankleGuideSetup']['nameTempl'] + self.guideSulfix
            self.ankleGuide = pm.PyNode(guideName)

            guideName = self.footDict['ballGuideSetup']['nameTempl'] + self.guideSulfix
            self.ballGuide = pm.PyNode(guideName)

            guideName = self.footDict['inGuideSetup']['nameTempl'] + self.guideSulfix
            self.inGuide = pm.PyNode(guideName)

            guideName = self.footDict['outGuideSetup']['nameTempl'] + self.guideSulfix
            self.outGuide = pm.PyNode(guideName)

            for finger in self.footDict['fingers']:
                self.fingerInstances[finger].getGuideFromScene()
        except:
            print 'algum nao funcionou'

    def getCntrlXform(self, key, cntrl, space='object'):
        pos = self.footDict['guideDict'][key][0] = cntrl.getTranslation(space='world').get()
        rot = self.footDict['guideDict'][key][1] = tuple(cntrl.getRotation(space='world'))
        return [pos, rot]

    def getDict(self):
        try:
            guideName = self.footDict['moveallGuideSetup']['nameTempl'] + '_guide'
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.footDict.get()
            dictRestored = json.loads(jsonDict)
            self.footDict.update(**dictRestored)

            self.footDict['guideDict']['moveall'] = rigFunctions.getObjTransforms (self.guideMoveall, 'world')

            guideName = self.footDict['centerGuideSetup']['nameTempl'] + self.guideSulfix
            self.centerGuide = pm.PyNode(guideName)
            self.footDict['guideDict']['center'] = rigFunctions.getObjTransforms (self.centerGuide, 'object')

            guideName = self.footDict['centerGuideSetup']['nameTempl'] + self.grpSulfix
            self.centerGuideGrp = pm.PyNode(guideName)

            guideName = self.footDict['tipGuideSetup']['nameTempl'] + self.guideSulfix
            self.tipGuide = pm.PyNode(guideName)
            self.footDict['guideDict']['tip'] = rigFunctions.getObjTransforms (self.tipGuide, 'object')

            guideName = self.footDict['heelGuideSetup']['nameTempl'] + self.guideSulfix
            self.heelGuide = pm.PyNode(guideName)
            self.footDict['guideDict']['heel'] = rigFunctions.getObjTransforms (self.heelGuide, 'object')

            guideName = self.footDict['ankleGuideSetup']['nameTempl'] + self.guideSulfix
            self.ankleGuide = pm.PyNode(guideName)
            self.footDict['guideDict']['ankle'] = rigFunctions.getObjTransforms (self.ankleGuide, 'object')

            guideName = self.footDict['ballGuideSetup']['nameTempl'] + self.guideSulfix
            self.ballGuide = pm.PyNode(guideName)
            self.footDict['guideDict']['ball'] = rigFunctions.getObjTransforms (self.ballGuide, 'object')

            guideName = self.footDict['inGuideSetup']['nameTempl'] + self.guideSulfix
            self.inGuide = pm.PyNode(guideName)
            self.footDict['guideDict']['in'] = rigFunctions.getObjTransforms (self.inGuide, 'object')

            guideName = self.footDict['outGuideSetup']['nameTempl'] + self.guideSulfix
            self.outGuide = pm.PyNode(guideName)
            self.footDict['guideDict']['out'] = rigFunctions.getObjTransforms (self.outGuide, 'object')

            for finger in self.footDict['fingers']:
                fingerDict = self.fingerInstances[finger].getDict()
                self.footDict['fingers'][finger].update(fingerDict)

        except:
            print 'algum nao funcionou'

        return self.footDict

    def mirrorConnectGuide(self, foot):
        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')
            self.guideMoveall = None

        if not self.guideMoveall:
            self.doGuide()

        if not foot.guideMoveall:
            foot.doGuide(**self.footDict['guideDict'])

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')

        if not pm.objExists('GUIDES'):
            pm.group(self.name + 'MirrorGuide_grp', n='GUIDES')

        else:
            pm.parent(self.name + 'MirrorGuide_grp', 'GUIDES')

        self.guideMoveall.setParent(self.mirrorGuide)
        self.mirrorGuide.scaleX.set(-1)
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

        for a, b in zip(self.footDict['fingers'], foot.footDict['fingers']):
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

            if self.footDict['fingers'][a]['folds'] == 2:
                f_origin.fold2Guide.translate >> f_mirror.fold2Guide.translate
                f_origin.fold2Guide.rotate >> f_mirror.fold2Guide.rotate
                f_origin.fold2Guide.scale >> f_mirror.fold2Guide.scale

        if foot.flipAxis:
            self.flipAxis = False
        else:
            self.flipAxis = True

    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()

        cntrlName = self.footDict['moveallCntrlSetup']['nameTempl']

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

        n = BC ^ AB

        pm.select(cl=True)
        m = rigFunctions.orientMatrix(mvector=AD, normal=n, pos=A, axis=self.axis)
        jntName = self.footDict['ankleJntSetup']['nameTempl'] + self.jntSulfix
        j1 = pm.joint(n=jntName)
        self.skinJoints.append(j1)
        pm.xform(j1, m=m, ws=True)
        pm.makeIdentity(j1, apply=True, r=1, t=0, s=1, n=0, pn=0)

        # cria os joints
        m = rigFunctions.orientMatrix(mvector=CD, normal=n, pos=D, axis=self.axis)
        jntName = self.footDict['toeJntSetup']['nameTempl'] + self.jntSulfix
        j2 = pm.joint(n=jntName)
        self.skinJoints.append(j2)
        pm.xform(j2, m=m, ws=True)
        pm.makeIdentity(j2, apply=True, r=1, t=0, s=1, n=0, pn=0)

        jntName = self.footDict['toeJntSetup']['nameTempl'] + self.tipJxtSulfix
        j3 = pm.joint(n=jntName)
        self.skinJoints.append(j3)
        pm.xform(j3, m=m, ws=True)
        pm.xform(j3, t=C, ws=True)
        pm.makeIdentity(j3, apply=True, r=1, t=0, s=1, n=0, pn=0)
        # e faz os ikhandles
        ballIkh = pm.ikHandle(sj=j1, ee=j2, sol="ikRPsolver")
        tipIkh = pm.ikHandle(sj=j2, ee=j3, sol="ikRPsolver")

        self.moveall = pm.group(em=True, n=cntrlName)
        self.moveall.translate.set(center)
        if not pm.objExists('MOVEALL'):
            pm.group(self.moveall, n='MOVEALL')
        else:
            pm.parent(self.moveall, 'MOVEALL')

        # esse controle deve levar o controle ik da ponta do limb para funcionar o pe
        displaySetup = self.footDict['toLimbCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.limbConnectionCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=j1, connType='parentConstraint',
                                                         **displaySetup)

        # base cntrl
        displaySetup = self.footDict['baseCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.baseCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.centerGuide, **displaySetup)
        pm.move(.8, 0, 0, self.baseCntrl, r=True, os=True)
        pm.xform(self.baseCntrl, rp=ankle, ws=True)
        pm.scale(self.baseCntrl, [1, 1, .5], r=True)
        pm.makeIdentity(self.baseCntrl, apply=True, r=0, t=1, s=1, n=0, pn=0)
        self.baseCntrl.addAttr('extraRollCntrls', min=0, max=1, dv=0, k=1)

        # slidePivot
        displaySetup = self.footDict['slideCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        slideCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.centerGuide, **displaySetup)
        slideCompensateGrp = pm.group(em=True, n=self.name + 'Slide_grp')
        pm.parent(slideCompensateGrp, slideCntrl, r=True)
        slideMulti = pm.createNode('multiplyDivide')
        slideCntrl.translate >> slideMulti.input1
        slideMulti.input2.set(-1, -1, -1)
        slideMulti.output >> slideCompensateGrp.translate

        # bank cntrls
        displaySetup = self.footDict['inCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        inCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.inGuide, **displaySetup)
        self.baseCntrl.extraRollCntrls >> inCntrl.getParent().visibility
        displaySetup = self.footDict['inCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        outCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.outGuide, **displaySetup)

        # tip/heel
        displaySetup = self.footDict['tipCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        tipCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.tipGuide, **displaySetup)

        displaySetup = self.footDict['heelCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        heelCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.heelGuide, **displaySetup)

        # toe
        displaySetup = self.footDict['toeCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        toeCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.ballGuide, **displaySetup)
        toeCntrl.translate.set(0.5, 0, 0)
        pm.makeIdentity(toeCntrl, apply=True, r=0, t=1, s=0, n=0, pn=0)
        pm.xform(toeCntrl, rp=(-0.5, 0, 0), r=True)

        # ball
        displaySetup = self.footDict['ballCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.ballCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.ballGuide, **displaySetup)

        # rollCntrl
        displaySetup = self.footDict['rollCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        rollCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=self.ballGuide, **displaySetup)
        rollCntrl.getParent().translateBy((0, 1.5, 1))

        for finger in self.footDict['fingers']:
            f = self.fingerInstances[finger]
            f.flipAxis = self.flipAxis
            dict = self.footDict['fingers'][finger]['guideDict']
            f.doRig()
            self.skinJoints += f.skinJoints
            if self.footDict['fingers'][finger]['isHeelFinger']:
                pm.parent(f.moveall, j1)
            else:
                pm.parent(f.moveall, j2)

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
        rollBlend = pm.createNode('blendColors')
        rollCntrl.heelLimit >> rollBlend.color1.color1R

        # setDrivens do controle do Roll
        animUU = pm.createNode('animCurveUU')  # cria curva
        multi = pm.createNode('multDoubleLinear')
        multi.input2.set(-1)
        pm.setKeyframe(animUU, float=float(0), value=float(0), itt='Linear', ott='Linear')
        pm.setKeyframe(animUU, float=float(1.5), value=float(1), itt='Linear', ott='Linear')
        pm.setKeyframe(animUU, float=float(3), value=float(0), itt='Linear', ott='Linear')
        rollCntrl.translateX >> animUU.input
        animUU.output >> rollBlend.blender
        rollBlend.outputR >> multi.input1
        multi.output >> self.ballCntrl.getParent().rotateZ

        animUA = pm.createNode('animCurveUA')
        pm.setKeyframe(animUA, float=float(-3), value=float(75), itt='Linear', ott='Linear')
        pm.setKeyframe(animUA, float=float(0), value=float(0), itt='Linear', ott='Linear')
        rollCntrl.translateX >> animUA.input
        animUA.output >> heelCntrl.getParent().rotateZ

        animUA = pm.createNode('animCurveUA')
        pm.setKeyframe(animUA, float=float(1.5), value=float(0), itt='Linear', ott='Linear')
        pm.setKeyframe(animUA, float=float(7), value=float(-180), itt='Linear', ott='Linear')
        rollCntrl.translateX >> animUA.input
        animUA.output >> tipCntrl.getParent().rotateZ

        animUA = pm.createNode('animCurveUA')
        pm.setKeyframe(animUA, float=float(0), value=float(0), itt='Linear', ott='Linear')
        pm.setKeyframe(animUA, float=float(2.5), value=float(120), itt='Linear', ott='Linear')
        rollCntrl.translateZ >> animUA.input
        # inverte se for mirror pq o controle tem

        if self.flipAxis:
            animUA.output >> inCntrl.getParent().rotateX
        else:
            animUA.output >> outCntrl.getParent().rotateX

        animUA = pm.createNode('animCurveUA')
        pm.setKeyframe(animUA, float=float(0), value=float(0), itt='Linear', ott='Linear')
        pm.setKeyframe(animUA, float=float(-2.5), value=float(-120), itt='Linear', ott='Linear')
        rollCntrl.translateZ >> animUA.input
        if self.flipAxis:
            animUA.output >> outCntrl.getParent().rotateX
        else:
            animUA.output >> inCntrl.getParent().rotateX

        # controles fk
        displaySetup = self.footDict['ankleFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.ankleFkCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=j1, connType='parentConstraint', **displaySetup)

        displaySetup = self.footDict['toeFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.toeFkCntrl = rigFunctions.cntrlCrv(name=cntrlName, obj=j2, connType='orientConstraint', **displaySetup)

        self.toeFkCntrl.getParent().setParent(self.ankleFkCntrl)
        self.ankleFkCntrl.getParent().setParent(self.moveall)

        # node tree ikfk Blend
        self.moveall.addAttr('ikfk', at='float', min=0, max=1, dv=1, k=1)
        ikfkRev = pm.createNode('reverse')
        ikfkVisCond1 = pm.createNode('condition')
        ikfkVisCond2 = pm.createNode('condition')

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

        # IMPLEMENTAR guardar a posicao dos guides
