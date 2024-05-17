#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Respalda archivo de saldos en servidor central
# Ejecutar en controlador: python2 -X4690shell RespSaldos.py
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Enero de 2021   
# Referencia: nestor.marin@flamingo.com.co

#######################################################################

import flFuncts
import os
import ConfigParser
import time
import socket
import ntpath
import json
import zipfile
from ftplib import FTP, error_perm, error_temp, all_errors

# Lee archivo de configuracion
conFile = ConfigParser.RawConfigParser()
conFile.read('backup.conf')

# Varibles de trabajo:
workDir		= conFile.get('RespSaldos', 'workDir')	# Carpeta de trabajo
fecha		= time.strftime("%Y%m%d")				# Fecha actual
hora		= time.strftime("%H%M%S")				# Hora actual
dia			= time.strftime("%A")					# Dia de la semana
mes			= time.strftime("%m")					# Mes del anio en letas
anio		= time.strftime("%Y")					# Anio
jsonFile	= workDir + 'Tiendas.JSON'				# Contiene list de tiendas y codigos
id_tienda	= flFuncts.fTienda()					# Identificacion de tienda
idRespaldo	= id_tienda + '_' + dia			  		# Identificacion del backup
nroErrores	= 0										# Contador de errores

logfileSaldos	= workDir + 'logs/RespSaldos'+ idRespaldo + '.log'	# Nombre del archivo para la huella del proceso
FTPDir 		= conFile.get('RespSaldos', 'FTPDir')	 # Directorio destino para el FTP del backup
FTPServer	= conFile.get('RespSaldos', 'FTPServer') # Destino para el FTP
FTPPasswd	= conFile.get('RespSaldos', 'FTPPasswd') # Password usuario FTP
FTPuser		= conFile.get('RespSaldos', 'FTPuser')	 # Usuario FTP
FTPPort		= conFile.get('RespSaldos', 'FTPPort')	 # Usuario FTP

# Arreglo con los meses del anio
meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

# Abre archivo con lista de tiendas:
with open(jsonFile) as files_file:
	# Carga el archivo en una estructura json en memoria:
	tiendas = json.load(files_file)

# Crea archivo huella de ejecuion:
logFile = open(logfileSaldos, "w")

logFile.write("INICIANDO TRANSMISION EN :" + fecha + ' ' + hora + '\n')


# El archivos de Saldos se toman de adx_idt1:
sourceDir = 'c:/adx_idt1/'

# La carpeta donde se copian los saldos al servidor FTP:
targetDir	= FTPDir + '/' + id_tienda[-3:] + '-' + tiendas[id_tienda] + '/' + anio  + '/' +  meses[int(mes) - 1]  + '/SALDOS'
logFile.write('targetDir' + targetDir + '\n')

# Incia la transferencia
try:
	logFile.write('Estableciendo conexion con ' + FTPServer + '\n')
	myFTP = FTP()
	myFTP.connect(FTPServer, FTPPort)
	myFTP.login(FTPuser, FTPPasswd)
	logFile.write('Conexion exitosa \n')
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

	fSaldo = sourceDir + 'UFSALDOS.DAT'
	fZippeSaldo = sourceDir + 'UFSALDOS.ZIP'
	logFile.write('Comprimiendo ' + fSaldo + '...\n')
	saldoZip = zipfile.ZipFile(fZippeSaldo, 'w')
	saldoZip.write(fSaldo, 'UFSALDOS.DAT', compress_type=zipfile.ZIP_DEFLATED)
	saldoZip.close()
	
	logFile.write('Transmite: ' + fZippeSaldo + '\n')
	fh = open(fZippeSaldo, 'r')
	fileSaldos = ntpath.basename(fZippeSaldo)
	myFTP.storbinary('STOR ' + fileSaldos, fh)

	fOrden = sourceDir + 'UFORDENS.DAT'
	fZippeOrden = sourceDir + 'UFORDENS.ZIP'
	logFile.write('Comprimiendo ' + fOrden + '...\n')
	ordenZip = zipfile.ZipFile(fZippeOrden, 'w')
	ordenZip.write(fOrden, 'UFORDENS.DAT', compress_type=zipfile.ZIP_DEFLATED)
	ordenZip.close()

	logFile.write('Transmite: ' + fZippeOrden + '\n')
	fh = open(fZippeOrden, 'r')
	fileOden = ntpath.basename(fZippeOrden)
	myFTP.storbinary('STOR ' + fileOden, fh)

	fh.close()

	logFile.write("Termina transmision de Saldos y ordenes ...\n")
except (all_errors, Exception) as why:
	logFile.write("Error: No se puede enviar FTP\n\t" + str(why) + '\n')
	nroErrores += 1

hora = time.strftime("%H%M%S")
logFile.write('FINAL TRANSMISION EN: ' + fecha + ' ' + hora + '\n')

# Cierra el archivo log:
logFile.close

# envia correo con log si hubo errores
if conFile.getboolean('RespSaldos', 'sendEmail') and nroErrores > 0:
	eMailFrom	= conFile.get('RespSaldos', 'eMailFrom')	# El que envia el correo
	eMailTo		= conFile.get('RespSaldos', 'eMailTo')		# Destinatarios del correo
	eMailSMTP	= conFile.get('RespSaldos', 'eMailSMTP')	# Servidor SMTP
	eMailPort	= conFile.get('RespSaldos', 'eMailPort')	# Puerto SMTP
	eMailPwd	= conFile.get('RespSaldos', 'eMailPwd')	# Clave de acceso al SMTP
	eMailSubjct	= conFile.get('RespSaldos', 'eMailSubjct')	# Asunto del correo
	eMailBody	= conFile.get('RespSaldos', 'eMailBody')	# Asunto del correo
	eMailSubjct = eMailSubjct + id_tienda +  ' a ' + fecha
	eMailBody   = eMailBody + id_tienda + ' a ' + fecha
	
	flFuncts.fSendEmail(eMailFrom, eMailTo, eMailSMTP, eMailPort, eMailSubjct, eMailBody, logfileSaldos)