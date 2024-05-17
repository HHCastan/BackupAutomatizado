#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Respalda archivos crtiticos de produccion
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Junio de 2016   
#
#######################################################################

import sys
import os.path
import shutil
import json

bkDirs=['idt1', 'idt4', 'ipgm', 'upgm']

idt1_ListFiles=[
	'ufpar001'
	,'ufpar002'
	,'ufpar003'
	,'ufpar004'
	,'ufpar005'
	,'ufpar189'
	,'ufpar902'
	,'ufpar953'
	]

idt4_ListFiles=[
	'eamtrana.dat'
	,'eamtranb.dat'
	]

ipgm_ListFiles=[
	'svuser.dat'
	,'eamts10l.286'
	]

upgm_ListFiles=[
	'udsainfo.sym'
	,'eamts10l.sym'
	]


for dirName in bkDirs:
	srcDir='c:/adx_' + dirName + '/'
	tgtDir='c:/respaldo/' + dirName + '/'

	print("Procesando Directorio: " + srcDir + "\n" )

	if os.path.exists(tgtDir):
		pass
	else:
		os.makedirs(tgtDir, 0750)

	for fileName in idt1_ListFiles:
		fileIn=srcDir + fileName
		fileOut=tgtDir + fileName
		if os.file.exists(fileIn)
			#shutil.copy2(fileIn, fileOut)
			print("Copia " + fileIn + " sobre " + fileOut)
