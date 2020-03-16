import pymel.core as pm
import maya.api.OpenMaya as om
import json
import copy
import autoRig3.tools.skinTools as skinTools
import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.vertexWalkTools as vtxWalk
import autoRig3.tools.attachTools as attachTools
import logging

logger = logging.getLogger('autoRig')

class EyeLid:
    def __init__(self, mesh=None, name='eyeLid', flipAxis=False):
        self.guideDict = {'moveall': [(12, 0, 0), (0, 0, 0), (1, 1, 1)], 'eyeCenter': [(0, 0, 0,), (0, 0, 0)],
                          'inCorner': [(10, 0, 2,), (0, 0, 0)], 'outCorner': [(14, 0, 2,), (0, 0, 0)],
                          'upCorner': [(12, 2, 2,), (0, 0, 0)], 'lowCorner': [(12, -2, 2,), (0, 0, 0)],
                          'upCtrlGrp': [(-2, 0, 2), (-1, 1, 2), (0, 2, 2), (1, 1, 2), (2, 0, 2)],
                          'lowCtrlGrp': [(-2, 0, 2), (-1, -1, 2), (0, -2, 2), (1, -1, 2), (2, 0, 2)],
                          'upCtrlCrv': [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
                          'lowCtrlCrv': [(0, 0, 0),(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]
                          }
        self.name = name
        self.flipAxis = flipAxis
        self.toExport = ['guideDict', 'name', 'eyeCenterGuideSetup', 'cornersGuideSetup']
        self.moveallGuideSetup = {'nameTempl': self.name + 'Moveall', 'icone': 'quadradoZ', 'size': 1, 'color': (1, 0, 0)}
        self.eyeCenterGuideSetup = {'nameTempl': self.name + 'EyeCenter', 'icone': 'circuloX', 'size': .8, 'color': (1, 0, 0)}
        self.cornersGuideSetup = {'nameTempl': self.name, 'icone': 'null', 'size': .05, 'color': (1, 0, 0)}
        self.guideSulfix = '_guide'
        self.jntSulfix = '_jxt'
        self.meshName = mesh
        self.skinJoints = []
        self.edgeLoop = None
        try:
            self.mesh = pm.PyNode(self.meshName)
        except:
            self.mesh = None

    def createCntrl(self, setupName='ctrl', nameTempl=None, posRot=None):
        displaySetup = self.__dict__[setupName + 'Setup'].copy ()
        if nameTempl:
            cntrlName = nameTempl
        else:
            cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, posRot=posRot, cntrlSulfix='', hasHandle=True, **displaySetup)
        return guide

    def setCntrl(self, cntrl, posRot, space='object'):
        cntrl.setTranslation(self.guideDict[posRot][0], space=space)
        cntrl.setRotation(self.guideDict[posRot][1], space='object')
        try:
            cntrl.setScale(self.guideDict[posRot][2])
        except:
            pass

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
            expDict[key] = self.__dict__[key]
        return expDict

    def doGuide(self, eyeball=None, edgeLoop=None, autoExtremes=True, **kwargs):
        self.__dict__.update(kwargs)

        if pm.objExists(self.name + 'Crv_grp'):
            pm.delete(self.name + 'Crv_grp')

        self.guideMoveall = self.createCntrl('moveallGuide')
        self.eyeCenter = self.createCntrl(setupName='eyeCenterGuide', nameTempl=self.name + 'EyeCenter' + self.guideSulfix)
        self.inCorner = self.createCntrl(setupName='cornersGuide', nameTempl=self.name + 'InCorner' + self.guideSulfix)
        self.outCorner = self.createCntrl(setupName='cornersGuide', nameTempl=self.name + 'OutCorner' + self.guideSulfix)
        self.upCorner = self.createCntrl(setupName='cornersGuide', nameTempl=self.name + 'UpCorner' + self.guideSulfix)
        self.lowCorner = self.createCntrl(setupName='cornersGuide', nameTempl=self.name + 'LowCorner' + self.guideSulfix)
        pm.parent(self.eyeCenter, self.inCorner, self.outCorner, self.upCorner, self.lowCorner, self.guideMoveall)

        crvGrp = pm.group(n=self.name+'Crv_grp', em=True)
        clsGuideGrp = pm.group(em=True, n=self.name + 'crvCtrlGuideClusters', p=crvGrp)
        clsGuideGrp.visibility.set(False)
        ctrlGuideGrp = pm.group(em=True, n=self.name + 'crvCtrlsGuide', p=self.guideMoveall)

        if eyeball:
            bbox = eyeball.getBoundingBox(space='world')
            pos = bbox.center()
            self.guideDict['moveall'][0] = (pos[0], pos[1], pos[2])
        else:
            logger.debug('no eyeball passed')

        if edgeLoop:
            self.edgeLoop = edgeLoop
            self.meshName = self.edgeLoop[0].name ().split ('.')[0]
            self.mesh = pm.PyNode (self.meshName)
        else:
            logger.debug('no edgeloop passed')
            #self.mesh = None
            self.edgeLoop = None

        if autoExtremes:
            try:
                pts = getEdgeLoopExtremesPoints(self.edgeLoop)
                inPos = pm.xform(pts[0], q=True, ws=True, t=True)
                outPos = pm.xform(pts[1], q=True, ws=True, t=True)
                upPos = pm.xform(pts[2], q=True, ws=True, t=True)
                lowPos = pm.xform(pts[3], q=True, ws=True, t=True)

                self.guideDict['inCorner'] = [inPos, (0, 0, 0)]
                self.guideDict['outCorner'] = [outPos, (0, 0, 0)]
                self.guideDict['upCorner'] = [upPos, (0, 0, 0)]
                self.guideDict['lowCorner'] = [lowPos, (0, 0, 0)]
            except:
                logger.debug('not possible autoextremes')


        self.setCntrl(self.guideMoveall, 'moveall', space='world')
        self.setCntrl(self.eyeCenter, 'eyeCenter', space='object')
        self.setCntrl(self.inCorner, 'inCorner', space='world')
        self.setCntrl(self.outCorner, 'outCorner', space='world')
        self.setCntrl(self.upCorner, 'upCorner', space='world')
        self.setCntrl(self.lowCorner, 'lowCorner', space='world')

        try:
            upEdgeLoop = selectLoopByLocators(mesh=self.mesh, loc1=self.inCorner, loc2=self.outCorner, loc3=self.upCorner)
            pm.select(cl=True)
            pm.select(upEdgeLoop)
            upCrv = pm.polyToCurve(form=2, degree=3, n=self.name + 'UpperCrv', ch=False)[0]

            if not atStart(loc=self.inCorner, crvName=upCrv):
                pm.reverseCurve(upCrv, ch=False, replaceOriginal=True)

            lowEdgeLoop = selectLoopByLocators(mesh=self.mesh, loc1=self.inCorner, loc2=self.outCorner, loc3=self.lowCorner)
            pm.select(cl=True)
            pm.select(lowEdgeLoop)
            lowCrv = pm.polyToCurve(form=2, degree=3, n=self.name + 'LowerCrv', ch=False)[0]

            if not atStart(loc=self.inCorner, crvName=lowCrv):
                pm.reverseCurve(lowCrv, ch=False, replaceOriginal=True)

            self.upCtrlCrv = pm.rebuildCurve(upCrv, s=2, rt=0, rpo=False, ch=False, n=self.name + 'upCtrl')[0]
            self.lowCtrlCrv = pm.rebuildCurve(lowCrv, s=2, rt=0, rpo=False, ch=False, n=self.name + 'lowCtrl')[0]

            pm.delete(upCrv, lowCrv)
        except:
            logger.debug('Found no edgeloop by locators. Using coordinates to draw')
            self.upCtrlCrv = pm.curve(n=self.name + 'upCrv_guide', d=3,
                                      p=self.guideDict['upCtrlGrp'])
            self.setCntrl(self.upCtrlCrv, 'moveall', space='world')
            self.lowCtrlCrv = pm.curve(n=self.name + 'lowCrv_guide', d=3,
                                       p=self.guideDict['lowCtrlGrp'])
            self.setCntrl(self.lowCtrlCrv, 'moveall', space='world')


        self.crvGuideCtrls = {'upCtrlCrv': [], 'lowCtrlCrv': []}

        for crvName in ['upCtrlCrv', 'lowCtrlCrv']:
            crv = self.__dict__[crvName]
            for i in range(5):
                cls = pm.cluster(crv.cv[i])[1]
                pm.parent(cls, clsGuideGrp)
                ctrl = controlTools.cntrlCrv(name=self.name + crvName + str(i), align='pivot', obj=cls, connType='pointConstraint',
                                             hasZeroGrp=True, cntrlSulfix='_ctrl', icone='bola', size=.05)
                pm.parent(ctrl.getParent(), ctrlGuideGrp)
                self.crvGuideCtrls[crvName].append(ctrl)

        for crvName in ['upCtrlCrv', 'lowCtrlCrv']:
            for i in range(5):
                self.crvGuideCtrls[crvName][i].setTranslation(self.guideDict[crvName][i], space='object')

        pm.parent(self.upCtrlCrv, self.lowCtrlCrv, crvGrp, r=True)

        try:
            facialGrp = pm.PyNode('facial_guides_grp')
            pm.parent (self.guideMoveall, crvGrp, facialGrp)
        except:
            pass

        pm.addAttr(self.guideMoveall, ln='eyeLidDict', dt='string')
        self.guideMoveall.eyeLidDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.eyeLidDict.get()
            DictRestored = json.loads(jsonDict)

            self.__dict__.update(**DictRestored)

            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation (space='world').get ()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform (self.guideMoveall, q=True, s=True, ws=True))

            guideName = self.eyeCenterGuideSetup['nameTempl'] + self.guideSulfix
            self.eyeCenter = pm.PyNode(guideName)
            self.guideDict['eyeCenter'][0] = self.eyeCenter.getTranslation (space='object').get ()
            self.guideDict['eyeCenter'][1] = tuple(self.eyeCenter.getRotation (space='object'))
            
            guideName = self.cornersGuideSetup['nameTempl']+'InCorner'+self.guideSulfix
            self.inCorner = pm.PyNode(guideName)
            self.guideDict['inCorner'][0] = self.inCorner.getTranslation (space='world').get()
            self.guideDict['inCorner'][1] = tuple(self.inCorner.getRotation (space='object'))
            
            guideName = self.cornersGuideSetup['nameTempl']+'OutCorner'+self.guideSulfix
            self.outCorner = pm.PyNode(guideName)
            self.guideDict['outCorner'][0] = self.outCorner.getTranslation (space='world').get()
            self.guideDict['outCorner'][1] = tuple(self.outCorner.getRotation (space='object'))
            
            guideName = self.cornersGuideSetup['nameTempl']+'UpCorner'+self.guideSulfix
            self.upCorner = pm.PyNode(guideName)
            self.guideDict['upCorner'][0] = self.upCorner.getTranslation (space='world').get()
            self.guideDict['upCorner'][1] = tuple(self.upCorner.getRotation (space='object'))
            
            guideName = self.cornersGuideSetup['nameTempl']+'LowCorner'+self.guideSulfix
            self.lowCorner = pm.PyNode(guideName)
            self.guideDict['lowCorner'][0] = self.lowCorner.getTranslation (space='world').get()
            self.guideDict['lowCorner'][1] = tuple(self.lowCorner.getRotation (space='object'))

            self.crvGuideCtrls = {'upCtrlCrv': [], 'lowCtrlCrv': []}
            for crvName in ['upCtrlCrv', 'lowCtrlCrv']:
                for i in range(5):
                    guideName = self.name+crvName+str(i)+'_ctrl'
                    ctrl = pm.PyNode(guideName)
                    self.crvGuideCtrls[crvName].append(ctrl)
                    self.guideDict[crvName][i] = ctrl.getTranslation(space='object').get()

        except:
            pass

    def mirrorConnectGuide(self, eyeLid):
        if pm.objExists (self.name + 'MirrorGuide_grp'):
            pm.delete (self.name + 'MirrorGuide_grp')
            self.guideMoveall = None

        if not self.guideMoveall:
            self.doGuide()

        if not eyeLid.guideMoveall:
            eyeLid.doGuide()

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')

        if not pm.objExists('facial_guides_grp'):
            pm.group(self.name + 'MirrorGuide_grp', n='facial_guides_grp')
        else:
            pm.parent(self.name + 'MirrorGuide_grp', 'facial_guides_grp')

        self.guideMoveall.setParent (self.mirrorGuide)

        # Felipe --> seta valores globais de escala
        scaleValue = tuple (pm.xform(self.guideMoveall, q=True, s=True, ws=True))
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.scaleY.set(1)
        self.mirrorGuide.scaleZ.set(1)
        self.mirrorGuide.scale.lock()
        self.mirrorGuide.rotate.lock()
        self.mirrorGuide.translate.lock()
        self.mirrorGuide.template.set(1)

        eyeLid.guideMoveall.translate >> self.guideMoveall.translate
        eyeLid.guideMoveall.rotate >> self.guideMoveall.rotate
        eyeLid.guideMoveall.scale >> self.guideMoveall.scale
        eyeLid.eyeCenter.translate >> self.eyeCenter.translate
        eyeLid.eyeCenter.rotate >> self.eyeCenter.rotate
        eyeLid.eyeCenter.scale >> self.eyeCenter.scale
        eyeLid.inCorner.translate >> self.inCorner.translate
        eyeLid.inCorner.rotate >> self.inCorner.rotate
        eyeLid.inCorner.scale >> self.inCorner.scale
        eyeLid.outCorner.translate >> self.outCorner.translate
        eyeLid.outCorner.rotate >> self.outCorner.rotate
        eyeLid.outCorner.scale >> self.outCorner.scale
        eyeLid.upCorner.translate >> self.upCorner.translate
        eyeLid.upCorner.rotate >> self.upCorner.rotate
        eyeLid.upCorner.scale >> self.upCorner.scale
        eyeLid.lowCorner.translate >> self.lowCorner.translate
        eyeLid.lowCorner.rotate >> self.lowCorner.rotate
        eyeLid.lowCorner.scale >> self.lowCorner.scale

        for crvName in self.crvGuideCtrls:
            for ctrl, ctrlMirror in zip(self.crvGuideCtrls[crvName], eyeLid.crvGuideCtrls[crvName]):
                ctrlMirror.getParent().translate >> ctrl.getParent().translate
                ctrlMirror.getParent().rotate >> ctrl.getParent().rotate
                ctrlMirror.getParent().scale >> ctrl.getParent().scale

                ctrlMirror.translate >> ctrl.translate
                ctrlMirror.rotate >> ctrl.rotate
                ctrlMirror.scale >> ctrl.scale

        if eyeLid.mesh:
            self.mesh = eyeLid.mesh

        if eyeLid.flipAxis:
            self.flipAxis = False
        else:
            self.flipAxis = True

    def doRig(self):
        cnstrGrp = pm.group(em=True, n=self.name+'EyeLid_constrained_grp')
        sysGrp = pm.group(em=True, n=self.name+'EyeLidSys_grp')
        crvsGrp = pm.group(em=True, n=self.name + 'Curves_grp')
        clsGrp = pm.group(em=True, n=self.name + 'Clusters_grp')
        jntGrp = pm.group(em=True, n=self.name + 'Joints_grp')
        locGrp = pm.group(em=True, n=self.name + 'Locators_grp')

        if pm.objExists('head_contrained'):
            constrained_grp = 'head_contrained'
        else:
            constrained_grp = pm.group(n='head_contrained', em=True)


        pm.parent(crvsGrp, clsGrp, jntGrp, locGrp, sysGrp)
        sysGrp.visibility.set(False)

        pm.delete(self.upCtrlCrv, self.lowCtrlCrv, ch=True)

        self.upEdgeLoop = selectLoopByLocators(mesh=self.mesh, loc1=self.inCorner, loc2=self.outCorner, loc3=self.upCorner)
        pm.select(self.upEdgeLoop)
        upCrv = pm.polyToCurve(form=2, degree=1, n=self.name+'UpperCrv', ch=False)[0]
        self.upCrv = pm.rebuildCurve(upCrv, rt=3, rpo=True, d=3, end=1, kr=0, kcp=1,
                                     kep=0, kt=0, s=25, tol=0.01, ch=False)[0]

        if not atStart(loc=self.inCorner, crvName=self.upCrv):
            pm.reverseCurve(self.upCrv, ch=False, replaceOriginal=True)

        self.lowEdgeLoop = selectLoopByLocators(mesh=self.mesh, loc1=self.inCorner, loc2=self.outCorner, loc3=self.lowCorner)
        pm.select(self.lowEdgeLoop)
        lowCrv = pm.polyToCurve(form=2, degree=1, n=self.name+'LowerCrv', ch=False)[0]
        self.lowCrv = pm.rebuildCurve(lowCrv, rt=3, rpo=True, d=3, end=1, kr=0, kcp=1,
                                      kep=0, kt=0, s=25, tol=0.01, ch=False)[0]

        if not atStart(loc=self.inCorner, crvName=self.lowCrv):
            pm.reverseCurve(self.lowCrv, ch=False, replaceOriginal=True)

        upBlink = pm.rebuildCurve(self.upCrv, s=20, rt=0, rpo=False, ch=False, n=self.name+'upBlink')[0]
        lowBlink = pm.rebuildCurve(self.lowCrv, s=20, rt=0, rpo=False, ch=False, n=self.name+'lowBlink')[0]
        upTarget = pm.rebuildCurve(self.upCrv, s=20, rt=0, rpo=False, ch=False, n=self.name+'upTarget')[0]
        lowTarget = pm.rebuildCurve(self.lowCrv, s=20, rt=0, rpo=False, ch=False, n=self.name+'lowTarget')[0]
        midTarget = pm.rebuildCurve(self.lowCrv, s=20, rt=0, rpo=False, ch=False, n=self.name+'midTarget')[0]

        pm.parent (upTarget, lowTarget, midTarget, lowBlink, upBlink, self.upCtrlCrv, self.lowCtrlCrv,
                   self.upCrv, self.lowCrv, crvsGrp)

        w1 = pm.wire(self.upCrv, w=upBlink)[0]
        w2 = pm.wire(self.lowCrv, w=lowBlink)[0]
        w3 = pm.wire(upTarget, w=self.upCtrlCrv)[0]
        w4 = pm.wire(lowTarget, w=self.lowCtrlCrv)[0]

        bs_upBlink = pm.blendShape(upTarget, midTarget, upBlink, n=self.name+"blendShapeUpBlink")
        bs_lowBlink = pm.blendShape(lowTarget, midTarget, lowBlink, n=self.name+"blendShapeLowBlink")
        bs_mid = pm.blendShape(lowTarget, upTarget, midTarget, n=self.name+"blendShapeLowBlink")

        # setting blendshape reverse connections
        rev_node = pm.createNode("reverse")
        pm.connectAttr(bs_upBlink[0].attr(midTarget.name()), rev_node + ".inputX")
        pm.connectAttr(rev_node + ".outputX", bs_upBlink[0].attr(upTarget.name()))
        rev_node = pm.createNode("reverse")
        pm.connectAttr(bs_lowBlink[0].attr(midTarget.name()), rev_node + ".inputX")
        pm.connectAttr(rev_node + ".outputX", bs_lowBlink[0].attr(lowTarget.name()))
        rev_node = pm.createNode("reverse")
        pm.connectAttr(bs_mid[0].attr(upTarget.name()), rev_node + ".inputX")
        pm.connectAttr(rev_node + ".outputX", bs_mid[0].attr(lowTarget.name()))

        # setting default values
        bs_mid[0].attr (upTarget.name ()).set (.3)

        cvsUp = self.upCtrlCrv.getCVs(space="world")
        cvsLow = self.lowCtrlCrv.getCVs(space="world")

        upCtrls=[]
        lowCtrls=[]
        cornerCtrls=[]

        for i in range(1, 4):
            pos = cvsUp[i]
            clsUp = pm.cluster(self.upCtrlCrv.cv[i], n=self.name+'ClsUp'+str(i))[1]
            pm.group()
            rp = pm.xform(clsUp, q=True, rp=True, ws=True)
            grp = pm.group(em=True, n=clsUp.name()+'off1_grp')
            pm.xform(grp, t=rp, ws=True)
            grp1 = pm.duplicate(grp, n=clsUp.name()+'off2_grp')[0]
            pm.parent(grp, grp1)
            pm.parent(clsUp.getParent(), grp)
            pm.parent(grp1, clsGrp)

            ctrlUp = controlTools.cntrlCrv (name=self.name + 'EyeLidUp' + str(i), obj=clsUp, connType='connection',
                                            hasZeroGrp=True, cntrlSulfix='_ctrl', icone='circuloZ', size=.1, offsets=1)

            ctrlUp.getParent().translate >> grp.translate
            ctrlUp.getParent().rotate >> grp.rotate
            ctrlUp.getParent().scale >> grp.scale

            pm.xform(ctrlUp.getParent(2), ws=True, t=pos)
            pm.parent(ctrlUp.getParent(2), cnstrGrp)
            upCtrls.append(ctrlUp)

            pos = cvsLow[i]
            clsLow = pm.cluster(self.lowCtrlCrv.cv[i], n=self.name+'ClsLow'+str(i))[1]
            pm.group()
            rp = pm.xform(clsLow, q=True, rp=True, ws=True)
            grp = pm.group(em=True, n=clsLow.name()+'off1_grp')
            pm.xform(grp, t=rp, ws=True)
            grp1 = pm.duplicate(grp, n=clsLow.name()+'off2_grp')[0]
            pm.parent(grp, grp1)
            pm.parent(clsLow.getParent(), grp)
            pm.parent(grp1, clsGrp)

            ctrlLow = controlTools.cntrlCrv (name=self.name + 'EyeLidLow' + str(i), obj=clsLow, connType='connection',
                                             hasZeroGrp=True, cntrlSulfix='_ctrl', icone='circuloZ', size=.1, offsets=1)

            ctrlLow.getParent().translate >> grp.translate
            ctrlLow.getParent().rotate >> grp.rotate
            ctrlLow.getParent().scale >> grp.scale

            pm.xform(ctrlLow.getParent(2), ws=True, t=pos)
            pm.parent(ctrlLow.getParent(2), cnstrGrp)
            lowCtrls.append(ctrlLow)

        for i in [0, 4]:
            pos = cvsUp[i]
            clsCorner = pm.cluster(self.upCtrlCrv.cv[i], self.lowCtrlCrv.cv[i], n=self.name+'ClsCorner'+str(i))[1]
            pm.group()
            rp = pm.xform(clsCorner, q=True, rp=True, ws=True)
            grp = pm.group(em=True, n=clsCorner.name()+'off1_grp')
            pm.xform(grp, t=rp, ws=True)
            grp1 = pm.duplicate(grp, n=clsCorner.name()+'off2_grp')[0]
            pm.parent(grp, grp1)
            pm.parent(clsCorner.getParent(), grp)
            pm.parent(grp1, clsGrp)

            ctrlCorner = controlTools.cntrlCrv(name=self.name + 'EyeLidCorner' + str(i), obj=clsCorner, connType='connection',
                                               hasZeroGrp=True, cntrlSulfix='_ctrl', icone='circuloZ', size=.1, offsets=1)

            pm.xform (ctrlCorner.getParent(2), ws=True, t=pos)
            pm.parent(ctrlCorner.getParent(2), cnstrGrp)
            cornerCtrls.append(ctrlCorner)

        upCrvNode = pm.PyNode(self.upCrv)
        lowCrvNode = pm.PyNode(self.lowCrv)
        centerPos = pm.xform(self.eyeCenter, q=True, ws=True, t=True)




        cvs = upCrvNode.getCVs(space="world")
        aimLocs = []
        for i, pos in enumerate(cvs):
            pm.select(cl=True)
            jntBase = pm.joint(p=centerPos, n=self.name+'EyelidUp_' + str (i) + '_zero')
            jnt = pm.joint(p=pos, n=self.name+'EyelidUp_' + str (i) + '_jnt')
            self.skinJoints.append(jnt.name())
            pm.joint(jntBase, e=True, zso=True, oj='xyz', sao='yup')
            pm.parent (jntBase, jntGrp)
            loc = pm.spaceLocator(p=[0, 0, 0], n=jnt.name() + 'UpAim_loc')
            loc.translate.set(pos)
            loc.localScale.set(.01, .01, .01)
            pm.aimConstraint(loc, jntBase, aim=(1, 0, 0), u=(0, 1, 0), wut='vector', wu=(0, 1, 0))
            pm.parent(loc, locGrp)
            aimLocs.append(loc)

        pm.select(aimLocs, self.upCrv)
        attachTools.hookOnCurve(tangent=False)

        cvs = lowCrvNode.getCVs(space="world")
        aimLocs = []
        for i, pos in enumerate(cvs):
            pm.select(cl=True)
            jntBase = pm.joint(p=centerPos, n=self.name+'EyelidLw_' + str (i) + '_zero')
            jnt = pm.joint(p=pos, n=self.name+'EyelidLw_' + str (i) + '_jnt')
            self.skinJoints.append(jnt.name())
            pm.joint(jntBase, e=True, zso=True, oj='xyz', sao='yup')
            pm.parent(jntBase, jntGrp)
            loc = pm.spaceLocator(p=[0, 0, 0], n=jnt.name () + 'LwAim_loc')
            loc.translate.set(pos)
            loc.localScale.set(.01, .01, .01)
            pm.aimConstraint(loc, jntBase, aim=(1, 0, 0), u=(0, 1, 0), wut='vector', wu=(0, 1, 0))
            pm.parent(loc, locGrp)
            aimLocs.append(loc)

        pm.select(aimLocs, self.lowCrv)
        attachTools.hookOnCurve(tangent=False)

        pm.parentConstraint(upCtrls[1], cornerCtrls[0], upCtrls[0].getParent(), mo=1)
        pm.parentConstraint(upCtrls[1], cornerCtrls[1], upCtrls[2].getParent(), mo=1)
        pm.parentConstraint(lowCtrls[1], cornerCtrls[0], lowCtrls[0].getParent(), mo=1)
        pm.parentConstraint(lowCtrls[1], cornerCtrls[1], lowCtrls[2].getParent(), mo=1)

        up_ctl = upCtrls[1]
        pm.addAttr(up_ctl, ln="blink", at="float", dv=0, minValue=0, maxValue=1, k=True)
        pm.addAttr(up_ctl, ln="blinkMult", at="float", dv=1, minValue=1, maxValue=2, k=True)
        pm.addAttr(up_ctl, ln="blinkHeight", at="float", dv=0.3, minValue=0, maxValue=1, k=True)
        pm.addAttr(up_ctl, ln="fleshyEye", at="float", dv=0.5, minValue=0, maxValue=1, k=True)

        fleshyEye_loc = pm.spaceLocator(n=self.name+'FleshyEye_loc')
        fleshyEye_loc.visibility.set(0)
        pm.parent(fleshyEye_loc, cnstrGrp)
        pm.xform(fleshyEye_loc, t=centerPos, ws=True)
        pm.parentConstraint(fleshyEye_loc, upCtrls[1].getParent(), mo=1)
        pm.parentConstraint(fleshyEye_loc, lowCtrls[1].getParent(), mo=1)
        fleshyEyeMulti = pm.createNode('multiplyDivide', name=self.name+'multiFleshy')
        fleshyEyeMulti.output.outputX >> fleshyEye_loc.rotate.rotateX
        fleshyEyeMulti.output.outputY >> fleshyEye_loc.rotate.rotateY
        fleshyEyeMulti.output.outputZ >> fleshyEye_loc.rotate.rotateZ
        up_ctl.fleshyEye >> fleshyEyeMulti.input2.input2X
        up_ctl.fleshyEye >> fleshyEyeMulti.input2.input2Y
        up_ctl.fleshyEye >> fleshyEyeMulti.input2.input2Z


        mult_node = pm.createNode('multDoubleLinear', name=self.name+'multBlink')
        up_ctl.blink >> mult_node.input1
        up_ctl.blinkMult >> mult_node.input2
        mult_node.output >> bs_upBlink[0].attr(midTarget.name())
        mult_node.output >> bs_lowBlink[0].attr(midTarget.name())

        up_ctl.blinkHeight >> bs_mid[0].attr(upTarget.name())

        reverse_node = pm.createNode('reverse', name=self.name+'blinkReverse')
        up_ctl.blink >> reverse_node.inputX
        reverse_node.outputX >> w1.scale[0]
        reverse_node.outputX >> w2.scale[0]
        reverse_node.outputX >> w3.scale[0]
        reverse_node.outputX >> w4.scale[0]

        self.guideMoveall.visibility.set(0)
        pm.parent(cnstrGrp, constrained_grp)

    def autoSkin(self, paralelLoops=5, holdJoint=None):
        skinCls = skinTools.findSkinCluster(self.mesh)

        edgeloop = self.upEdgeLoop+self.lowEdgeLoop

        if not skinCls:
            pm.skinCluster(self.mesh, holdJoint)
            influencesToAdd = self.skinJoints
        else:
            influenceList = pm.skinCluster(skinCls, query=True, influence=True)
            influencesToAdd = [x for x in self.skinJoints if x not in influenceList]

        pm.skinCluster(skinCls, e=True, ai=influencesToAdd, wt=0)

        vtx = vtxWalk.edgeLoopToVextex(edgeloop)
        pm.skinPercent(skinCls, vtx, resetToDefault=True)
        skinTools.edgeSkin(edgeLoopOriginal=edgeloop, paralelLoopNum=5)

def getConcentricVertexLoop(loop, nbLoops):
    """Get concentric vertex loops

    Arguments:
        loop (list): Vertex loop list
        nbLoops (int): Number of loops to search

    Returns:
        list: the loop list

    """
    loopList = []
    allLoops = []
    for x in loop:
        allLoops.append(x)
    loopList.append(loop)

    for x in range(nbLoops):
        tempLoopList = []
        for v in loop:
            connected = v.connectedVertices()
            for cv in connected:
                if cv not in loop:
                    if cv not in allLoops:
                        allLoops.append(cv)
                        tempLoopList.append(cv)
        loop = []
        for c in tempLoopList:
            loop.append(c)

        loopList.append(tempLoopList)

    return loopList

def getVertexRowsFromLoops(loopList):
    """Get vertex rows from edge loops

    Arguments:
        loopList (list): Edge loop list

    Returns:
        list: vertex rows

    """
    rows = []
    for x in loopList[0]:
        rows.append([x])

    loopListLength = len(loopList) - 1

    for i in range(loopListLength):
        for e, r in enumerate(rows):
            cvs = r[-1].connectedVertices()
            # little trick to force the expansion in 2 directions
            cvs2 = False
            if len(r) > 2:
                cvs2 = r[-2].connectedVertices()

            if cvs2:
                for cv in cvs2:
                    if cv in loopList[i + 1]:
                        rows[e].append(cv)
                        continue
            for cv in cvs:
                if cv in loopList[i + 1]:
                    rows[e].append(cv)
                    continue
    return rows

def getClosestVertex(mayaMesh,pos=[0,0,0]):
    mVector = om.MVector(pos) #using MVector type to represent position
    selectionList = om.MSelectionList()
    selectionList.add(mayaMesh)
    dPath= selectionList.getDagPath(0)
    mMesh=om.MFnMesh(dPath)
    ID = mMesh.getClosestPoint(om.MPoint(mVector),space=om.MSpace.kWorld)[1] #getting closest face ID
    list=pm.ls( pm.polyListComponentConversion (mayaMesh+'.f['+str(ID)+']',ff=True,tv=True),flatten=True)#face's vertices list
    #setting vertex [0] as the closest one
    d=mVector-om.MVector(pm.xform(list[0],t=True,ws=True,q=True))
    smallestDist2=d.x*d.x+d[1]*d[1]+d[2]*d[2] #using distance squared to compare distance
    closest=list[0]
    #iterating from vertex [1]
    for i in range(1,len(list)) :
        d=mVector-om.MVector(pm.xform(list[i],t=True,ws=True,q=True))
        d2=d.x*d.x+d[1]*d[1]+d[2]*d[2]
        if d2<smallestDist2:
            smallestDist2=d2
            closest=list[i]
    return closest

def getEdgeLoopExtremesPoints(edgeLoop):
    vertexList = []
    for x in edgeLoop:
        cv = x.connectedVertices()
        for v in cv:
            if v not in vertexList:
                vertexList.append(v)
    maxX = None
    maxY = None
    minX = None
    minY = None
    upPos = None
    lowPos = None
    inPos = None
    outPos = None

    for x in vertexList:
        pos = x.getPosition(space='world')
        if maxX is None or pos[0] > maxX:
            maxX = pos[0]
            outPos = x
        if maxY is None or pos[1] > maxY:
            maxY = pos[1]
            upPos = x
        if minX is None or pos[0] < minX:
            minX = pos[0]
            inPos = x
        if minY is None or pos[1] < minY:
            minY = pos[1]
            lowPos = x
    return inPos, outPos, upPos, lowPos

def edgeLoopSort(edgeLoop, vertStart, vertEnd=None):
    extremesVertices = []
    edgeLoopSorted = []
    edgeCurrent = None
    count = 0
    hasNext = True
    firstHalf = []
    secondHalf = []

    for e in edgeLoop:
        for vxt in e.connectedVertices():
            valency = len(vxt.connectedEdges())
            if valency > 4:
                extremesVertices.append(vxt)
    if extremesVertices:
        vertexCurrent = extremesVertices[0]
        cutVertex = vertStart
    else:
        vertexCurrent = vertStart
        cutVertex = vertEnd

    while hasNext:
        connEdges = [x for x in vertexCurrent.connectedEdges() if
                     x in edgeLoop and x != edgeCurrent and x not in edgeLoopSorted]
        if connEdges:
            edgeCurrent = connEdges[0]
            vertexCurrent = [x for x in edgeCurrent.connectedVertices() if x != vertexCurrent][0]
            edgeLoopSorted.append(edgeCurrent)
            if cutVertex and vertexCurrent == cutVertex:
                firstHalf = copy.copy(edgeLoopSorted)
        else:
            hasNext = False

        count += 1
        if count > 100:
            break

    if cutVertex:
        try:
            secondHalf = [x for x in edgeLoopSorted if x not in firstHalf]
        except:
            pass

    return [edgeLoopSorted, firstHalf, secondHalf]

def selectLoopByLocators(mesh=None, loc1=None, loc2=None, loc3=None):
    pos1 = pm.xform(loc1, q=True, ws=True, t=True)
    pos2 = pm.xform(loc2, q=True, ws=True, t=True)
    pos3 = pm.xform(loc3, q=True, ws=True, t=True)
    closest1 = getClosestVertex(mesh.name(), pos=pos1)
    closest2 = getClosestVertex(mesh.name(), pos=pos2)
    closest3 = getClosestVertex(mesh.name(), pos=pos3)
    pm.select(closest1)
    edges = closest1.connectedEdges()
    foundLoop=None
    for e in edges:
        edgeloop = pm.polySelect(mesh, edgeLoop=e.index())
        vertexLoop = pm.ls(pm.polyListComponentConversion(fe=True, tv=True), fl=True)
        if closest2 in vertexLoop and closest3 in vertexLoop:
            foundLoop = vertexLoop

    foundEdgeloop = []
    for vtx in foundLoop:
        edges = vtx.connectedEdges()
        for e in edges:
            conVtxs = e.connectedVertices()
            if conVtxs[0] in foundLoop and conVtxs[1] in foundLoop:
                foundEdgeloop.append(e)

    sortedEdgeloop = edgeLoopSort(foundEdgeloop, closest1,closest2)
    rev=False
    foundSegment = None
    for i in range(1, 3):
        pm.select(sortedEdgeloop[i])
        vertexLoop = pm.ls(pm.polyListComponentConversion(fe=True, tv=True), fl=True)
        if closest3 in vertexLoop:
            foundSegment = sortedEdgeloop[i]

    return foundSegment

def atStart(loc=None, crvName=None):
    crv = pm.PyNode(crvName)
    Ax, Ay, Az = pm.xform(crv.cv[0], t=True, ws=True, q=True)
    Bx, By, Bz = pm.xform(crv.cv[-1], t=True, ws=True, q=True)
    Cx, Cy, Cz = pm.xform(loc, t=True, q=True, ws=True)

    dist1 = ((Ax - Cx) ** 2 + (Ay - Cy) ** 2 + (Az - Cz) ** 2) ** 0.5
    dist2 = ((Bx - Cx) ** 2 + (By - Cy) ** 2 + (Bz - Cz) ** 2) ** 0.5

    if dist1 < dist2:
        return True
    else:
        return False

def eyeLidJnts(eyeCenter,eyeUp, verts):
    #selecione os vertives da palpebra
    center = pm.PyNode (eyeCenter)
    centerPos = center.translate.get()
    for vert in verts:
        pos = vert.getPosition(space='world')
        pm.select (cl=True)
        jntBase = pm.joint (p=centerPos)
        jnt =  pm.joint (p=pos)
        pm.joint( jntBase, e=True, zso=True, oj='xyz', sao='yup')
        loc = pm.spaceLocator (p=[0,0,0], n=jnt.name()+'Aim_loc')
        loc.translate.set(pos)
        pm.aimConstraint ( loc, jntBase,aim=(1,0,0), u=(0,1,0),wut='objectrotation', wu=(0,1,0), wuo=eyeUp)

def eyeDirRig():
    sel = pm.ls(sl=True)
    if not len(sel) == 3:
        logger.info('selecione joint da cabeca e as esferas do olho')
    else:
        for obj in sel[1:3]:
            cls = pm.cluster (obj)
            loc = pm.group(empty=True, n='eyeRot_grp')
            pos = pm.xform  (cls, q=True, ws=True, rp=True)
            pm.delete (cls)
            loc.translate.set(pos)
            loc1= loc.duplicate (n='eyeRotFk_grp')[0]
            loc2= loc.duplicate (n='eyeRotAim_grp')[0]
            loc3= loc.duplicate (n='eyeRotDeform_grp')[0]
            loc.rotate >> loc3.rotate
            loc.rotate >> loc3.rotate
            pm.orientConstraint (loc1,loc2,loc)
            #faz controles
            cntrlFk = gen.createCntrl (loc1.name(),loc1.name(),.5, 'ponteiroReto', 1)
            pm.orientConstraint (cntrlFk,loc1, mo=True)
            cntrlAim = gen.createCntrl (loc2.name(),loc2.name(),.5, 'circuloZ', 1)
            aim = pm.PyNode(cntrlAim)
            aim.translate.set([0,0,2])
            aim.rename ('eyeAimTgt')
            pm.aimConstraint ( aim, loc2,aim=(0,0,1), u=(0,1,0),wut='objectrotation', wu=(1,0,0), wuo=sel[0])

        aimList = pm.ls ('eyeAimTgt*', type='transform')
        aimGrp = pm.group(empty=True, n='eyeAim_grp')
        tmp = pm.pointConstraint (aimList,aimGrp)
        pm.delete (tmp)

        cntrlAimGrp = gen.createCntrl (aimGrp.name(),aimGrp.name(),1, 'circuloX', 1)
        pm.parent (aimList, cntrlAimGrp)
