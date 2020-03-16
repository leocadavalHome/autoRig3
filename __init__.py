from maya import cmds
import autoRig3.ui.old.bipedRigUI as win

def autoRigWin():
    print 'init autoRig v3.1.5'
    a = win.BipedAutoRigUI()
    a.createWindow()

def popoToolsAutoRun():
    pass

def popoToolsMenu(mainMenu):
    if cmds.menuItem('autoRig3_menu', ex=True):
        return

    cmds.menuItem( 'autoRig3_menu', label='AutoRig3', subMenu=True, tearOff=True, parent=mainMenu )

    cmds.menuItem( 'autoRig3UI_menu', label='AutoRig3 window',
                   c='import autoRig3.ui.autoRigUI as autoRigUI;win = autoRigUI.autoRig3UI()win.dock.show()')

if __name__ == "__main__":
    print 'init autoRig v3.0.0'
    a = win.BipedAutoRigUI()
    a.createWindow()