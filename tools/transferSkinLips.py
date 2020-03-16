# transferencia de skin dos jxt trans para skin (pivotaveis)

'''
Lock a influencia de todos os jnts da mesh
Selecione os vertices da regiao dos labios (que giram com o roll) e rode o script
'''

import pymel.core as pm
import logging

logger = logging.getLogger('autoRig')

selection = cmds.ls(sl=1, fl=1)

skinNode = pm.ls(pm.listHistory(pm.ls(sl=1, o=1), lv=0, pdo=1),type='skinCluster')[0].name()

lipsSkinJnt = pm.ls('*_*_lips_rbbn_*_trans_jxt')
jntTransList = []
jntSkinList = []
allSkinJntList = []
for jnt in lipsSkinJnt:
    jntSkin = jnt.replace('trans','skin')
    
    jntTransList.append(pm.PyNode(jnt))
    jntSkinList.append(pm.PyNode(jntSkin))
    allSkinJntList.append(jnt)
    allSkinJntList.append(jntSkin)
    
allSkinJntList = jntTransList + jntSkinList

for jnt in lipsSkinJnt:
    jntSkin = jnt.replace('trans','skin')
    
    exceptJntList = list(allSkinJntList)
    currentInfList = [jnt, jntSkin]
    
    exceptJntList.remove(jnt)
    exceptJntList.remove(jntSkin)
    
    for eachJnt in exceptJntList:
        pm.skinCluster (skinNode, e=1, inf=eachJnt, lw=1)
        
    for eachJnt in currentInfList:
        pm.skinCluster (skinNode, e=1, inf=eachJnt, lw=1)

    cmds.skinPercent(skinNode, transformValue=[(str(jntSkin), 1.0), (str(jnt.name()), 0.0)])

    
    
