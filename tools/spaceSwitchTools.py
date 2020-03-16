import pymel.core as pm
import logging

logger = logging.getLogger('autoRig')

def createSpc(driver=None, name=None, type=None):
    drvGrp = pm.group(empty=True, n=name + '_drv')
    pos = pm.xform(driver, q=True, ws=True, t=True)
    pm.xform(drvGrp, t=pos, ws=True)

    if driver:
        pm.parentConstraint(driver, drvGrp, mo=True)
    spcGrp = pm.group(empty=True, n=name + '_spc')
    pm.parent(spcGrp, drvGrp)
    if not pm.objExists('spaces'):
        spcs = pm.group(name + '_drv', n='spaces')
        if not pm.objExists('MOVEALL'):
            pm.group(spcs, n='MOVEALL')
        else:
            pm.parent(spcs, 'MOVEALL')
    else:
        pm.parent(name + '_drv', 'spaces')

def addSpc(target, spaceList, switcher, type='parent', posSpc=None):
    for space in spaceList:
        if type == 'parent':
            cns = pm.parentConstraint(space + '_spc', switcher, mo=True)
        elif type == 'orient':
            cns = pm.orientConstraint(space + '_spc', switcher, mo=True)
            if posSpc:
                pm.pointConstraint(posSpc, switcher, mo=True)
            else:
                pm.pointConstraint(target.getParent(2), switcher, mo=True)

        if target.hasAttr('spcSwitch'):
            enumTxt = target.spcSwitch.getEnums()
            connects = target.spcSwitch.connections(d=True, s=False, p=True)
            index = len(enumTxt.keys())
            enumTxt[space] = index
            target.deleteAttr('spcSwitch')
            target.addAttr('spcSwitch', at='enum', en=enumTxt, k=True)
            if connects:
                for c in connects:
                    target.spcSwitch >> c
        else:
            target.addAttr('spcSwitch', at='enum', en=space, k=True)
            index = 0

        cond = pm.createNode('condition', n=switcher + space + 'Cond')
        target.spcSwitch >> cond.firstTerm
        cond.secondTerm.set(index)
        cond.operation.set(0)
        cond.colorIfTrueR.set(1)
        cond.colorIfFalseR.set(0)
        cond.outColor.outColorR >> cns.attr(space + '_spcW' + str(index))