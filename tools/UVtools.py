import pymel.core as pm
import logging

logger = logging.getLogger('autoRig')

def transferUVRigged(source, target, mode=3):
    shapes = pm.listRelatives(target, s=1, c=1, f=1)
    shapeOrig = None
    for shp in shapes:
        if pm.getAttr(shp + '.intermediateObject') and pm.listConnections(shp):
            shapeOrig = shp
    if shapeOrig:
        pm.setAttr(shapeOrig + '.intermediateObject', 0)
        pm.transferAttributes(source, shapeOrig, transferPositions=0, transferNormals=0,
                              transferUVs=1, transferColors=0, sampleSpace=mode,
                              searchMethod=3, flipUVs=0, colorBorders=1)
        pm.delete(shapeOrig, ch=1)
        pm.setAttr(shapeOrig + '.intermediateObject', 1)
    else:
        pm.transferAttributes(source, target, transferPositions=0, transferNormals=0,
                              transferUVs=1, transferColors=0, sampleSpace=mode,
                              searchMethod=3, flipUVs=0, colorBorders=1)
        pm.delete(target, ch=1)
    print 'transfer done!'

