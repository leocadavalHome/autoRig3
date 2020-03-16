import os.path
import pymel.core as pm

import autoRig3.modules.jaw as jaw
import autoRig3.modules.lookAt as lookAt
import autoRig3.modules.squash as squash
import autoRig3.modules.mouthBlends as mouth
import autoRig3.modules.eyeLid as eyelid
import autoRig3.composites.eyeBrows as eyeBrows
import autoRig3.modules.lips as lips
import autoRig3.modules.tweaks as tweaks
import autoRig3.modules.eyes as eyes
import autoRig3.tools.interface as interface
import autoRig3.tools.UVtools as UVtools

import autoRig3.tools.meshConnectTools as meshConnect
import autoRig3.tools.spaceSwitchTools as space
import autoRig3.tools.skinTools as skin
import autoRig3.tools.attachTools as attatchTools
import logging


logger = logging.getLogger(__name__)
logger.setLevel(10)

def addHideAtts():
    sel = pm.ls (sl=True)
    obj = sel[0]

    pm.addAttr (obj, ln='FACIAL', at='enum', en='------', k=1)
    pm.addAttr (obj, ln='squashCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='eyebrowBlendCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='eyebrowTweakCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='eyeSocketCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='eyelidCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='faceTweaksCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='mouthBlendCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='lipsCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='jawCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='teethCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='tongueCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='lookatCtrlVis', at='float', min=0, max=1, dv=0, k=1)

    pm.addAttr (obj, ln='BODY', at='enum', en='------', k=1)
    pm.addAttr (obj, ln='limbBezierCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='limbBendCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='limbMidCtrlVis', at='float', min=0, max=1, dv=0, k=1)
    pm.addAttr (obj, ln='tweaksCtrlVis', at='float', min=0, max=1, dv=0, k=1)

    pm.addAttr (obj, ln='IKFK', at='enum', en='------', k=1)
    pm.addAttr (obj, ln='lookatIKFK', at='float', min=0, max=1, dv=0, k=1)

    larm = pm.PyNode ('L_armBezierMoveall')
    rarm = pm.PyNode ('R_armBezierMoveall')
    lleg = pm.PyNode ('L_legBezierMoveall')
    rleg = pm.PyNode ('R_legBezierMoveall')
    look = pm.PyNode ('lookAtCtrl_grp')
    jaw = pm.PyNode ('jaw_ctrl_grp')
    rlid = pm.PyNode ('R_eyeLidEyeLid_constrained_grp')
    llid = pm.PyNode ('L_eyeLidEyeLid_constrained_grp')
    mouthBlends = pm.PyNode ('mouthCornersMoveall')
    tweak1 = pm.PyNode ('faceConstrained')
    tweak2 = pm.PyNode ('R_squintConstrained')
    tweak3 = pm.PyNode ('L_squintConstrained')
    lips = pm.PyNode ('lips_ctrl_grp')
    lbrowTweak = pm.PyNode ('L_eyeBrowtweakCtrls_grp')
    rbrowTweak = pm.PyNode ('R_eyeBrowtweakCtrls_grp')
    rbrowblend = pm.PyNode ('R_eyeBrowSliders_grp')
    lbrowblend = pm.PyNode ('L_eyeBrowSliders_grp')
    headSquash = pm.PyNode ('headSquashCtrl_grp')
    jawdSquash = pm.PyNode ('jawSquashCtrl_grp')
    lsocket = pm.PyNode ('L_eyeSocket_ctrl_grp')
    rsocket = pm.PyNode ('R_eyeSocket_ctrl_grp')
    tongue = pm.PyNode ('tongue0_grp')
    teeth1 = pm.PyNode ('teeth_up_ctrl_grp')
    teeth2 = pm.PyNode ('teeth_dw_ctrl_grp')

    obj.squashCtrlVis >> headSquash.visibility
    obj.squashCtrlVis >> jawdSquash.visibility
    obj.eyebrowBlendCtrlVis >> rbrowblend.visibility
    obj.eyebrowBlendCtrlVis >> lbrowblend.visibility
    obj.eyebrowTweakCtrlVis >> lbrowTweak.visibility
    obj.eyebrowTweakCtrlVis >> rbrowTweak.visibility
    obj.eyeSocketCtrlVis >> lsocket.visibility
    obj.eyeSocketCtrlVis >> rsocket.visibility
    obj.eyelidCtrlVis >> rlid.visibility
    obj.eyelidCtrlVis >> llid.visibility
    obj.faceTweaksCtrlVis >> tweak1.visibility
    obj.faceTweaksCtrlVis >> tweak2.visibility
    obj.faceTweaksCtrlVis >> tweak3.visibility
    obj.mouthBlendCtrlVis >> mouthBlends.visibility
    obj.lipsCtrlVis >> lips.visibility
    obj.jawCtrlVis >> jaw.visibility
    obj.teethCtrlVis >> teeth1.visibility
    obj.teethCtrlVis >> teeth2.visibility
    obj.tongueCtrlVis >> tongue.visibility

    obj.limbMidCtrlVis >> larm.midCtrlViz
    obj.limbMidCtrlVis >> rarm.midCtrlViz
    obj.limbMidCtrlVis >> lleg.midCtrlViz
    obj.limbMidCtrlVis >> rleg.midCtrlViz

    obj.limbBezierCtrlVis >> larm.bezierCtrlViz
    obj.limbBezierCtrlVis >> rarm.bezierCtrlViz
    obj.limbBezierCtrlVis >> lleg.bezierCtrlViz
    obj.limbBezierCtrlVis >> rleg.bezierCtrlViz

    obj.limbBendCtrlVis >> larm.bendExtraCtrlViz
    obj.limbBendCtrlVis >> rarm.bendExtraCtrlViz
    obj.limbBendCtrlVis >> lleg.bendExtraCtrlViz
    obj.limbBendCtrlVis >> rleg.bendExtraCtrlViz

    obj.lookatCtrlVis >> look.visibility
    obj.lookatIKFK >> look.ikFk

olhoesq='Esquimo_Olho_Esq_source01'

#COPY
objs = pm.ls(sl=True)
for src in ['recept', 'source01', 'source02']:
    newSrc = meshConnect.copyToSource(obj=objs[0], sourceName=src)
    try:
        srcGrp = pm.PyNode(src+'_mesh_grp')
        pm.parent (newSrc, srcGrp)
    except:
        raise
        pass

#HOLD JNTs
for src in ['recept', 'source01', 'source02']:
    jnt = pm.joint(n=src+'Hold_jxt')
    try:
        headJnt = pm.PyNode('head_jnt')
        pos= pm.xform (headJnt, q=True, t=True,ws=True)
        pm.xform(jnt, t=pos, ws=True)
    except:
        pass

    try:
        srcGrp = pm.PyNode (src + '_sys_grp')
        pm.parent (jnt, srcGrp)
    except:
        pass


###Source01
#EYEDIR
ed = lookAt.EyesDir(name='lookAt')
ed.doGuide(eyeball=olhoesq)
headJnt = pm.PyNode('head_jnt')
ed.doRig(upVectorObj=headJnt)
space.addSpc(ed.lookAt_ctrl, ['global', 'head', 'cog'], ed.lookAt_ctrl.getParent())

j = jaw.Jaw(name='jaw')
j.doGuide()
j.doRig()
j.getDict()


#EYELIDS
e = eyelid.EyeLid(name='L_eyeLid', mesh='Esquimo_Cabeca_source01')
f = eyelid.EyeLid(name='R_eyeLid', mesh='Esquimo_Cabeca_source01')

edges = pm.ls(sl=True, fl=True) #selecione um edgeloop
eyeball = pm.PyNode(olhoesq)

e.doGuide(eyeball=eyeball, edgeLoop=edges)
f.doGuide()
f.mirrorConnectGuide(e)

e.getDict()
f.getDict()
e.doGuide(eyeball=eyeball)
f.doGuide()
f.mirrorConnectGuide(e)

e.doRig()
f.doRig()

try:
    LeyeJnt = pm.PyNode('L_eye_jxt')
    ReyeJnt = pm.PyNode('R_eye_jxt')
    Rmulti = pm.PyNode('R_eyeLidmultiFleshy')
    Lmulti = pm.PyNode('L_eyeLidmultiFleshy')
    LeyeJnt.rotate.rotateX >> Lmulti.input1.input1X
    LeyeJnt.rotate.rotateY >> Lmulti.input1.input1Y
    LeyeJnt.rotate.rotateZ >> Lmulti.input1.input1Z

    ReyeJnt.rotate.rotateX >> Rmulti.input1.input1X
    ReyeJnt.rotate.rotateY >> Rmulti.input1.input1Y
    ReyeJnt.rotate.rotateZ >> Rmulti.input1.input1Z
except:
    pass

#EYEBROW
eyebrow = eyeBrows.EyeBrows(name='eyeBrow', sourceObj=['cabeca_neutra', 'sobrancelha_neutra'],
                            targetUp=['cabeca_sobrUp', 'sobrancelha_up'],
                            targetDown=['cabeca_sobrDown', 'sobrancelha_down'])
eyebrow.getDict()
eyebrow.doGuide()
eyebrow.doRig()

#MOUTH CORNERS
m = mouth.MouthBlends(name='mouthCorners')
m.getDict()
m.doGuide()
m.doRig()

targetObj = pm.PyNode('cabecaTargets')
shapes = pm.ls(sl=True)# selecionar os blends da boca e o neutro
m.ccnnectBStoCtrl(targetObj=targetObj, shapes=shapes, splitFalloff=2)
###SOURCE02

##LIPS
l = lips.Lips()

l.doGuide() #selecione um edgeloop
l.doRig()
l.getDict()

#TWEAKS
Lt = tweaks.Tweaks(name='L_squint', num=2, hasMulti=True)
Rt = tweaks.Tweaks(name='R_squint', num=2, hasMulti=True)
Ct = tweaks.Tweaks(name='face', num=2, hasMulti=True)

Lt.doGuide()
Rt.doGuide()
Ct.doGuide()
Rt.mirrorConnectGuide(Lt)

Lt.doRig()
Rt.doRig()
Ct.doRig()

Lt.getDict()
Rt.getDict()


sh = squash.Squash(name='headSquash')
sh.doGuide()
sh.doRig()
sh.getDict()

s = squash.Squash(name='jawSquash')
s.doGuide()
s.doRig()
s.getDict()

#SOCKETS

addHideAtts() #selecionar o controle q vai receber os atributos

allJoints = pm.ls(type='joint')
for j in allJoints:
    j.drawStyle.set(1)

allGeo = pm.ls (type='geometry')
for g in allGeo:





attatchTools.hookOnMesh(mode=3)

import autoRig3.tools.rigFunctions as rigfunctions
rigfunctions.addMultiply()


import lcRigToolbox as tbox
tbox.hookOnCurve()


dirName = os.path.expanduser('~/maya/autoRig3')
if not os.path.exists(dirName):
    os.mkdir(dirName)
path = os.path.join(dirName, 'save3.skin')
models = pm.ls(sl=True)
skin.saveSkinning(path, meshes=models)
logger.debug("saved!!")

dirName = os.path.expanduser('~/maya/autoRig3')
path = os.path.join(dirName, 'save3.skin')
skin.loadSkinning(path)
logger.debug("loaded!!")


import autoRig3.tools.blendShapeTools as split
sel = pm.ls(sl=True)
neutro = sel.pop(-1)
for obj in sel:
    split.splitSidesAPI(obj, neutro, falloff=2)

## TRANSFER UVs
sel = pm.ls(sl=True)
UVtools.transferUVRigged(source=sel[0], target=sel[1])

#CLEAN
import autoRig3.tools.cleanerTools as cleanner
import pymel.core as pm
objs= pm.ls(sl=True)
for obj in objs:
    cleanner.deleteIntermediateShapes(obj)
    cleanner.freezeVertices(obj)
    cleanner.deleteHistory(obj)



#CONNECT
objs = pm.ls(sl=True)
meshConnect.connectSources(source=objs[0], target=objs[1], toFinal=False)
upCrv = pm.polyToCurve(form=2, degree=1, n='UpperCrv', ch=False)[0]
x = pm.rebuildCurve(upCrv, rt=3, rpo=True, d=3, end=1, kr=0, kcp=1, kep=0, kt=0, s=25, tol=0.01, ch=False)[0]


