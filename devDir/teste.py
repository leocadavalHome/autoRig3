import autoRig3.modules.moveAllModule as moveall

x=moveall.Moveall(name='viralata')

x.doRig()


import pymel.core as pm

sel = pm.ls(sl=True, fl=True)
for cv in sel:
    pm.cluster(cv)

sel = pm.ls(sl=True, fl=True)
for cv in sel:
    pm.select(cl=True)
    jnt = pm.joint()
    pos = pm.xform(cv, q=True, ws=True, t=True)
    pm.xform(jnt, ws=True, t=pos)