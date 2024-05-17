#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Respalda archivos del tlog en servidor central
# Ejecutar en controlador: python2 -X4690shell RespTlog.py
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Diciembre de 2020   
# Referencia: nestor.marin@flamingo.com.co

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
workDir		= conFile.get('RespTlog', 'workDir')	# Carpeta de trabajo
fecha		= time.strftime("%Y%m%d")				# Fecha actual
hora		= time.strftime("%H%M%S")				# Hora actual
dia			= time.strftime("%A")					# Dia de la semana
mes			= time.strftime("%m")					# Mes del anio en letas
anio		= time.strftime("%Y")					# Anio
jsonFile	= workDir + 'Tiendas.JSON'				# Contiene list de tiendas y codigos
id_tienda	= flFuncts.fTienda()					# Identificacion de tienda
idRespaldo	= id_tienda + '_' + dia			  		# Identificacion del backup
nroErrores	= 0										# Contador de errores
fechaVTA    = flFuncts.getFechaVtaxPLU()            # Fecha interna del archivo VTA
diaVTA      = fechaVTA[6:]                          # Dia interno del archivo VTA
mesVTA      = fechaVTA[4:-2]                        # Mes interno del archivo VTA en letras
anioVTA     = fechaVTA[:4]                          # Anio interno del archivo VTA

logFileName	= workDir + 'logs/RespTlog'+ idRespaldo + '.log'	# Nombre del archivo para la huella del proceso
FTPDir 		= conFile.get('RespTlog', 'FTPDir')		# Directorio destino para el FTP del backup
FTPServer	= conFile.get('RespTlog', 'FTPServer')	# Destino para el FTP
FTPPasswd	= conFile.get('RespTlog', 'FTPPasswd')	# Password usuario FTP
FTPuser		= conFile.get('RespTlog', 'FTPuser')	# Usuario FTP
FTPPort		= conFile.get('RespTlog', 'FTPPort')	# Usuario FTP

# Arreglo con los meses del anio
meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

# Abre archivo con lista de tiendas:
with open(jsonFile) as files_file:
	# Carga el archivo en una estructura json en memoria:
	tiendas = json.load(files_file)

# Crea archivo huella de ejecuion:
logFile = open(logFileName, "w")

logFile.write("INICIANDO TRANSMISION EN :" + fecha + ' ' + hora + '\n')



# Los Tlogs se toman del respaldo generado en el cierre:

#fileName = 'LG' + time.strftime("%d%m%y") + '.' + id_tienda
fileName = 'LG' + diaVTA + mesVTA + anioVTA[-2:]  + '.' + id_tienda
tlogs = os.listdir('c:/respaldo/logtrx/')
for file in tlogs:
    if (file[:2] == 'LG' or file[:2] == 'lg'):
        fileName = file 
sourceDir = 'c:/respaldo/logtrx/'

# La carpeta donde se copian los tlogs al servidor FTP:
targetDir	= FTPDir + '/' + id_tienda[-3:] + '-' + tiendas[id_tienda] + '/' + anioVTA  + '/' +  meses[int(mesVTA) - 1] 
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
	tlog = sourceDir + fileName
	logFile.write('Transmite: ' + tlog + '\n')
	fh = open(tlog, 'r')
	fileName = ntpath.basename(tlog)
	myFTP.storbinary('STOR ' + fileName, fh)
	fh.close()

	logFile.write("Termina transmision de tlog ...\n")
except (all_errors, Exception) as why:
	logFile.write("Error: No se puede enviar FTP\n\t" + str(why) + '\n')
	nroErrores += 1

hora = time.strftime("%H%M%S")
logFile.write('FINAL TRANSMISION EN: ' + fecha + ' ' + hora + '\n')

# Cierra el archivo log:
logFile.close

# envia correo con log si hubo errores
if conFile.getboolean('RespTlog', 'sendEmail') and nroErrores > 0:
	eMailFrom	= conFile.get('RespTlog', 'eMailFrom')    # El que envia el correo
	eMailTo		= conFile.get('RespTlog', 'eMailTo')      # Destinatarios del correo
	eMailSMTP	= conFile.get('RespTlog', 'eMailSMTP')    # Servidor SMTP
	eMailPort	= conFile.get('RespTlog', 'eMailPort')    # Puerto SMTP
	eMailPwd	= conFile.get('RespTlog', 'eMailPwd')     # Clave de acceso al SMTP
	eMailSubjct	= conFile.get('RespTlog', 'eMailSubjct')  # Asunto del correo
	eMailBody	= conFile.get('RespTlog', 'eMailBody')    # Asunto del correo
	eMailSubjct = eMailSubjct + id_tienda +  ' a ' + fecha
	eMailBody   = eMailBody + id_tienda + ' a ' + fecha
	
	flFuncts.fSendEmail(eMailFrom, eMailTo, eMailSMTP, eMailPort, eMailSubjct, eMailBody, logFileName)