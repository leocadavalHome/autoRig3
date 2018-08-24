import resetModules
resetModules.resetSessionForScript()

import pymel.core as pm
from autoRig3.modules.footModule import Foot

from autoRig3.modules.handModule import Hand
from autoRig3.modules.chainModule import  Chain
from autoRig3.modules.neckModule import  Neck


import autoRig3.tools.interface as interface
import os.path


x = Neck()
x.doGuide()
x.getDict()



print 'ok'
dirName = os.path.expanduser('~/maya/autoRig3')
if not os.path.exists(dirName):
    os.mkdir(dirName)
path = os.path.join(dirName, 'name.skin')
print path


interface.saveSkinning('Human_BaseMesh1', path)



interface.loadSkinning('Human_BaseMesh1', path)




meshGrp  = pm.PyNode('MESH')
print meshGrp

children = meshGrp.getChildren()
print children