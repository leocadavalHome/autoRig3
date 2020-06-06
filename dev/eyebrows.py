import autoRig3.modules.eyeBrowBlend as eyebrows
import pymel.core as pm

sourceObj = pm.PyNode('corpo_rev')
targetObj = pm.PyNode('corpo_up')

Rmin = pm.PyNode('locator1')
min = pm.PyNode('locator2')
mid = pm.PyNode('locator3')
max = pm.PyNode('locator4')
min2 = pm.PyNode('locator5')
max2 = pm.PyNode('locator6')

RMin = pm.xform(Rmin, ws=True, t=True, q=True)[0]
Xmax = pm.xform(max, ws=True, t=True, q=True)[0]
Xmin = pm.xform(min, ws=True, t=True, q=True)[0]
Xmid = pm.xform(mid, ws=True, t=True, q=True)[0]
Xmin2 = pm.xform(min2, ws=True, t=True, q=True)[0]
Xmax2 = pm.xform(max2, ws=True, t=True, q=True)[0]

target = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=targetObj, sliceMin=RMin, sliceMid=Xmin, sliceMax=Xmin, outName='splitedA')


targetB = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=target, sliceMin=Xmin, sliceMid=Xmin, sliceMax=Xmax, outName='splitedB')
targetC = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=target, sliceMin=Xmin, sliceMid=Xmax, sliceMax=Xmax, outName='splitedC')

L_outTarget1 = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=targetB, sliceMin=Xmin, sliceMid=Xmin, sliceMax=Xmid, outName='L_In')

L_outTarget1a = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=L_outTarget1, sliceMin=Xmin, sliceMid=Xmin, sliceMax=Xmin2, outName='L_In_a')
L_outTarget1b = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=L_outTarget1, sliceMin=Xmin, sliceMid=Xmin2, sliceMax=Xmin2, outName='L_In_b')


L_outTarget2 = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=targetB, sliceMin=Xmin, sliceMid=Xmid, sliceMax=Xmid, outName='L_MidIn')
L_outTarget3 = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=targetC, sliceMin=Xmid, sliceMid=Xmid, sliceMax=Xmax, outName='L_MidOut')

L_outTarget3a = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=L_outTarget3 , sliceMin=Xmid, sliceMid=Xmid, sliceMax=Xmax2, outName='L_MidOut_a')
L_outTarget3b = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=L_outTarget3 , sliceMin=Xmid, sliceMid=Xmax2, sliceMax=Xmax2, outName='L_MidOut_b')

L_outTarget4 = eyebrows.taperSideAPI(sourceObj=sourceObj, targetObj=targetC, sliceMin=Xmid, sliceMid=Xmax, sliceMax=Xmax, outName='L_Out')