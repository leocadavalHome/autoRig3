import pymel.core as pm
import logging

logger = logging.getLogger('autoRig')

def attachObj(obj, mesh, u, v, follOn, mode=1):
    rivetGrpName = follOn
    if not pm.objExists(rivetGrpName):
        pm.group(n=rivetGrpName, em=1)

    foll = pm.createNode('follicle')
    follDag = foll.firstParent()
    follDag.setParent(rivetGrpName)

    mesh.worldMatrix[0] >> foll.inputWorldMatrix
    meshShape = pm.listRelatives(mesh, s=True)[0]
    if pm.objectType(meshShape) == 'mesh':
        mesh.outMesh >> foll.inputMesh
    else:
        mesh.local >> foll.inputSurface

    foll.outTranslate >> follDag.translate
    foll.outRotate >> follDag.rotate
    follDag.translate.lock()
    follDag.rotate.lock()
    follDag.parameterU.set(u)
    follDag.parameterV.set(v)
    if mode == 1:
        pm.parent(obj, follDag)
    elif mode == 2:
        pm.parentConstraint(follDag, obj, mo=True)
    elif mode == 3:
        pm.pointConstraint(follDag, obj, mo=True)
    elif mode == 4:
        pm.parentConstraint(follDag, obj, mo=False)
    return follDag

def hookOnMesh(inputs=None, mode=3, follOn='vzRivet_grp'):
    '''
    gruda um objeto sobre a mesh.
    Trabalha com uma lista via selecao ou parametro inputs (o parametro eh prioridade)

    :param inputs:
    Lista com os objetos a serem grudados na mesh
    O ultimo objeto da lista deve ser a mesh.

    :param mode:
    1 - parent
    2 - parentConstraint (maintainOffset = True)
    3 - pointConstraint  (maintainOffset = True)
    4 - parentConstarint (maintainOffset = False)
    :return:
    '''

    if inputs:
        sel = inputs
    else:
        sel = pm.ls(sl=True)

    if sel == []:
        pm.warning('Nao foram passados objetos para hookOnMesh')
        return

    mesh = sel[-1]
    meshShape = pm.listRelatives(mesh, s=True)[0]
    if pm.objectType(meshShape) == 'mesh':

        cpom = pm.createNode('closestPointOnMesh')
        sampleGrpA = pm.group(empty=True)
        meshShape.worldMesh >> cpom.inMesh
    else:

        cpom = pm.createNode('closestPointOnSurface')
        sampleGrpA = pm.group(empty=True)
        meshShape.worldSpace[0] >> cpom.inputSurface

        uRange = meshShape.minMaxRangeU.get()
        vRange = meshShape.minMaxRangeV.get()

        uSize = uRange[1] - uRange[0]
        vSize = vRange[1] - vRange[0]

    sampleGrpA.translate >> cpom.inPosition
    pm.parent(sampleGrpA, mesh)

    for obj in sel[:-1]:
        # objShape = obj.getShape()[0]
        pos = pm.xform(obj, q=True, ws=True, rp=True)
        pm.xform(sampleGrpA, ws=True, t=pos)

        if pm.objectType(meshShape) == 'mesh':
            closestU = cpom.parameterU.get()
            closestV = cpom.parameterV.get()
        else:
            closestU = (cpom.parameterU.get() - uRange[0] ) / uSize
            closestV = (cpom.parameterV.get() - vRange[0] ) / vSize

        foll = attachObj(obj, mesh, closestU, closestV, follOn, mode)

    pm.delete(cpom, sampleGrpA)

    return foll

def hookOnCurve(mode=1, tangent = False):
    sel = pm.ls (sl=True)
    crv=sel[-1]
    sampleNPoC = pm.createNode ('nearestPointOnCurve')
    sampleGrpA  = pm.group (empty=True)
    crv.worldSpace[0] >> sampleNPoC.inputCurve
    sampleGrpA.translate >> sampleNPoC.inPosition

    for obj in sel[:-1]:
        wp= pm.xform (obj, t=True, ws=True, q=True)
        pm.xform (sampleGrpA, t=wp, ws=True)
        hookPar = sampleNPoC.parameter.get()
        if mode==1:
            hookPoci = pm.createNode ('pointOnCurveInfo')
            crv.worldSpace[0] >> hookPoci.inputCurve
            hookPoci.position >> obj.translate
            hookPoci.parameter.set(hookPar)
            if tangent:
                pm.tangentConstraint (crv, obj, aimVector=(-1, 0, 0),upVector=(0,1, 0),worldUpType="vector",worldUpVector =(0, 1, 0))
        elif mode==2:
            mpathName = pm.pathAnimation(obj, c=crv)
            mpath = pm.PyNode(mpathName)
            deleteConnection(mpath.uValue)
            mpath.uValue.set(hookPar)
    pm.delete (sampleNPoC, sampleGrpA)

def deleteConnection(plug):
	if pm.connectionInfo(plug, isDestination=True):
		plug = pm.connectionInfo(plug, getExactDestination=True)
		readOnly = pm.ls(plug, ro=True)
		#delete -icn doesn't work if destination attr is readOnly
		if readOnly:
			source = pm.connectionInfo(plug, sourceFromDestination=True)
			pm.disconnectAttr(source, plug)
		else:
			pm.delete(plug, icn=True)
