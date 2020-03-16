import pymel.core as pm
import autoRig3.tools.blendShapeTools as blendShapeTools
import re


bsNode = pm.PyNode('blendShape26')
print bsNode
targetList = pm.ls(sl=True)
print targetList


addTargets(sourceObj=sourceObj[0], splittedTargets=targetList)

appliedTargetNames = pm.listAttr(bsNode.w, m=True)
print pm.blendShape(bsNode, q=True, wc=True)
print appliedTargetNames
print len(appliedTargetNames)

bsNode = sourceObj.getShape().listConnections(type='blendShape', s=True, d=False)


def getNamebyIndex(bsNode, index):
    weightList = pm.aliasAttr(bsNode, q=True)
    indexString = [weightList.index(x) for x in weightList if '[' + str(index) + ']' in x]
    return weightList[int(indexString[0]) - 1]

lcorner = pm.PyNode('L_mouthCorner_ctrl')
rcorner = pm.PyNode('R_mouthCorner_ctrl')
sourceObj = [pm.PyNode('human_head_targets')]

for i in range(4):
    print i