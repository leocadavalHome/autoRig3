import autoRig3.ui.dockWidget as dock
import autoRig3.ui.bodyRigUI as bodyRigUI
import autoRig3.ui.facialRigUI as facialRigUI
import autoRig3.ui.renamingUI as renamingUI
import autoRig3.ui.skinUI as skinUI
import autoRig3.ui.controlsUI as controlsUI
import autoRig3.ui.transformsUI as transformsUI
import autoRig3.ui.sourcesUI as sourcesUI

dock.createDock(bodyRigUI.BodyRigUI)
dock.createDock(facialRigUI.FacialRigUI)
dock.createDock(renamingUI.RenamingUI)
dock.createDock(skinUI.SkinUI)
dock.createDock(controlsUI.ControlsUI)
dock.createDock(transformsUI.TransformsUI)
dock.createDock(sourcesUI.SourcesUI)


print 'try:\n\tdock.createWidget()\nexcept:\n\tpass'.format()