import pymel.core as pm
import logging

logger = logging.getLogger('autoRig')

def makeGroup (name='group', matrix=None, obj=None, connectToLast=False, coords=None, parent=None, suffix = None):

    if suffix == None:
        sufixo = '_grp'
    else:
        sufixo = suffix

    if not connectToLast:
        pm.select(cl=True)

    grp = pm.group(n=name+sufixo, em=1)

    if obj:
        pm.xform(obj, m=matrix, q=True, ws=True)
        pm.xform(grp, m=matrix, ws=True)

    if matrix:
        pm.xform(grp, m=matrix, ws=True)

    elif coords:
        pm.xform(grp, t=coords[0], ws=1)
        pm.xform(grp, ro=coords[1], ws=1)
        pm.xform(grp, s=coords[2], ws=1)

    if parent:
        grp.setParent(parent)

    return grp

def zeroOut(objList=None, suffix=None):
    if not objList:
        objList = pm.ls(sl=True)

    for obj in objList:
        if pm.nodeType(obj) == 'joint':
            dup = pm.duplicate(obj, rc=1, n=obj[:-3] + "zero")

            try:
                for eachChild in pm.listRelatives (dup[0], c=1):
                    pm.delete (eachChild)
            except:
                pass
            pm.parent(obj, dup[0])
        else:
            parent = obj.getParent()

            if not suffix:
                suffix = '_grp'

            #todo fazer o grupo nao repetir o nome nem deixar o sulfixo
            if obj.endswith(suffix):
                zero = pm.group(em=True, n=obj.nodeName[:-len(suffix)]+'off'+suffix)
            else:
                zero = pm.group(em=True, n=obj+suffix)

            pm.delete(pm.parentConstraint(obj, zero, mo=False))

            pm.parent(obj, zero)

            if parent:
                parent = parent[0]
                pm.parent(zero, parent)

def addMultiply(sel=None):
    if not sel:
        sel = pm.ls (sl=True)

    for obj in sel:
        grp = obj.listRelatives(p=True)[0]
        obj = grp.listRelatives(c=True)[0]
        nm=obj.name()
        off=obj.duplicate (n=nm+'Offset')[0]
        shp=off.getShape()
        pm.delete (shp)
        child=off.listRelatives (c=True)
        pm.delete (child)
        pm.parent (obj, off)
        mlt = pm.createNode ('multiplyDivide')
        mlt.input2.set([-1,-1,-1])
        obj.translate >> mlt.input1
        mlt.output >> off.translate

