import pymel.core as pm

class AimTwistDivider:
    """
        Cria um sistema q orienta o grupo mid segundo a posicao e twist de start e end.
        fazendo a media
        Limitado a 180 graus
        Parametros:
            start:
            mid:
            end:

    """

    ##IMPLEMENTAR:
    # todo outras orientacoes. Atualmente somente X down

    def __init__(self, start=None, end=None, mid=None):
        if not start:
            self.start = pm.group(em=True, n='start')
        else:
            self.start = start
        if not end:
            self.end = pm.group(em=True, n='end')
        else:
            self.end = end
        if not mid:
            self.mid = pm.group(em=True, n='mid')
        else:
            self.mid = mid
            # cria nodes
        vecProd1 = pm.createNode('vectorProduct')
        vecProd2 = pm.createNode('vectorProduct')
        vecProd3 = pm.createNode('vectorProduct')
        vecProd4 = pm.createNode('vectorProduct')
        add1 = pm.createNode('plusMinusAverage')
        add2 = pm.createNode('plusMinusAverage')
        matrix4by4 = pm.createNode('fourByFourMatrix')
        decomposeMatrix1 = pm.createNode('decomposeMatrix')
        decomposeMatrix2 = pm.createNode('decomposeMatrix')
        decomposeMatrix3 = pm.createNode('decomposeMatrix')
        decomposeMatrix3 = pm.createNode('decomposeMatrix')
        multiMatrix = pm.createNode('multMatrix')

        # ver se funciona so com worldMatrix
        self.start.worldMatrix[0] >> vecProd1.matrix
        vecProd1.input1.set((0, 1, 0))
        vecProd1.operation.set(3)
        self.end.worldMatrix[0] >> vecProd2.matrix
        vecProd2.input1.set((0, 1, 0))
        vecProd2.operation.set(3)

        vecProd1.output >> add1.input3D[0]
        vecProd2.output >> add1.input3D[1]
        add1.operation.set(1)

        self.start.worldMatrix[0] >> decomposeMatrix1.inputMatrix
        decomposeMatrix1.outputTranslate >> add2.input3D[1]

        self.end.worldMatrix[0] >> decomposeMatrix2.inputMatrix
        decomposeMatrix2.outputTranslate >> add2.input3D[0]
        add2.operation.set(2)

        add1.output3D >> vecProd3.input2
        add2.output3D >> vecProd3.input1
        vecProd3.operation.set(2)

        vecProd3.output >> vecProd4.input1
        add2.output3D >> vecProd4.input2
        vecProd4.operation.set(2)

        add2.output3Dx >> matrix4by4.in00
        add2.output3Dy >> matrix4by4.in01
        add2.output3Dz >> matrix4by4.in02

        vecProd4.outputX >> matrix4by4.in10
        vecProd4.outputY >> matrix4by4.in11
        vecProd4.outputZ >> matrix4by4.in12

        matrix4by4.output >> multiMatrix.matrixIn[0]
        self.mid.parentInverseMatrix[0] >> multiMatrix.matrixIn[1]
        multiMatrix.matrixSum >> decomposeMatrix3.inputMatrix

        decomposeMatrix3.outputRotate >> self.mid.rotate
        pm.pointConstraint(self.start, self.end, self.mid, mo=False)
