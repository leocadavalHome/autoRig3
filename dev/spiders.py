import pymel.core as pm
import autoRig3.modules.limbModule as  limb
import autoRig3.modules.ribbonBezier as ribbon
import autoRig3.modules.moveAllModule as moveall
import autoRig3.modules.chainModule  as chain

mAll = moveall.Moveall(name='CHARACTER')
mAll.doRig()

body = chain.Chain('body', divNum=2)
head = chain.Chain('head', divNum=2)
body.doGuide()
head.doGuide()

body.getDict()
head.getDict()

head.doRig()
body.doRig()


L_mandibula = chain.Chain('L_mandibula')
R_mandibula = chain.Chain('R_mandibula')

L_mandibula.doGuide()
R_mandibula.doGuide()
R_mandibula.mirrorConnectGuide(L_mandibula)

L_mandibula.doRig()
R_mandibula.doRig()


L_Shoulder1 = chain.Chain('L_leg1Shoulder')
L_Shoulder2 = chain.Chain('L_leg2Shoulder')
L_Shoulder3 = chain.Chain('L_leg3Shoulder')
L_Shoulder4 = chain.Chain('L_leg4Shoulder')

R_Shoulder1 = chain.Chain('R_leg1Shoulder')
R_Shoulder2 = chain.Chain('R_leg2Shoulder')
R_Shoulder3 = chain.Chain('R_leg3Shoulder')
R_Shoulder4 = chain.Chain('R_leg4Shoulder')



L_Shoulder1.doGuide()
R_Shoulder1.doGuide()
R_Shoulder1.mirrorConnectGuide(L_Shoulder1)

L_Shoulder2.doGuide()
R_Shoulder2.doGuide()
R_Shoulder2.mirrorConnectGuide(L_Shoulder2)

L_Shoulder3.doGuide()
R_Shoulder3.doGuide()
R_Shoulder3.mirrorConnectGuide(L_Shoulder3)

L_Shoulder4.doGuide()
R_Shoulder4.doGuide()
R_Shoulder4.mirrorConnectGuide(L_Shoulder4)

L_Shoulder1.getDict()
L_Shoulder2.getDict()
L_Shoulder3.getDict()
L_Shoulder4.getDict()
R_Shoulder1.getDict()
R_Shoulder2.getDict()
R_Shoulder3.getDict()
R_Shoulder4.getDict()

L_Shoulder1.doRig()
L_Shoulder2.doRig()
L_Shoulder3.doRig()
L_Shoulder4.doRig()

R_Shoulder1.doRig()
R_Shoulder2.doRig()
R_Shoulder3.doRig()
R_Shoulder4.doRig()


L_leg1 = limb.Limb(name='L_leg1')
L_leg2 = limb.Limb(name='L_leg2')
L_leg3 = limb.Limb(name='L_leg3')
L_leg4 = limb.Limb(name='L_leg4')
R_leg1 = limb.Limb(name='R_leg1')
R_leg2 = limb.Limb(name='R_leg2')
R_leg3 = limb.Limb(name='R_leg3')
R_leg4 = limb.Limb(name='R_leg4')

L_leg1.doGuide()
R_leg1.doGuide()
R_leg1.mirrorConnectGuide(L_leg1)
L_leg2.doGuide()
R_leg2.doGuide()
R_leg2.mirrorConnectGuide(L_leg2)
L_leg3.doGuide()
R_leg3.doGuide()
R_leg3.mirrorConnectGuide(L_leg3)
L_leg4.doGuide()
R_leg4.doGuide()
R_leg4.mirrorConnectGuide(L_leg4)

L_leg1.getDict()
R_leg1.getDict()
L_leg2.getDict()
R_leg2.getDict()
L_leg3.getDict()
R_leg3.getDict()
L_leg4.getDict()
R_leg4.getDict()

L_leg1.doRig()
R_leg1.doRig()
L_leg2.doRig()
R_leg2.doRig()
L_leg3.doRig()
R_leg3.doRig()
L_leg4.doRig()
R_leg4.doRig()

L_ribbon1 = ribbon.RibbonBezier(name='L_ribbon1', size=L_leg1.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)
R_ribbon1 = ribbon.RibbonBezier(name='R_ribbon1', size=L_leg1.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)
L_ribbon2 = ribbon.RibbonBezier(name='L_ribbon2', size=L_leg1.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)
R_ribbon2 = ribbon.RibbonBezier(name='R_ribbon2', size=L_leg1.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)
L_ribbon3 = ribbon.RibbonBezier(name='L_ribbon3', size=L_leg1.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)
R_ribbon3 = ribbon.RibbonBezier(name='R_ribbon3', size=L_leg1.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)
L_ribbon4 = ribbon.RibbonBezier(name='L_ribbon4', size=L_leg1.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)
R_ribbon4 = ribbon.RibbonBezier(name='R_ribbon4', size=L_leg1.jointLength, numJnts=6, offsetStart=0.1, offsetEnd=0.1)

L_ribbon1.doRig()
R_ribbon1.doRig()
L_ribbon2.doRig()
R_ribbon2.doRig()
L_ribbon3.doRig()
R_ribbon3.doRig()
L_ribbon4.doRig()
R_ribbon4.doRig()

L_ribbon1.connectToLimb(L_leg1)
R_ribbon1.connectToLimb(R_leg1)
L_ribbon2.connectToLimb(L_leg2)
R_ribbon2.connectToLimb(R_leg2)
L_ribbon3.connectToLimb(L_leg3)
R_ribbon3.connectToLimb(R_leg3)
L_ribbon4.connectToLimb(L_leg4)
R_ribbon4.connectToLimb(R_leg4)

cogCntrl = pm.PyNode('bodyChainFk_ctrl')
cogCntrl.addAttr('L_leg1_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('R_leg1_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('L_leg2_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('R_leg2_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('L_leg3_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('R_leg3_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('L_leg4_FkIk', at='float', dv=1, max=1, min=0, k=1)
cogCntrl.addAttr('R_leg4_FkIk', at='float', dv=1, max=1, min=0, k=1)

cogCntrl.addAttr('L_leg1_poleVec', at='float', dv=0, max=1, min=0, k=1)
cogCntrl.addAttr('R_leg1_poleVec', at='float', dv=0, max=1, min=0, k=1)
cogCntrl.addAttr('L_leg2_poleVec', at='float', dv=0, max=1, min=0, k=1)
cogCntrl.addAttr('R_leg2_poleVec', at='float', dv=0, max=1, min=0, k=1)
cogCntrl.addAttr('L_leg3_poleVec', at='float', dv=0, max=1, min=0, k=1)
cogCntrl.addAttr('R_leg3_poleVec', at='float', dv=0, max=1, min=0, k=1)
cogCntrl.addAttr('L_leg4_poleVec', at='float', dv=0, max=1, min=0, k=1)
cogCntrl.addAttr('R_leg4_poleVec', at='float', dv=0, max=1, min=0, k=1)

cogCntrl.R_leg1_FkIk >> R_leg1.moveall.ikfk
cogCntrl.L_leg1_FkIk >> L_leg1.moveall.ikfk
cogCntrl.R_leg2_FkIk >> R_leg2.moveall.ikfk
cogCntrl.L_leg2_FkIk >> L_leg2.moveall.ikfk
cogCntrl.R_leg3_FkIk >> R_leg3.moveall.ikfk
cogCntrl.L_leg3_FkIk >> L_leg3.moveall.ikfk
cogCntrl.R_leg4_FkIk >> R_leg4.moveall.ikfk
cogCntrl.L_leg4_FkIk >> L_leg4.moveall.ikfk

cogCntrl.R_leg1_poleVec >> R_leg1.moveall.poleVec
cogCntrl.L_leg1_poleVec >> L_leg1.moveall.poleVec
cogCntrl.R_leg2_poleVec >> R_leg2.moveall.poleVec
cogCntrl.L_leg2_poleVec >> L_leg2.moveall.poleVec
cogCntrl.R_leg3_poleVec >> R_leg3.moveall.poleVec
cogCntrl.L_leg3_poleVec >> L_leg3.moveall.poleVec
cogCntrl.R_leg4_poleVec >> R_leg4.moveall.poleVec
cogCntrl.L_leg4_poleVec >> L_leg4.moveall.poleVec

