import pymel.core as pm
from autoRig3.modules import fingerModule
import autoRig3.tools.rigFunctions as rigFunctions
import json

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

    def __init__(self, name='hand', axis='X', flipAxis=False,
                 fingers=None, **kwargs):
        self.fingers = fingers
        if not fingers:
            fingers = [('Thumb', 1), ('Index', 2), ('Middle', 2), ('Ring', 2), ('Pink', 2)]
            self.fingers = fingers
            self.fingerNum = 5
        else:
            self.fingerNum = len(fingers)
        self.name = name
        self.axis = axis
        self.flipAxis = flipAxis
        self.skinJoints = []
        self.guideMoveall = None

        self.guideSulfix = '_guide'
        self.jntSulfix = '_jnt'
        self.jxtSulfix = '_jxt'
        self.tipJxtSulfix = 'Tip_jxt'
        grpSulfix = '_grp'

        self.handDict = {'name': name, 'axis': axis, 'flipAxis': flipAxis}
        self.handDict['fingers'] = {}
        self.fingerInstances = {}
        self.handDict['guideDict'] = {'moveall': [(0, 0, 0), (0, 0, 0)]}
        self.handDict['moveallGuideSetup'] = {'nameTempl': self.name + 'MoveAll', 'icone': 'quadradoX',
                                              'size': 1.5, 'color': (1, 0, 0)}

        self.handDict.update(kwargs)

        for i, finger in enumerate(fingers):
            fingerName = self.name + finger[0]
            fingerOffset = (((self.fingerNum / 2) * .3) - (i * .3))
            self.handDict['fingers'][finger[0]] = {'name': fingerName,
                                                   'folds': finger[1],
                                                   'guideDict': {
                                                                   'moveall': [(0, 0, fingerOffset), (0, 0, 0)],
                                                                   'palm': [(0, 0, 0), (0, 0, 0)],
                                                                   'base': [(1, 0, 0), (0, 0, 0)],
                                                                   'tip': [(2, 0, 0), (0, 0, 0)],
                                                                   'fold1': [(0, 0.05, 0), (0, 0, 0)],
                                                                   'fold2': [(0, 0, 0), (0, 0, 0)]
                                                                }}

            self.fingerInstances['finger' + str(i + 1)] = None

        for key, values in self.handDict['fingers'].iteritems():
            f = fingerModule.Finger(name=values['name'], axis=self.axis, flipAxis=self.flipAxis, folds=values['folds'])
            self.fingerInstances[key] = f


    def doGuide(self, **kwargs):
        # IMPLEMENTAR update do handDict - talvez handGuideDict
        self.handDict.update(kwargs)

        displaySetup = self.handDict['moveallGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.guideMoveall = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='',
                                                  hasHandle=True, **displaySetup)

        if not pm.objExists('GUIDES'):
            pm.group(self.guideMoveall, n='GUIDES')
        else:
            pm.parent(self.guideMoveall, 'GUIDES')

        for finger in self.handDict['fingers']:

            f = self.fingerInstances[finger]
            dict = self.handDict['fingers'][finger]['guideDict']
            f.doGuide(**dict)
            pm.parent(f.guideMoveall, self.guideMoveall)

        self.guideMoveall.setTranslation(self.handDict['guideDict']['moveall'][0], space='world')
        self.guideMoveall.setRotation(self.handDict['guideDict']['moveall'][1], space='world')

        pm.addAttr(self.guideMoveall, ln='handDict', dt='string')
        self.guideMoveall.handDict.set(json.dumps(self.handDict))


    def getGuideFromScene(self):
        try:
            guideName = self.name + 'MoveAll_guide'
            self.guideMoveall = pm.PyNode(guideName)

            for finger in self.handDict['fingers']:
                self.fingerInstances[finger].getGuideFromScene()
        except:
            print 'algum nao funcionou'

    def getDict(self):
        try:
            guideName = self.handDict['moveallGuideSetup']['nameTempl'] + '_guide'
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.handDict.get()
            dictRestored = json.loads(jsonDict)
            self.handDict.update(**dictRestored)
            self.handDict['guideDict']['moveall'] = rigFunctions.getObjTransforms(self.guideMoveall, 'world')

            for finger in self.handDict['fingers']:
                instance = self.fingerInstances[finger]
                fingerDict = instance.getDict()

                self.handDict['fingers'][finger] = fingerDict
        except:
            print 'algum nao funcionou'

        return self.handDict

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
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.template.set(1)

        hand.guideMoveall.translate >> self.guideMoveall.translate
        hand.guideMoveall.rotate >> self.guideMoveall.rotate
        hand.guideMoveall.scale >> self.guideMoveall.scale

        for a, b in zip(self.handDict['fingers'], hand.handDict['fingers']):
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

            if self.handDict['fingers'][a]['folds'] == 2:
                f_origin.fold2Guide.translate >> f_mirror.fold2Guide.translate
                f_origin.fold2Guide.rotate >> f_mirror.fold2Guide.rotate
                f_origin.fold2Guide.scale >> f_mirror.fold2Guide.scale

    def doRig(self, **kwargs):
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

        for finger in self.handDict['fingers']:
            f = self.fingerInstances[finger]
            f.flipAxis = self.flipAxis
            f.doRig()
            self.skinJoints += f.skinJoints
            pm.parent(f.moveall, self.moveall)

        # IMPLEMENTAR atualizar o guideDict