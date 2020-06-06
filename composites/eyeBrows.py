import autoRig3.modules.eyeBrowBlend as eyeBrow
import autoRig3.tools.blendShapeTools as blendShapeTools
import pymel.core as pm
import logging

logger = logging.getLogger('autoRig')

class EyeBrows:
    def __init__(self, name='eyeBrow', sourceObj=None, targetNeutral=None,
                 targetUp=None, targetDown=None, targetCompress=None):
        self.name = name
        self.sourceObj = [pm.PyNode(x) for x in sourceObj]
        self.targetNeutral = [pm.PyNode(x) for x in targetNeutral]
        self.targetUp = [pm.PyNode(x) for x in targetUp]
        self.targetDown = [pm.PyNode(x) for x in targetDown]
        self.targetCompress = [pm.PyNode(x) for x in targetCompress]
        self.L_eyebrow = eyeBrow.EyeBrowBlend(name='L_'+self.name)
        self.R_eyebrow = eyeBrow.EyeBrowBlend(name='R_'+self.name)
 
    def doGuide(self):
        self.L_eyebrow.doGuide()
        self.R_eyebrow.doGuide()
        self.R_eyebrow.mirrorConnectGuide(self.L_eyebrow)
        
    def getDict(self):
        self.R_eyebrow.getDict()
        self.L_eyebrow.getDict()

    def doConnectToCtrls(self, sourceObj=None, firstIndex=None):
        baseName = sourceObj.split('_')[0]
        bsNode = sourceObj.getShape().listConnections(type='blendShape', s=True, d=False)

        for side in ['L_', 'R_']:
            for ctrl in ['In', 'MidIn', 'MidOut', 'Out']:
                slider = pm.PyNode(side + self.name + ctrl + '_ctrl')
                for shape in ['Up', 'Down']:
                    slider.getParent().attr(shape.lower() + 'Value') >> bsNode[0].attr(side + baseName + shape + ctrl)

            slider = pm.PyNode(side + self.name + 'In_ctrl')
            slider.getParent().attr('compressValue') >> bsNode[0].attr(side + baseName + 'Compress')

    def doRig(self):
        self.L_eyebrow.doRig()
        self.R_eyebrow.doRig()
        for sourceObj, targetNeutral, targetUp, targetDown, targetCompress in zip(self.sourceObj, self.targetNeutral,
                                                                                  self.targetUp, self.targetDown,
                                                                                  self.targetCompress):
            targetList = self.doBlendSplit(name=self.name, sourceObj=sourceObj, targetNeutral=targetNeutral,
                                           targetUp=targetUp, targetDown=targetDown, targetCompress=targetCompress,
                                           L_eyebrow=self.L_eyebrow, R_eyebrow=self.R_eyebrow)

            firstIndex = blendShapeTools.addTargets(sourceObj=sourceObj, splittedTargets=targetList)
            self.doConnectToCtrls(sourceObj=sourceObj, firstIndex=firstIndex)


    @staticmethod
    def doBlendSplit(name='eyeBrow', sourceObj=None, targetNeutral=None, targetUp=None,
                     targetDown=None, targetCompress=None, L_eyebrow=None, R_eyebrow=None):

        baseName = sourceObj.nodeName().split('_')[0]

        upShapes = eyeBrow.shapeDivide(name=baseName+'Up', targetNeutral=targetNeutral, targetObj=targetUp,
                                       L_eyeBrowGuide=L_eyebrow, R_eyeBrow_guide=R_eyebrow)

        downShapes = eyeBrow.shapeDivide(name=baseName+'Down', targetNeutral=targetNeutral, targetObj=targetDown,
                                         L_eyeBrowGuide=L_eyebrow, R_eyeBrow_guide=R_eyebrow)

        Xmax = pm.xform(L_eyebrow.guideMoveall, ws=True, t=True, q=True)[0]
        Xmin = pm.xform(R_eyebrow.guideMoveall, ws=True, t=True, q=True)[0]
        falloff = Xmax - Xmin
        compressShapes = blendShapeTools.splitSidesAPI(baseName=baseName+'Compress', targetObj=targetCompress,
                                                       sourceObj=targetNeutral,falloff=falloff)

        return upShapes+downShapes+compressShapes


