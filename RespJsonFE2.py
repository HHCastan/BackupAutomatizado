#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Recupera los logs de FE desde las terminales
# Extrae los JSON de las FE
# Respalda esos JSON en servidor central
# Ejecutar en controlador: python2 -X4690shell RespJsonFE2.py
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Noviembre de 2022

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

# La lista de terminales Fijas:
fixTrmList = flFuncts.fGetFixedTerminalList()

# Varibles de trabajo:
fecha		= time.strftime("%Y%m%d")				    # Fecha actual
hora		= time.strftime("%H%M%S")				    # Hora actual
dia			= time.strftime("%d")					    # Dia de la semana
mes			= time.strftime("%m")					    # Mes del anio en letas
anio		= time.strftime("%Y")					    # Anio
workDir		= conFile.get('RespJsonFE', 'workDir')	    # Carpeta de trabajo
FTPDir 		= conFile.get('RespJsonFE', 'FTPDir')		# Directorio destino para el FTP del backup
FTPServer	= conFile.get('RespJsonFE', 'FTPServer')	# Destino para el FTP
FTPPasswd	= conFile.get('RespJsonFE', 'FTPPasswd')	# Password usuario FTP
FTPuser		= conFile.get('RespJsonFE', 'FTPuser')		# Usuario FTP
FTPPort		= conFile.get('RespJsonFE', 'FTPPort')		# Usuario FTP
                                                        
jsonFile	= workDir + 'Tiendas.JSON'				    # Contiene list de tiendas y codigos
id_tienda	= flFuncts.fTienda()					    # Identificacion de tienda
nmb_tienda  = flFuncts.fNmbTienda(id_tienda, workDir)   # Nombre de la tienda
idRespaldo	= id_tienda + '_' + dia			  		    # Identificacion del backup
nroErrores	= 0										    # Contador de errores
logFileName	= workDir + 'logs/RespJsonFE'+ idRespaldo + '.log'	# Nombre del archivo para la huella del proceso

# Arreglo con los meses del anio
meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']


# Crea archivo huella de ejecuion:
logFile = open(logFileName, "w")

logFile.write("INICIANDO TRANSMISION EN :" + fecha + ' ' + hora + '\n')

# La carpeta donde se copian los vtaX al servidor FTP:
targetDir = FTPDir + '/' + id_tienda[-2:] + '-' + nmb_tienda + '/' + anio  + '/' + mes +  '/' + dia
if int(id_tienda) > 99:
    targetDir = FTPDir + '/' + id_tienda[-3:] + '-' + nmb_tienda + '/' + anio  + '/' + mes +  '/' + dia

logFile.write("Ruta de subida: " + targetDir + '\n')    

remoteFE = 'f:/lds/logs/factura-electronica.log'
remoteFE1 = 'f:/lds/logs/factura-electronica.log.1'
remoteFE2 = 'f:/lds/logs/factura-electronica.log.2'
remoteFE3 = 'f:/lds/logs/factura-electronica.log.3'
remoteFE4 = 'f:/lds/logs/factura-electronica.log.4'
remoteFE5 = 'f:/lds/logs/factura-electronica.log.5'
fePM = 'f:/lds/logs/factura-electronica_PM.log'
localDir = workDir + 'out/FE_logs'
fePMTarget = localDir + '/fe' + fecha + '_PM.log'


# Si no existe el directorio local lo crea
if os.path.exists(localDir):
	pass
else:
	os.makedirs(localDir, 0750)

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
    for trm in fixTrmList:
        fileName = localDir + '/fe' + fecha + '_' + trm[5:8] + '.log'
        fileName1 = localDir + '/fe' + fecha + '_' + trm[5:8] + '.1.log'
        fileName2 = localDir + '/fe' + fecha + '_' + trm[5:8] + '.2.log'
        fileName3 = localDir + '/fe' + fecha + '_' + trm[5:8] + '.3.log'
        fileName4 = localDir + '/fe' + fecha + '_' + trm[5:8] + '.4.log'
        fileName5 = localDir + '/fe' + fecha + '_' + trm[5:8] + '.5.log'
        logFile.write('Inicia transmision de ' + fileName + '\n')
        try:
            flFuncts.fCopyFromTrm(trm, remoteFE, fileName, logFile)
            flFuncts.fCopyFromTrm(trm, remoteFE1, fileName1, logFile)
            flFuncts.fCopyFromTrm(trm, remoteFE2, fileName2, logFile)
            flFuncts.fCopyFromTrm(trm, remoteFE3, fileName3, logFile)
            flFuncts.fCopyFromTrm(trm, remoteFE4, fileName4, logFile)
            flFuncts.fCopyFromTrm(trm, remoteFE5, fileName5, logFile)
            logFile.write('Archivo copiado correctamente\n')
            jsonFileList = flFuncts.fExtractJsonFE(fileName, localDir, logFile)
            jsonFileList = flFuncts.fExtractJsonFE(fileName1, localDir, logFile)
            jsonFileList = flFuncts.fExtractJsonFE(fileName2, localDir, logFile)
            jsonFileList = flFuncts.fExtractJsonFE(fileName3, localDir, logFile)
            jsonFileList = flFuncts.fExtractJsonFE(fileName4, localDir, logFile)
            jsonFileList = flFuncts.fExtractJsonFE(fileName5, localDir, logFile)
            for fjname in jsonFileList:
                if os.path.isfile(fjname):
                    logFile.write('Conectando...\n')
                    fh = open(fjname, 'r')
                    fileNameS = ntpath.basename(fjname)
                    trace = myFTP.storbinary('STOR ' + fileNameS, fh)
                    logFile.write( trace + '\n')
                    fh.close()
                else:
                    logFile.write('No existe archivo a enviar: ' + fjname + ' \n')
                    nroErrores += 1
        except (all_errors,Exception, IOError):
            logFile.write('Error copiando log desde ' + trm + '\n')
            
    # copia archivo log de las por moviles
    os.system('copy ' + fePM + ' ' + fePMTarget)
    fh = open(fePMTarget, 'r')
    fileNameS = ntpath.basename(fePMTarget)
    myFTP.storbinary('STOR ' + fileNameS, fh)
    fh.close()

except (all_errors, Exception) as why:
    logFile.write('Error: No se puede enviar FTP\n\t' + str(why) + '\n')
    nroErrores += 1
else:    
    logFile.write('Finaliza sin errores\n')


# Cierra el archivo log:
logFile.close

