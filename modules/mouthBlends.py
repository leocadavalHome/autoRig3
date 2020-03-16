import pymel.core as pm
import autoRig3.tools.controlTools as controlTools
import autoRig3.tools.blendShapeTools as blendShapeTools
import json
import logging

logger = logging.getLogger('autoRig')

class MouthBlends:
    def __init__(self, name='mouthCorners'):
        self.name = name
        self.guideSulfix = '_guide'
        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1,1,1)],
                          'lcorner': [(0.5, 0, 0), (0,0,0)],
                          'rcorner': [(-.5, 0, 0), (0,0,0)]}

        self.moveallGuideSetup = {'nameTempl': self.name + 'Moveall', 'icone': 'quadradoZ', 'size': 1, 'color': (1, 0, 0)}
        self.lcornerGuideSetup = {'nameTempl': self.name + 'L_corner', 'icone': 'cubo', 'size': 1, 'color': (1, 0, 0)}
        self.rcornerGuideSetup = {'nameTempl': self.name + 'R_corner', 'icone': 'cubo', 'size': 1, 'color': (1, 0, 0)}

        self.moveallCtrlSetup = {'nameTempl': self.name + 'Moveall', 'icone': 'grp', 'size': 1, 'color': (1, 0, 0)}
        self.lcornerCtrlSetup = {'nameTempl': self.name + 'L_corner', 'icone': 'trianguloMinusZ', 'size': .5, 'color': (0, 1, 1)}
        self.rcornerCtrlSetup = {'nameTempl': self.name + 'R_corner', 'icone': 'trianguloMinusZ', 'size': .5, 'color': (0, 1, 1)}
        self.toExport = ['name',
                         'guideDict',
                         'moveallGuideSetup',
                         'moveallCtrlSetup',
                         'lcornerCtrlSetup',
                         'rcornerGuideSetup',
                         'lcornerCtrlSetup',
                         'rcornerCtrlSetup']

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
                expDict[key] = self.__dict__[key]
        return expDict

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

    def doGuide(self):
        if pm.objExists('facial_guides_grp'):
            moveall_grp = 'facial_guides_grp'
        else:
            moveall_grp = pm.group(n='facial_guides_grp', em=True)

        self.guideMoveall = self.createCntrl('moveallGuide')
        self.lcornerGuide = self.createCntrl('lcornerGuide')
        self.rcornerGuide = self.createCntrl('rcornerGuide')

        pm.parent (self.lcornerGuide, self.rcornerGuide, self.guideMoveall)

        self.setCntrl (self.guideMoveall, 'moveall')
        self.setCntrl(self.lcornerGuide, 'lcorner')
        self.setCntrl(self.rcornerGuide, 'rcorner')

        self.mirror_mdn = pm.createNode('multiplyDivide')
        self.mirror_mdn.input2X.set(-1)

        self.lcornerGuide.translate >> self.mirror_mdn.input1
        self.mirror_mdn.output >> self.rcornerGuide.translate

        pm.parent(self.guideMoveall, moveall_grp)

        pm.toggle(self.lcornerGuide, selectHandle=True)

        pm.addAttr(self.guideMoveall, ln='mouthBlendDict', dt='string')
        self.guideMoveall.mouthBlendDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            self.guideMoveall = pm.PyNode(self.name + 'Moveall_guide')
            jsonDict = self.guideMoveall.mouthBlendDict.get()
            dictRestored = json.loads(jsonDict)
            self.__dict__.update(**dictRestored)

            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)
            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            guideName = self.lcornerGuideSetup['nameTempl'] + self.guideSulfix
            self.lcornerGuide = pm.PyNode(guideName)
            self.guideDict['lcorner'][0] = self.lcornerGuide.getTranslation(space='object').get()
            self.guideDict['lcorner'][1] = tuple(self.lcornerGuide.getRotation(space='object'))

            guideName = self.rcornerGuideSetup['nameTempl'] + self.guideSulfix
            self.rcornerGuide = pm.PyNode(guideName)
            self.guideDict['rcorner'][0] = self.rcornerGuide.getTranslation(space='object').get()
            self.guideDict['rcorner'][1] = tuple(self.rcornerGuide.getRotation(space='object'))
        except:
            pass

    def doRig(self, bsDict=None):
        if not self.guideMoveall:
            self.doGuide()

        self.guideMoveall.visibility.set(0)

        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')
        self.moveall = pm.group(em=True, n=self.name + 'Moveall')

        if pm.objExists('head_contrained'):
            constrained_grp = 'head_contrained'
        else:
            constrained_grp = pm.group(n='head_contrained', em=True)

        if bsDict:
            self.bsDict = bsDict

        size=0.8
        pm.select(cl=True)
        self.lcornerCntrl = controlTools.cntrlCrv(name='L_mouthCorner', obj=self.lcornerGuide, icone='trianguloMinusZ', size=.5)
        pm.addAttr (self.lcornerCntrl, ln="up", at="double")
        pm.addAttr (self.lcornerCntrl, ln="down", at="double")
        pm.addAttr (self.lcornerCntrl, ln="wide", at="double")
        pm.addAttr (self.lcornerCntrl, ln="narrow", at="double")
        pm.addAttr (self.lcornerCntrl, ln="upWide", at="double")
        pm.addAttr (self.lcornerCntrl, ln="upNarrow", at="double")
        pm.addAttr (self.lcornerCntrl, ln="downWide", at="double")
        pm.addAttr (self.lcornerCntrl, ln="downNarrow", at="double")

        attr = {self.lcornerCntrl: ["tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]}
        key = attr.keys ()
        for k in key:
            for item in attr[k]:
                pm.setAttr(k + "." + item, k=False, l=True)

        lClampX = pm.createNode("clamp", n="l_mouthX_clamp")
        lClampX.maxR.set(100)
        lClampX.minG.set(-100)
        lClampY = pm.createNode("clamp", n="l_mouthY_clamp")
        lClampY.maxR.set(100)
        lClampY.minG.set(-100)

        lMultX = pm.createNode("multiplyDivide", n="l_mouthX_md")
        lMultX.input2Y.set(-1)
        lMultY = pm.createNode("multiplyDivide", n="l_mouthY_md")
        lMultY.input2Y.set(-1)

        self.lcornerCntrl.translateX >> lClampX.inputR
        self.lcornerCntrl.translateX >> lClampX.inputG
        lClampX.outputR >> lMultX.input1X
        lClampX.outputG >> lMultX.input1Y
        self.lcornerCntrl.translateY >> lClampY.inputR
        self.lcornerCntrl.translateY >> lClampY.inputG
        lClampY.outputR >> lMultY.input1X
        lClampY.outputG >> lMultY.input1Y
        lMultX.outputX >> self.lcornerCntrl.wide
        lMultX.outputY >> self.lcornerCntrl.narrow
        lMultY.outputX >> self.lcornerCntrl.up
        lMultY.outputY >> self.lcornerCntrl.down
        
        multiUpWide = pm.createNode("multiplyDivide", n="MD_l_combo_up_wide")
        multiUpNarrow = pm.createNode("multiplyDivide", n="MD_l_combo_up_narrow")
        multiDownWide = pm.createNode("multiplyDivide", n="MD_l_combo_down_wide")
        multiDownNarrow = pm.createNode("multiplyDivide", n="MD_l_combo_down_narrow")

        self.lcornerCntrl.up >> multiUpWide.input1X
        self.lcornerCntrl.wide >> multiUpWide.input2X
        multiUpWide.outputX >> self.lcornerCntrl.upWide
        self.lcornerCntrl.up >> multiUpNarrow.input1X
        self.lcornerCntrl.narrow >> multiUpNarrow.input2X
        multiUpNarrow.outputX >> self.lcornerCntrl.upNarrow
        self.lcornerCntrl.down >> multiDownWide.input1X
        self.lcornerCntrl.wide >> multiDownWide.input2X
        multiDownWide.outputX >> self.lcornerCntrl.downWide
        self.lcornerCntrl.down >> multiDownNarrow.input1X
        self.lcornerCntrl.narrow >> multiDownNarrow.input2X
        multiDownNarrow.outputX >> self.lcornerCntrl.downNarrow

        self.rcornerCntrl = controlTools.cntrlCrv(name='R_mouthCorner', obj=self.rcornerGuide, icone='trianguloMinusZ', size=.5)
        self.rcornerCntrl.getParent().rotateY.set(180)

        pm.addAttr (self.rcornerCntrl, ln="up", at="double")
        pm.addAttr (self.rcornerCntrl, ln="down", at="double")
        pm.addAttr (self.rcornerCntrl, ln="wide", at="double")
        pm.addAttr (self.rcornerCntrl, ln="narrow", at="double")
        pm.addAttr (self.rcornerCntrl, ln="upWide", at="double")
        pm.addAttr (self.rcornerCntrl, ln="upNarrow", at="double")
        pm.addAttr (self.rcornerCntrl, ln="downWide", at="double")
        pm.addAttr (self.rcornerCntrl, ln="downNarrow", at="double")

        attrR = {self.rcornerCntrl: ["tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]}
        keyR = attrR.keys ()
        for kk in keyR:
            for cadaItem in attrR[kk]:
                pm.setAttr (kk + "." + cadaItem, k=False, l=True)

        rClampX = pm.createNode("clamp", n="l_mouthX_clamp")
        rClampX.maxR.set(100)
        rClampX.minG.set(-100)
        rClampY = pm.createNode("clamp", n="l_mouthY_clamp")
        rClampY.maxR.set(100)
        rClampY.minG.set(-100)
        rMultX = pm.createNode("multiplyDivide", n="r_mouthX_md")
        rMultX.input2Y.set(-1)
        rMultXNeg = pm.createNode("multiplyDivide", n="r_mouthX_md_neg")
        rMultY = pm.createNode("multiplyDivide", n="r_mouthY_md")
        rMultY.input2Y.set(-1)
        
        self.rcornerCntrl.translateX >> rClampX.inputR
        self.rcornerCntrl.translateX >> rClampX.inputG
        rClampX.outputR >> rMultX.input1X
        rClampX.outputG >> rMultX.input1Y
        rMultX.outputY >> rMultXNeg.input1X
        rMultX.outputX >> rMultXNeg.input1Y
        self.rcornerCntrl.translateY >> rClampY.inputR
        self.rcornerCntrl.translateY >> rClampY.inputG
        rClampY.outputR >> rMultY.input1X
        rClampY.outputG >> rMultY.input1Y
        rMultXNeg.outputY >> self.rcornerCntrl.wide
        rMultXNeg.outputX >> self.rcornerCntrl.narrow
        rMultY.outputX >> self.rcornerCntrl.up
        rMultY.outputY >> self.rcornerCntrl.down

        rMultiUpWide = pm.createNode("multiplyDivide", n="MD_r_combo_up_wide")
        rMultiUpNarrow = pm.createNode("multiplyDivide", n="MD_r_combo_up_narrow")
        rMultiDownWide = pm.createNode("multiplyDivide", n="MD_r_combo_down_wide")
        rMultiDwonWide = pm.createNode ("multiplyDivide", n="MD_r_combo_down_narrow")

        self.rcornerCntrl.up >> rMultiUpWide.input1X
        self.rcornerCntrl.wide >> rMultiUpWide.input2X
        rMultiUpWide.outputX >> self.rcornerCntrl.upWide
        self.rcornerCntrl.up >> rMultiUpNarrow.input1X
        self.rcornerCntrl.narrow >> rMultiUpNarrow.input2X
        rMultiUpNarrow.outputX >> self.rcornerCntrl.upNarrow
        self.rcornerCntrl.down >> rMultiDownWide.input1X
        self.rcornerCntrl.wide >> rMultiDownWide.input2X
        rMultiDownWide.outputX >> self.rcornerCntrl.downWide
        self.rcornerCntrl.down >> rMultiDwonWide.input1X
        self.rcornerCntrl.narrow >> rMultiDwonWide.input2X
        rMultiDwonWide.outputX >> self.rcornerCntrl.downNarrow

        pm.parent(self.lcornerCntrl.getParent(), self.rcornerCntrl.getParent(), self.moveall)
        pm.parent(self.moveall, constrained_grp)

    def doConnectToCntrls(self, sourceObj=None, firstIndex=None):
        bsNode = blendShapeTools.getBlendShapeNode(sourceObj=sourceObj)

        lcorner = self.lcornerCntrl
        rcorner = self.rcornerCntrl
        counter = 0
        attrList = ['up', 'down', 'wide', 'narrow', 'upWide', 'upNarrow', 'downWide', 'downNarrow']
        for attrName in attrList:
            for ctrl in [rcorner, lcorner]:
                try:
                    ctrl.attr(attrName) >> bsNode.attr(blendShapeTools.getNamebyIndex(bsNode, counter + firstIndex))
                    counter += 1
                except:
                    logger.debug('Nao foi possivel conectar ctrl {0}{1}'.format(ctrl.name()[:2], attrName))

    def doRigAndApplyTargets(self, sourceObj=None, targetList=None, offsets=.02):
        splittedTargetList = blendShapeTools.splitShapes(targetList=targetList, falloff=offsets)
        firstIndex = blendShapeTools.addTargets(sourceObj=sourceObj, splittedTargets=splittedTargetList)

        self.doRig()
        self.doConnectToCntrls(sourceObj=sourceObj, firstIndex=firstIndex)


def targetOrder(targetList=None):
    if len(targetList) > 9:
        logger.info('Foram selecionado mais q 8 shapes e o neutro')
        return

    up = None
    down = None
    wide = None
    narrow = None
    upWide = None
    upNarrow = None
    downWide = None
    downNarrow = None
    neutral = None

    for obj in targetList:
        name = obj.nodeName()
        if 'up' in name or 'Up' in name or 'UP' in name or 'smile' in name or 'Smile' in name or 'SMILE' in name:
            if 'wide' in name or 'Wide' in name or 'WIDE' in name:
                upWide = obj
            elif 'narrow' in name or 'Narrow' in name or 'NARROW' in name:
                upNarrow = obj
            else:
                up = obj
        elif 'down' in name or 'Down' in name or 'DOWN' in name or 'frown' in name or 'Frown' in name or 'FROWN' in name \
                or 'sad' in name or 'Sad' in name or 'SAD' in name:
            if 'wide' in name or 'Wide' in name or 'WIDE' in name:
                downWide = obj
            elif 'narrow' in name or 'Narrow' in name or 'NARROW' in name:
                downNarrow = obj
            else:
                down = obj
        elif 'wide' in name or 'Wide' in name or 'WIDE' in name:
            wide = obj
        elif 'narrow' in name or 'Narrow' in name or 'NARROW' in name:
            narrow = obj
        elif 'neutro' in name or 'Neutro' in name or 'NEUTRO' in name or 'neutral' in name or 'Neutral' in name or \
                'NEUTRAL' in name or 'base' in name or 'Base' in name or 'BASE' in name:
            neutral = obj
        else:
            logger.info('Nao identificou o blendshape!, %s' % obj)

    return [up, down, wide, narrow, upWide, upNarrow, downWide, downNarrow, neutral]
