import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.matrixTools as matrixTools
import autoRig3.tools.jointTools as jointTools
import pymel.core as pm
import pymel.util.mathutils as mathutils
import maya.api.OpenMaya as om2
import json
import logging

logger = logging.getLogger('autoRig')

class EyeBrowBlend:
    def __init__(self, name='eyeBrow'):
        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)], 'sliceMax': [(12, 0, 0,), (0, 0, 0)],
                          'sliceMid': [(7, 0, 0), (0, 0, 0)], 'sliceMin': [(2, 0, 0), (0, 0, 0)],
                          'sliceInBtw1': [(4.5, 0, 0), (0, 0, 0)], 'sliceInBtw2': [(9.5, 0, 0), (0, 0, 0)],
                          'tweak1': [(2.5, 0, 0), (0, 0, 0)], 'tweak2': [(5.5, 0, 0), (0, 0, 0)], 'tweak3': [(8.5, 0, 0), (0, 0, 0)],
                          'tweak4': [(11.5, 0, 0), (0, 0, 0)]}
        self.name = name
        self.flipAxis = False
        self.toExport = ['guideDict', 'name', 'sliceGuideSetup', 'tweakGuideSetup', 'flipAxis']
        self.moveallGuideSetup = {'nameTempl': self.name + 'Moveall', 'icone': 'circuloX', 'size': 3,
                                  'color': (1, 0, 0)}
        self.sliceGuideSetup = {'nameTempl': self.name + 'SliceMax', 'icone': 'quadradoX', 'size': 2,
                              'color': (32, .7, .17)}
        self.tweakGuideSetup = {'nameTempl': self.name+'Tweak', 'icone': 'bola', 'size': .2, 'color': (32, .7, .17)}
        self.guideSulfix = '_guide'
        self.jntSulfix = '_jxt'
        self.tweakCtrlSetup = {'nameTempl': self.name + 'Tweak', 'icone': 'bola', 'size': .2, 'color': (32, .7, .17)}
        self.jntSetup = {'nameTempl': self.name, 'size': .1}

    def createCntrl(self, setupName='ctrl', nameTempl=None):
        displaySetup = self.__dict__[setupName+'Setup'].copy()
        if nameTempl:
            cntrlName = nameTempl
        else:
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

    def doGuide(self, **kwargs):
        self.__dict__.update(kwargs)
        self.guideMoveall = self.createCntrl('moveallGuide')
        self.sliceMax = self.createCntrl(setupName='sliceGuide', nameTempl=self.name+'SliceMax'+self.guideSulfix)
        self.sliceMin = self.createCntrl(setupName='sliceGuide', nameTempl=self.name+'SliceMin'+self.guideSulfix)
        self.sliceMid = self.createCntrl(setupName='sliceGuide', nameTempl=self.name+'SliceMid'+self.guideSulfix)
        self.sliceInBtw1 = self.createCntrl(setupName='sliceGuide', nameTempl=self.name + 'SliceInBtw1' + self.guideSulfix)
        self.sliceInBtw2 = self.createCntrl(setupName='sliceGuide', nameTempl=self.name + 'SliceInBtw2' + self.guideSulfix)
        self.tweak1 = self.createCntrl(setupName='tweakGuide', nameTempl=self.name+'Tweak1'+self.guideSulfix)
        self.tweak2 = self.createCntrl(setupName='tweakGuide', nameTempl=self.name+'Tweak2'+self.guideSulfix)
        self.tweak3 = self.createCntrl(setupName='tweakGuide', nameTempl=self.name+'Tweak3'+self.guideSulfix)
        self.tweak4 = self.createCntrl(setupName='tweakGuide', nameTempl=self.name+'Tweak4'+self.guideSulfix)
        pm.parent (self.sliceMin, self.sliceMax, self.sliceMid,self.tweak1, self.tweak2, self.tweak3, self.tweak4,
                   self.sliceInBtw1, self.sliceInBtw2,
                   self.guideMoveall)

        self.setCntrl(self.guideMoveall, 'moveall')
        self.setCntrl(self.sliceMax, 'sliceMax')
        self.setCntrl(self.sliceMid, 'sliceMid')
        self.setCntrl(self.sliceMin, 'sliceMin')
        self.setCntrl(self.sliceInBtw1, 'sliceInBtw1')
        self.setCntrl(self.sliceInBtw2, 'sliceInBtw2')
        self.setCntrl(self.tweak1, 'tweak1')
        self.setCntrl(self.tweak2, 'tweak2')
        self.setCntrl(self.tweak3, 'tweak3')
        self.setCntrl(self.tweak4, 'tweak4')

        pm.addAttr(self.guideMoveall, ln='eyeBrowDict', dt='string')
        self.guideMoveall.eyeBrowDict.set(json.dumps(self.exportDict()))
        
    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.eyeBrowDict.get()
            DictRestored = json.loads(jsonDict)

            self.__dict__.update(**DictRestored)

            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            guideName = self.name+'SliceMax'+self.guideSulfix
            self.sliceMax = pm.PyNode(guideName)
            self.guideDict['sliceMax'][0] = self.sliceMax.getTranslation(space='object').get()
            self.guideDict['sliceMax'][1] = tuple(self.sliceMax.getRotation(space='object'))

            guideName = self.name+'SliceMin'+self.guideSulfix
            self.sliceMin = pm.PyNode(guideName)
            self.guideDict['sliceMin'][0] = self.sliceMin.getTranslation(space='object').get()
            self.guideDict['sliceMin'][1] = tuple(self.sliceMin.getRotation(space='object'))

            guideName = self.name+'SliceMid'+self.guideSulfix
            self.sliceMid = pm.PyNode(guideName)
            self.guideDict['sliceMid'][0] = self.sliceMid.getTranslation(space='object').get()
            self.guideDict['sliceMid'][1] = tuple(self.sliceMid.getRotation(space='object'))

            guideName = self.name+'SliceInBtw1'+self.guideSulfix
            self.sliceInBtw1 = pm.PyNode(guideName)
            self.guideDict['sliceInBtw1'][0] = self.sliceInBtw1.getTranslation(space='object').get()
            self.guideDict['sliceInBtw1'][1] = tuple(self.sliceInBtw1.getRotation(space='object'))

            guideName = self.name+'SliceInBtw2'+self.guideSulfix
            self.sliceInBtw2 = pm.PyNode(guideName)
            self.guideDict['sliceInBtw2'][0] = self.sliceInBtw2.getTranslation(space='object').get()
            self.guideDict['sliceInBtw2'][1] = tuple(self.sliceInBtw2.getRotation(space='object'))

            guideName = self.name+'Tweak1'+self.guideSulfix
            self.tweak1 = pm.PyNode(guideName)
            self.guideDict['tweak1'][0] = self.tweak1.getTranslation(space='object').get()
            self.guideDict['tweak1'][1] = tuple(self.tweak1.getRotation(space='object'))

            guideName = self.name+'Tweak2'+self.guideSulfix
            self.tweak2 = pm.PyNode(guideName)
            self.guideDict['tweak2'][0] = self.tweak2.getTranslation(space='object').get()
            self.guideDict['tweak2'][1] = tuple(self.tweak2.getRotation(space='object'))

            guideName = self.name+'Tweak3'+self.guideSulfix
            self.tweak3 = pm.PyNode(guideName)
            self.guideDict['tweak3'][0] = self.tweak3.getTranslation(space='object').get()
            self.guideDict['tweak3'][1] = tuple(self.tweak3.getRotation(space='object'))

            guideName = self.name+'Tweak4'+self.guideSulfix
            self.tweak4 = pm.PyNode(guideName)
            self.guideDict['tweak4'][0] = self.tweak4.getTranslation(space='object').get()
            self.guideDict['tweak4'][1] = tuple(self.tweak4.getRotation(space='object'))
        except:
            pass

    def mirrorConnectGuide(self, eyeBrow):
        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')
            self.guideMoveall = None

        if not self.guideMoveall:
            self.doGuide()

        if not eyeBrow.guideMoveall:
            eyeBrow.doGuide()

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')

        #if not pm.objExists('GUIDES'):
        #    pm.group(self.name + 'MirrorGuide_grp', n='GUIDES')
        #else:
        #    pm.parent(self.name + 'MirrorGuide_grp', 'GUIDES')

        self.guideMoveall.setParent(self.mirrorGuide)

        #Felipe --> seta valores globais de escala
        scaleValue = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.scaleY.set(1)
        self.mirrorGuide.scaleZ.set(1)
        self.mirrorGuide.scale.lock()
        self.mirrorGuide.rotate.lock()
        self.mirrorGuide.translate.lock()
        self.mirrorGuide.template.set(1)

        eyeBrow.guideMoveall.translate >> self.guideMoveall.translate
        eyeBrow.guideMoveall.rotate >> self.guideMoveall.rotate
        eyeBrow.guideMoveall.scale >> self.guideMoveall.scale
        eyeBrow.sliceMax.translate >> self.sliceMax.translate
        eyeBrow.sliceMax.rotate >> self.sliceMax.rotate
        eyeBrow.sliceMax.scale >> self.sliceMax.scale
        eyeBrow.sliceMid.translate >> self.sliceMid.translate
        eyeBrow.sliceMid.rotate >> self.sliceMid.rotate
        eyeBrow.sliceMid.scale >> self.sliceMid.scale
        eyeBrow.sliceMin.translate >> self.sliceMin.translate
        eyeBrow.sliceMin.rotate >> self.sliceMin.rotate
        eyeBrow.sliceMin.scale >> self.sliceMin.scale

        eyeBrow.sliceInBtw1.translate >> self.sliceInBtw1.translate
        eyeBrow.sliceInBtw1.rotate >> self.sliceInBtw1.rotate
        eyeBrow.sliceInBtw1.scale >> self.sliceInBtw1.scale
        eyeBrow.sliceInBtw2.translate >> self.sliceInBtw2.translate
        eyeBrow.sliceInBtw2.rotate >> self.sliceInBtw2.rotate
        eyeBrow.sliceInBtw2.scale >> self.sliceInBtw2.scale

        eyeBrow.tweak1.translate >> self.tweak1.translate
        eyeBrow.tweak1.rotate >> self.tweak1.rotate
        eyeBrow.tweak1.scale >> self.tweak1.scale

        eyeBrow.tweak2.translate >> self.tweak2.translate
        eyeBrow.tweak2.rotate >> self.tweak2.rotate
        eyeBrow.tweak2.scale >> self.tweak2.scale

        eyeBrow.tweak3.translate >> self.tweak3.translate
        eyeBrow.tweak3.rotate >> self.tweak3.rotate
        eyeBrow.tweak3.scale >> self.tweak3.scale

        eyeBrow.tweak4.translate >> self.tweak4.translate
        eyeBrow.tweak4.rotate >> self.tweak4.rotate
        eyeBrow.tweak4.scale >> self.tweak4.scale

        if eyeBrow.flipAxis:
            self.flipAxis = False
        else:
            self.flipAxis = True

    def doRig(self):
        if pm.objExists(self.name+'Constrained_grp'):
            pm.delete(self.name+'Constrained_grp')
        if pm.objExists(self.name+'tweakSys_grp'):
            pm.delete(self.name+'tweakSys_grp')

        cnstrGrp = pm.group(n=self.name+'Constrained_grp', em=True)
        allSliderGrp = pm.group(n=self.name+'Sliders_grp', em=True)
        tweakCtrlGrp = pm.group(n=self.name+'tweakCtrls_grp', em=True)

        tweakJntGrp = pm.group(n=self.name+'tweakSys_grp', em=True)

        pm.parent(tweakCtrlGrp, allSliderGrp, cnstrGrp)
        tweakJntGrp.visibility.set(False)

        basePos = pm.xform(self.guideMoveall, t=True, q=True, ws=True)

        masterSlderGrp = pm.group(em=True, name=self.name+'global_grp')
        masterSliderCtrl = pm.circle(nr=(0, 0, 1), r=0.2, n=self.name+'global_ctrl')[0]
        pm.parent(masterSliderCtrl, masterSlderGrp)
        pm.parent(masterSlderGrp, allSliderGrp)

        p1 = pm.xform(self.tweak4, q=True, ws=True, t=True)[0]
        p2 = pm.xform(self.tweak3, q=True, ws=True, t=True)[0]

        pm.xform(masterSlderGrp, t=(p1+(p1-p2), basePos[1] + 1, basePos[2] + 1), ws=True)

        displaySetup = self.tweakCtrlSetup.copy()
        tweakGuides = [self.tweak1, self.tweak2, self.tweak3, self.tweak4]
        slidersNames = ['InA', 'InB', 'MidIn', 'MidOutA', 'MidOutB', 'Out']

        guide1Xpos = pm.xform(self.tweak1, q=True, ws=True, t=True)[0]
        guide2Xpos = pm.xform(self.tweak2, q=True, ws=True, t=True)[0]
        offset = guide2Xpos - guide1Xpos

        sliderList = []
        sideMove = True

        for i in range(6):
            slider = createSlider(self.name+slidersNames[i], size=0.1, sideMove=sideMove)
            sliderList.append(slider)
            pm.xform(slider.getParent(), t=(guide1Xpos+offset*i, basePos[1]+1, basePos[2]+1), ws=True)
            pm.parent(slider.getParent(), allSliderGrp)

            addNode = pm.createNode('addDoubleLinear')
            clampConn = pm.listConnections(slider.translateY, p=True, d=True)
            for conn in clampConn:
                addNode.output >> conn
            masterSliderCtrl.translateY >> addNode.input1
            slider.translateY >> addNode.input2

            pm.parent(slider.getParent(), masterSliderCtrl)
            sideMove = False

        for i in range(4):
            guide = tweakGuides[i]

            cntrlName = displaySetup['nameTempl']+str(i)
            jntName = self.jntSetup['nameTempl']+str(i)
            jnt = jointTools.makeJoint(name=jntName, obj=guide, jntSulfix='_jxt', hasZero=True, connectToLast=False)
            ctrl = controlTools.cntrlCrv(name=cntrlName, obj=jnt, connType='connection', offsets=1, **displaySetup)
            pm.parent(jnt.getParent(), tweakJntGrp)
            pm.parent(ctrl.getParent(2), tweakCtrlGrp)

        self.guideMoveall.visibility.set(0)

def createSlider(name='slider', size=0.1, sideMove=False):
    if pm.objExists(name+'_grp'):
        pm.delete(name+'_grp')

    sliderGrp = pm.group(em=True, name=name+'_grp')
    sliderCtrl = pm.circle(nr=(0, 0, 1), r=size, n=name+'_ctrl')[0]
    pm.parent(sliderCtrl, sliderGrp)
    #sliderCtrl.setLimit('translateMaxY', 3)
    #sliderCtrl.setLimit('translateMinY', -3)

    sliderClamp = pm.createNode('clamp')
    sliderSetRange = pm.createNode('setRange')
    sliderClamp.maxR.set(200)
    sliderClamp.minG.set(-200)

    sliderClamp.output >> sliderSetRange.value
    sliderSetRange.minX.set(0)
    sliderSetRange.maxX.set(100)
    sliderSetRange.oldMinX.set(0)
    sliderSetRange.oldMaxX.set(200)
    sliderSetRange.minY.set(100)
    sliderSetRange.maxY.set(0)
    sliderSetRange.oldMinY.set(-200)
    sliderSetRange.oldMaxY.set(0)

    sliderCtrl.translateY >> sliderClamp.input.inputR
    sliderCtrl.translateY >> sliderClamp.input.inputG

    sliderGrp.addAttr('upValue', at='float', dv=0, k=0)
    sliderGrp.addAttr('downValue', at='float', dv=0, k=0)

    sliderSetRange.outValue.outValueX >> sliderGrp.upValue
    sliderSetRange.outValue.outValueY >> sliderGrp.downValue

    if sideMove:
        sliderClamp.maxB.set(200)
        sliderSetRange.minZ.set(0)
        sliderSetRange.maxZ.set(100)
        sliderSetRange.oldMinZ.set(0)
        sliderSetRange.oldMaxZ.set(100)
        sliderCtrl.translateX >> sliderClamp.input.inputB
        sliderGrp.addAttr('compressValue', at='float', dv=0, k=0)
        sliderSetRange.outValue.outValueZ >> sliderGrp.compressValue

    return sliderCtrl

def shapeDivide (name='div', targetNeutral=None, targetObj=None, L_eyeBrowGuide=None, R_eyeBrow_guide=None):
    L_eyeBrow = L_eyeBrowGuide
    R_eyeBrow = R_eyeBrow_guide

    Xmax = pm.xform(L_eyeBrow.guideMoveall, ws=True, t=True, q=True)[0]
    Xmin = pm.xform(R_eyeBrow.guideMoveall, ws=True, t=True, q=True)[0]
    R_target = taperSideAPI(targetNeutral, targetObj, Xmin, Xmin, Xmax, 'R_A')
    L_target = taperSideAPI(targetNeutral, targetObj, Xmin, Xmax, Xmax, 'L_A')

    Xmax = pm.xform(L_eyeBrow.sliceMax, ws=True, t=True, q=True)[0]
    Xmin = pm.xform(L_eyeBrow.sliceMin, ws=True, t=True, q=True)[0]
    Xmid = pm.xform(L_eyeBrow.sliceMid, ws=True, t=True, q=True)[0]
    XinBtw1 = pm.xform(L_eyeBrow.sliceInBtw1, ws=True, t=True, q=True)[0]
    XinBtw2 = pm.xform(L_eyeBrow.sliceInBtw2, ws=True, t=True, q=True)[0]
    L_target1 = taperSideAPI(targetNeutral, L_target, Xmin, Xmin, Xmax, 'L_B')
    L_target2 = taperSideAPI(targetNeutral, L_target, Xmin, Xmax, Xmax, 'L_C')

    L_outTarget1 = taperSideAPI(targetNeutral, L_target1, Xmin, Xmin, Xmid, 'L_' + name + 'In')

    L_outTarget1a = taperSideAPI(targetNeutral, L_outTarget1, Xmin, Xmin, XinBtw1, 'L_' + name + 'InA')
    L_outTarget1b = taperSideAPI(targetNeutral, L_outTarget1, Xmin, XinBtw1, XinBtw1, 'L_' + name + 'InB')

    L_outTarget2 = taperSideAPI(targetNeutral, L_target1, Xmin, Xmid, Xmid, 'L_' + name + 'MidIn')
    L_outTarget3 = taperSideAPI(targetNeutral, L_target2, Xmid, Xmid, Xmax, 'L_' + name + 'MidOut')

    L_outTarget3a = taperSideAPI(targetNeutral, L_outTarget3, Xmid, Xmid, XinBtw2, 'L_' + name + 'MidOutA')
    L_outTarget3b = taperSideAPI(targetNeutral, L_outTarget3, Xmid, XinBtw2, XinBtw2, 'L_' + name + 'MidOutB')

    L_outTarget4 = taperSideAPI(targetNeutral, L_target2, Xmid, Xmax, Xmax, 'L_' + name + 'Out')

    Xmin = pm.xform(R_eyeBrow.sliceMax, ws=True, t=True, q=True)[0]
    Xmax = pm.xform(R_eyeBrow.sliceMin, ws=True, t=True, q=True)[0]
    Xmid = pm.xform(R_eyeBrow.sliceMid, ws=True, t=True, q=True)[0]
    XinBtw1 = pm.xform(R_eyeBrow.sliceInBtw1, ws=True, t=True, q=True)[0]
    XinBtw2 = pm.xform(R_eyeBrow.sliceInBtw2, ws=True, t=True, q=True)[0]
    R_target1 = taperSideAPI(targetNeutral, R_target, Xmin, Xmin, Xmax, 'R_B')
    R_target2 = taperSideAPI(targetNeutral, R_target, Xmin, Xmax, Xmax, 'R_C')

    R_outTarget1 = taperSideAPI(targetNeutral, R_target2, Xmid, Xmax, Xmax, 'R_' + name + 'In')

    R_outTarget1a = taperSideAPI(targetNeutral, R_outTarget1, Xmin, Xmin, XinBtw1, 'R_' + name + 'InA')
    R_outTarget1b = taperSideAPI(targetNeutral, R_outTarget1, Xmin, XinBtw1, XinBtw1, 'R_' + name + 'InB')

    R_outTarget2 = taperSideAPI(targetNeutral, R_target2, Xmid, Xmid, Xmax, 'R_' + name + 'MidIn')
    R_outTarget3 = taperSideAPI(targetNeutral, R_target1, Xmin, Xmid, Xmid, 'R_' + name + 'MidOut')

    R_outTarget3a = taperSideAPI(targetNeutral, R_outTarget3, Xmid, Xmid, XinBtw2, 'R_' + name + 'MidOutA')
    R_outTarget3b = taperSideAPI(targetNeutral, R_outTarget3, Xmid, XinBtw2, XinBtw2, 'R_' + name + 'MidOutB')

    R_outTarget4 = taperSideAPI(targetNeutral, R_target1, Xmin, Xmin, Xmid, 'R_' + name + 'Out')

    return [L_outTarget1a, L_outTarget1b, L_outTarget2, L_outTarget3a, L_outTarget3b, L_outTarget4,
            R_outTarget1a, R_outTarget1b, R_outTarget2, R_outTarget3a, R_outTarget3b, R_outTarget4]


def taperSideAPI(sourceObj, targetObj, sliceMin, sliceMid, sliceMax, outName='splited'):
    tgtVertex = getObjVertex(targetObj.name())
    srcVertex = getObjVertex(sourceObj.name())

    target = pm.duplicate(targetObj, n=outName)[0]
    pm.move(target, 0, 10, 0, r=1)

    newPntArray = om2.MPointArray()

    for id in range(len(srcVertex)):
        x = tgtVertex[id].x
        per = 1

        if x > sliceMin and x <= sliceMid:
            per = mathutils.smoothstep(sliceMin, sliceMid, x)
            per = 1.0 - per
        elif x >= sliceMid and x < sliceMax:
            per = mathutils.smoothstep(sliceMid, sliceMax, x)
        elif x < sliceMin:
            if sliceMin == sliceMid:
                per = 0
            else:
                per = 1

        elif x > sliceMax:
            if sliceMax == sliceMid:
                per = 0
            else:
                per = 1

        newPntArray.append(om2.MPoint(srcVertex[id][0] * per + tgtVertex[id][0] * (1.0 - per),
                                      srcVertex[id][1] * per + tgtVertex[id][1] * (1.0 - per),
                                      srcVertex[id][2] * per + tgtVertex[id][2] * (1.0 - per)))
    setObjVertex(target.name(), newPntArray)
    return target

def getObjVertex(obj):
    sel = om2.MSelectionList()
    sel.add(obj)
    selObj = sel.getDagPath(0)
    mfnObject = om2.MFnMesh(selObj)

    return mfnObject.getPoints()

def setObjVertex(obj, vxtArray):
    sel = om2.MSelectionList()
    sel.add(obj)
    selObj = sel.getDagPath(0)
    mfnObject = om2.MFnMesh(selObj)

    return mfnObject.setPoints(vxtArray)

def getBBox(obj):
    sel = om2.MSelectionList ()
    sel.add(obj)
    selObj = sel.getDagPath (0)

    mfnObject = om2.MFnMesh (selObj)
    return mfnObject.boundingBox


def getValue(x, max):
    value = (1 - x / max) / 2
    return clamp(value, 0, 1)


def clamp(value, low, high):
    if value < low:
        return low
    if (value > high):
        return high
    return value

