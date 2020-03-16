import pymel.core as pm
import logging

logger = logging.getLogger('autoRig')

def freezeVertices(obj):
    meshes = obj.getShapes()

    for mesh in meshes:
        if mesh.isIntermediate():
            continue
        try:
            hasTrasnforms = mesh.getAttr('pnts', mi=True)
            if len(hasTrasnforms) > 1:
                pm.polyMoveVertex(mesh)
                pm.delete(mesh, ch=True)
                pm.select(cl=True)
        except:
            print('freeze vertices fail')
            return None
    return obj

def deleteHistory(obj):
    try:
        geos = obj.getShapes()
        pm.delete(geos, ch=True)
    except:
        return None

    return obj

def deleteIntermediateShapes(obj):
    geos = obj.getShapes()

    for geo in geos:
        if geo.isIntermediate():
            cntWMAux = pm.connectionInfo(geo + '.worldMesh[0]', isSource=True)
            if not cntWMAux:
                pm.delete(geo)
    return obj
