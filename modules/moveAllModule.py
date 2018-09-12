import pymel.core as pm
import autoRig3.tools.rigFunctions as rigFunctions
import json


class Moveall:
    """
    cria um moveall com os grupos determinados
        Parametros:
            name (string): nome do personagem
            name (string): nome do personagem
            connType (string): determina se os sistemas ficarao filhos dos controles
                               ou numa pasta separadas ligados por constraint
    """

    def __init__(self, name='character', connType='parent', **kwargs):
        self.name = name
        self.conn = connType
        self.guideMoveall = None
        self.guideSulfix = '_guide'
        self.moveallDict = {'name': self.name,
                            'conn': self.conn,
                            'guideDict': {'moveall': [(0, 0, 0), (0, 0, 0)]}}
        self.moveallGuideDict = {'moveall': [(0, 0, 0), (0, 0, 0)]}
        self.moveallDict['moveallGuideSetup'] = {'nameTempl': self.name + 'MoveAll', 'size': 8,
                                                 'icone': 'circuloPontaY', 'color': (1, 0, 0)}

        self.moveallDict.update(kwargs)
        self.moveallGuideDict.update(self.moveallDict['guideDict'])
        self.moveallDict['guideDict'] = self.moveallGuideDict.copy()

    def doGuide(self, **kwargs):
        self.moveallDict.update(kwargs)
        # self.guideMoveall=pm.group(n=guideName, em=True)
        # self.guideMoveall=pm.circle (n=guideName , c=(0,0,0),nr=(1,0,0), sw=360,r=1 ,d=3,ut=0,ch=0)[0]

        displaySetup = self.moveallDict['moveallGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.guideMoveall = rigFunctions.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', **displaySetup)

        if pm.objExists('GUIDES'):
            self.guideGrp = pm.PyNode('GUIDES')
        else:
            self.guideGrp = pm.group(em=True, n='GUIDES')

        pm.parent(self.guideMoveall, self.guideGrp)

        pm.addAttr(self.guideMoveall, ln='moveallDict', dt='string')
        self.guideMoveall.moveallDict.set(json.dumps(self.moveallDict))

    def getDict(self):
        try:
            cntrlName = self.moveallDict['moveAllCntrlSetup']['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(cntrlName)

            jsonDict = self.guideMoveall.moveallDict.get()
            dictRestored = json.loads(jsonDict)
            self.moveallDict.update(**dictRestored)
            self.movelallDict['guideDict']['moveall'] = rigFunctions.getObjTransforms (self.guideMoveall, 'world')

        except:
            print 'algum nao funcionou'

    def getGuideFromScene(self):
        try:
            guideName = self.moveallDict['moveallGuideSetup']['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(guideName)

            displaySetup = self.moveallDict['moveallGuideSetup'].copy()
            cntrlName = displaySetup['nameTempl'] + self.guideSulfix
            self.guideMoveallCrv = pm.PyNode(cntrlName)
        except:
            print 'algum nao funcionou'

    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()
        if pm.objExists('GUIDES'):
            self.guideGrp = pm.PyNode('GUIDES')
        else:
            self.guideGrp = pm.group(em=True, n='GUIDES')
        if pm.objExists('MOVEALL'):
            self.moveallGrp = pm.PyNode('MOVEALL')
            self.moveallGrp.setParent(w=True)
        else:
            self.moveallGrp = pm.group(em=True, n='MOVEALL')

        if pm.objExists('NOMOVE'):
            self.nomoveGrp = pm.PyNode('NOMOVE')
            self.nomoveGrp.setParent(w=True)
        else:
            self.nomoveGrp = pm.group(em=True, n='NOMOVE')

        if pm.objExists('DATA'):
            self.dataGrp = pm.PyNode('DATA')
            self.dataGrp.setParent(w=True)
        else:
            self.dataGrp = pm.group(em=True, n='DATA')

        if pm.objExists('MESH'):
            self.meshGrp = pm.PyNode('MESH')
            self.meshGrp.setParent(w=True)
        else:
            self.meshGrp = pm.group(em=True, n='MESH')

        if pm.objExists(self.name.upper()):
            pm.delete(self.name.upper())

        self.moveall3 = rigFunctions.cntrlCrv(name=self.name + 'Moveall3', icone='circuloPontaY', size=10)
        self.moveall2 = rigFunctions.cntrlCrv(name=self.name + 'Moveall2', icone='circuloPontaY', size=8)
        self.moveall = rigFunctions.cntrlCrv(name=self.name + 'Moveall', icone='circuloPontaY', size=6)

        self.moveall.getParent().setParent(self.moveall2)
        self.moveall2.getParent().setParent(self.moveall3)

        # aqui ver se eh melhor ter o o grupo MOVEALL na pasta DATA ou filho dos controles moveall
        # por default vai
        self.nomoveGrp.setParent(self.dataGrp)
        rigGrp = pm.group(self.moveall3.getParent(), self.dataGrp, self.meshGrp, n=self.name.upper())

        if self.conn == 'parent':
            self.moveallGrp.setParent(self.moveall)
        else:
            self.moveallGrp.setParent(self.dataGrp)

        self.guideGrp.visibility.set(0)