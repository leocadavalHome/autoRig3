import pymel.core as pm
import autoRig3.tools.controlTools as controlTools
import json
import logging

logger = logging.getLogger('autoRig')

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
        self.toExport = {'name', 'guideDict', 'moveallGuideSetup', 'moveAllCntrlSetup', 'moveAll2CntrlSetup',
                         'moveAll3CntrlSetup'}

        self.guideDict = {'moveall': [(0, 0, 0), (0, 0, 0), (1, 1, 1)]}
        self.moveallGuideSetup = {'nameTempl': self.name + 'MoveAll', 'size': 8,
                                  'icone': 'circuloPontaY', 'color': (1, 0, 0)}
        self.moveAllCntrlSetup = {'nameTempl': self.name + 'MoveAll', 'icone': 'circuloX',
                                  'color': (1, 1, 0), 'size': 6}
        self.moveAll2CntrlSetup = {'nameTempl': self.name + 'MoveAll2', 'icone': 'circuloX',
                                  'color': (1, 1, 0), 'size': 8}
        self.moveAll3CntrlSetup = {'nameTempl': self.name + 'MoveAll3', 'icone': 'circuloX',
                                  'color': (1, 1, 0), 'size': 10}

        self.sources = {'recept', 'source01', 'source02', 'modeled'}
        self.moveall3 = None
        self.moveall2 = None
        self.moveall = None

    def setCntrl (self, cntrl, posRot, space='object'):
        cntrl.setTranslation(self.guideDict[posRot][0], space=space)
        cntrl.setRotation(self.guideDict[posRot][1], space=space)

        # Felipe --> condicao para setar valor de escala no moveall dos limbs
        try:
            cntrl.setScale(self.guideDict[posRot][2])

        except:
            pass

    def exportDict(self):
        expDict = {}
        for key in self.toExport:
                expDict[key] = self.__dict__[key]
        return expDict


    def doGuide(self, **kwargs):
        self.__dict__.update(kwargs)
        # self.guideMoveall=pm.group(n=guideName, em=True)
        # self.guideMoveall=pm.circle (n=guideName , c=(0,0,0),nr=(1,0,0), sw=360,r=1 ,d=3,ut=0,ch=0)[0]

        displaySetup = self.moveallGuideSetup.copy()
        cntrlName = displaySetup['nameTempl'] + self.guideSulfix

        if pm.objExists(cntrlName):
            pm.delete(cntrlName)

        self.guideMoveall = controlTools.cntrlCrv(name=cntrlName, hasZeroGrp=False, cntrlSulfix='', **displaySetup)

        if pm.objExists('GUIDES'):
            self.guideGrp = pm.PyNode('GUIDES')
        else:
            self.guideGrp = pm.group(em=True, n='GUIDES')

        self.setCntrl(self.guideMoveall, 'moveall', space='world')

        pm.parent(self.guideMoveall, self.guideGrp)

        pm.addAttr(self.guideMoveall, ln='moveallDict', dt='string')
        self.guideMoveall.moveallDict.set(json.dumps(self.exportDict()))


    def getDict(self):
        try:
            cntrlName = self.moveallGuideSetup['nameTempl'] + self.guideSulfix
            self.guideMoveall = pm.PyNode(cntrlName)

            jsonDict = self.guideMoveall.moveallDict.get()
            dictRestored = json.loads(jsonDict)

            self.__dict__.update(**dictRestored)

            self.guideDict['moveall'][0] = self.guideMoveall.getTranslation(space='world').get()
            self.guideDict['moveall'][1] = tuple(self.guideMoveall.getRotation(space='world'))
            self.guideDict['moveall'][2] = tuple(self.guideMoveall.getScale())
        except:
            pass

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

        if pm.objExists('HAIR_GUIDES'):
            self.hairGrp = pm.PyNode('HAIR_GUIDES')
            self.hairGrp.setParent(w=True)
        else:
            self.hairGrp = pm.group(em=True, n='HAIR_GUIDES')

        if pm.objExists('constrained_grp'):
            self.constrainedGrp = pm.PyNode('constrained_grp')
            self.constrainedGrp.setParent(w=True)
        else:
            self.constrainedGrp = pm.group(em=True, n='constrained_grp')

        if pm.objExists('blendshapes_grp'):
            self.blendshapesGrp = pm.PyNode('blendshapes_grp')
            self.blendshapesGrp.setParent(w=True)
        else:
            self.blendshapesGrp = pm.group(em=True, n='blendshapes_grp')

        for source in self.sources:
            if pm.objExists(source):
                self.sourcesGrp = pm.PyNode(source+'_grp')
                self.sourcesGrp.setParent(w=True)
            else:
                self.sourcesGrp = pm.group(em=True, n=source+'_grp')
                self.sourcesMeshGrp = pm.group(em=True, n=source+'_mesh_grp')
                self.sourcesSysGrp = pm.group(em=True, n=source+'_sys_grp')
                pm.parent(self.sourcesMeshGrp, self.sourcesSysGrp, self.sourcesGrp)
                pm.parent(self.sourcesGrp, self.blendshapesGrp)


        if pm.objExists('MESH'):
            self.meshGrp = pm.PyNode('MESH')
            self.meshGrp.setParent(w=True)
        else:
            self.meshGrp = pm.group(em=True, n='MESH')

        if pm.objExists('proxies'):
            self.proxies = pm.PyNode('proxies')
            self.proxies.setParent(w=True)
        else:
            self.proxies = pm.group(em=True, n='proxies')

        if pm.objExists(self.name.upper()):
            pm.delete(self.name.upper())

        self.moveall3 = controlTools.cntrlCrv(name=self.name + '_moveall3', icone='circuloY', size=10)
        self.moveall2 = controlTools.cntrlCrv(name=self.name + '_moveall2', icone='circuloY', size=8)
        self.moveall = controlTools.cntrlCrv(name=self.name + '_moveall', icone='circuloY', size=6)

        self.moveall.getParent().setParent(self.moveall2)
        self.moveall2.getParent().setParent(self.moveall3)

        # aqui ver se eh melhor ter o o grupo MOVEALL na pasta DATA ou filho dos controles moveall
        # por default vai
        self.nomoveGrp.setParent(self.dataGrp)
        pm.parent(self.nomoveGrp, self.constrainedGrp, self.blendshapesGrp, self.hairGrp, self.dataGrp)
        rigGrp = pm.group( self.meshGrp, self.dataGrp, self.moveall3.getParent(), self.proxies, n=self.name.upper())

        if self.conn == 'parent':
            self.moveallGrp.setParent(self.moveall)
        else:
            self.moveallGrp.setParent(self.dataGrp)

        self.guideGrp.visibility.set(0)