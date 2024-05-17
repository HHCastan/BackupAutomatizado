#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Respalda archivos VTA en servidor central
# Ejecutar en controlador: python2 -X4690shell RespVta.py
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
workDir     = conFile.get('PlanosVta', 'workDir')     # Carpeta de trabajo
fecha       = time.strftime("%Y%m%d")                 # Fecha actual
hora        = time.strftime("%H%M%S")                 # Hora actual
dia         = time.strftime("%A")                     # Dia de la semana
mes         = time.strftime("%m")                     # Mes del anio en letras
anio        = time.strftime("%Y")                     # Anio
fechaVTA    = flFuncts.getFechaVtaxPLU()              # Fecha interna del archivo VTA
diaVTA      = fechaVTA[6:]                            # Dia interno del archivo VTA
mesVTA      = fechaVTA[4:-2]                          # Mes interno del archivo VTA en letras
anioVTA     = fechaVTA[:4]                            # Anio interno del archivo VTA
                                                      
jsonFile    = workDir + 'Tiendas.JSON'                # Contiene list de tiendas y codigos
id_tienda   = flFuncts.fTienda()                      # Identificacion de tienda
nmb_tienda  = flFuncts.fNmbTienda(id_tienda, workDir) # Nombre de la tienda
idRespaldo  = id_tienda + '_' + diaVTA                # Identificacion del backup
nroErrores  = 0                                       # Contador de errores
                                                      
FTPDir      = conFile.get('PlanosVta', 'FTPDir')      # Directorio destino para el FTP del backup
FTPServer   = conFile.get('PlanosVta', 'FTPServer')   # Destino para el FTP
FTPPasswd   = conFile.get('PlanosVta', 'FTPPasswd')   # Password usuario FTP
FTPuser     = conFile.get('PlanosVta', 'FTPuser')     # Usuario FTP
FTPPort     = conFile.get('PlanosVta', 'FTPPort')     # Usuario FTP

logFileName = workDir + 'logs/PlanosVta'+ idRespaldo + '.log' # Nombre del archivo para la huella del proceso

# Arreglo con los meses del anio
meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

# Abre archivo con lista de tiendas:
with open(jsonFile) as files_file:
    # Carga el archivo en una estructura json en memoria:
    tiendas = json.load(files_file)

# Crea archivo huella de ejecuion:
logFile = open(logFileName, "w")

logFile.write("INICIANDO TRANSMISION EN :" + fecha + ' ' + hora + '\n')
logFile.write("Se detecta fecha interna en archivos :" + fechaVTA + '\n')

# Los Planos Vta se toman de C:/ADX_UDT1/:
sourceDir = 'C:/ADX_UDT1/'
vtaList = []
vtaList.append(sourceDir + 'VTATRAKF.DAT')
vtaList.append(sourceDir + 'VTAXVEN.DAT')
vtaList.append(sourceDir + 'VTAXTOF.DAT')
vtaList.append(sourceDir + 'VTAXPLU.DAT')
vtaList.append(sourceDir + 'VTAXMP.DAT')
vtaList.append(sourceDir + 'VTAXLOG.DAT')
vtaList.append(sourceDir + 'VTAXDCTO.DAT')
vtaList.append(sourceDir + 'VTAXBASE.DAT')
vtaList.append(sourceDir + 'CONSEFIS.DAT')
vtaList.append(sourceDir + 'AUTORIZA.DAT')
vtaList.append(sourceDir + 'VTAXIND.DAT')
# 2022-02-17: Por solicitud de desarrollo se adiciona C:/ADX_IDT4/EAMRPT12.DAT
vtaList.append('C:/ADX_IDT4/EAMRPT12.DAT')

# La carpeta donde se copian los vtaX al servidor FTP:

targetDir = FTPDir + '/' + id_tienda[-2:] + '-' + nmb_tienda + '/' + anioVTA  + '/' + mesVTA +  '/' + diaVTA
if int(id_tienda) > 99:
    targetDir = FTPDir + '/' + id_tienda[-3:] + '-' + nmb_tienda + '/' + anioVTA  + '/' + mesVTA +  '/' + diaVTA
    
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
    for vtaX in vtaList:
        logFile.write('Transmite: ' + vtaX + '\n')
        if os.path.isfile(vtaX):
            fh = open(vtaX, 'r')
            fileName = ntpath.basename(vtaX)
            myFTP.storbinary('STOR ' + fileName, fh)
            fh.close()
        else:
            logFile.write('No existe archivo a enviar: ' + vtaX + ' \n')
            nroErrores += 1

    logFile.write("Termina transmision de vtaX ...\n")
    # Elimina el archivo del short para evitar que se acumule
    flFuncts.fRemoveFile('C:/ADX_IDT4/EAMRPT12.DAT')

except (all_errors, Exception) as why:
    logFile.write("Error: No se puede enviar FTP\n\t" + str(why) + '\n')
    nroErrores += 1

hora = time.strftime("%H%M%S")
logFile.write('FINAL TRANSMISION EN: ' + fecha + ' ' + hora + '\n')

# Cierra el archivo log:
logFile.close

# envia correo con log si hubo errores
if conFile.getboolean('PlanosVta', 'sendEmail') and nroErrores > 0:
    eMailFrom   = conFile.get('PlanosVta', 'eMailFrom')   # El que envia el correo
    eMailTo     = conFile.get('PlanosVta', 'eMailTo')     # Destinatarios del correo
    eMailSMTP   = conFile.get('PlanosVta', 'eMailSMTP')   # Servidor SMTP
    eMailPort   = conFile.get('PlanosVta', 'eMailPort')   # Puerto SMTP
    eMailPwd    = conFile.get('PlanosVta', 'eMailPwd')    # Clave de acceso al SMTP
    eMailSubjct = conFile.get('PlanosVta', 'eMailSubjct') # Asunto del correo
    eMailBody   = conFile.get('PlanosVta', 'eMailBody')   # Asunto del correo
    eMailSubjct = eMailSubjct + id_tienda +  ' a ' + fechaVTA
    eMailBody = eMailBody + id_tienda + ' a ' + fechaVTA
    
    flFuncts.fSendEmail(eMailFrom, eMailTo, eMailSMTP, eMailPort, eMailSubjct, eMailBody, logFileName)
	
