# transfer input history
'''
1 - Selecione o source e adicione o target(s) a selecao
2 - Rode o script
'''

import maya.cmds as cmds
import maya.mel as mel
import logging

logger = logging.getLogger('autoRig')

def transferInputHistory():
    selection = cmds.ls(sl=1)
    if selection:
        source = selection[0]
        deformers = cmds.listHistory(source, pdo=1, il=2)
        deformers.reverse()

        for target in selection[1:]:
            for e, deformer in enumerate(deformers[1:]):
                if cmds.nodeType(deformer) == 'skinCluster':
                    skinningMethod = cmds.getAttr(deformer + '.skinningMethod')
                    transferSkin([source, target], skinningMethod)
                else:
                    cmds.deformer(deformer, e=True, g=target, ex=e)

    ##### Falta fazer:
    # - Copiar mapa do deformador original, como de delta mush
    # - Se o input for blendshape, nao usar deformer, criar um node com os blends originais

def copySkin(sel):
    if sel:
        source = sel[0]
        dest = sel[1:]

        for d in dest:
            cmds.copySkinWeights(source, d, noMirror=True, surfaceAssociation='closestPoint',
                                 influenceAssociation='oneToOne')
        cmds.select(sel[1:])
        mel.eval('removeUnusedInfluences')

def transferSkin(sel, skinningMethod):

    if len(sel) > 1:
        source = sel[0]
        dest = sel[1:]

        infs = cmds.skinCluster(source, query=True, influence=True)
        if not infs:
            print 'Source object "' + source + '" does not have influences attached!'
        else:
            for d in dest:
                cmds.select(infs, d)
                cmds.skinCluster(toSelectedBones=1, normalizeWeights=1, rui=0, sm=skinningMethod)
            cmds.select(source, dest)
            copySkin(sel)

    else:
        print 'Please select at least ONE source object and ONE destination object.'
