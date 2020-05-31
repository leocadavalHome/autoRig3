import pymel.core as pm
import logging

logger = logging.getLogger('autoRig')

def makeJoint(name='joint', matrix=None, obj=None, connectToLast=False,
              jntSulfix='', hasZero=False, coords=None, scaleCompensate=True,
              label=None):

    if not connectToLast:
        pm.select(cl=True)

    if hasZero:
        zeroJnt = pm.joint(n=name+'Zero')

    jnt = pm.joint(n=name+jntSulfix)

    if obj:
        t = pm.xform(obj, t=True, q=True, ws=True)
        ro = pm.xform(obj, ro=True, q=True, ws=True)
        if hasZero:
            pm.xform(zeroJnt, t=t, ro=ro, ws=True)
        else:
            pm.xform(jnt, t=t, ro=ro, ws=True)

    if matrix:
        if hasZero:
            pm.xform(zeroJnt, m=matrix, ws=True)
        else:
            pm.xform(jnt, m=matrix, ws=True)
    elif coords:
        pm.xform(jnt, t=coords[0], ws=1)
        pm.xform(jnt, ro=coords[1], ws=1)
        pm.xform(jnt, s=coords[2], ws=1)

    if label:
        '''
        Precisa estar no padrao: (side(str), otherType(str))
        side: 'center', 'left' ou 'right'
        otherType: 'label_name'

        Automaticamente o script seta:
        type: 18(Other)
        side: middle: 0  | left: 1  | right: 2
        '''

        if label[0] == 'middle':
            side = 0
        elif label[0] == 'left':
            side = 1
        elif label[0] == 'right':
            side = 2
        else:
            pm.warning('label side nao reconhecido.')

        labelName = label[1]
        pm.setAttr(jnt + '.side', side)
        pm.setAttr(jnt + '.type', 18)
        pm.setAttr(jnt + '.otherType', labelName, type="string")

    pm.makeIdentity(jnt, apply=True, r=1, t=0, s=0, n=0, pn=0)

    if hasZero:
        pm.makeIdentity(zeroJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)

    return jnt


def zeroJoints(jointsList=None):
    if not jointsList:
        jointsList = pm.ls(sl=1)

    for eachJnt in jointsList:
        dup = pm.duplicate(eachJnt, rc=1, n=eachJnt[:-3]+"zero")

        try:
            for eachChild in pm.listRelatives(dup[0], c=1):
                pm.delete(eachChild)
        except:
            pass
        pm.parent(eachJnt, dup[0])

