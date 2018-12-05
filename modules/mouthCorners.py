# Based on script by Jeff Rosenthal
# Modified by Leonardo Cadaval
# 03/12/2018

################################################################################
# Creates left and ride side variations of a blendshape along the X axis
#
# Select your source face, then select the blendshape you created
# run the script!
#
# Usage:
#
# sel = pm.ls(sl=True)
# neutro = sel.pop(-1)
# print sel
# x = MouthCorners (name='MouthCorners', receiptMesh=neutro, targetShapes = sel)
# x.doGuide()
# x.doRig()



import pymel.core as pm
import maya.api.OpenMaya as om2
import autoRig3.tools.rigFunctions as rigFunctions

class MouthCorners:
    def __init__(self, name='mouthCorners', bsDict=None,  receiptMesh=None, targetShapes = None ):
        self.name = name
        self.receiptMesh = receiptMesh
        self.targetShapes = targetShapes
        self.mouthCornersGuideDict = {'moveall': [0, 0, 0], 'lcorner': [.5, 0, 0], 'rcorner': [-.5, 0, 0]}
        self.bsDict = bsDict


    def doGuide(self):
        if pm.objExists(self.name + 'Moveall_guide'):
            pm.delete(self.name + 'Moveall_guide')
        self.guideMoveall = pm.group(em=True, n=self.name + 'Moveall_guide')
        self.lcornerGuide = pm.spaceLocator(n=self.name + 'LCorner_guide')
        self.lcornerGuide.translate.set(self.mouthCornersGuideDict['lcorner'])
        self.lcornerGuide.localScale.set(0.1, 0.1, 0.1)
        self.rcornerGuide = pm.spaceLocator(n=self.name + 'RCorner_guide')
        self.rcornerGuide.translate.set(self.mouthCornersGuideDict['rcorner'])
        self.rcornerGuide.localScale.set(0.1, 0.1, 0.1)
        pm.parent(self.lcornerGuide, self.rcornerGuide, self.guideMoveall)

    def getGuideFromScene(self):
        self.guideMoveall = pm.PyNode(self.name + 'Moveall_guide')
        self.lcornerGuide = pm.PyNode(self.name + 'LCorner_guide')
        self.rcornerGuide = pm.PyNode(self.name + 'RCorner_guide')

    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()

        if pm.objExists(self.name + 'Moveall'):
            pm.delete(self.name + 'Moveall')
        self.moveall = pm.group(em=True, n=self.name + 'Moveall')

        self.lcornerCntrl = rigFunctions.cntrlCrv(name='LCorner', obj=self.lcornerGuide, icone='circuloZ', size=.5)
        self.lcornerCntrl.getParent().scaleX.set(-1)
        self.rcornerCntrl = rigFunctions.cntrlCrv(name='RCorner', obj=self.rcornerGuide, icone='circuloZ', size=.5)

        splitedTargets=[]
        for target in self.targetShapes:
            split = splitSidesAPI(targetObj=target, sourceObj=self.receiptMesh, falloff=0.2)
            splitedTargets=splitedTargets+split

        print splitedTargets

        self.bsDict=organizeShapes(splitedTargets)

        bsNodeName = pm.blendShape (splitedTargets, self.receiptMesh)
        print bsNodeName
        bsNode = pm.PyNode (bsNodeName[0])

        pm.parent(self.lcornerCntrl.getParent(), self.rcornerCntrl.getParent(), self.moveall)

        #tmp = pm.ls(pm.listHistory(self.receiptMesh, future=False), type='blendShape')
        #if tmp:
        #    bsNode = tmp[0]
        #else:
        #    print 'Nao encontrou blendShape node'


        connectToPainel(self.lcornerCntrl, bsNode, 'translateX', self.bsDict['L_narrow'], .3,
                             self.bsDict['L_wide'], -.3)
        connectToPainel(self.lcornerCntrl, bsNode, 'translateY', self.bsDict['L_up'], .3, self.bsDict['L_down'],-.3)
        connectToPainel(self.rcornerCntrl, bsNode, 'translateX', self.bsDict['R_narrow'], .3,
                             self.bsDict['R_wide'], -.3)
        connectToPainel(self.rcornerCntrl, bsNode, 'translateY', self.bsDict['R_up'], .3, self.bsDict['R_down'],-.3)

        for prefix in ['L_', 'R_']:
            for shpA in ['up', 'down']:
                for shpB in ['wide', 'narrow']:
                    multi1 = pm.createNode('multDoubleLinear')
                    bsNode.attr(self.bsDict[prefix + shpA]) >> multi1.input1
                    bsNode.attr(self.bsDict[prefix + shpB]) >> multi1.input2
                    multi1.output >> bsNode.attr(self.bsDict[prefix + shpA + '_' + shpB])


def connectToPainel(cntrl, bsNode, param, bsMax, vMax, bsMin='', vMin=None):
    ##funcao que conecta o movimento dos controles aos blendShapes
    sR = pm.createNode('setRange')
    c = pm.createNode('clamp')
    sR.maxX.set(1)
    sR.minX.set(0)
    sR.oldMaxX.set(vMax)
    sR.oldMinX.set(0)
    c.maxR.set(1)
    cntrl.attr(param) >> sR.valueX
    sR.outValueX >> c.inputR
    c.outputR >> bsNode.attr(bsMax)
    if bsMin:
        sR.maxY.set(0)
        sR.minY.set(1)
        sR.oldMaxY.set(0)
        sR.oldMinY.set(vMin)
        c.maxG.set(1)
        cntrl.attr(param) >> sR.valueY
        sR.outValueY >> c.inputG
        c.outputG >> bsNode.attr(bsMin)

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
    sel = om2.MSelectionList()
    sel.add(obj)
    selObj = sel.getDagPath(0)

    mfnObject = om2.MFnMesh(selObj)
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


def splitSidesAPI(targetObj, sourceObj, falloff=0.2):
    # look at number of verticies
    pm.select(sourceObj)
    tgtVertex = getObjVertex(targetObj.name())
    srcVertex = getObjVertex(sourceObj.name())

    bBox = getBBox(targetObj.name())
    rgtX = bBox.max.x
    # duplicate face twice (one left, one right)
    targetObj_Lft = pm.duplicate(targetObj, n='L_' + targetObj)[0]
    pm.move(targetObj_Lft, rgtX * -2.1, 0, 0, r=1)
    targetObj_Rgt = pm.duplicate(targetObj, n='R_' + targetObj)[0]
    pm.move(targetObj_Rgt, rgtX * 2.1, 0, 0, r=1)

    side = 1
    # on each object
    for target in ([targetObj_Rgt, targetObj_Lft]):
        side *= -1
        newPoint = om2.MPoint()
        newPntArray = om2.MPointArray()
        for id in range(len(srcVertex)):
            # get vert positions

            # find difference
            differencePos = (srcVertex[id][0] - tgtVertex[id][0], srcVertex[id][1] - tgtVertex[id][1],
                             srcVertex[id][2] - tgtVertex[id][2])

            # get falloff amount from side of object
            falloffDist = getValue(srcVertex[id][0], falloff * side)

            # move vert difference * falloff amount
            newPntArray.append(om2.MPoint(tgtVertex[id][0] + (differencePos[0] * falloffDist),
                                          tgtVertex[id][1] + (differencePos[1] * falloffDist),
                                          tgtVertex[id][2] + (differencePos[2] * falloffDist)))
        setObjVertex(target.name(), newPntArray)
    return [targetObj_Lft.name(), targetObj_Rgt.name()]


def organizeShapes(blendShapes):
    search = ['up', 'down', 'wide', 'narrow']
    resultDict = {}
    print blendShapes
    for obj in blendShapes:
        searchText = obj.lower()
        found = []
        for word in search:
            if word in searchText:
                found.append(word)

        if len(found) == 1:
            if 'up' in found:
                if 'L_' in obj:
                    resultDict['L_up'] = obj
                elif 'R_':
                    resultDict['R_up'] = obj
            elif 'down' in found:
                if 'L_' in obj:
                    resultDict['L_down'] = obj
                elif 'R_':
                    resultDict['R_down'] = obj
            elif 'wide' in found:
                if 'L_' in obj:
                    resultDict['L_wide'] = obj
                elif 'R_':
                    resultDict['R_wide'] = obj
            elif 'narrow' in found:
                if 'L_' in obj:
                    resultDict['L_narrow'] = obj
                elif 'R_':
                    resultDict['R_narrow'] = obj
        elif len(found) == 2:
            if 'up' in found:
                if 'wide' in found:
                    if 'L_' in obj:
                        resultDict['L_up_wide'] = obj
                    elif 'R_':
                        resultDict['R_up_wide'] = obj
                elif 'narrow' in found:
                    if 'L_' in obj:
                        resultDict['L_up_narrow'] = obj
                    elif 'R_':
                        resultDict['R_up_narrow'] = obj
            elif 'down' in found:
                if 'wide' in found:
                    if 'L_' in obj:
                        resultDict['L_down_wide'] = obj
                    elif 'R_':
                        resultDict['R_down_wide'] = obj
                elif 'narrow' in found:
                    if 'L_' in obj:
                        resultDict['L_down_narrow'] = obj
                    elif 'R_':
                        resultDict['R_down_narrow'] = obj
    return resultDict

