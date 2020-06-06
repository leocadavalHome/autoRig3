import pymel.core as pm
import maya.api.OpenMaya as om2
import logging
import re
logger = logging.getLogger('autoRig')

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

def splitSidesAPI(targetObj=None, sourceObj=None, baseName=None, falloff = 0.2):
    '''

    Based on script by Jeff Rosenthal
    Modified by Leonardo Cadaval
    03/12/2018
    Creates left and ride side variations of a blendshape along the X axis
    Select your source face, then select the blendshape you created
    run the script!

    :param targetObj:
    :param sourceObj:
    :param falloff:
    :return:
    '''

    # look at number of verticies
    pm.select (sourceObj)
    tgtVertex = getObjVertex(targetObj.name())
    srcVertex = getObjVertex(sourceObj.name())


    bBox = getBBox(targetObj.name())
    rgtX = bBox.max.x
    # duplicate face twice (one left, one right)

    if baseName:
        tgtName = baseName
    else:
        tgtName = targetObj

    targetObj_Lft = pm.duplicate(targetObj, n='R_'+tgtName)[0]
    pm.move(targetObj_Lft, rgtX * -2.1, 0, 0, r=1)
    targetObj_Rgt = pm.duplicate(targetObj, n='L_'+tgtName)[0]
    pm.move(targetObj_Rgt, rgtX * 2.1, 0, 0, r=1)

    side = 1
    # on each object
    for target in ([targetObj_Lft, targetObj_Rgt]):
        side *= -1
        newPoint = om2.MPoint()
        newPntArray = om2.MPointArray()
        for id in range(len(srcVertex)):
            # get vert positions

            # find difference
            differencePos = (srcVertex[id][0] - tgtVertex[id][0], srcVertex[id][1] - tgtVertex[id][1],
                             srcVertex[id][2] - tgtVertex[id][2])

            # get falloff amount from side of object
            falloffDist = getValue(srcVertex[id][0], falloff*side)

            # move vert difference * falloff amount
            newPntArray.append(om2.MPoint(tgtVertex[id][0]+(differencePos[0] * falloffDist),
                               tgtVertex[id][1]+(differencePos[1] * falloffDist),
                               tgtVertex[id][2]+(differencePos[2] * falloffDist)))
        setObjVertex(target.name(), newPntArray)

    return [targetObj_Lft, targetObj_Rgt]


def splitShapes(targetList=None, falloff=.2):
    bsList = targetList[:-1]
    neutro = targetList[-1]
    splittedTargetList = []
    for obj in bsList:
        if obj:
            logger.debug('splitting %s' % obj)
            L_splitted, R_splitted = splitSidesAPI(obj, neutro, falloff=falloff)
            splittedTargetList.append(L_splitted)
            splittedTargetList.append(R_splitted)
    return splittedTargetList


def addTargets(sourceObj=None, splittedTargets=list()):
    firstIndex = 0
    bsNode = getBlendShapeNode(sourceObj)

    if bsNode:
        appliedTargetNames = pm.listAttr(bsNode.w, m=True)

        firstIndex = nextFreeIndex(bsNode)
        for i, target in enumerate(splittedTargets):
            if target.name() in appliedTargetNames:
                delete_blendshape_target(bsNode.name(), getIndexByName(bsNode, target.name()))
                pm.aliasAttr(bsNode.name()+'.'+target.name(), rm=True)

            pm.blendShape(bsNode, edit=True, t=(sourceObj.name(), i + firstIndex, target.name(), 1.0))
            print ('reapplying target{1} index {0}'.format(i+firstIndex, target.name()))
        pm.delete(splittedTargets)
    else:
        firstIndex = 0
        pm.blendShape(splittedTargets, sourceObj)
        #pm.delete(splittedTargets)

    return firstIndex


def delete_blendshape_target(blendshape_name, target_index):
    pm.select(d=True)
    pm.removeMultiInstance(blendshape_name + ".weight[%s]" % target_index, b=True)
    pm.removeMultiInstance(blendshape_name + ".inputTarget[0].inputTargetGroup[%s]" % target_index, b=True)


def nextFreeIndex(blsNode):
    allTargets = pm.aliasAttr(blsNode, q=True)
    weightList = allTargets[1::2]
    max_index = 0
    for weight in weightList:
        split_w = re.split('\[(.*?)\]', str(weight))
        index = int(split_w[1])
        max_index = max(max_index, index)
    return max_index+1


def getBlendShapeNode(sourceObj):
    history = pm.listHistory(sourceObj, il=2, pdo=1)
    blendNodes = [x for x in history if isinstance(x, pm.nodetypes.BlendShape)]
    if blendNodes:
        return blendNodes[-1] # get last blendShape, if there is a predeform one. Need to check
    else:
        return None


def getIndexByName(bsNode, targetName):
    weightList = pm.aliasAttr(bsNode, q=True)
    nameIndex = weightList.index(targetName)
    bsIndex = re.split('\[(.*?)\]', str(weightList[nameIndex+1]))
    return int(bsIndex[1])


def getNamebyIndex(bsNode, index):
    weightList = pm.aliasAttr(bsNode, q=True)
    indexString = [weightList.index(x) for x in weightList if '[' + str(index) + ']' in x]
    return weightList[int(indexString[0]) - 1]