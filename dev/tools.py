if not cmds.objExists('CTRL_lr'):
    cmds.createDisplayLayer(name='CTRL_lr', empty=True)
    cmds.setAttr('CTRL_lr.color', 22)

if not selection:
    if not cmds.objExists('MESH_lr'):
        cmds.createDisplayLayer(name='MESH_lr', empty=True)
    if cmds.objExists('MESH'):
        cmds.editDisplayLayerMembers('MESH_lr', 'MESH', noRecurse=True)

    if cmds.objExists('CTRL'):
        cmds.editDisplayLayerMembers('CTRL_lr', 'CTRL', noRecurse=True)

    selection = cmds.ls('*trl')



