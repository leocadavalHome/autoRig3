import pymel.core as pm
import autoRig3.tools.controlTools as controlTools
import json
import logging

logger = logging.getLogger('autoRig')

class EyesDir:
    def __init__(self, name='eyes'):
        self.name = name
        self.guideDict = {'moveall': [(0, 0, 0), (0,0,0), (1,1,1)], 'L_eyeLookAt': [(.4, 1, -.6), (0,0,0)],
                          'R_eyeLookAt': [(-.4, 1, -.6), (0, 0, 0)], 'L_lookAt': [(0,0,1.5), (0,0,0)],
                          'R_lookAt': [(0,0,1.5), (0,0,0)]}

        self.toExport = ['name','guideDict', 'moveallGuideSetup', 'L_eyeLookAtGuideSetup','R_eyeLookAtGuideSetup',
                         'L_lookAtGuideSetup', 'R_lookAtGuideSetup']

        self.guideSulfix = '_guide'
        self.moveallGuideSetup = {'nameTempl': self.name + 'Moveall', 'icone': 'quadradoZ', 'size': 1, 'color': (1, 0, 0)}
        self.L_eyeLookAtGuideSetup = {'nameTempl': 'L_eyeLookAt', 'icone': 'quadradoZ', 'size': .3, 'color': (32, .7, .17)}
        self.R_eyeLookAtGuideSetup = {'nameTempl': 'R_eyeLookAt', 'icone': 'quadradoZ', 'size': .3, 'color': (32, .7, .17)}
        self.L_lookAtGuideSetup = {'nameTempl': 'L_lookAt', 'icone': 'cubo', 'size': .3,'color': (0, 1, 1)}
        self.R_lookAtGuideSetup = {'nameTempl': 'R_lookAt', 'icone': 'cubo', 'size': .3, 'color': (0, 1, 1)}

        self.moveallCtrlSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'grp', 'size': 1.8, 'color': (1, 1, 0)}

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
        try:
            cntrl.setScale(self.guideDict[posRot][2])
        except:
            pass

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
                expDict[key] = self.__dict__[key]
        return expDict

    def doGuide(self, eyeball=None):

        if pm.objExists('facial_guides_grp'):
            facialGrp = 'facial_guides_grp'
        else:
            facialGrp = pm.group(n='facial_guides_grp', em=True)

        if pm.objExists(self.name + 'Moveall_guide'):
            pm.delete(self.name + 'Moveall_guide')

        self.guideMoveall = self.createCntrl('moveallGuide')
        self.L_eyeLookAtGuide = self.createCntrl('L_eyeLookAtGuide')
        self.R_eyeLookAtGuide = self.createCntrl('R_eyeLookAtGuide')
        self.L_lookAtGuide = self.createCntrl('L_lookAtGuide')
        self.R_lookAtGuide = self.createCntrl('R_lookAtGuide')

        pm.parent(self.L_lookAtGuide, self.L_eyeLookAtGuide)
        pm.parent(self.R_lookAtGuide, self.R_eyeLookAtGuide)
        pm.parent(self.L_eyeLookAtGuide,self.R_eyeLookAtGuide,self.guideMoveall, r=True)

        self.setCntrl(self.guideMoveall, 'moveall')
        self.setCntrl(self.L_eyeLookAtGuide, 'L_eyeLookAt')
        self.setCntrl(self.R_eyeLookAtGuide, 'R_eyeLookAt')
        self.setCntrl(self.L_lookAtGuide, 'L_lookAt')
        self.setCntrl(self.R_lookAtGuide, 'R_lookAt')

        self.mirrorTranslate_mdn = pm.createNode('multiplyDivide')
        self.mirrorRotate_mdn = pm.createNode('multiplyDivide')
        self.mirrorLookAt_mdn = pm.createNode('multiplyDivide')
        self.mirrorLookAtAim_mdn = pm.createNode('multiplyDivide')

        self.mirrorTranslate_mdn.input2X.set(-1)
        self.mirrorRotate_mdn.input2Y.set(-1)
        self.mirrorRotate_mdn.input2Z.set(-1)
        self.mirrorLookAt_mdn.input2X.set(-1)
        self.mirrorLookAtAim_mdn.input2X.set(-1)

        self.L_eyeLookAtGuide.translate >> self.mirrorLookAt_mdn.input1
        self.mirrorLookAt_mdn.output >> self.R_eyeLookAtGuide.translate

        self.L_lookAtGuide.translate >> self.mirrorLookAtAim_mdn.input1
        self.mirrorLookAtAim_mdn.output >> self.R_lookAtGuide.translate

        pm.parent(self.guideMoveall, facialGrp)

        if eyeball:
            try:
                eyeballNode = pm.PyNode(eyeball)
                bbox = eyeballNode.getBoundingBox(space='world')
                pos = bbox.center()
                x = pm.spaceLocator()
                pm.xform(x, t=pos, ws=True)
                pm.delete(x)
                pm.xform(self.guideMoveall, t=(0, pos[1], pos[2]), ws=True)
                pm.xform(self.L_eyeLookAtGuide, t=pos, ws=True)
                pm.xform(self.L_lookAtGuide, t=(pos[0], pos[1], pos[2] + 5), ws=True)
            except:
                logger.debug('Nao foi possivel alinhar')

        pm.addAttr(self.guideMoveall, ln='eyesDict', dt='string')
        self.guideMoveall.eyesDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.eyesDict.get()
            limbDictRestored = json.loads(jsonDict)

            self.__dict__.update(**limbDictRestored)

            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)
            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            guideName = self.L_eyeLookAtGuideSetup['nameTempl'] + self.guideSulfix
            self.L_eyeLookAtGuide = pm.PyNode(guideName)
            self.guideDict['L_eyeLookAt'][0] = self.L_eyeLookAtGuide.getTranslation(space='object').get()
            self.guideDict['L_eyeLookAt'][1] = tuple(self.L_eyeLookAtGuide.getRotation(space='object'))

            guideName = self.R_eyeLookAtGuideSetup['nameTempl'] + self.guideSulfix
            self.R_eyeLookAtGuide = pm.PyNode(guideName)
            self.guideDict['R_eyeLookAt'][0] = self.R_eyeLookAtGuide.getTranslation(space='object').get()
            self.guideDict['R_eyeLookAt'][1] = tuple(self.R_eyeLookAtGuide.getRotation(space='object'))

            guideName = self.L_lookAtGuideSetup['nameTempl'] + self.guideSulfix
            self.L_lookAtGuide = pm.PyNode(guideName)
            self.guideDict['L_lookAt'][0] = self.L_lookAtGuide.getTranslation(space='object').get()
            self.guideDict['L_lookAt'][1] = tuple(self.L_lookAtGuide.getRotation(space='object'))

            guideName = self.R_lookAtGuideSetup['nameTempl'] + self.guideSulfix
            self.R_lookAtGuide = pm.PyNode(guideName)
            self.guideDict['R_lookAt'][0] = self.R_lookAtGuide.getTranslation(space='object').get()
            self.guideDict['R_lookAt'][1] = tuple(self.R_lookAtGuide.getRotation(space='object'))
        except:
            pass

    def doRig(self, upVectorObj=None):
        sufix_skin = 'jxt'
        sufix = 'end'

        if not self.guideMoveall:
            self.doGuide()
        self.guideMoveall.visibility.set(0)

        if pm.objExists(self.name + "Ctrl_grp"):
            pm.delete(self.name + "Ctrl_grp")

        if pm.objExists(self.name + 'Sys_grp'):
            pm.delete(self.name + 'Sys_grp')

        self.moveall = pm.group(em=True, n=self.name + 'Sys_grp')
        self.moveall.visibility.set(0)

        if pm.objExists('head_contrained'):
            constrained_grp = 'head_contrained'
        else:
            constrained_grp = pm.group(n='head_contrained', em=True)

        L_eyeTranslate = pm.xform(self.L_eyeLookAtGuide, q=True, ws=True, t=True)
        L_eyeRotate = pm.xform(self.L_eyeLookAtGuide, q=True, ws=True, ro=True)

        R_eyeTranslate = pm.xform(self.R_eyeLookAtGuide, q=True, ws=True, t=True)
        R_eyeRotate = pm.xform(self.R_eyeLookAtGuide, q=True, ws=True, ro=True)

        pm.select(cl=True)
        L_eyeJntZero = pm.joint(p=L_eyeTranslate, n='L_eye_zero')
        L_eyeJntSkin = pm.joint(p=L_eyeTranslate, n='L_eye_' + sufix_skin)
        pm.xform(L_eyeJntZero, ws=True, ro=L_eyeRotate)

        pm.select(cl=True)
        R_eyeJntZero = pm.joint(p=R_eyeTranslate, n='R_eye_zero')
        R_eyeJntSkin = pm.joint(p=R_eyeTranslate, n='R_eye_' + sufix_skin)
        pm.xform(R_eyeJntZero, ws=True, ro=R_eyeRotate)

        self.L_eye_loc1 = pm.spaceLocator(n=L_eyeJntSkin + '1_loc', )
        self.R_eye_loc1 = pm.spaceLocator(n=R_eyeJntSkin + '1_loc', )
        self.L_eye_loc1.translate.set(L_eyeTranslate)
        self.R_eye_loc1.translate.set(R_eyeTranslate)
        self.L_eye_loc1.visibility.set(0)
        self.R_eye_loc1.visibility.set(0)

        self.L_eye_loc2 = pm.spaceLocator(n=L_eyeJntSkin + '2_loc', )
        self.R_eye_loc2 = pm.spaceLocator(n=R_eyeJntSkin + '2_loc', )
        self.L_eye_loc2.translate.set(L_eyeTranslate)
        self.R_eye_loc2.translate.set(R_eyeTranslate)
        self.L_eye_loc2.visibility.set(0)
        self.R_eye_loc2.visibility.set(0)

        ctrlGrp = pm.group(em=True, n=self.name+'Ctrl_grp')
        pm.addAttr(ctrlGrp, ln='ikFk', k=True, dv=0, max=1, min=0)
        Lbld = pm.createNode('blendColors', n='L_eyeDirIkfkBlend')
        Rbld = pm.createNode('blendColors', n='R_eyeDirIkfkBlend')

        self.L_eye_loc1.rotate >> Lbld.color1
        self.R_eye_loc1.rotate >> Rbld.color1
        self.L_eye_loc2.rotate >> Lbld.color2
        self.R_eye_loc2.rotate >> Rbld.color2
        ctrlGrp.ikFk >> Lbld.blender
        ctrlGrp.ikFk >> Rbld.blender
        Lbld.output >> L_eyeJntSkin.rotate
        Rbld.output >> R_eyeJntSkin.rotate

        self.L_lookAt_ctrl = controlTools.cntrlCrv(name='L_lookAt_ctrl', obj=self.L_lookAtGuide, align='posRot', connType=None, size=.3, icone='circuloZ')
        self.R_lookAt_ctrl = controlTools.cntrlCrv(name='R_lookAt_ctrl', obj=self.R_lookAtGuide, align='posRot', connType=None, size=.3, icone='circuloZ')
        self.L_rotate_ctrl = controlTools.cntrlCrv(name='L_Rotate_ctrl', obj=self.L_eye_loc2, align='posRot', connType='connectionR', size=.6, icone='ponteiroReto_Z')
        self.R_rotate_ctrl = controlTools.cntrlCrv(name='R_Rotate_ctrl', obj=self.R_eye_loc2, align='posRot', connType='connectionR', size=.6, icone='ponteiroReto_Z')
        self.lookAt_ctrl = controlTools.cntrlCrv(name='lookAt_ctrl', obj=None, connType=None, size=1, icone='circuloZ')

        rev = pm.createNode('reverse', n='eyeDirIkFkVizRev')
        ctrlGrp.ikFk >> rev.input.inputX
        ctrlGrp.ikFk >> self.lookAt_ctrl.getParent().visibility
        rev.output.outputX >> self.L_rotate_ctrl.getParent().visibility
        rev.output.outputX >> self.R_rotate_ctrl.getParent().visibility

        pm.delete(pm.parentConstraint(self.L_lookAt_ctrl, self.R_lookAt_ctrl, self.lookAt_ctrl.getParent(), mo=False))

        pm.addAttr(self.lookAt_ctrl, ln='followHead', k=True)

        pm.move(0, -.6, 0, self.lookAt_ctrl + '.cv[1]', r=1, os=1, wd=1)
        pm.move(-.2, 0, 0, self.lookAt_ctrl + '.cv[3]', r=1, os=1, wd=1)
        pm.move(0, .5, 0, self.lookAt_ctrl + '.cv[5]', r=1, os=1, wd=1)
        pm.move(.2, 0, 0, self.lookAt_ctrl + '.cv[7]', r=1, os=1, wd=1)

        for ctrl in [self.L_rotate_ctrl, self.R_rotate_ctrl]:
            ctrl.translateZ.lock()
            ctrl.scale.lock()
            ctrl.visibility.lock()
            ctrl.translateX.setKeyable(0)
            ctrl.translateY.setKeyable(0)
            ctrl.translateZ.setKeyable(0)
            ctrl.scaleX.setKeyable(0)
            ctrl.scaleY.setKeyable(0)
            ctrl.scaleZ.setKeyable(0)
            ctrl.visibility.setKeyable(0)

        for ctrl in [self.L_lookAt_ctrl, self.R_lookAt_ctrl, self.L_lookAt_ctrl]:
            ctrl.translateZ.lock()
            ctrl.rotate.lock()
            ctrl.scale.lock()
            ctrl.visibility.lock()
            ctrl.translateZ.setKeyable(0)
            ctrl.rotateX.setKeyable(0)
            ctrl.rotateY.setKeyable(0)
            ctrl.rotateZ.setKeyable(0)
            ctrl.scaleX.setKeyable(0)
            ctrl.scaleY.setKeyable(0)
            ctrl.scaleZ.setKeyable(0)
            ctrl.visibility.setKeyable(0)

        if not upVectorObj:
            pm.aimConstraint(self.L_lookAt_ctrl, self.L_eye_loc1, offset=(0, 0, 0), weight=1, aimVector=[0, 0, 1],
                             upVector=[0, 1, 0], worldUpType="objectrotation", worldUpObject=self.lookAt_ctrl)

            pm.aimConstraint(self.R_lookAt_ctrl, self.R_eye_loc1, offset=(0, 0, 0), weight=1, aimVector=[0, 0, 1],
                             upVector=[0, 1, 0], worldUpType="objectrotation", worldUpObject=self.lookAt_ctrl)
        else:
            pm.aimConstraint(self.L_lookAt_ctrl, self.L_eye_loc1, offset=(0, 0, 0), weight=1, aimVector=[0, 0, 1],
                             upVector=[0, 1, 0], worldUpType="objectrotation", worldUpObject=upVectorObj,
                             worldUpVector=[1, 0, 0])

            pm.aimConstraint(self.R_lookAt_ctrl, self.R_eye_loc1, offset=(0, 0, 0), weight=1, aimVector=[0, 0, 1],
                             upVector=[0, 1, 0], worldUpType="objectrotation", worldUpObject=upVectorObj,
                             worldUpVector=[1, 0, 0])


        pm.parent(L_eyeJntZero, R_eyeJntZero, self.moveall)
        pm.parent(self.L_lookAt_ctrl.getParent(), self.R_lookAt_ctrl.getParent(), self.lookAt_ctrl)
        pm.parent(self.L_rotate_ctrl.getParent(), self.R_rotate_ctrl.getParent(), self.L_eye_loc1, self.R_eye_loc1,
                  self.L_eye_loc2, self.R_eye_loc2, self.lookAt_ctrl.getParent(), ctrlGrp)
        pm.parent(ctrlGrp, constrained_grp)
