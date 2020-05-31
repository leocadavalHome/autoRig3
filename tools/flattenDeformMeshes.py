
import pymel.core as pm
import logging

logger = logging.getLogger('autoRig')

def findSource(obj):
    objErrorList = []
    history = pm.listHistory(obj, il=2, pdo=1)
    source = None
    vtxNum = len(obj.vtx)

    for deform in history:
        blendShape = None
        compatibleConnections = []

        if isinstance(deform, pm.nodetypes.BlendShape):
            blendShape = deform
            connections = pm.listConnections(blendShape,  type=pm.nodetypes.Mesh, )
            if len(connections) == 1: # so existe um source no blendshape
                source = connections[0]
            else:
                for connection in connections:
                    if len(connection.vtx) == vtxNum:
                        print 'a mesh ', connection, 'eh compativel com ', obj
                        compatibleConnections.append(connection)

                if len(compatibleConnections) == 1: # so existe uma conexao compativel:
                    source = compatibleConnections[0]

                elif len(compatibleConnections) == 0:
                    pm.warning ('nao existem itens compativeis no node de blendshape encontrado')

                elif len(compatibleConnections) > 1:
                    pm.warning ('existe mais de um item compativel no node de blendshape encontrado')
                    # comparando nomes:
                    print '>> Item selecionado: \n>>>',obj
                    objPrefix = obj.split('_geo')[0]
                    print '>> Nome para comparacao: \n>>>',objPrefix
                    for compatibleObj in compatibleConnections:
                        print '>> Comparando com: \n>>>',compatibleObj
                        if str(objPrefix) in str(compatibleObj):
                            source = compatibleObj
                            print '>>>> Item ',source, ' OK <<<<'
                    if not source:
                        pm.warning('nao existe item compativel. Comparacao: objOrig', obj, 'itens compativeis: ',
                                   compatibleConnections)



    return source

def mergeInputSource():
    lista = pm.ls(sl=1)
    listaError = []
    for sel in lista:
        itemList = []
        if sel.getShape():
            itemList.append(sel)
        else:
            print 'Um grupo selecionado'
            itensIntoSel = pm.listRelatives(ad=1, ni=1, s=0, typ='transform')
            for itemInto in itensIntoSel:
                if itemInto.getShape():
                    itemList.append(itemInto)

        for item in itemList:
            itemShape = None
            itemShapes = pm.listRelatives(item, s=1, c=1, f=1)
            for shape in itemShapes:
                if pm.getAttr(shape + '.intermediateObject') and pm.listConnections(shape):
                    itemShape = shape

            source = findSource(item)
            if source:
                sourceShape = source.getShape()
                print '> conectando', item, 'com', source
                print 'item: ', item
                print 'itemShape: ', itemShape
                print 'source: ', source
                print 'sourceShape', sourceShape

                sourceShape.outMesh >> itemShape.inMesh
                print ' ----------- # ----------- # ----------- '
            else:
                listaError.append(item)

    if listaError:
        print '>>> Nao foi possivel conectar os itens:'
        for each in listaError:
            print '>  ',each

mergeInputSource()