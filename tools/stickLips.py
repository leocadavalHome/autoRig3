import autoRig3.tools.vertexWalkTools as vtxWalk
import maya.api.OpenMaya as om
import pymel.core as pm
import autoRig3.tools.skinTools as skinTools
import copy

edge = pm.ls(sl=True, fl=True)
mesh = pm.ls(edge[0], o=True)[0]

## do guide
extremes = vtxWalk.getEdgeLoopExtremesPoints(edge)
pm.select(extremes)
locs = []
for vtx in extremes:
    loc = pm.spaceLocator()
    pos = pm.xform(vtx, q=True, t=True, ws=True)
    pm.xform(loc, t=pos, ws=True)
    locs.append(loc)


## do joints
pos = pm.xform(locs[3], q=True, ws=True, t=True)
pm.select(cl=True)
jntUpper = pm.joint(n='Mid_upper')
pm.xform(jntUpper, t=pos, ws=True)

pos = pm.xform(locs[2], q=True, ws=True, t=True)
pm.select(cl=True)
jntLower = pm.joint(n='Mid_lower')
pm.xform(jntLower, t=pos, ws=True)


L_edge = vtxWalk.getLoopByLocators(mesh=mesh, loc1=locs[2], loc2=locs[3], loc3=locs[1])
L_vertices = vtxWalk.edgeLoopToVextex(L_edge)
#get corner pos again, because it can be tweaked
cornerPos = pm.xform(locs[1], q=True, ws=True, t=True)
cornerVertex = vtxWalk.getClosestVertex(mesh=mesh, pos=cornerPos)
cornerIndex = L_vertices.index(cornerVertex)

L_jointsUp = []
for i, vtx in enumerate(L_vertices[1:cornerIndex]):
    pm.select(cl=True)
    jnt = pm.joint(n='L_upper'+str(i))
    pos = pm.xform(vtx, q=True, t=True, ws=True)
    pm.xform(jnt, t=pos, ws=True)
    L_jointsUp.append(jnt)
L_jointsUp.reverse()

L_jointsLw = []
for i, vtx in enumerate(L_vertices[cornerIndex+1:-1]):
    pm.select(cl=True)
    jnt = pm.joint(n='L_lower'+str(i))
    pos = pm.xform(vtx, q=True, t=True, ws=True)
    pm.xform(jnt, t=pos, ws=True)
    L_jointsLw.append(jnt)

pm.select(L_jointsUp[6], L_jointsLw[6])

R_edge = vtxWalk.getLoopByLocators(mesh=mesh, loc1=locs[2], loc2=locs[3], loc3=locs[0])
R_vertices = vtxWalk.edgeLoopToVextex(R_edge)
#get corner pos again, because it can be tweaked
cornerPos = pm.xform(locs[0], q=True, ws=True, t=True)
cornerVertex = vtxWalk.getClosestVertex(mesh=mesh, pos = cornerPos)
cornerIndex = R_vertices.index(cornerVertex)

R_jointsUp = []
for i, vtx in enumerate(R_vertices[cornerIndex+1:-1]):
    pm.select(cl=True)
    jnt = pm.joint(n='R_upper'+str(i))
    pos = pm.xform(vtx, q=True, t=True, ws=True)
    pm.xform(jnt, t=pos, ws=True)
    R_jointsUp.append(jnt)

R_jointsLw = []
for i, vtx in enumerate(R_vertices[1:cornerIndex]):
    pm.select(cl=True)
    jnt = pm.joint(n='R_lower'+str(i))
    pos = pm.xform(vtx, q=True, t=True, ws=True)
    pm.xform(jnt, t=pos, ws=True)
    R_jointsLw.append(jnt)
R_jointsLw.reverse()

pm.select(R_jointsUp[1], R_jointsLw[1])

## init variaveis
iniOffset = True
stickyMin1 = 0
stickyMax1 = 20
stickyMin2 = 20
stickyMax2 = 40
L_ctrl = pm.spaceLocator(n='L_sticky_ctrl')
R_ctrl = pm.spaceLocator(n='R_sticky_ctrl')
L_ctrl.addAttr('sticky', at='float', k=1, dv=0, min=0)
R_ctrl.addAttr('sticky', at='float', k=1, dv=0, min=0)
L_ctrl.addAttr('offset', at='float', k=1, dv=0, min=0)
R_ctrl.addAttr('offset', at='float', k=1, dv=0, min=0)
L_ctrl.addAttr('height', at='float', k=1, dv=0, min=0, max=1)
R_ctrl.addAttr('height', at='float', k=1, dv=0, min=0, max=1)

def stickyPairSetup(name='sticky', upperJnt=None, lowerJnt=None, ctrl1=None, ctrl2=None,
                    stickyMin1=0, stickyMin2=0, stickyMax1=0, stickyMax2=0,
                    iniOffset=False):

    ##Calcula o centro (usar vetores pra facilitar a conta)
    a = pm.xform(upperJnt, q=True, ws=True, t=True)
    b = pm.xform(lowerJnt, q=True, ws=True, t=True)
    upperPos = om.MVector(a[0], a[1], a[2])
    lowerPos = om.MVector(b[0], b[1], b[2])
    centerPos = (upperPos+lowerPos)/2

    #opcao de fazer o offset no centro ou alinhado aos vertices
    if iniOffset:
        upperOffsetPos = (centerPos.x, upperPos.y, centerPos.z)
        lowerOffsetPos = (centerPos.x, lowerPos.y, centerPos.z)
    else:
        upperOffsetPos = (centerPos.x, centerPos.y, centerPos.z)
        lowerOffsetPos = (centerPos.x, centerPos.y, centerPos.z)

    #cria os grupos(joints agora)
    pm.select(cl=True)
    upperOffsetJoint = pm.joint(name=name+'Upper_Offset')
    upperDriverJoint = pm.joint(name=name+'Upper_Driver')

    pm.xform(upperOffsetJoint, ws=True, t=upperOffsetPos)
    pm.parent(upperOffsetJoint, upperJnt)

    pm.select(cl=True)
    lowerOffsetJoint = pm.joint(name=name+'Lower_Offset')
    lowerDriverJoint = pm.joint(name=name+'Lower_Driver')
    pm.xform(lowerOffsetJoint, ws=True, t=lowerOffsetPos)
    pm.parent(lowerOffsetJoint, lowerJnt)

    pm.select(cl=True)
    upperOffsetBindJoint = pm.joint(name=name+'UpperSkin_Offset')
    upperBindJoint = pm.joint(name=name+'UpperSkin_jxt')
    pm.xform(upperOffsetBindJoint, ws=True, t=(upperPos.x,upperPos.y,upperPos.z))

    pm.select(cl=True)
    lowerOffsetBindJoint = pm.joint(name=name+'LowerSkin_Offset')
    lowerBindJoint = pm.joint(name=name+'LowerSkin_jxt')
    pm.xform(lowerOffsetBindJoint, ws=True, t=(lowerPos.x,lowerPos.y,lowerPos.z))

    #cria os nodes para o blend de posicao do driver
    upperAddMatrix = pm.createNode('wtAddMatrix')
    upperMultiMatrix = pm.createNode('multMatrix')
    upperDecomposeMatrix = pm.createNode('decomposeMatrix')
    lowerAddMatrix = pm.createNode('wtAddMatrix')
    lowerMultiMatrix = pm.createNode('multMatrix')
    lowerDecomposeMatrix = pm.createNode('decomposeMatrix')

    stickyUpperSetRange = pm.createNode('setRange')
    stickyLowerSetRange = pm.createNode('setRange')
    stickyUpperAdd = pm.createNode('addDoubleLinear')
    stickylowerAdd = pm.createNode('addDoubleLinear')
    stickClamp = pm.createNode('clamp')
    stickOffset = pm.createNode('plusMinusAverage')
    stickyReverse = pm.createNode('reverse')

    ctrl1.sticky >> stickyUpperSetRange.valueX
    ctrl2.sticky >> stickyUpperSetRange.valueY
    ctrl1.sticky >> stickyLowerSetRange.valueX
    ctrl2.sticky >> stickyLowerSetRange.valueY


    ctrl1.height >> stickyReverse.inputX

    stickyUpperSetRange.minX.set(0)
    ctrl1.height >> stickyUpperSetRange.maxX
    ctrl1.height >> stickyUpperSetRange.maxY

    stickyLowerSetRange.minY.set(0)
    stickyReverse.outputX >> stickyLowerSetRange.maxX
    stickyReverse.outputX >> stickyLowerSetRange.maxY

    stickyUpperSetRange.oldMinX.set(stickyMin1)
    stickyUpperSetRange.oldMinY.set(stickyMin2)
    stickyLowerSetRange.oldMinX.set(stickyMin1)
    stickyLowerSetRange.oldMinY.set(stickyMin2)


    stickOffset.input2D[0].input2Dx.set(stickyMax1)
    ctrl1.offset >> stickOffset.input2D[1].input2Dx
    stickOffset.output2Dx >> stickyUpperSetRange.oldMaxX
    stickOffset.output2Dx >> stickyLowerSetRange.oldMaxX

    stickOffset.input2D[0].input2Dy.set(stickyMax2)
    ctrl2.offset >> stickOffset.input2D[1].input2Dy
    stickOffset.output2Dy >> stickyUpperSetRange.oldMaxY
    stickOffset.output2Dy >> stickyLowerSetRange.oldMaxY

    stickyUpperSetRange.outValueX >> stickyUpperAdd.input1
    stickyUpperSetRange.outValueY >> stickyUpperAdd.input2
    stickyUpperAdd.output >> stickClamp.inputR
    stickClamp.maxR.set(1)

    stickyLowerSetRange.outValueX >> stickylowerAdd.input1
    stickyLowerSetRange.outValueY >> stickylowerAdd.input2
    stickylowerAdd.output >> stickClamp.inputG
    stickClamp.maxG.set(1)

    #faz as conexoes para o blend da posicao do driver
    upperOffsetJoint.worldMatrix[0] >> upperAddMatrix.wtMatrix[0].matrixIn
    stickClamp.outputR >> upperAddMatrix.wtMatrix[0].weightIn
    lowerOffsetJoint.worldMatrix[0] >> upperAddMatrix.wtMatrix[1].matrixIn
    stickClamp.outputR >> upperAddMatrix.wtMatrix[1].weightIn
    upperOffsetJoint.worldInverseMatrix >> upperMultiMatrix.matrixIn[0]
    upperAddMatrix.matrixSum >> upperMultiMatrix.matrixIn[1]
    upperMultiMatrix.matrixSum >> upperDecomposeMatrix.inputMatrix
    upperDecomposeMatrix.outputTranslate >> upperDriverJoint.translate

    upperOffsetJoint.worldMatrix[0] >> lowerAddMatrix.wtMatrix[0].matrixIn
    stickClamp.outputG >> lowerAddMatrix.wtMatrix[0].weightIn
    lowerOffsetJoint.worldMatrix[0] >> lowerAddMatrix.wtMatrix[1].matrixIn
    stickClamp.outputG >> lowerAddMatrix.wtMatrix[1].weightIn
    lowerOffsetJoint.worldInverseMatrix >> lowerMultiMatrix.matrixIn[0]
    lowerAddMatrix.matrixSum >> lowerMultiMatrix.matrixIn[1]
    lowerMultiMatrix.matrixSum >> lowerDecomposeMatrix.inputMatrix
    lowerDecomposeMatrix.outputTranslate >> lowerDriverJoint.translate

    upperDriverJoint.translate >> upperBindJoint.translate
    lowerDriverJoint.translate >> lowerBindJoint.translate


total = len(L_jointsUp)
incr = 20.0/total-1
print incr
for i, jnts in enumerate(zip(L_jointsUp, L_jointsLw)):
    print i, jnts
    print incr*i
    stickyPairSetup(name='L_sticky'+str(i),
                    upperJnt=jnts[0], lowerJnt=jnts[1], ctrl1=L_ctrl, ctrl2=R_ctrl,
                    stickyMin1=incr*i, stickyMin2=40-incr*(i+1),
                    stickyMax1=incr*(i+1), stickyMax2=40-incr*i,
                    iniOffset=False)

stickyPairSetup(name='mid_sticky',
                upperJnt=jntUpper, lowerJnt=jntLower, ctrl1=L_ctrl, ctrl2=R_ctrl,
                stickyMin1=total, stickyMin2=40-total-incr,
                stickyMax1=total+incr, stickyMax2=40-incr,
                iniOffset=False)


for i, jnts in enumerate(zip(R_jointsUp, R_jointsLw)):
    print i, jnts
    print incr*i
    stickyPairSetup(name='R_sticky'+str(i),
                    upperJnt=jnts[0], lowerJnt=jnts[1], ctrl1=R_ctrl, ctrl2=L_ctrl,
                    stickyMin1=incr*i, stickyMin2=40-incr*(i+1),
                    stickyMax1=incr*(i+1), stickyMax2=40-incr*i,
                    iniOffset=False)

edgeloop = pm.ls(sl=True, fl=True)
skinTools.edgeSkin(edgeLoopOriginal=edgeloop, paralelLoopNum= 2)