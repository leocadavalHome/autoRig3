import pymel.core as pm
import json
import autoRig3.modules.baseModule as baseClass
import autoRig3.tools.controlTools as controlTools
import logging

logger = logging.getLogger('autoRig')

class EyeSocket (baseClass.BaseModule):
    def __init__(self, name='eyeSocket'):
        super(EyeSocket, self).__init__()

        self.name = name
        self.guideDict = {'moveall': [(0, 0, 0), (0,0,0), (1,1,1)], 'L_eyeSocket': [(.4, 1, -.6), (0,0,0)],
                          'R_eyeSocket': [(-.4, 1, -.6), (0, 0, 0)]}

        self.toExport = ['name', 'guideDict', 'moveallGuideSetup', 'L_eyeSocketGuideSetup', 'R_eyeSocketGuideSetup']

        self.guideSulfix = '_guide'
        self.moveallGuideSetup = {'nameTempl': self.name + 'Moveall', 'icone': 'quadradoZ', 'size': .5, 'color': (1, 0, 0)}
        self.L_eyeSocketGuideSetup = {'nameTempl': 'L_eyeSocket', 'icone': 'quadradoZ', 'size': .3, 'color': (32, .7, .17)}
        self.R_eyeSocketGuideSetup = {'nameTempl': 'R_eyeSocket', 'icone': 'quadradoZ', 'size': .3, 'color': (32, .7, .17)}
        self.moveallCtrlSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'grp', 'size': 1, 'color': (1, 1, 0)}


    def doGuide(self, eyeball=None):
        if pm.objExists('facial_guides_grp'):
            facialGrp = 'facial_guides_grp'
        else:
            facialGrp = pm.group(n='facial_guides_grp', em=True)

        if pm.objExists(self.name + 'Moveall_guide'):
            pm.delete(self.name + 'Moveall_guide')

        self.guideMoveall = self.createCntrl('moveallGuide')
        self.L_eyeSocketGuide = self.createCntrl('L_eyeSocketGuide')
        self.R_eyeSocketGuide = self.createCntrl('R_eyeSocketGuide')
        pm.parent(self.L_eyeSocketGuide, self.R_eyeSocketGuide, self.guideMoveall, r=True)

        self.setCntrl(self.guideMoveall, 'moveall')
        self.setCntrl(self.L_eyeSocketGuide, 'L_eyeSocket')
        self.setCntrl(self.R_eyeSocketGuide, 'R_eyeSocket')

        self.mirrorTranslate_mdn = pm.createNode('multiplyDivide')
        self.mirrorRotate_mdn = pm.createNode('multiplyDivide')
        self.mirrorLookAt_mdn = pm.createNode('multiplyDivide')
        self.mirroSocketAim_mdn = pm.createNode('multiplyDivide')

        self.mirrorTranslate_mdn.input2X.set(-1)
        self.mirrorRotate_mdn.input2Y.set(-1)
        self.mirrorRotate_mdn.input2Z.set(-1)
        self.mirrorLookAt_mdn.input2X.set(-1)
        self.mirroSocketAim_mdn.input2X.set(-1)

        self.L_eyeSocketGuide.translate >> self.mirrorLookAt_mdn.input1
        self.mirrorLookAt_mdn.output >> self.R_eyeSocketGuide.translate

        pm.parent(self.guideMoveall, facialGrp)

        if eyeball:
            try:
                eyeballNode = pm.PyNode(eyeball)
                bbox = eyeballNode.getBoundingBox(space='world')
                pos = bbox.center()
                zmax = bbox.max().z
                pm.xform(self.guideMoveall, t=(0, pos[1], pos[2] + 5), ws=True)
                pm.xform(self.L_eyeSocketGuide, t=(pos[0], pos[1], zmax), ws=True)
            except:
                logger.debug('Nao foi possivel alinhar')


        pm.addAttr(self.guideMoveall, ln='socketDict', dt='string')
        self.guideMoveall.socketDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.socketDict.get()
            limbDictRestored = json.loads(jsonDict)

            self.__dict__.update(**limbDictRestored)

            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)
            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            guideName = self.L_eyeSocketGuideSetup['nameTempl'] + self.guideSulfix
            self.L_eyeSocketGuide = pm.PyNode(guideName)
            self.guideDict['L_eyeSocket'][0] = self.L_eyeSocketGuide.getTranslation(space='object').get()
            self.guideDict['L_eyeSocket'][1] = tuple(self.L_eyeSocketGuide.getRotation(space='object'))

            guideName = self.R_eyeSocketGuideSetu['nameTempl'] + self.guideSulfix
            self.R_eyeSocketGuide = pm.PyNode(guideName)
            self.guideDict['R_eyeSocket'][0] = self.R_eyeSocketGuide.getTranslation(space='object').get()
            self.guideDict['R_eyeSocket'][1] = tuple(self.R_eyeSocketGuide.getRotation(space='object'))
        except:
            pass

    def doRig(self):
        sufix_skin = 'jxt'
        sufix = 'end'

        if not self.guideMoveall:
            self.doGuide()
        self.guideMoveall.visibility.set(0)

        if pm.objExists(self.name + "_constrained_grp"):
            pm.delete(self.name + "_constrained_grp")

        if pm.objExists(self.name + 'Sys_grp'):
            pm.delete(self.name + 'Sys_grp')

        self.sysGrp = pm.group(em=True, n=self.name + 'Sys_grp')
        self.sysGrp.visibility.set(0)

        self.constrainedGrp = pm.group(em=True, n=self.name + '_constrained_grp')

        if pm.objExists('head_contrained'):
            constrained_grp = 'head_contrained'
        else:
            constrained_grp = pm.group(n='head_contrained', em=True)

        L_eyeTranslate = pm.xform(self.L_eyeSocketGuide, q=True, ws=True, t=True)
        L_eyeRotate = pm.xform(self.L_eyeSocketGuide, q=True, ws=True, ro=True)

        R_eyeTranslate = pm.xform(self.R_eyeSocketGuide, q=True, ws=True, t=True)
        R_eyeRotate = pm.xform(self.R_eyeSocketGuide, q=True, ws=True, ro=True)

        pm.select(cl=True)
        L_eyeJntZero = pm.joint(p=L_eyeTranslate, n='L_eyeSocket_zero')
        L_eyeJntSkin = pm.joint(p=L_eyeTranslate, n='L_eyeSocket_' + sufix_skin)
        pm.xform(L_eyeJntZero, ws=True, ro=L_eyeRotate)

        pm.select(cl=True)
        R_eyeJntZero = pm.joint(p=R_eyeTranslate, n='R_eyeSocket_zero')
        R_eyeJntSkin = pm.joint(p=R_eyeTranslate, n='R_eyeSocket_' + sufix_skin)
        pm.xform(R_eyeJntZero, ws=True, ro=R_eyeRotate)

        self.LsocketCtrl = controlTools.cntrlCrv(name='L_eyeSocket_ctrl', obj=L_eyeJntSkin, align='posRot',
                                                 connType='connection', size=1, icone='circuloZ')
        self.RsocketCtrl = controlTools.cntrlCrv(name='R_eyeSocket_ctrl', obj=R_eyeJntSkin, align='posRot',
                                                 connType='connection', size=1, icone='circuloZ')


        pm.parent(R_eyeJntZero, L_eyeJntZero, self.sysGrp)
        pm.parent(self.LsocketCtrl.getParent(), self.RsocketCtrl.getParent(), self.constrainedGrp)
        pm.parent(self.constrainedGrp, constrained_grp)