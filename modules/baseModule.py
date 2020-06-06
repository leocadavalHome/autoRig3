import pymel.core as pm
import autoRig3.tools.controlTools as controlTools

class BaseModule(object):
    def __init__(self, **kwargs):
        self.guideDict = {}
        self.toExport = []
        self.guideSulfix = None

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
                expDict[key] = self.__dict__[key]
        return expDict

    def loadDict(self):
        pass

    def saveDict(self):
        pass

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

    def getCntrl(self, cntrl, posRot , space='object'):
        self.guideDict[posRot][0] = cntrl.getTranslation(space=space).get()
        self.guideDict[posRot][1] = tuple(cntrl.getRotation(space='object'))
        try:
            self.guideDict[posRot][2] = tuple(pm.xform(cntrl, q=True, s=True, r=True))
        except:
            pass

    def doGuide(self, **kwargs):
        pass

    def getDict(self):
        pass

    def mirrorConnectGuide(self, limb):
        pass

    def doRig(self):
        pass