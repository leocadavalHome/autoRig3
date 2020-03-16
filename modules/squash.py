import pymel.core as pm
import autoRig3.tools.controlTools as controlTools
import json
import logging

logger = logging.getLogger('autoRig')

class Squash:
    def __init__(self, name='squash'):
        self.guideDict = {'base': [(0, 0, 0), (0, 0, 0)], 'end': [(0, 10, 0), (0, 0, 0)], 'ctrl': [(0, 1, 0), (0, 0, 0)],
                          'mid': [(0, 0, 0), (0, 0, 0)], 'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)]}
        self.guideMoveall = None
        self.name = name
        self.moveallGuideSetup = {'nameTempl': self.name+'Moveall', 'icone': 'circuloY', 'size': 4, 'color': [332, .9, .2]}
        self.ctrlGuideSetup = {'nameTempl': self.name+'Ctrl', 'icone': 'bola', 'size': .5, 'color': [332, .9, .2]}
        self.baseGuideSetup = {'nameTempl': self.name+'Base', 'icone': 'circuloY', 'size': 2, 'color': [332, .9, .2]}
        self.endGuideSetup = {'nameTempl': self.name+'End', 'icone': 'circuloY', 'size': 2, 'color': [332, .9, .2]}
        self.midGuideSetup = {'nameTempl': self.name+'Mid', 'icone': 'circuloY', 'size': 3, 'color': [332, .9, .2]}
        self.toExport = ['guideDict', 'name', 'moveallGuideSetup', 'ctrlGuideSetup', 'baseGuideSetup', 'endGuideSetup',
                         'midGuideSetup']
        self.guideSulfix = '_guide'

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
                expDict[key] = self.__dict__[key]
        return expDict

    def createCntrl(self, cntrlName, hasZeroGrp=False):
        displaySetup = self.__dict__[cntrlName+'Setup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix
        if pm.objExists(cntrlName):
            pm.delete(cntrlName)
        guide = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=hasZeroGrp, cntrlSulfix='', hasHandle=True, **displaySetup)
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
            facialGrp = 'facial_guides_grp'
        else:
            facialGrp = pm.group(n='facial_guides_grp', em=True)

        if pm.objExists(self.name + 'Moveall_guide'):
            pm.delete(self.name + 'Moveall_guide')

        self.ctrlGuide= self.createCntrl('ctrlGuide')
        self.baseGuide = self.createCntrl('baseGuide')
        self.endGuide = self.createCntrl('endGuide')
        self.midGuide = self.createCntrl('midGuide', hasZeroGrp=True)
        self.guideMoveall = self.createCntrl('moveallGuide')

        pm.parent(self.ctrlGuide, self.endGuide)
        pm.parent(self.baseGuide, self.endGuide, self.midGuide.getParent(), self.guideMoveall)

        self.setCntrl(self.ctrlGuide, 'ctrl')
        self.setCntrl(self.baseGuide, 'base')
        self.setCntrl(self.endGuide, 'end')
        self.setCntrl(self.midGuide, 'mid')
        self.setCntrl(self.guideMoveall, 'moveall', space='world')

        pm.parentConstraint(self.baseGuide, self.endGuide, self.midGuide.getParent(), w=1, mo=False)

        pm.setAttr(self.baseGuide.translateX, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.baseGuide.translateZ, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.baseGuide.scaleX, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.baseGuide.scaleY, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.baseGuide.scaleZ, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.baseGuide.rotateX, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.baseGuide.rotateY, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.baseGuide.rotateZ, lock=True, keyable=False, channelBox=False)

        pm.setAttr(self.endGuide.translateX, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.endGuide.translateZ, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.endGuide.scaleX, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.endGuide.scaleY, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.endGuide.scaleZ, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.endGuide.rotateX, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.endGuide.rotateY, lock=True, keyable=False, channelBox=False)
        pm.setAttr(self.endGuide.rotateZ, lock=True, keyable=False, channelBox=False)


        self.length = pm.createNode('distanceBetween')
        self.baseGuide.worldMatrix[0] >> self.length.inMatrix1
        self.endGuide.worldMatrix[0] >> self.length.inMatrix2

        self.midPos = pm.createNode('distanceBetween')
        self.baseGuide.worldMatrix[0] >> self.midPos.inMatrix1
        self.midGuide.worldMatrix[0] >> self.midPos.inMatrix2

        pm.parent (self.guideMoveall, facialGrp)

        pm.addAttr(self.guideMoveall, ln='squashDict', dt='string')
        self.guideMoveall.squashDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        try:
            guideName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            jsonDict = self.guideMoveall.squashDict.get()
            squashDictRestored = json.loads(jsonDict)

            self.__dict__.update(**squashDictRestored)

            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
            self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

            guideName = self.ctrlGuideSetup['nameTempl'] + self.guideSulfix
            self.ctrlGuide = pm.PyNode(guideName)
            self.guideDict['ctrl'][0] = self.ctrlGuide.getTranslation(space='object').get()
            self.guideDict['ctrl'][1] = tuple(self.ctrlGuide.getRotation(space='object'))

            guideName = self.baseGuideSetup['nameTempl'] + self.guideSulfix
            self.baseGuide = pm.PyNode(guideName)
            self.guideDict['base'][0] = self.baseGuide.getTranslation(space='object').get()
            self.guideDict['base'][1] = tuple(self.baseGuide.getRotation(space='object'))

            guideName = self.endGuideSetup['nameTempl'] + self.guideSulfix
            self.endGuide = pm.PyNode(guideName)
            self.guideDict['end'][0] = self.endGuide.getTranslation(space='object').get()
            self.guideDict['end'][1] = tuple(self.endGuide.getRotation(space='object'))

            guideName = self.midGuideSetup['nameTempl'] + self.guideSulfix
            self.midGuide = pm.PyNode(guideName)
            self.guideDict['mid'][0] = self.midGuide.getTranslation(space='object').get()
            self.guideDict['mid'][1] = tuple(self.midGuide.getRotation(space='object'))
        except:
            pass

    def doRig(self):

        if pm.objExists('head_contrained'):
            constrained_grp = 'head_contrained'
        else:
            constrained_grp = pm.group(n='head_contrained', em=True)

        if pm.objExists(self.name + "Ctrl_grp"):
            pm.delete(self.name + "Ctrl_grp")

        if pm.objExists(self.name + 'Sys_grp'):
            pm.delete(self.name + 'Sys_grp')

        deformLength = self.length.distance.get()
        proxy = pm.polyCube(n="def_proxy", ch=False)[0]
        matrix = pm.xform (self.midGuide, m=True, ws=True, q=True)
        pm.xform(proxy, m=matrix, ws=True)
        proxy.scaleY.set(deformLength)
        pm.select(proxy)
        squash = pm.nonLinear(type='squash')
        pm.nonLinear(squash[0], e=True, lowBound=0, highBound=1, startSmoothness=0, endSmoothness=0)
        pm.select(proxy)
        bendA = pm.nonLinear(type='bend')
        pm.nonLinear(bendA[0],e=True, lowBound=0, highBound=1, curvature=0)
        pm.select(proxy)
        bendB = pm.nonLinear(type='bend')
        pm.nonLinear(bendB[0], e=True, lowBound=0, highBound=1, curvature=0)

        matrix = pm.xform(self.baseGuide, m=True, ws=True, q=True)
        deformers = pm.group(em=True,  n=self.name + 'Sys_grp')
        pm.xform(deformers, m=matrix, ws=True)
        pm.parent(squash, bendA, bendB, proxy, deformers)
        pm.setAttr(deformers + ".visibility", 0)

        pm.xform(squash[1], m=matrix, ws=True)
        pm.xform(bendA[1], m=matrix, ws=True)
        pm.xform(bendB[1], m=matrix, ws=True)

        pm.xform (bendB[1], ro=(0, 90 ,0), r=True)
        pm.setAttr(bendB[0] + ".highBound", deformLength)
        pm.setAttr(bendA[0] + ".highBound", deformLength)
        pm.setAttr(squash[0] + ".highBound", deformLength)

        ## Criar controle
        squashCtrl = pm.curve(d=1, p=[(-1, 0, -2), (1, 0, -2), (1, 0, 2), (3, 0, 2), (0, 0, 5), (-3, 0, 2), (-1, 0, 2),
                                      (-1, 0, -2)], k=[0, 1, 2, 3, 4, 5, 6, 7], n="squash_ctrl")
        pm.xform(squashCtrl, cp=True)
        squashCtrl.rotateX.set(90)
        squashCtrl.scale.set((0.5, 0.5, 0.5))
        pm.makeIdentity(squashCtrl, apply=True, t=1, r=1, s=1, n=0, pn=1)
        squashGrp = pm.group(squashCtrl, n=self.name+"Ctrl_grp")
        pm.parent(squashGrp, constrained_grp)

        matrix = pm.xform(self.ctrlGuide, m=True, ws=True, q=True)
        pm.xform(squashGrp, m=matrix, ws=True)

        # Conectar controle
        mult = pm.shadingNode('multiplyDivide', asUtility=True)
        pm.connectAttr((squashCtrl) + '.translateY', mult + '.input1Y')
        pm.connectAttr((squashCtrl) + '.translateX', mult + '.input1X')
        pm.connectAttr((squashCtrl) + '.translateZ', mult + '.input1Z')
        pm.setAttr(mult + '.input2X', 5)
        pm.setAttr(mult + '.input2Y', .2)
        pm.setAttr(mult + '.input2Z', -5)

        pm.connectAttr(mult + '.outputY', squash[0] + '.factor')
        pm.connectAttr(mult + '.outputX', bendA[0] + '.curvature')
        pm.connectAttr(mult + '.outputZ', bendB[0] + '.curvature')

        maxExpandPos = self.midPos.distance.get()/deformLength
        pm.setAttr(squash[0]+'.maxExpandPos', maxExpandPos)
        self.guideMoveall.visibility.set(0)
