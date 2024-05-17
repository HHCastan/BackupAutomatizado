#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Recupera archivos crtiticos de produccion listados en BACKUP.JSON
# Ejecutar en controlador: python2 -X4690shell restore.py
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Octubre de 2016   
#######################################################################

import sys
import os.path
import json
import shutil
import time
import tarfile
import flFuncts

# Varibles:
workDir		= 'm:/respaldo/'						# Carpeta de trabajo
workDirOut	= workDir + 'out/'						# Directorio temporal del respaldo
fecha		= time.strftime("%Y%m%d")				# Fecha actual
jsonFile	= workDir + 'BACKUP.JSON'				# Contiene nombres de objetos a recuperar
errores		= []									# Para manejo de errores
NodoCC		= "ADXLXACN::"							# Archivos en el controlador CC
NodoDD		= "ADXLXADN::"							# Archivos en el controlador DD
tgzFile		= ''									# Archivo empaquetado donde esta el backup
logFileName	= workDir + 'restore'+ fecha + '.log'	# Nombre del archivo para la huella del proceso

# Crea el archivo log, si ya existe lo sobrescribe
logFile = open(logFileName, "w")

# Solicita el nombre del archivo con el backup
while ((not tgzFile) or tgzFile == ''):
	tgzFile = raw_input('Ingrese nombre de backup en formato tgz: ')
	SiNo = raw_input('Ha ingresado: ' + tgzFile + '. Quiere continuar (N/s)? ')
	if((SiNo == '' or SiNo == 'N' or SiNo == 'n') or (SiNo <> 'S' and SiNo <> 's')):
		tgzFile = ''
		continue
	if(not os.path.exists(tgzFile)):
		Enter = raw_input('Archivo no existe. [Enter] para intentar nuevamente')
		tgzFile = ''

print('Nombre arhivo tgz: ' + tgzFile)

# Establece riesgos con el usuario y valida deseo de recuperar el backup:
print('ATENCION: USTED ESTA A PUNTO DE INICIAR UNA ACTIVIDAD DE RECUPERACION')
print('          DE INFORMACION. TODOS LOS DATOS QUE HAYAN SIDO MODIFICADOS')
print('          DESDE LA CREACION DEL BACKUP A RECUPERAR HASTA EL MOMENTO')
print('          SERAN REEMPLAZADOS. USTED DEBE ESTAR SEGURO ANTES DE CONTINUAR.')
SiNo = raw_input('Seguro de que desea recuperar este backup (N/s)? ')
if((SiNo == '' or SiNo == 'N' or SiNo == 'n') or (SiNo <> 'S' and SiNo <> 's')):
	quit()

# Borra el directorio temporal destino
if os.path.exists(workDirOut):
	shutil.rmtree(workDirOut, ignore_errors = 'false')
	logFile.write("Backup previo ha sido borrado: "+ workDirOut + '\n')
else:
	logFile.write("No existe backup previo: " + workDirOut + '\n')

# Desempaquetado de archivos respaldados:
flFuncts.fUnTarBackup(tgzFile, workDir, logFile)

# Verifica existencia del directorio con los archivos a recuperar
if os.path.exists(workDirOut):
	logFile.write("Encontrado directorio: "+ workDirOut + '\n')
else:
	logFile.write("No existe backup a recuperar: " + workDirOut + '\n')
	print("No existe backup a recuperar: " + workDirOut + '\n')
	quit()

# Abre archivo con lista de objetos a recuperar:
with open(jsonFile) as files_file:
	# Carga el archivo en una estructura json en memoria:
	backup = json.load(files_file)

# Inicia recorrido de la coleccion en memoria:
for key, value in backup.iteritems():
	for disco, directorios in value.iteritems():
		logFile.write('Recuperando Disco: ' + disco + ':/ ...\n')
		for directorio, listaArchivos in directorios.iteritems():
			targetDir = disco + ':/' + directorio
			logFile.write('Recuperando Directorio: ' + targetDir + '/ ...\n')
			nodoOrigen = listaArchivos[0]['Nodo']
			sourceDir = workDirOut + listaArchivos[0]['DirTmp']
			
			# Verifica existencia de directorio a recuperar
			if os.path.exists(sourceDir):
				logFile.write('Origen encontrado: ' + sourceDir + ' ...\n')
				flFuncts.fCopyDir(sourceDir, targetDir, logFile, nodoOrigen)
			else:
				logFile.write('Origen no encontrado: ' + sourceDir + ' \n')
				print('Origen no encontrado: ' + sourceDir)
				continue


logFile.write('FINAL RESTORE\n')

# Cierra el archivo log:
logFile.close