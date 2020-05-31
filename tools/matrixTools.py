import pymel.core as pm
import maya.api.OpenMaya as om
import logging

logger = logging.getLogger('autoRig')

def orientMatrix(mvector, normal, pos, axis):
    '''
    funcao q devolve uma matriz apartir dos
    
    :param mvector:
    :param normal:
    :param pos:
    :param axis:
    :return:
    '''

    # criando a matriz do conforme a orientacao dada pela direcao AB, pela normal e na posicao pos
    AB = mvector
    nNormal = normal.normal()
    A = pos
    x = nNormal ^ AB.normal()
    t = x.normal() ^ nNormal

    if axis == 'Y':
        list = [nNormal.x, nNormal.y, nNormal.z, 0, t.x, t.y, t.z, 0, x.x, x.y, x.z, 0, A.x, A.y, A.z, 1]
    elif axis == 'Z':
        list = [x.x, x.y, x.z, 0, nNormal.x, nNormal.y, nNormal.z, 0, t.x, t.y, t.z, 0, A.x, A.y, A.z, 1]
    else:
        list = [t.x, t.y, t.z, 0, nNormal.x, nNormal.y, nNormal.z, 0, x.x * -1, x.y * -1, x.z * -1, 0, A.x, A.y, A.z, 1]
    m = om.MMatrix(list)
    return m

def composeMMatrix(vecX, vecY, vecZ, vecP):
    list = [vecX.x, vecX.y, vecX.z, 0, vecY.x, vecY.y, vecY.z, 0, vecZ.x, vecZ.y, vecZ.z, 0, vecP.x, vecP.y, vecP.z, 1]
    m = om.MMatrix(list)
    return m

def twistExtractor(name='twistExtractor', parent=None, child=None, param=None):
    multiMatrix = pm.createNode('multMatrix', n=name+'MultiMatrix')
    decomposeMatrix = pm.createNode('decomposeMatrix', n=name+'DecomposeMatrix')
    quatToEuler = pm.createNode('quatToEuler', n=name+'QuatToEuler')

    child.worldMatrix[0] >> multiMatrix.matrixIn[0]
    parent.worldInverseMatrix[0] >> multiMatrix.matrixIn[1]
    multiMatrix.matrixSum >> decomposeMatrix.inputMatrix

    decomposeMatrix.outputQuatX >> quatToEuler.inputQuatX
    decomposeMatrix.outputQuatW >> quatToEuler.inputQuatW

    quatToEuler.outputRotateX >> param


# todo matrix connect