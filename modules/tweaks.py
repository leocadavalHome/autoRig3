#!/usr/bin/python
# coding: utf-8
import pymel.core as pm
import autoRig3.tools.controlTools as controlTools
import json
import logging

logger = logging.getLogger('autoRig')

class Tweaks:
    def __init__(self, name='tweak', num=1, hasMulti=True, **kwargs):
        self.name = name
        self.hasMulti = hasMulti
        self.num = num
        self.jntPrefix = '_jnt'
        self.guideMoveall = None
        self.guideSulfix = '_guide'
        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)]}
        for i in range(self.num):
            self.guideDict[self.name+'Tweak' + str(i + 1)] = [(i * .5, 0, 0), (0, 0, 0), (1, 1, 1)]

        self.guideSetup = {'nameTempl': self.name+'Tweak', 'icone': 'bola', 'size': .2, 'color': (32, .7, .17)}
        self.moveallGuideSetup = {'nameTempl': self.name+'Moveall', 'icone': 'quadradoZ', 'size': 1, 'color': (1, 0, 0)}
        self.drvSetup = {'nameTempl': self.name + '_drv', 'icone': 'grp', 'size': 1, 'color': (1, 1, 0)}
        self.ctrlSetup = {'nameTempl': self.name, 'icone': 'bola', 'size': .5, 'color': (1, 1, 0)}
        self.toExport = ['name', 'hasMulti', 'guideDict', 'num', 'moveallGuideSetup', 'guideSetup', 'drvSetup', 'ctrlSetup']

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
                expDict[key] = self.__dict__[key]
        return expDict

    def createCntrl(self, cntrlName, nameSulfix = ''):
        displaySetup = self.__dict__[cntrlName+'Setup'].copy()
        cntrlName = displaySetup['nameTempl'] + nameSulfix + self.guideSulfix
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

        moveallName = self.moveallGuideSetup['nameTempl']+self.guideSulfix

        if pm.objExists(moveallName):
            pm.delete(moveallName)

        self.guideMoveall = self.createCntrl('moveallGuide')
        self.setCntrl(self.guideMoveall, 'moveall')

        self.guideList = []

        for i in range(self.num):
            guideName = self.guideSetup['nameTempl'] + str(i + 1)
            guide = self.createCntrl('guide', nameSulfix=str(i + 1))
            self.guideList.append(guide)
            guide.setParent(self.guideMoveall)
            self.setCntrl(guide, guideName, space='object')

        pm.addAttr(self.guideMoveall, ln='tweakDict', dt='string')
        self.guideMoveall.tweakDict.set(json.dumps(self.exportDict()))

    def getDict(self):
        moveallName = self.moveallGuideSetup['nameTempl']+self.guideSulfix
        self.guideMoveall = pm.PyNode(moveallName)

        jsonDict = self.guideMoveall.tweakDict.get()
        dictRestored = json.loads(jsonDict)

        self.__dict__.update(**dictRestored)

        self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='object').get()
        self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='object'))
        self.guideDict['moveall'][2] = tuple(pm.xform(self.guideMoveall, q=True, s=True, ws=True))

        self.guideList = []
        for i in range(self.num):
            guideName = self.guideSetup['nameTempl'] + str(i + 1)
            guide = pm.PyNode(guideName+self.guideSulfix)
            self.guideList.append(guide)

            self.guideDict[guideName][0] = guide.getTranslation(space='object').get()
            self.guideDict[guideName][1] = tuple(guide.getRotation(space='object'))
            self.guideDict[guideName][2] = tuple(pm.xform(guide, q=True, s=True, ws=True))


    def mirrorConnectGuide(self, tweak):
        if not self.guideMoveall:
            self.doGuide()

        if not tweak.guideMoveall:
            tweak.doGuide()

        if pm.objExists(self.name + 'MirrorGuide_grp'):
            pm.delete(self.name + 'MirrorGuide_grp')

        self.mirrorGuide = pm.group(em=True, n=self.name + 'MirrorGuide_grp')


        self.guideMoveall.setParent(self.mirrorGuide)
        self.mirrorGuide.scaleX.set(-1)
        self.mirrorGuide.template.set(1)

        tweak.guideMoveall.translate >> self.guideMoveall.translate
        tweak.guideMoveall.rotate >> self.guideMoveall.rotate
        tweak.guideMoveall.scale >> self.guideMoveall.scale

        for i in range(self.num):
            tweak.guideList[i].translate >> self.guideList[i].translate
            tweak.guideList[i].rotate >> self.guideList[i].rotate
            tweak.guideList[i].scale >> self.guideList[i].scale

    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()

        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')

        self.drvGrp = pm.group(em=True, n=self.name + 'Sys_grp')
        self.drvGrp.visibility.set(False)
        self.cntrlGrp = pm.group(em=True, n=self.name + 'Ctrls_grp')
        self.moveall = pm.group(self.cntrlGrp, n=self.name + 'Constrained')

        self.cntrlList = []

        for i in range(self.num):
            pm.select(cl=True)
            jnt = pm.joint(n=self.name + str(i + 1) + self.jntPrefix)
            pos = pm.xform(self.guideList[i], q=True, ws=True, t=True)
            pm.xform(jnt, ws=True, t=pos)
            drvName = self.drvSetup['nameTempl'] + str(i + 1) + '_drv'
            drv = controlTools.cntrlCrv(name=drvName, obj=jnt, connType='parent', **self.drvSetup)
            cntrlName = self.ctrlSetup['nameTempl'] + str(i + 1)
            cntrl = controlTools.cntrlCrv(name=cntrlName, obj=drv, connType='connection',
                                          offsets=1, **self.ctrlSetup)

            if self.hasMulti:
                mlt = pm.createNode('multiplyDivide')
                mlt.input2.set([-1, -1, -1])
                cntrl.translate >> mlt.input1
                mlt.output >> cntrl.getParent().translate

            self.cntrlList.append(cntrl)
            cntrl.getParent(2).setParent(self.cntrlGrp)
            drv.getParent().setParent(self.drvGrp)

