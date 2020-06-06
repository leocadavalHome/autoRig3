import pymel.core as pm
import autoRig3.modules.limbModule as  limb
import autoRig3.modules.ribbonBezier as ribbon
import autoRig3.modules.moveAllModule as moveall
import autoRig3.modules.chainModule  as chain


lfrShoulder = chain.Chain('Lfr_legShoulder')
rfrShoulder = chain.Chain('Rfr_legShoulder')
lbkShoulder = chain.Chain('Lbk_legShoulder')
rbkShoulder = chain.Chain('Rbk_legShoulder')


lfrShoulder.doGuide()
rfrShoulder.doGuide()
rfrShoulder.mirrorConnectGuide(lfrShoulder)
lbkShoulder.doGuide()
rbkShoulder.doGuide()
rbkShoulder.mirrorConnectGuide(lbkShoulder)

lfrShoulder.doRig()
rfrShoulder.doRig()
lbkShoulder.doRig()
rbkShoulder.doRig()


mAll = moveall.Moveall(name='CHARACTER')
mAll.doRig()

lfleg= limb.Limb(name='Lfr_leg')
rfleg= limb.Limb(name='Rfr_leg')

lbleg= limb.Limb(name='Lbk_leg')
rbleg= limb.Limb(name='Rbk_leg')


lfleg.doGuide()
rfleg.doGuide()
rfleg.mirrorConnectGuide(lfleg)
lbleg.doGuide()
rbleg.doGuide()
rbleg.mirrorConnectGuide(lbleg)


lfleg.getDict()
rfleg.getDict()
lbleg.getDict()
rbleg.getDict()

lfleg.doRig()
rfleg.doRig()
lbleg.doRig()
rbleg.doRig()

lfrribbon = ribbon.RibbonBezier(name='Lfr_ribbon', size=lfleg.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)
rfrribbon = ribbon.RibbonBezier(name='Rfr_ribbon', size=rfleg.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)
lbkribbon = ribbon.RibbonBezier(name='Lbk_ribbon', size=lbleg.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)
rbkribbon = ribbon.RibbonBezier(name='Rbk_ribbon', size=rbleg.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)


lfrribbon.doRig()
rfrribbon.doRig()
lbkribbon.doRig()
rbkribbon.doRig()

lfrribbon.connectToLimb(lfleg)
rfrribbon.connectToLimb(rfleg)
lbkribbon.connectToLimb(lbleg)
rbkribbon.connectToLimb(rbleg)

cogCntrl = pm.PyNode('cog_ctrl_ctrl')
cogCntrl.addAttr('L_arm_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('R_arm_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('L_leg_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('R_leg_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('Spine_FkIk', at='float', dv=1, max=1, min=0, k=1)

cogCntrl.addAttr('L_arm_poleVec', at='float', dv=0, max=1, min=0, k=1)
cogCntrl.addAttr('R_arm_poleVec', at='float', dv=0, max=1, min=0, k=1)
cogCntrl.addAttr('L_leg_poleVec', at='float', dv=0, max=1, min=0, k=1)
cogCntrl.addAttr('R_leg_poleVec', at='float', dv=0, max=1, min=0, k=1)

cogCntrl.R_leg_FkIk >> rbleg.moveall.ikfk
cogCntrl.L_leg_FkIk >> lbleg.moveall.ikfk
cogCntrl.R_arm_FkIk >> rfleg.moveall.ikfk
cogCntrl.L_arm_FkIk >> lfleg.moveall.ikfk
cogCntrl.R_arm_poleVec >> rfleg.moveall.poleVec
cogCntrl.L_arm_poleVec >> lfleg.moveall.poleVec
cogCntrl.R_leg_poleVec >> rbleg.moveall.poleVec
cogCntrl.L_leg_poleVec >> lbleg.moveall.poleVec