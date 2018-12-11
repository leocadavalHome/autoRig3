import pymel.core as pm
import autoRig3.modules.eyeBrows as eyeBrows
import autoRig3.modules.jaw as jaw
import autoRig3.modules.mouthCorners as mouthCorners


sel = pm.ls(sl=True)
neutro = sel.pop(-1)

mCorners = mouthCorners.MouthCorners(name='MouthCorners', receiptMesh=neutro, targetShapes=sel)
L_eyeBrow = eyeBrows.EyeBrow(name='L_brow', mesh=neutro)
R_eyeBrow = eyeBrows.EyeBrow(name='R_brow', mesh=neutro, flipAxis=True)
mouthJaw = jaw.Jaw(name='jaw')

mCorners.getGuideFromScene()
L_eyeBrow.getGuideFromScene()
mouthJaw.getGuideFromScene()

L_eyeBrow.doGuide()
R_eyeBrow.mirrorConnectGuide(L_eyeBrow)

mCorners.doGuide()
mouthJaw.doGuide()

mouthJaw.doRig()
mCorners.doRig()

L_eyeBrow.doRig()
R_eyeBrow.doRig()


print mCorners.bsDict

mouthCorners.splitSidesAPI(targetObj=pm.PyNode('male02_eyeblink_geo'), sourceObj=pm.PyNode('male02_body_receipt'), falloff=0.2)
mouthCorners.splitSidesAPI(targetObj=pm.PyNode('male02_half_eyeblink_geo'), sourceObj=pm.PyNode('male02_body_receipt'), falloff=0.2)