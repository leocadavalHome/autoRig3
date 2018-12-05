import pymel.core as pm
import autoRig3.modules.eyeBrows as eyeBrows
import autoRig3.modules.jaw as jaw
import autoRig3.modules.mouthCorners as mouthCorners


sel = pm.ls(sl=True)
neutro = sel.pop(-1)

mCorners = mouthCorners.MouthCorners(name='MouthCorners', receiptMesh=neutro, targetShapes=sel)
L_eyeBrow = eyeBrows.EyeBrow(name='L_brow', mesh='corpo1')
R_eyeBrow = eyeBrows.EyeBrow(name='R_brow', mesh='corpo1', flipAxis=True)
mouthJaw = jaw.Jaw(name='jaw')

L_eyeBrow.doGuide()
R_eyeBrow.mirrorConnectGuide(L_eyeBrow)
mCorners.doGuide()
mouthJaw.doGuide()

mouthJaw.doRig()
L_eyeBrow.doRig()
R_eyeBrow.doRig()
mCorners.doRig()