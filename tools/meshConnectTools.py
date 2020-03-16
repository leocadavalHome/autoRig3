import pymel.core as pm
import logging

logger = logging.getLogger('autoRig')

def getIntermediateObj(obj):
    geos = obj.getShapes()
    for geo in geos:
        if geo.isIntermediate() and pm.connectionInfo(geo + '.worldMesh[0]', isSource=True):
            return geo

#todo melhorar algoritmo de adicao de sources
def copyToSource(obj=None, sourceName='recept'):
    baseName = obj.nodeName().split('_grp')[0]
    newSource = pm.duplicate(obj, n=baseName + '_' + sourceName + '_grp')[0]
    children = newSource.listRelatives(ad=True, type='transform')
    for child in children:
        newName = child.nodeName().replace('_grp', '_' + sourceName + '_grp')
        newName2 = newName.replace('_geo', '_' + sourceName)
        pm.rename(child, newName2)
    return newSource

def connectSources(source=None, target=None, toFinal=False):
    sourceChildren = source.listRelatives(ad=True, type='transform')
    targetChildren = target.listRelatives(ad=True, type='transform')

    sourceName = source.nodeName().split('_')[-1]
    if sourceName == 'grp':
        sourceName = source.nodeName().split('_')[-2]

    if toFinal:
        targetName = 'geo'
    else:
        targetName = target.nodeName().split('_')[-1]
        if targetName == 'grp':
            targetName = target.nodeName().split('_')[-2]

    log = []
    for sourceChild in sourceChildren:
        if sourceChild.getShape():
            try:
                targetNodeName = sourceChild.nodeName().replace(sourceName, targetName)
                targetChild = pm.PyNode(targetNodeName)
            except:
                print 'Nao achou o shape para conectar', targetNodeName
                log.append(targetNodeName)

            sourceChildShape = sourceChild.getShape()
            targetChildShapeOrig = getIntermediateObj(targetChild)

            print sourceChildShape, targetChildShapeOrig

            sourceChildShape.outMesh >> targetChildShapeOrig.inMesh
