#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Recupera los logs de FE desde las terminales
# Extrae los JSON de las FE
# Respalda esos JSON en servidor central
# Ejecutar en controlador: python3 -X4690shell RespJsonFE.py
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Noviembre de 2022

#######################################################################

import flFuncts
import os
from configparser import ConfigParser
import time
import socket
import ntpath
import json
import logging
import os4690
from ftplib import FTP, error_perm, error_temp, all_errors

#######################################################################
# Declaracion de variables gobales
#######################################################################


#######################################################################
# Function fTransferJsons
#######################################################################
# transmite por FTP la lista de archivos entregada
#######################################################################
def fTransferJsons(jsonFileList, myFTP, logFile, nroErrores):
    try:
        for fjname in jsonFileList:
            if os.path.isfile(fjname):
                logging.info('Conectando a FTP para transmitir ' + fjname + '...\n')
                fh = open(fjname, 'r')
                fileNameS = ntpath.basename(fjname)
                trace = myFTP.storbinary('STOR ' + fileNameS, fh)
                logging.info( trace + '\n')
                fh.close()
            else:
                logging.info('No existe archivo a enviar: ' + fjname + ' \n')
                nroErrores += 1
    except (all_errors,Exception, IOError) as why:
        logging.info('Error en FTP: ' + str(why) + '\n')
# FIN funcion	
   
# ##################################################################################################
# Main
#

# Lee archivo de configuracion
conFile = ConfigParser()
conFile.read(os4690.resolvepath('backup.conf'))

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
logFileName	= 'logs/RespJsonFE'+ idRespaldo + '.log'	# Nombre del archivo para la huella del proceso

# Arreglo con los meses del anio
meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']


# Crea archivo huella de ejecuion:
logging.basicConfig(filename=logFileName, level=logging.DEBUG)


logging.info("INICIANDO TRANSMISION EN :" + fecha + ' ' + hora + '\n')

# La carpeta donde se copian los vtaX al servidor FTP:
targetDir = FTPDir + '/' + id_tienda[-2:] + '-' + nmb_tienda + '/' + anio  + '/' + mes +  '/' + dia
if int(id_tienda) > 99:
    targetDir = FTPDir + '/' + id_tienda[-3:] + '-' + nmb_tienda + '/' + anio  + '/' + mes +  '/' + dia

logging.info("Ruta de subida: " + targetDir + '\n')    

remoteFE = 'f:/lds/logs/factura-electronica.log'
remoteFE2 = 'f:/lds/logs/factura-electronica.log.1'
fePM = 'f:/lds/logs/factura-electronica.log'
localDir = workDir + 'out/FE_logs'
fePMTarget = localDir + '/fe' + fecha + '_PM.log'


# Si no existe el directorio local lo crea
if os.path.exists(os4690.resolvepath(localDir)):
	pass
else:
	os.makedirs(os4690.resolvepath(localDir), 0o750)

# Incia la transferencia 
try:
    myFTP = FTP(FTPServer)
    myFTP.login(FTPuser, FTPPasswd)
    logging.info("Conectado con sitio " + FTPServer)
    # Cambia al directorio destno. Si no existe, lo crea
    def cdTree(currentDir):
        if currentDir != "":
            logging.info("Me ubico en directorio remoto: " + currentDir)
            try:
                myFTP.cwd(currentDir)
            except (all_errors, Exception, IOError):
                cdTree("/".join(currentDir.split("/")[:-1]))
                myFTP.mkd(currentDir)
                myFTP.cwd(currentDir)

    cdTree(targetDir)
    for trm in fixTrmList:
        fileName = localDir + '/fe' + fecha + '_' + trm[5:8] + '.log'
        fileName2 = localDir + '/fe' + fecha + '_' + trm[5:8] + '_2.log'
        logging.info('Inicia transmision de ' + fileName + ' y de ' + fileName2 + '\n')
        try:
            # inicia el copiado del log desde la terminal hacia el controlador
            flFuncts.fCopyFromTrm(trm, remoteFE, fileName, logFile)
            # Por si hubo cambio de log durante el dia, se trae tambien el segundo respaldo
            flFuncts.fCopyFromTrm(trm, remoteFE2, fileName2, logFile)
            logging.info('Archivos copiado correctamente\n')
            # concatena el log 2 al log 1:
            with open(fileName, "w") as l1:
                with open(fileName2) as l2:
                    for line in l2:
                        l1.write(line)
                    l1.write("\n")
            logging.info('concatenados los logs de ' + trm + '\n')
            # Extrae los JSON del log de java de la terminal
            jsonFileList = flFuncts.fExtractJsonFE(fileName, localDir, logFile)
            fTransferJsons(jsonFileList, myFTP, logFile, nroErrores)
        except (all_errors,Exception, IOError) as why:
            logging.info('Error procesando log: ' + str(why) + '\n')
            
    # FIN: for trm in fixTrmList:
    
    # copia archivo log de las por moviles
    if os.path.isfile(fePM):
        os.system('copy ' + fePM + ' ' + fePMTarget)
        jsonFileList = flFuncts.fExtractJsonFE(fePMTarget, localDir, logFile)
        fTransferJsons(jsonFileList, myFTP, logFile, nroErrores)
    else:
        os.system('No existe log de POS movil para procesar')

except (all_errors, Exception) as why:
    logging.info('Error: No se puede enviar FTP\n\t' + str(why) + '\n')
    nroErrores += 1
else:    
    logging.info('Finaliza sin errores\n')


# Cierra el archivo log:
logFile.close

