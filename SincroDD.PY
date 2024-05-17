#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Actualiza el DD con archivos crtiticos de produccion listados en Sincro.JSON
# Ejecutar en controlador: python2 -X4690shell SincroDD.py
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Junio de 2016   
# TO DO: Si el origne es DD, primero se copia al CC

#######################################################################

import sys
import os.path
import json
import time
import shutil
import flFuncts
import tarfile
import ConfigParser

workDir     = 'm:/respaldo/'
fecha		= time.strftime("%Y%m%d")				# Fecha actual
hora		= time.strftime("%H%M%S")				# Hora actual
dia			= time.strftime("%A")					# Dia de la semana
jsonFile	= 'm:/respaldo/Sincro.JSON'				# Contiene nombres de objetos a sincronizar
errores		= []									# Para manejo de errores
NodoCC		= "ADXLXACN::"							# Archivos en el controlador CC
NodoDD		= "ADXLXADN::"							# Archivos en el controlador DD
tienda		= flFuncts.fTienda()					# Identificacion de tienda
idBackup	= tienda + '_' + dia			  		# Identificacion del backup
tgzFile		= workDir + 'backup'+ idBackup +'.tgz'	# Archivo empaquetado donde queda el backup
logFileName	= workDir + '/logs/sincro'+ idBackup + '.log'	# Nombre del archivo para la huella del proceso

# Si no existe el directorio de logs, lo crea
if os.path.exists(workDir + '/logs'):
	pass
else:
	os.makedirs(workDir + '/logs', 0750)

# Crea el archivo log, si ya existe lo sobrescribe
logFile = open(logFileName, "w")

logFile.write("Iniciando sincronizacion en :" + fecha + ' ' + hora + '\n')

# Abre archivo con lista de objetos a respaldar:
with open(jsonFile) as files_file:
	# Carga el archivo en una estructura json en memoria:
	sincro = json.load(files_file)

# Inicia recorrido de la coleccion en memoria:
for key, value in sincro.iteritems():
	for disco, directorios in value.iteritems():
		logFile.write('Respaldando Disco: ' + disco + ':/ ...\n')
		for directorio, listaArchivos in directorios.iteritems():
			logFile.write('Respaldando Directorio: ' + disco + ':/' + directorio + '/ ...\n')
			for  archivo in listaArchivos:
				targetDir = workDirOut + archivo["DirTmp"]
				sourceDir = disco + ':/' + directorio + '/'
				
				# Si no existe el directorio destino, lo crea
				if os.path.exists(targetDir):
					pass
				else:
					os.makedirs(targetDir, 0750)

				origen = sourceDir + archivo["Nombre"]
				destino = targetDir + archivo["Nombre"]
				nodoOrigen = archivo["Nodo"]
				comprimir = archivo["Comprimir"]
				fileName = archivo["Nombre"]
				
				flFuncts.fCopyUtil(sourceDir, targetDir, fileName, comprimir, logFile, nodoOrigen)

# Empaquetado de archivos respaldados:
flFuncts.fTarBackup(tgzFile, workDir, logFile)

# FTP del backup:
if conFile.getboolean('BACKUP', 'FTP_activo'):
	FTPDir 		= conFile.get('BACKUP', 'FTPDir')		# Directorio destino para el FTP del backup
	FTPServer	= conFile.get('BACKUP', 'FTPServer')	# Destino para el FTP
	FTPPasswd	= conFile.get('BACKUP', 'FTPPasswd')	# Password usuario FTP
	FTPuser		= conFile.get('BACKUP', 'FTPuser')		# Usuario FTP
	FTPPort		= conFile.get('BACKUP', 'FTPPort')		# Usuario FTP
	flFuncts.fUploadFileFTP(tgzFile, FTPDir, FTPServer, FTPPort, FTPuser, FTPPasswd, logFile)

hora = time.strftime("%H%M%S")
logFile.write('FINAL RESPALDO en: ' + fecha + ' ' + hora + '\n')

# Cierra el archivo log:
logFile.close

# envia correo con log
if conFile.getboolean('BACKUP', 'sendEmail'):
	eMailFrom	= conFile.get('BACKUP', 'eMailFrom')	# El que envia el correo
	eMailTo		= conFile.get('BACKUP', 'eMailTo')		# Destinatarios del correo
	eMailSMTP	= conFile.get('BACKUP', 'eMailSMTP')	# Servidor SMTP
	eMailPort	= conFile.get('BACKUP', 'eMailPort')	# Puerto SMTP
	eMailPwd	= conFile.get('BACKUP', 'eMailPwd')		# Clave de acceso al SMTP
	eMailSubjct	= conFile.get('BACKUP', 'eMailSubjct')	# Asunto del correo
	eMailBody	= conFile.get('BACKUP', 'eMailBody')	# Asunto del correo
	eMailSubjct = eMailSubjct + tienda +  ' a ' + fecha
	eMailBody = eMailBody + tienda + ' a ' + fecha
	
	flFuncts.fSendEmail(eMailFrom, eMailTo, eMailSMTP, eMailPort, eMailSubjct, eMailBody, logFileName)