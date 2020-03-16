import pymel.core as pm
import logging
import os.path

import autoRig3.modules.jaw as jaw
import autoRig3.modules.lookAt as lookAt
import autoRig3.modules.squash as squash
import autoRig3.modules.mouthBlends as mouth
import autoRig3.modules.eyeLid as eyelid
import autoRig3.composites.eyeBrows as eyeBrows
import autoRig3.modules.lips as lips
import autoRig3.modules.eyeSocket as eyeSocket
import autoRig3.tools.spaceSwitchTools as space
import logging

logger = logging.getLogger('autoRig')
logger.setLevel(10)

reload(jaw)
reload(lookAt)
reload(squash)
reload(mouth)
reload(eyelid)
reload(eyeBrows)
reload(lips)
reload(space)

def addHideAtts():
    sel = pm.ls (sl=True)
    obj = sel[0]

    pm.addAttr (obj, ln='FACIAL', at='enum', en='------', k=1)
    pm.addAttr (obj, ln='squashCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='eyebrowBlendCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='eyebrowTweakCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='eyeSocketCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='eyelidCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='faceTweaksCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='mouthBlendCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='lipsCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='jawCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='teethCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='tongueCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='lookatCtrlVis', at='float', min=0, max=1, dv=0, k=1)

    pm.addAttr (obj, ln='BODY', at='enum', en='------', k=1)
    pm.addAttr (obj, ln='limbBezierCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='limbBendCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='limbMidCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='tweaksCtrlVis', at='float', min=0, max=1, dv=0, k=1)

    pm.addAttr (obj, ln='IKFK', at='enum', en='------', k=1)
    pm.addAttr (obj, ln='lookatIKFK', at='float', min=0, max=1, dv=0, k=1)

    larm = pm.PyNode ('L_armBezierMoveall')
    rarm = pm.PyNode ('R_armBezierMoveall')
    lleg = pm.PyNode ('L_legBezierMoveall')
    rleg = pm.PyNode ('R_legBezierMoveall')
    look = pm.PyNode ('lookAtCtrl_grp')
    jaw = pm.PyNode ('jaw_ctrl_grp')
    rlid = pm.PyNode ('R_eyeLidEyeLid_constrained_grp')
    llid = pm.PyNode ('L_eyeLidEyeLid_constrained_grp')
    mouthBlends = pm.PyNode ('mouthCornersMoveall')
    tweak1 = pm.PyNode ('faceConstrained')
    tweak2 = pm.PyNode ('R_squintConstrained')
    tweak3 = pm.PyNode ('L_squintConstrained')
    lips = pm.PyNode ('lips_ctrl_grp')
    lbrowTweak = pm.PyNode ('L_eyeBrowtweakCtrls_grp')
    rbrowTweak = pm.PyNode ('R_eyeBrowtweakCtrls_grp')
    rbrowblend = pm.PyNode ('R_eyeBrowSliders_grp')
    lbrowblend = pm.PyNode ('L_eyeBrowSliders_grp')
    headSquash = pm.PyNode ('headSquashCtrl_grp')
    jawdSquash = pm.PyNode ('jawSquashCtrl_grp')
    lsocket = pm.PyNode ('L_eyeSocket_ctrl_grp')
    rsocket = pm.PyNode ('R_eyeSocket_ctrl_grp')
    tongue = pm.PyNode ('tongue0_grp')
    teeth1 = pm.PyNode ('teeth_up_ctrl_grp')
    teeth2 = pm.PyNode ('teeth_dw_ctrl_grp')

    obj.squashCtrlVis >> headSquash.visibility
    obj.squashCtrlVis >> jawdSquash.visibility
    obj.eyebrowBlendCtrlVis >> rbrowblend.visibility
    obj.eyebrowBlendCtrlVis >> lbrowblend.visibility
    obj.eyebrowTweakCtrlVis >> lbrowTweak.visibility
    obj.eyebrowTweakCtrlVis >> rbrowTweak.visibility
    obj.eyeSocketCtrlVis >> lsocket.visibility
    obj.eyeSocketCtrlVis >> rsocket.visibility
    obj.eyelidCtrlVis >> rlid.visibility
    obj.eyelidCtrlVis >> llid.visibility
    obj.faceTweaksCtrlVis >> tweak1.visibility
    obj.faceTweaksCtrlVis >> tweak2.visibility
    obj.faceTweaksCtrlVis >> tweak3.visibility
    obj.mouthBlendCtrlVis >> mouthBlends.visibility
    obj.lipsCtrlVis >> lips.visibility
    obj.jawCtrlVis >> jaw.visibility
    obj.teethCtrlVis >> teeth1.visibility
    obj.teethCtrlVis >> teeth2.visibility
    obj.tongueCtrlVis >> tongue.visibility

    obj.limbMidCtrlVis >> larm.midCtrlViz
    obj.limbMidCtrlVis >> rarm.midCtrlViz
    obj.limbMidCtrlVis >> lleg.midCtrlViz
    obj.limbMidCtrlVis >> rleg.midCtrlViz

    obj.limbBezierCtrlVis >> larm.bezierCtrlViz
    obj.limbBezierCtrlVis >> rarm.bezierCtrlViz
    obj.limbBezierCtrlVis >> lleg.bezierCtrlViz
    obj.limbBezierCtrlVis >> rleg.bezierCtrlViz

    obj.limbBendCtrlVis >> larm.bendExtraCtrlViz
    obj.limbBendCtrlVis >> rarm.bendExtraCtrlViz
    obj.limbBendCtrlVis >> lleg.bendExtraCtrlViz
    obj.limbBendCtrlVis >> rleg.bendExtraCtrlViz

    obj.lookatCtrlVis >> look.visibility
    obj.lookatIKFK >> look.ikFk

class Facial:
    def __init__(self, ui = None):
        self.ui = ui

        self.lookAt = None
        self.eyelid = None
        self.eyeSocket = None
        self.jaw = None
        self.lips = None
        self.eyebrow = None
        self.mouth = None
        self.headSquash = None
        self.jawSquash  = None
        self.tweaks = None
        self.headJnts = None

    def uiSetup(self):
        try:
            logger.debug('Setting FacialUI...')
            self.ui.lookat_doGuide_btn.clicked.connect(self.lookAt_doGuide)
            self.ui.lookat_doRig_btn.clicked.connect(self.lookAt_doRig)
            self.ui.lookat_headJntPick_btn.clicked.connect (lambda par = self.ui.lookat_headJnt_txt:
                                                            self.setFieldFromSel(field = par))
            self.ui.lookat_eyeballSelectPick_btn.clicked.connect (lambda par = self.ui.lookat_eyeball_txt:
                                                            self.setFieldFromSel(field = par))

            self.ui.eyelid_doGuide_btn.clicked.connect (self.eyelid_doGuide)
            self.ui.eyelid_doRig_btn.clicked.connect(self.eyelid_doRig)
            self.ui.eyelid_autoSkin_btn.clicked.connect(self.eyelid_autoSkin)

            self.ui.eyelid_edgeSelectPick_btn.clicked.connect(lambda par=self.ui.eyelid_edgeSelect_txt:
                                                              self.setFieldFromSel(field=par, multiple=True))
            self.ui.eyelid_eyeballSelectPick_btn.clicked.connect(lambda par = self.ui.eyelid_eyeball_txt:
                                                                  self.setFieldFromSel(field = par))
            self.ui.eyelid_holdJntlSelectPick_btn.clicked.connect(lambda par = self.ui.eyelid_holdJnt_txt:
                                                                  self.setFieldFromSel(field = par))

            self.ui.socket_eyeballBrowse_btn.clicked.connect (lambda par = self.ui.socket_eyeball_txt:
                                                            self.setFieldFromSel(field = par))

            self.ui.socket_doGuide_btn.clicked.connect(self.socket_doGuide)
            self.ui.socket_doRig_btn.clicked.connect(self.socket_doRig)

            self.ui.jaw_doGuide_btn.clicked.connect(self.jaw_doGuide)
            self.ui.jaw_doRig_btn.clicked.connect(self.jaw_doRig)

            self.ui.lips_doGuide_btn.clicked.connect(self.lips_doGuide)
            self.ui.lips_doRig_btn.clicked.connect(self.lips_doRig)
            self.ui.lips_autoSkin_btn.clicked.connect(self.lips_autoSkin)
            self.ui.lips_edgeSelect_btn.clicked.connect(lambda par=self.ui.lips_edgeSelect_txt:
                                                        self.setFieldFromSel(field=par, multiple=True))

            self.ui.eyebrow_doGuide_btn.clicked.connect (self.eyebrowBlend_doGuide)
            self.ui.eyebrow_doRig_btn.clicked.connect(self.eyebrowBlend_doRig)
            self.ui.eyebrow_targetsBrowse_btn.clicked.connect (lambda par=self.ui.eyebrow_targets_txt:
                                                                self.setFieldFromSel(field = par, multiple=True))
            self.ui.eyebrow_upShapeBrowse_btn.clicked.connect (lambda par=self.ui.eyebrow_upShape_txt:
                                                            self.setFieldFromSel(field = par, multiple=True))
            self.ui.eyebrow_downShapeBrowse_btn.clicked.connect (lambda par=self.ui.eyebrow_downShape_txt:
                                                            self.setFieldFromSel(field = par, multiple=True))
            self.ui.eyebrow_neutralShapeBrowse_btn.clicked.connect (lambda par=self.ui.eyebrow_neutralShape_txt:
                                                            self.setFieldFromSel(field = par, multiple=True))
            self.ui.eyebrow_compressShapeBrowse_btn.clicked.connect (lambda par=self.ui.eyebrow_compressShape_txt:
                                                            self.setFieldFromSel(field = par, multiple=True))

            self.ui.mouth_targetsBrowse_btn.clicked.connect (lambda par=self.ui.mouth_targets_txt:
                                                             self.setFieldFromSel(field=par, multiple=True))
            self.ui.mouth_doGuide_btn.clicked.connect(self.mouthBlends_doGuide)
            self.ui.mouth_doRig_btn.clicked.connect(self.mouthBlends_doRig)
            self.ui.mouth_autoDetectShapes_btn.clicked.connect(self.mouthBlends_autoDetect)

            self.ui.squash_doGuide_btn.clicked.connect(self.headSquash_doGuide)
            self.ui.squash_doRig_btn.clicked.connect(self.headSquash_doRig)

            self.ui.jawSquash_doGuide_btn.clicked.connect(self.jawSquash_doGuide)
            self.ui.jawSquash_doRig_btn.clicked.connect(self.jawSquash_doRig)

        except:
            logger.error('ui setup failled!')
            raise

    @staticmethod
    def setFieldFromSel(field=None, multiple=False):
        sel = pm.ls(sl=True, fl=True)

        if not sel:
            logging.info('nothing is selected!')
            return

        if multiple:
            name = (', ').join([x.name () for x in sel])
            field.setText(name)
        else:
            name = sel[0].name()
            field.setText(name)

        return name
        logger.debug (name)

    @staticmethod
    def getObjFromField(field=None):
        text = field.text()
        try:
            objs =[pm.PyNode(x) for x in text.split(',')]
            if len(objs) == 1:
                objs = objs[0]
        except:
            objs = None
            logger.info('cant find objs')

        return objs

    def lookAt_doGuide(self):
        getDictFromScene = self.ui.lookat_getGuide_chk.isChecked()
        eyeball = self.getObjFromField(self.ui.lookat_eyeball_txt)
        self.lookAt = lookAt.EyesDir(name='lookAt')

        if getDictFromScene:
            self.lookAt.getDict()
        pm.undoInfo(openChunk=True)
        try:
            self.lookAt.doGuide(eyeball=eyeball)
        finally:
            pm.undoInfo(closeChunk=True)

    def lookAt_doRig(self):
        headJnt = self.getObjFromField(self.ui.lookat_headJnt_txt)

        pm.undoInfo(openChunk=True)
        try:
            self.lookAt.doRig(upVectorObj=headJnt)

            try:
                space.addSpc(self.lookAt.lookAt_ctrl, ['global', 'head', 'cog'],
                             self.lookAt.lookAt_ctrl.getParent())
            except:
                pass
        finally:
            pm.undoInfo(closeChunk=True)

    def eyelid_doGuide(self):
        getDictFromScene = self.ui.eyelid_getGuide_chk.isChecked()

        eyeball = self.getObjFromField(self.ui.eyelid_eyeball_txt)

        self.Leyelid = eyelid.EyeLid(name='L_eyeLid')
        self.Reyelid = eyelid.EyeLid(name='R_eyeLid')

        pm.undoInfo(openChunk=True)
        try:
            if getDictFromScene:
                self.Leyelid.getDict()
                self.Reyelid.getDict()
                edges = self.getObjFromField(self.ui.eyelid_edgeSelect_txt)
                self.Leyelid.doGuide(eyeball=eyeball, edgeLoop=edges, autoExtremes=False)
                self.Reyelid.doGuide()
                self.Reyelid.mirrorConnectGuide(self.Leyelid)
            else:
                edges = self.getObjFromField(self.ui.eyelid_edgeSelect_txt)
                self.Leyelid.doGuide(eyeball=eyeball, edgeLoop=edges, autoExtremes=True)
                self.Reyelid.doGuide()
                self.Reyelid.mirrorConnectGuide(self.Leyelid)
        finally:
            pm.undoInfo(closeChunk=True)

    def eyelid_doRig(self):

        pm.undoInfo(openChunk=True)
        try:
            self.Leyelid.doRig()
            self.Reyelid.doRig()

            try:
                LeyeJnt = pm.PyNode('L_eye_jxt')
                ReyeJnt = pm.PyNode('R_eye_jxt')
                Rmulti = pm.PyNode('R_eyeLidmultiFleshy')
                Lmulti = pm.PyNode('L_eyeLidmultiFleshy')
                LeyeJnt.rotate.rotateX >> Lmulti.input1.input1X
                LeyeJnt.rotate.rotateY >> Lmulti.input1.input1Y
                LeyeJnt.rotate.rotateZ >> Lmulti.input1.input1Z

                ReyeJnt.rotate.rotateX >> Rmulti.input1.input1X
                ReyeJnt.rotate.rotateY >> Rmulti.input1.input1Y
                ReyeJnt.rotate.rotateZ >> Rmulti.input1.input1Z
            except:
                pass
        finally:
            pm.undoInfo(closeChunk=True)

    def eyelid_autoSkin(self):
        num = self.ui.eyelid_paralelEdges_spin.value()
        holdJnt = pm.PyNode(self.getObjFromField(self.ui.eyelid_holdJnt_txt))
        print holdJnt.name()
        self.Leyelid.autoSkin(paralelLoops=num, holdJoint=holdJnt)
        self.Reyelid.autoSkin(paralelLoops=num, holdJoint=holdJnt)

    def socket_doGuide(self):
        self.eyeSocket = eyeSocket.EyeSocket()
        eyeball = self.getObjFromField(self.ui.socket_eyeball_txt)
        getDictFromScene = self.ui.socket_getGuide_chk.isChecked()

        pm.undoInfo(openChunk=True)
        try:
            if getDictFromScene:
                self.eyeSocket.getDict()

            self.eyeSocket.doGuide(eyeball=eyeball)
        finally:
            pm.undoInfo(closeChunk=True)

    def socket_doRig(self):
        pm.undoInfo(openChunk=True)
        try:
            self.eyeSocket.doRig()
        finally:
            pm.undoInfo(closeChunk=True)
    def jaw_doGuide(self):
        getGuidefromScene = self.ui.jaw_getGuide_chk.isChecked()
        self.jaw = jaw.Jaw(name='jaw')

        pm.undoInfo(openChunk=True)
        try:
            if getGuidefromScene:
                self.jaw.getDict()

            self.jaw.doGuide()
        finally:
            pm.undoInfo(closeChunk=True)

    def jaw_doRig(self):
        pm.undoInfo(openChunk=True)
        try:
            self.jaw.doRig()
        finally:
            pm.undoInfo(closeChunk=True)

    def lips_doGuide(self):
        getGuidefromScene = self.ui.lips_getGuide_chk.isChecked()
        self.lips = lips.Lips()

        pm.undoInfo(openChunk=True)
        try:
            if getGuidefromScene:
                self.lips.getDict()

            edges = self.getObjFromField(self.ui.lips_edgeSelect_txt)
            self.lips.doGuide(edges=edges)
        finally:
            pm.undoInfo(closeChunk=True)

    def lips_doRig(self):
        pm.undoInfo(openChunk=True)
        try:
            self.lips.doRig()
        finally:
            pm.undoInfo(closeChunk=True)

    def lips_autoSkin(self):
        num1 = self.ui.lips_paralelEdges1_spin.value()
        num2 = self.ui.lips_paralelEdges2_spin.value()
        holdJnt = pm.PyNode(self.getObjFromField(self.ui.lips_holdJnt_txt))

        pm.undoInfo(openChunk=True)
        try:
            self.lips.autoSkin(paralelLoops1=num1, paralelLoops2=num2, holdJoint=holdJnt)
        finally:
            pm.undoInfo(closeChunk=True)

    def eyebrowBlend_doGuide(self):
        getGuideFromScene = self.ui.eyebrow_getGuide_chk.isChecked()

        sourceObjs = self.getObjFromField(self.ui.eyebrow_targets_txt)
        neutralObjs = self.getObjFromField(self.ui.eyebrow_neutralShape_txt)
        targetUp = self.getObjFromField(self.ui.eyebrow_upShape_txt)
        targetDown = self.getObjFromField(self.ui.eyebrow_downShape_txt)
        targetCompress = self.getObjFromField(self.ui.eyebrow_compressShape_txt)

        if not isinstance(sourceObjs, list):
            sourceObjs=[sourceObjs]
        if not isinstance(neutralObjs, list):
            neutralObjs = [neutralObjs]
        if not isinstance(targetUp, list):
            targetUp=[targetUp]
        if not isinstance(targetDown, list):
            targetDown=[targetDown]
        if not isinstance(targetCompress, list):
            targetCompress=[targetCompress]

        self.eyebrow = eyeBrows.EyeBrows(name='eyeBrow',
                                         sourceObj=sourceObjs,
                                         targetNeutral=neutralObjs,
                                         targetUp=targetUp,
                                         targetDown=targetDown,
                                         targetCompress=targetCompress)

        pm.undoInfo(openChunk=True)
        try:

            if getGuideFromScene:
                self.eyebrow.getDict()

            self.eyebrow.doGuide()
        finally:
            pm.undoInfo(closeChunk=True)

    def eyebrowBlend_doRig(self):
        pm.undoInfo(openChunk=True)
        try:
            self.eyebrow.doRig()
        finally:
            pm.undoInfo(closeChunk=True)

    def mouthBlends_doGuide(self):
        getGuideFromScene = self.ui.mouth_getGuide_chk.isChecked()

        self.mouth = mouth.MouthBlends(name='mouthCorners')

        pm.undoInfo(openChunk=True)
        try:
            if getGuideFromScene:
                self.mouth.getDict()

            self.mouth.doGuide()
        finally:
            pm.undoInfo(closeChunk=True)

    def mouthBlends_doRig(self):
        applyTargets = self.ui.mouth_splitShapes_chk.isChecked()
        pm.undoInfo(openChunk=True)
        try:
            if applyTargets:
                sourceObj = self.getObjFromField(self.ui.mouth_targets_txt)
                targetList = self.mouthBlends_getTargetListFromUI()

                self.mouth.doRigAndApplyTargets(sourceObj=sourceObj, targetList=targetList, offsets=0.02)
            else:
                self.mouth.doRig()
        finally:
            pm.undoInfo(closeChunk=True)

    def mouthBlends_autoDetect(self):
        sel = pm.ls(sl=True, fl=True)
        if not sel:
            logger.info('Nothing is selected!')

        orderedTargets = mouth.targetOrder(targetList=sel)

        if orderedTargets:
            for i, tgt in enumerate(['up', 'down', 'wide', 'narrow', 'upWide', 'upNarrow',
                                     'downWide', 'downNarrow', 'neutral']):
                try:
                    self.ui.__dict__['mouth_'+tgt+'Shape_txt'].setText(orderedTargets[i].name())
                except:
                    logger.debug('Nao foi possivel setar %s' % tgt)

    def mouthBlends_getTargetListFromUI(self):
        targetList = []
        for i, tgt in enumerate(['up', 'down', 'wide', 'narrow', 'upWide', 'upNarrow',
                                 'downWide', 'downNarrow', 'neutral']):
            targetName = self.ui.__dict__['mouth_' + tgt + 'Shape_txt'].text()
            try:
                targetList.append(pm.PyNode(targetName))
            except:
                targetList.append(None)

        return targetList

    def headSquash_doGuide(self):
        getDictFromScene = self.ui.squash_getGuide_chk.isChecked()
        self.headSquash = squash.Squash(name='headSquash')
        pm.undoInfo(openChunk=True)
        try:
            if getDictFromScene:
                self.headSquash.getDict()

            self.headSquash.doGuide()
        finally:
            pm.undoInfo(closeChunk=True)

    def headSquash_doRig(self):
        pm.undoInfo(openChunk=True)
        try:
            self.headSquash.doRig()
        finally:
            pm.undoInfo(closeChunk=True)

    def jawSquash_doGuide(self):
        getDictFromScene = self.ui.squash_getGuide_chk.isChecked()
        self.jawSquash = squash.Squash (name='jawSquash')

        pm.undoInfo(openChunk=True)
        try:
            if getDictFromScene:
                self.jawSquash.getDict()

            self.jawSquash.doGuide()
        finally:
            pm.undoInfo(closeChunk=True)

    def jawSquash_doRig(self):
        pm.undoInfo(openChunk=True)
        try:
            self.jawSquash.doRig()
        finally:
            pm.undoInfo(closeChunk=True)



