import autoRig3.dev.stickyLips as stickyLips
import pymel.core as pm
import autoRig3.tools.skinTools as skinTools
import autoRig3.tools.vertexWalkTools as vtxWalk

edges = pm.ls(sl=True, fl=True)
x = stickyLips.StickyLips()

x.doGuide(edgeLoop=edges)

x.doRig(iniOffset=True)

edges2 = pm.ls(sl=True, fl=True)
skinTools.edgeSkin(edgeLoopOriginal=edges2, paralelLoopNum=4)

skinJoints = pm.ls('L_stick*_Offset')
print skinJoints
sk = [y for y in [x.getChildren() for x in skinJoints]]
print sk