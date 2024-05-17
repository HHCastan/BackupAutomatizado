#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Respalda archivos del journal en servidor central
# Ejecutar en controlador: python2 -X4690shell RespJournal.py
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Marzo de 2017   

#######################################################################

import flFuncts
import os
import ConfigParser
import time
import socket
import ntpath
import json
from ftplib import FTP, error_perm, error_temp, all_errors

# Lee archivo de configuracion
conFile = ConfigParser.RawConfigParser()
conFile.read('backup.conf')

# Varibles de trabajo:
workDir		= conFile.get('RespJournal', 'workDir')	# Carpeta de trabajo
fecha		= time.strftime("%Y%m%d")				# Fecha actual
hora		= time.strftime("%H%M%S")				# Hora actual
dia			= time.strftime("%A")					# Dia de la semana
mes			= time.strftime("%m")					# Mes del anio en letas
anio		= time.strftime("%Y")					# Anio
jsonFile	= workDir + 'Tiendas.JSON'				# Contiene list de tiendas y codigos
id_tienda	= flFuncts.fTienda()					# Identificacion de tienda
idRespaldo	= id_tienda + '_' + dia			  		# Identificacion del backup
nroErrores	= 0										# Contador de errores

logFileName	= workDir + 'logs/RespJournal'+ idRespaldo + '.log'	# Nombre del archivo para la huella del proceso
FTPDir 		= conFile.get('RespJournal', 'FTPDir')		# Directorio destino para el FTP del backup
FTPServer	= conFile.get('RespJournal', 'FTPServer')	# Destino para el FTP
FTPPasswd	= conFile.get('RespJournal', 'FTPPasswd')	# Password usuario FTP
FTPuser		= conFile.get('RespJournal', 'FTPuser')		# Usuario FTP
FTPPort		= conFile.get('RespJournal', 'FTPPort')		# Usuario FTP

# Arreglo con los meses del anio
meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

# Abre archivo con lista de tiendas:
with open(jsonFile) as files_file:
	# Carga el archivo en una estructura json en memoria:
	tiendas = json.load(files_file)

# Crea archivo huella de ejecuion:
logFile = open(logFileName, "w")

logFile.write("INICIANDO TRANSMISION EN :" + fecha + ' ' + hora + '\n')


sourceDir = "C:/ej/j/"
targetDir = "m:/respaldo/out/ej/"
origen = sourceDir + "j??????"
destino = targetDir + "j??????"
nodoOrigen = "CC"
comprimir = "false"
fileName = "j??????"

# Primero depura la carpeta temporal para evitar pasar basura:
flFuncts.fEmptyFolder(targetDir)

flFuncts.fCopyUtil(sourceDir, targetDir, fileName, comprimir, logFile, nodoOrigen)

# Los jounals se toman del backup automatico:
journals = 'j??????'
sourceDir = 'm:/respaldo/out/ej/'
journalList = flFuncts.fFilelist(journals, sourceDir)
journalLog = sourceDir + fecha

# La carpeta donde se copian los journals al servidor FTP:
targetDir	= FTPDir + '/' + id_tienda[-2:] + '-' + tiendas[id_tienda].replace(" ", "_") + '/' + anio  + '/' +  mes + '-' + meses[int(mes) - 1] + '-' + anio
if int(id_tienda) > 99:
    targetDir	= FTPDir + '/' + id_tienda[-3:] + '-' + tiendas[id_tienda].replace(" ", "_") + '/' + anio  + '/' +  mes + '-' + meses[int(mes) - 1] + '-' + anio

logFile.write("Ruta de subida :" + targetDir + '\n')

# Incia la transferencia
try:
	myFTP = FTP()
	myFTP.connect(FTPServer, FTPPort)
	myFTP.login(FTPuser, FTPPasswd)
	# Cambia al directorio destno. Si no existe, lo crea
	def cdTree(currentDir):
		if currentDir != "":
			try:
				myFTP.cwd(currentDir)
			except (all_errors, Exception, IOError):
				cdTree("/".join(currentDir.split("/")[:-1]))
				myFTP.mkd(currentDir)
				myFTP.cwd(currentDir)
	
	cdTree(targetDir)
	for journal in journalList:
		logFile.write('Transmite: ' + journal + '\n')
		if os.path.isfile(journal):
			fh = open(journal, 'r')
			fileName = ntpath.basename(journal)
			myFTP.storbinary('STOR ' + fileName, fh)
			fh.close()
		else:
			logFile.write('No existe archivo a enviar\n')
			nroErrores += 1
    
	logFile.write('Transmite Log: ' + journalLog + '\n')
	if os.path.isfile(journalLog):
		fh = open(journalLog, 'r')
		fileName = ntpath.basename(journalLog)
		myFTP.storbinary('STOR ' + fileName, fh)
		fh.close()
	else:
		logFile.write('No existe journalLog a enviar\n')
		nroErrores += 1
	logFile.write("Termina transmision de Journal electronicos...\n")
except (all_errors, Exception) as why:
	logFile.write("Error: No se puede enviar FTP\n\t" + str(why) + '\n')
	nroErrores += 1

hora = time.strftime("%H%M%S")
logFile.write('FINAL TRANSMISION EN: ' + fecha + ' ' + hora + '\n')

# Cierra el archivo log:
logFile.close

# envia correo con log si hubo errores
if conFile.getboolean('RespJournal', 'sendEmail') and nroErrores > 0:
	eMailFrom	= conFile.get('RespJournal', 'eMailFrom')	# El que envia el correo
	eMailTo		= conFile.get('RespJournal', 'eMailTo')		# Destinatarios del correo
	eMailSMTP	= conFile.get('RespJournal', 'eMailSMTP')	# Servidor SMTP
	eMailPort	= conFile.get('RespJournal', 'eMailPort')	# Puerto SMTP
	eMailPwd	= conFile.get('RespJournal', 'eMailPwd')	# Clave de acceso al SMTP
	eMailSubjct	= conFile.get('RespJournal', 'eMailSubjct')	# Asunto del correo
	eMailBody	= conFile.get('RespJournal', 'eMailBody')	# Asunto del correo
	eMailSubjct = eMailSubjct + id_tienda +  ' a ' + fecha
	eMailBody = eMailBody + id_tienda + ' a ' + fecha
	
	flFuncts.fSendEmail(eMailFrom, eMailTo, eMailSMTP, eMailPort, eMailSubjct, eMailBody, logFileName)