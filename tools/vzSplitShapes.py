# Based on script by Jeff Rosenthal
# Modified by Leonardo Cadaval
# 03/12/2018

################################################################################
# Creates left and ride side variations of a blendshape along the X axis
#
# Select your source face, then select the blendshape you created
# run the script!
#


import pymel.core as pm
import maya.api.OpenMaya as om2
import logging

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

def splitSidesAPI(targetObj, sourceObj, falloff = 0.2):

    # look at number of verticies
    pm.select (sourceObj)
    tgtVertex = getObjVertex(targetObj.name())
    srcVertex = getObjVertex(sourceObj.name())


    bBox = getBBox(targetObj.name())
    rgtX = bBox.max.x
    # duplicate face twice (one left, one right)
    targetObj_Lft = pm.duplicate(targetObj, n='R_' + targetObj)[0]
    pm.move(targetObj_Lft, rgtX * -2.1, 0, 0, r=1)
    targetObj_Rgt = pm.duplicate(targetObj, n='L_' + targetObj)[0]
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